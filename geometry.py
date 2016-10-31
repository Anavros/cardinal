
import malt

def inside(point, quad):
    """
    >>> quad = [
    ... (0, 2), (2, 2),
    ... (0, 0), (2, 0)
    ... ]
    >>> inside((1, 1), quad)
    True
    >>> inside((1, 3), quad)
    False
    """
    v1, v2, v3, v4 = quad
    conditions = [
        point[0] >= v1[0],
        point[1] <= v1[1],
        point[0] <= v2[0],
        point[1] <= v2[1],
        point[0] >= v3[0],
        point[1] >= v3[1],
        point[0] <= v4[0],
        point[1] >= v4[1],
    ]
    #malt.log("{} in {}: {}".format(
        #point, quad, all(conditions)), level="BUG")
    # Confusing!
    return all(conditions)
