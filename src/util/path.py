def normalize_path(path: str):
    if path.startswith('.'):
        return path
    return './' + path


def normalize_paths(paths: list[str]):
    return [normalize_path(path) for path in paths]