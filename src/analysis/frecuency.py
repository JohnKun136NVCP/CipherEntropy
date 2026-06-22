from collections import Counter


def byte_frequency(data: bytes):
    freq = Counter(data)

    # vector de 256 posiciones
    vector = [0] * 256

    for byte_val, count in freq.items():
        vector[byte_val] = count

    return vector


def byte_frequency_normalized(data: bytes):
    freq = byte_frequency(data)
    total = len(data)

    if total == 0:
        return freq

    return [f / total for f in freq]
