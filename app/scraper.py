from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict

import requests
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

_memory_cache: Dict[str, str] = {}


class ScraperError(Exception):
    pass


def validate_url(url: str) -> str:
    if not url or not url.startswith(("http://", "https://")):
        raise ScraperError("Invalid URL. Use http:// or https://")
    return url.strip()


def _cache_key(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


def _cache_path(url: str) -> Path:
    return DATA_DIR / f"{_cache_key(url)}.json"


def _extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    lines = []
    for el in soup.find_all(["h1", "h2", "h3", "p", "li", "code", "pre"]):
        text = el.get_text(" ", strip=True)
        if text:
            lines.append(text)

    return "\n".join(lines)


# 🔥 IMPORTANT FIX
def filter_api_content(text: str) -> str:
    lines = text.split("\n")

    filtered = []
    for line in lines:
        l = line.lower()

        if (
            "/" in line
            or any(m in l for m in ["get", "post", "put", "delete", "patch"])
            or "endpoint" in l
            or "api" in l
        ):
            filtered.append(line)

    return "\n".join(filtered[:300])


def scrape_documentation(url: str) -> str:
    url = validate_url(url)

    if url in _memory_cache:
        return _memory_cache[url]

    cache_file = _cache_path(url)
    if cache_file.exists():
        cached = json.loads(cache_file.read_text())
        return cached["content"]

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    content = _extract_text(response.text)
    content = filter_api_content(content)  # 🔥 KEY FIX

    cache_file.write_text(json.dumps({"content": content}))
    _memory_cache[url] = content

    return content