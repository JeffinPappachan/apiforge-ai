import re
from typing import Dict, List


class GeneratorError(Exception):
    pass


def clean_function_name(path: str) -> str:
    """
    Convert API path into a valid Python function name
    """
    name = path.strip("/")

    # Replace invalid characters with underscore
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)

    # Remove multiple underscores
    name = re.sub(r"_+", "_", name)

    # Remove leading/trailing underscores
    name = name.strip("_")

    return name or "root"


def extract_params(params: List) -> List[str]:
    """
    Normalize params list (handles dict or string formats)
    """
    result = []
    for p in params:
        if isinstance(p, dict):
            result.append(p.get("name", "param"))
        else:
            result.append(str(p))
    return result


def generate_python_sdk(api: Dict) -> str:
    """
    Generate a clean Python SDK from API structure
    """
    base_url = api.get("base_url", "")
    endpoints = api.get("endpoints", [])

    if not base_url:
        raise GeneratorError("Missing base_url in API data.")

    lines = []
    lines.append("import requests\n")
    lines.append("class APIClient:")
    lines.append("    def __init__(self, base_url=None):")
    lines.append(f"        self.base_url = base_url or '{base_url}'\n")

    for ep in endpoints:
        method = ep.get("method", "GET").lower()
        path = ep.get("path", "/")
        params = extract_params(ep.get("params", []))

        func_name = clean_function_name(path)

        # Function name prefix
        if method == "get":
            prefix = "get"
        elif method == "post":
            prefix = "create"
        elif method == "put":
            prefix = "update"
        elif method == "delete":
            prefix = "delete"
        else:
            prefix = method

        full_func_name = f"{prefix}_{func_name}"

        # Build parameter signature
        param_signature = ", ".join(params) if params else ""
        if param_signature:
            param_signature = ", " + param_signature

        lines.append(f"    def {full_func_name}(self{param_signature}):")

        # Build params dict
        if params:
            param_dict = ", ".join([f"'{p}': {p}" for p in params])
            lines.append(f"        params = {{{param_dict}}}")
        else:
            lines.append("        params = None")

        # HTTP request
        if method == "get":
            lines.append(
                f"        return requests.get(f'{{self.base_url}}{path}', params=params)\n"
            )

        elif method == "post":
            lines.append(
                f"        return requests.post(f'{{self.base_url}}{path}', json=params)\n"
            )

        elif method == "put":
            lines.append(
                f"        return requests.put(f'{{self.base_url}}{path}', json=params)\n"
            )

        elif method == "delete":
            lines.append(
                f"        return requests.delete(f'{{self.base_url}}{path}', params=params)\n"
            )

        else:
            lines.append(
                f"        return requests.request('{method.upper()}', f'{{self.base_url}}{path}', params=params)\n"
            )

    lines.append("\n# Example usage")
    lines.append("client = APIClient()")

    return "\n".join(lines)