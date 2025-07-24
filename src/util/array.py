def unique(seq, key=None):
    seen = set()
    seen_add = seen.add
    for item in seq:
        if key is None:
            value = item
        elif isinstance(item, dict):
            value = item[key]
        else:
            value = getattr(item, key)
        if value in seen:
            continue
        seen_add(value)
        yield item