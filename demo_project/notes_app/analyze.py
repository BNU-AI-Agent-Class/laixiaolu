"""analyze.py — 对笔记做一些统计。"""
from collections import Counter
from .store import all_notes


def tag_counts():
    """统计每个标签出现了多少次,返回按次数排序的列表。"""
    counter = Counter()
    for note in all_notes():
        counter.update(note["tags"])
    return counter.most_common()


def summary():
    """生成一段统计摘要。"""
    notes = all_notes()
    counts = tag_counts()
    if not counts:
        return f"共有 {len(notes)} 条笔记。\n还没有任何标签。"
    top_tag = counts[0][0]
    lines = [
        f"共有 {len(notes)} 条笔记。",
        f"最常用的标签是 #{top_tag}。",
        f"一共用过 {len(counts)} 个不同标签。",
    ]
    return "\n".join(lines)
