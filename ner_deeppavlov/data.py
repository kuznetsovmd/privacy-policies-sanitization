

def add_pad(array, pad_item):
    return [pad_item, *array, pad_item]


def boundries(array, coords, tags):
    boundries = []
    start = -1
    for i, d in enumerate(array):
        if any([d == t for t in tags]) and start < 0:
            start = coords[i][0]
        if all([d != t for t in tags]) and start >= 0:
            boundries.append((start, coords[i-1][1]))
            start = -1
    return boundries


def unwrap(array):
    return [ai for a in array for ai in a]