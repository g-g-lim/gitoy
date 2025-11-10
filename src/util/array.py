def unique(seq, key=None):
    seen = set()
    for item in seq:
        if key is None:
            value = item
        elif isinstance(item, dict):
            value = item[key]
        elif callable(getattr(item, key, None)):
            value = getattr(item, key)()
        elif getattr(item, key) is not None:
            value = getattr(item, key)
        else:
            value = item[key]
        if value in seen:
            continue
        seen.add(value)
        yield item