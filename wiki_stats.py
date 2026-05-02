#!/usr/bin/env python3
"""Wiki 文件统计工具 — 可被 app.py 调用，也可命令行独立运行。"""
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

WIKI_BASE = Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents/爱马仕华/wiki/wiki/concepts"


def collect_stats(wiki_dir: Path) -> Dict:
    """扫描目录下的 .md 文件，返回统计结果字典。"""
    if not wiki_dir.exists():
        return {"error": f"目录不存在: {wiki_dir}"}

    files = list(wiki_dir.rglob("*.md"))
    if not files:
        return {"error": f"在 {wiki_dir} 下没有找到任何 .md 文件"}

    stats_list = []
    total_chars = 0
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
            chars = len(text)
            total_chars += chars
            stats_list.append({
                "path": f,
                "name": f.name,
                "relative": str(f.relative_to(wiki_dir)),
                "chars": chars,
                "mtime": f.stat().st_mtime,
            })
        except Exception:
            pass

    stats_list.sort(key=lambda x: x["chars"], reverse=True)

    return {
        "dir": str(wiki_dir),
        "total_files": len(stats_list),
        "total_chars": total_chars,
        "largest": stats_list[0] if stats_list else None,
        "smallest": stats_list[-1] if stats_list else None,
        "recent3": sorted(stats_list, key=lambda x: x["mtime"], reverse=True)[:3],
        "all_files": stats_list,
    }


def fmt_size(chars: int) -> str:
    if chars >= 1_000_000:
        return f"{chars / 1_000_000:.1f}M"
    if chars >= 1_000:
        return f"{chars / 1_000:.1f}K"
    return str(chars)


def print_report(stats: Dict) -> None:
    """命令行输出统计报告。"""
    if "error" in stats:
        print(stats["error"])
        return

    print("=" * 50)
    print(f"{'Wiki Concepts 统计报告':^50}")
    print("=" * 50)
    print(f"  扫描目录 : {stats['dir']}")
    print(f"  文件数量 : {stats['total_files']} 个 .md 文件")
    print(f"  总字符数 : {fmt_size(stats['total_chars'])} 字符")
    print()
    print("── 最大文件 " + "─" * 30)
    s = stats["largest"]
    print(f"  {s['name']}  ({fmt_size(s['chars'])} 字符)")
    print(f"  路径: {s['relative']}")
    print()
    print("── 最小文件 " + "─" * 30)
    s = stats["smallest"]
    print(f"  {s['name']}  ({fmt_size(s['chars'])} 字符)")
    print(f"  路径: {s['relative']}")
    print()
    print("── 最近修改的 3 个文件 " + "─" * 15)
    for i, s in enumerate(stats["recent3"], 1):
        mtime_str = datetime.fromtimestamp(s["mtime"]).strftime("%Y-%m-%d %H:%M")
        print(f"  {i}. {s['name']}")
        print(f"     修改时间: {mtime_str}  大小: {fmt_size(s['chars'])} 字符")
    print("=" * 50)


def main():
    if len(sys.argv) > 1:
        wiki_dir = Path(sys.argv[1])
    else:
        wiki_dir = WIKI_BASE
    stats = collect_stats(wiki_dir)
    print_report(stats)


if __name__ == "__main__":
    main()
