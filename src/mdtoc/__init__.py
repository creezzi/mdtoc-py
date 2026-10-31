"""Markdown table of contents generation with GitHub style anchors."""
from __future__ import annotations

import re
from typing import List, Tuple

__all__ = ["headings", "build_toc", "update"]

START, END = "<!-- toc -->", "<!-- /toc -->"


def _anchor(title: str) -> str:
    text = re.sub(r"[`*_]", "", title).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def headings(markdown: str, max_level: int = 6) -> List[Tuple[int, str, str]]:
    """(level, title, anchor) for each ATX heading outside fenced code blocks."""
    found, seen, fence = [], {}, None
    for line in markdown.splitlines():
        marker = re.match(r"^\s*(```|~~~)", line)
        if marker:
            fence = None if fence == marker.group(1) else (fence or marker.group(1))
            continue
        if fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if not m or len(m.group(1)) > max_level:
            continue
        title = m.group(2)
        anchor = _anchor(title)
        count = seen.get(anchor, 0)
        seen[anchor] = count + 1
        found.append((len(m.group(1)), title, anchor if not count else f"{anchor}-{count}"))
    return found


def build_toc(markdown: str, max_level: int = 3) -> str:
    items = [h for h in headings(markdown, max_level) if h[2]]
    if not items:
        return ""
    base = min(level for level, _, _ in items)
    return "\n".join(f"{'  ' * (level - base)}- [{title}](#{anchor})" for level, title, anchor in items)


def update(markdown: str, max_level: int = 3) -> str:
    """Replace the block between the toc markers, excluding the marker lines from the TOC."""
    if START not in markdown or END not in markdown:
        raise ValueError(f"missing {START} / {END} markers")
    head, rest = markdown.split(START, 1)
    _, tail = rest.split(END, 1)
    toc = build_toc(head + tail, max_level)
    return f"{head}{START}\n{toc}\n{END}{tail}"
