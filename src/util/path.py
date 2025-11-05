def normalize_path(path: str):
    if path.startswith("."):
        return path
    return "./" + path


def normalize_paths(paths: list[str]):
    return [normalize_path(path) for path in paths]


def accumulate_paths(path: str):
    parts = path.split("/")
    result = []
    for i in range(1, len(parts) + 1):
        prefix = "." if parts[0] == "." else ""
        joined = "/".join(parts[:i])
        # 첫 번째가 '.'이면 항상 './'로 시작하게
        if prefix and not joined.startswith("./"):
            joined = prefix + joined.lstrip(".")
        result.append(joined)
    return result
