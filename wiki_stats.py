#!/usr/bin/env python3
import sys
from pathlib import Path
from datetime import datetime

WIKI_BASE = Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents/爱马仕华/wiki/wiki/concepts"


def fmt_size(chars):
    if chars >= 1_000_000:
        return f"{chars / 1_000_000:.1f}M 字符"
    if chars >= 1_000:
        return f"{chars / 1_000:.1f}K 字符"
    return f"{chars} 字符"


def main():
    # 支持命令行参数指定目录，默认用 wiki 路径
    if len(sys.argv) > 1:
        wiki_dir = Path(sys.argv[1])
    else:
        wiki_dir = WIKI_BASE

    if not wiki_dir.exists():
        print(f"目录不存在: {wiki_dir}")
        return

    files = list(wiki_dir.rglob("*.md"))

    if not files:
        print(f"在 {wiki_dir} 下没有找到任何 .md 文件")
        return

    stats = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            mtime = f.stat().st_mtime
            stats.append({"path": f, "chars": len(content), "mtime": mtime})
        except OSError:
            pass

    total_files = len(stats)
    total_chars = sum(s["chars"] for s in stats)
    by_chars = sorted(stats, key=lambda s: s["chars"])
    by_mtime = sorted(stats, key=lambda s: s["mtime"], reverse=True)

    largest = by_chars[-1]
    smallest = by_chars[0]
    recent3 = by_mtime[:3]

    print("=" * 50)
    print("       Wiki Concepts 统计报告")
    print("=" * 50)
    print(f"  扫描目录 : {wiki_dir}")
    print(f"  文件数量 : {total_files} 个 .md 文件")
    print(f"  总字符数 : {fmt_size(total_chars)}")
    print()

    print("── 最大文件 ──────────────────────────────")
    print(f"  {largest['path'].name}  ({fmt_size(largest['chars'])})")
    print(f"  路径: {largest['path'].relative_to(wiki_dir)}")
    print()

    print("── 最小文件 ──────────────────────────────")
    print(f"  {smallest['path'].name}  ({fmt_size(smallest['chars'])})")
    print(f"  路径: {smallest['path'].relative_to(wiki_dir)}")
    print()

    print("── 最近修改的 3 个文件 ───────────────────")
    for i, s in enumerate(recent3, 1):
        mtime_str = datetime.fromtimestamp(s["mtime"]).strftime("%Y-%m-%d %H:%M")
        print(f"  {i}. {s['path'].name}")
        print(f"     修改时间: {mtime_str}  大小: {fmt_size(s['chars'])}")
    print("=" * 50)


if __name__ == "__main__":
    main()
