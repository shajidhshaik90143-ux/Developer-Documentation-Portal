import json
import re
import html
from datetime import datetime

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"[-\s]+", "-", text).strip("-")

def tags_list(tags):
    return [x.strip() for x in (tags or "").split(",") if x.strip()]

def document_to_dict(row):
    return {k: row[k] for k in row.keys()}

def export_json(rows):
    return json.dumps([document_to_dict(r) for r in rows], indent=2, ensure_ascii=False)

def export_markdown(row):
    meta = f"""---
title: {row['title']}
slug: {row['slug']}
category: {row['category']}
tags: {row['tags']}
author: {row['author']}
status: {row['status']}
difficulty: {row['difficulty']}
---

"""
    return meta + row["content"]

def safe_filename(name):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_") or "document"

def reading_time(text):
    words = len((text or "").split())
    return max(1, round(words / 200))

def parse_import_json(raw):
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("JSON root must be a list of documents.")
    return data

def format_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return value
