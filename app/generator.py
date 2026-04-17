def generate_sdk(api: dict) -> str:
    base_url = api.get("base_url", "")
    endpoints = api.get("endpoints", [])

    lines = []
    lines.append("import requests\n")
    lines.append("class APIClient:")
    lines.append("    def __init__(self):")
    lines.append(f"        self.base_url = '{base_url}'\n")

    for ep in endpoints:
        method = ep["method"].lower()
        path = ep["path"]

        func_name = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
        if not func_name:
            func_name = "root"

        if method == "get":
            lines.append(f"    def get_{func_name}(self):")
            lines.append(f"        return requests.get(f'{{self.base_url}}{path}')\n")

        elif method == "post":
            lines.append(f"    def create_{func_name}(self, data):")
            lines.append(f"        return requests.post(f'{{self.base_url}}{path}', json=data)\n")

        elif method == "put":
            lines.append(f"    def update_{func_name}(self, data):")
            lines.append(f"        return requests.put(f'{{self.base_url}}{path}', json=data)\n")

        elif method == "delete":
            lines.append(f"    def delete_{func_name}(self):")
            lines.append(f"        return requests.delete(f'{{self.base_url}}{path}')\n")

    lines.append("\n# Example usage")
    lines.append("client = APIClient()")

    return "\n".join(lines)