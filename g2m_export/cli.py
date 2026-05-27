import argparse
import sys
import yaml
from datetime import datetime
from pathlib import Path
from .git_utils import (
    get_git_root,
    get_remote_url,
    get_current_branch,
    parse_repo_info,
)
from .scanner import scan_files
from .markdown_writer import (
    generate_header,
    generate_file_section,
    write_to_file,
)


def load_config(config_path: Path) -> dict:
    """指定されたパスからYAML形式の設定ファイルを読み込む。

    ファイルが存在しない、または内容が空の場合は空の辞書を返す。
    読み込みに失敗した場合は、エラーメッセージを表示し空の辞書を返す。
    """
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config if config is not None else {}
        except yaml.YAMLError as e:
            print(
                f"設定ファイルの解析に失敗しました（現象）。{config_path} の内容が正しいYAML形式か確認してください（対処方法）。詳細: {e}（原因）"
            )
            return {}
        except OSError as e:
            print(
                f"設定ファイルの読み込みに失敗しました（現象）。{config_path} のアクセス権限などを確認してください（対処方法）。詳細: {e}（原因）"
            )
            return {}
    return {}


def main():
    parser = argparse.ArgumentParser(
        description="G2M-Export: Gitリポジトリを単一のMarkdownファイルにエクスポートします。"
    )
    parser.add_argument(
        "src_dir",
        nargs="?",
        default=".",
        help="スキャン対象のディレクトリ (既定: カレントディレクトリ)",
    )
    parser.add_argument(
        "--config", default="g2m_config.yaml", help="設定ファイルのパス"
    )
    parser.add_argument("--output", help="出力するMarkdownファイルのパス")
    parser.add_argument("--output-dir", help="出力先のディレクトリ")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=None,
        help="既存の出力ファイルを上書きする",
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_false",
        dest="overwrite",
        help="既存の出力ファイルを上書きしない (既定)",
    )
    parser.add_argument(
        "--max-mb",
        type=float,
        help="1ファイルあたりの最大サイズ(MB) (既定: 95.0)",
    )
    parser.add_argument(
        "--stop-threshold-mb",
        type=float,
        help="実行全体での処理合計サイズ上限(MB) (既定: 950.0)",
    )

    args = parser.parse_args()

    src_dir = Path(args.src_dir).resolve()

    config_path = Path(args.config)
    # 明示的に指定されていない場合、スキャン対象ディレクトリ直下の設定ファイルを優先的に探す
    if args.config == "g2m_config.yaml":
        src_config = src_dir / "g2m_config.yaml"
        if src_config.exists():
            config_path = src_config

    config = load_config(config_path)
    ignore_patterns = config.get("ignore_patterns", [])
    binary_extensions = config.get("binary_extensions", [])
    output_dir_config = config.get("output_dir", "output")
    overwrite_config = config.get("overwrite", False)
    max_mb_config = config.get("max_mb", 95.0)
    stop_threshold_mb_config = config.get("stop_threshold_mb", 950.0)

    # 優先順位: コマンドライン引数 > 設定ファイル > デフォルト
    overwrite = overwrite_config
    if args.overwrite is not None:
        overwrite = args.overwrite

    max_mb = args.max_mb if args.max_mb is not None else max_mb_config
    stop_threshold_mb = (
        args.stop_threshold_mb
        if args.stop_threshold_mb is not None
        else stop_threshold_mb_config
    )

    output_dir = Path(args.output_dir or output_dir_config)
    if not output_dir.is_absolute():
        # 出力ディレクトリが相対パスで指定された場合、カレントディレクトリを基準に解決する
        output_dir = Path.cwd() / output_dir

    git_root = get_git_root(src_dir)
    remote_url = ""
    branch = ""
    if git_root:
        remote_url = get_remote_url(git_root)
        branch = get_current_branch(git_root)

    if args.output:
        output_path_base = Path(args.output)
        if not output_path_base.is_absolute():
            output_path_base = output_dir / output_path_base
    else:
        # 出力先が指定されていない場合、Gitリポジトリ名やディレクトリ名に基づいたファイル名を自動生成する
        if git_root:
            proj_key, repo_name = parse_repo_info(remote_url)
            if not repo_name:
                repo_name = git_root.name

            if proj_key:
                base_name = f"【Repo】 {proj_key}_{repo_name}"
            else:
                base_name = f"【Repo】 {repo_name}"
        else:
            base_name = f"【Dir】 {src_dir.name}"

        if not overwrite:
            # 実行時点のタイムスタンプを取得 (Suffix用)
            now = datetime.now()
            suffix = now.strftime("_%y%m%d_%H%M%S")
            filename = f"{base_name}{suffix}.md"
        else:
            filename = f"{base_name}.md"

        output_path_base = output_dir / filename

    # 上書き不許可時にファイルが既に存在するかチェック (分割なしの場合のベースパス)
    if not overwrite and output_path_base.exists():
        print(
            f"出力ファイルが既に存在します（現象）。既存のファイルを移動するか、--overwrite オプションを指定してください（対処方法）。詳細: {output_path_base} が既に存在します（原因）"
        )
        sys.exit(1)

    # 出力先ディレクトリの作成
    try:
        output_path_base.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(
            f"出力先ディレクトリの作成に失敗しました（現象）。権限を確認してください（対処方法）。詳細: {e}（原因）"
        )
        sys.exit(1)

    # 上書き許可時、古い分割ファイル（_2.md, _3.md など）が残っている場合は削除する
    if overwrite and output_path_base.parent.exists():
        for p in output_path_base.parent.iterdir():
            if (
                p.is_file()
                and p.name.startswith(output_path_base.stem + "_")
                and p.name.endswith(output_path_base.suffix)
            ):
                idx_str = p.stem[len(output_path_base.stem) + 1 :]
                if idx_str.isdigit():
                    try:
                        p.unlink()
                    except OSError:
                        pass

    print(f"{src_dir} をスキャン中...")
    files = sorted(scan_files(src_dir, ignore_patterns, binary_extensions))
    print(f"{len(files)} 個のファイルが見つかりました。")

    max_bytes = max_mb * 1024 * 1024
    stop_threshold_bytes = stop_threshold_mb * 1024 * 1024
    total_bytes_written = 0
    file_index = 1
    current_content = []
    current_content_bytes = 0

    header = generate_header(git_root.name if git_root else src_dir.name)
    header_bytes = len(header.encode("utf-8"))

    def get_output_path(base_path: Path, index: int) -> Path:
        if index == 1:
            return base_path
        return base_path.with_name(f"{base_path.stem}_{index}{base_path.suffix}")

    def flush_content(content_list, index):
        nonlocal total_bytes_written
        content_str = "\n".join(content_list)
        out_path = get_output_path(output_path_base, index)

        # 書き込み可能か事前にチェックする (J2Mの仕様に合わせて各分割ファイルでもチェック)
        if not overwrite and out_path.exists():
            print(
                f"出力ファイルが既に存在します（現象）。既存のファイルを移動するか、--overwrite オプションを指定してください（対処方法）。詳細: {out_path} が既に存在します（原因）"
            )
            sys.exit(1)

        try:
            if out_path.exists():
                with open(out_path, "r+", encoding="utf-8"):
                    pass
            else:
                with open(out_path, "a", encoding="utf-8"):
                    pass
        except OSError as e:
            print(
                f"出力ファイルへのアクセス権限がないか、ファイルがロックされています（現象）。出力先の権限や他プログラムでの利用状況を確認してください（対処方法）。詳細: {e}（原因）"
            )
            sys.exit(1)

        try:
            write_to_file(out_path, content_str)
            written_size = len(content_str.encode("utf-8"))
            total_bytes_written += written_size
            print(
                f"{out_path} にエクスポートされました。 ({written_size / (1024 * 1024):.2f} MB)"
            )
        except OSError as e:
            print(
                f"ファイルの書き出しに失敗しました（現象）。出力先ディレクトリの権限やディスク容量を確認してください（対処方法）。詳細: {e}（原因）"
            )
            sys.exit(1)

    current_content.append(header)
    current_content_bytes += header_bytes

    for file_path in files:
        section = generate_file_section(src_dir, file_path, remote_url, branch)
        section_bytes = len(section.encode("utf-8"))

        # 全体制限のチェック
        if (
            total_bytes_written + current_content_bytes + section_bytes
            > stop_threshold_bytes
        ):
            print(
                f"全体サイズ制限 ({stop_threshold_mb} MB) を超えるため、スキャンを中断します。"
            )
            break

        # 1ファイル制限のチェック
        if (
            current_content_bytes + section_bytes > max_bytes
            and len(current_content) > 1
        ):
            # 現在の内容を書き出し、新しいファイルを開始
            flush_content(current_content, file_index)
            file_index += 1
            current_content = [header, section]
            current_content_bytes = header_bytes + section_bytes
        else:
            current_content.append(section)
            current_content_bytes += section_bytes

    if current_content and len(current_content) > 1:
        flush_content(current_content, file_index)
    elif file_index == 1 and current_content:
        # ファイルが1つも見つからなかった場合でも、ヘッダーのみ出力するか？
        # 現状のJ2Mの挙動に合わせるなら、ヘッダーのみでも出力する。
        # ただし、filesが空の場合は len(current_content) == 1 (headerのみ)
        flush_content(current_content, file_index)


if __name__ == "__main__":
    main()
