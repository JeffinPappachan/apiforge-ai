from __future__ import annotations

import json
import re


class ParserError(Exception):
    pass


def _extract_json_block(payload: str) -> str:
    payload = payload.strip()
    payload = payload.replace("```json", "").replace("```", "")

    match = re.search(r"\{.*\}", payload, re.DOTALL)
    if not match:
        raise ParserError("No JSON found")

    return match.group(0)


def normalize_api_structure(raw_text: str) -> dict:
    try:
        data = json.loads(_extract_json_block(raw_text))
    except Exception:
        data = {}

    base_url = data.get("base_url", "")
    auth = data.get("auth", "None")
    endpoints = data.get("endpoints", [])

    # 🔥 FALLBACK (NO FAIL SYSTEM)
    if not endpoints:
        matches = re.findall(r"(GET|POST|PUT|DELETE)\s+(/[a-zA-Z0-9/_{}-]+)", raw_text)

        for method, path in matches:
            endpoints.append({
                "path": path,
                "method": method,
                "description": "",
                "params": []
            })

    if not endpoints:
        raise ParserError("No API endpoints found")

    return {
        "base_url": base_url,
        "auth": auth,
        "endpoints": endpoints,
    }