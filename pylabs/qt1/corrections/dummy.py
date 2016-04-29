from pylabs.qt1.simplefitting import fitT1


def correct(S, A, B1, expected, fit, TR):
    """Dummy implementation of a correction method
    S           nvials * nflipangles    signal values per flip angle
    A           nflipangles             flip angles in radians
    B1          nvials                  B1 factor per vial
    expected    nvials                  model T1 per vial
    fit         nvials                  original T1 fit value
    TR          one value               e.g. 14.
    """
    return fitT1(S, A, B1, TR)
