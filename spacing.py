
def height(total, percent, inset):
    """
    Args:
        avail_w
        avail_h
        insets
    Raises:
        ValueError: Split is too large and will not fit.
    """
    assert percent <= 1.0, "percentage must be in (0.0, 1.0]"
    wanted = percent * total_height
    available = total - inset
    if available >= wanted:
        return wanted
    else:
        raise ValueError("Split height is too large for screen.")
