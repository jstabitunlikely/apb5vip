def get_int(signal,
            suppress_error: bool = True) -> int:
    try:
        sig = int(signal.value)
    except ValueError as ve:
        if suppress_error:
            sig = 0
        else:
            raise ve
    return sig
