from pylabs.qt1.simplefitting import fitT1


def create(S, A, B1, expected, fit, TR):
    """Dummy construction/estimating of a correction method
    S           nvials * nflipangles    signal values per flip angle
    A           nflipangles             flip angles in radians
    B1          nvials                  B1 factor per vial
    expected    nvials                  model T1 per vial
    fit         nvials                  original T1 fit value
    TR          one value               e.g. 14.

    Should return data needed for apply() e.g. coefficients
    """
    return fitT1(S, A, B1, TR)

def apply(correction, S, A, B1):
    """Dummy application of a correction method to data
    correction  ?                       data returned by create() function
    S           nvials * nflipangles    signal values per flip angle
    A           nflipangles             flip angles in radians
    B1          nvials                  B1 factor per vial
    """
    return correction
    
