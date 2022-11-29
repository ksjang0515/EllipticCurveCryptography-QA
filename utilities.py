def number_to_binary(num, length=None):
    binary = (
        list(map(int, reversed(bin(num)[2:].zfill(length))))
        if length
        else list(map(int, reversed(bin(num)[2:])))
    )
    return binary
