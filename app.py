#!/usr/bin/env python3
"""Wiki Stats — Web 版"""
from pathlib import Path
from flask import Flask, render_template_string

from wiki_stats import collect_stats, fmt_size
from datetime import datetime

app = Flask(__name__)

# 服务器上的 wiki 路径
SERVER_WIKI_DIR = Path("/home/hermeshua/wiki/wiki/concepts")
# 本地开发用
LOCAL_WIKI_DIR = Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents/爱马仕华/wiki/wiki/concepts"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wiki 统计</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
            padding: 40px 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        h1 {
            font-size: 28px;
            color: #1a1a1a;
            margin-bottom: 8px;
        }
        .subtitle { color: #666; margin-bottom: 30px; font-size: 14px; }
        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            text-align: center;
        }
        .card .number { font-size: 32px; font-weight: 700; color: #2563eb; }
        .card .label { font-size: 13px; color: #666; margin-top: 4px; }
        .section {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .section h2 {
            font-size: 16px;
            color: #1a1a1a;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid #eee;
        }
        .file-item {
            padding: 8px 0;
            border-bottom: 1px solid #f5f5f5;
        }
        .file-item:last-child { border-bottom: none; }
        .file-name { font-weight: 500; color: #2563eb; font-size: 14px; }
        .file-meta { font-size: 12px; color: #888; margin-top: 2px; }
        .file-size { display: inline-block; background: #e8f0fe; color: #2563eb; padding: 1px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
        @media (max-width: 600px) {
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Wiki 统计</h1>
        <p class="subtitle">{{ stats.dir }}</p>

        <div class="grid">
            <div class="card">
                <div class="number">{{ stats.total_files }}</div>
                <div class="label">文件总数</div>
            </div>
            <div class="card">
                <div class="number">{{ fmt_size(stats.total_chars) }}</div>
                <div class="label">总字符数</div>
            </div>
            <div class="card">
                <div class="number">{{ stats.all_files|length }}</div>
                <div class="label">扫描文件</div>
            </div>
        </div>

        <div class="section">
            <h2>📄 最大文件</h2>
            <div class="file-item">
                <div class="file-name">{{ stats.largest.name }}</div>
                <div class="file-meta">{{ fmt_size(stats.largest.chars) }} 字符 · {{ stats.largest.relative }}</div>
            </div>
        </div>

        <div class="section">
            <h2>📄 最小文件</h2>
            <div class="file-item">
                <div class="file-name">{{ stats.smallest.name }}</div>
                <div class="file-meta">{{ fmt_size(stats.smallest.chars) }} 字符 · {{ stats.smallest.relative }}</div>
            </div>
        </div>

        <div class="section">
            <h2>🕐 最近修改</h2>
            {% for f in stats.recent3 %}
            <div class="file-item">
                <div class="file-name">{{ f.name }}</div>
                <div class="file-meta">
                    {{ f.mtime_str }} · <span class="file-size">{{ fmt_size(f.chars) }}</span>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>"""


def _choose_wiki_dir() -> Path:
    """自动选择 wiki 目录：优先服务器路径，其次本地路径。"""
    if SERVER_WIKI_DIR.exists():
        return SERVER_WIKI_DIR
    return LOCAL_WIKI_DIR


@app.route("/")
def index():
    wiki_dir = _choose_wiki_dir()
    stats = collect_stats(wiki_dir)

    if "error" in stats:
        return f"<h1>出错</h1><p>{stats['error']}</p>", 500

    # 格式化时间
    for f in stats["recent3"]:
        f["mtime_str"] = datetime.fromtimestamp(f["mtime"]).strftime("%Y-%m-%d %H:%M")

    return render_template_string(HTML_TEMPLATE, stats=stats, fmt_size=fmt_size)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
