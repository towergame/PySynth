class Envelope:
    """
    A class representing a linear(*) envelope

    Attributes
    ----------
    a : float
        The attack time in seconds
    d : float
        The decay time in seconds
    s : float
        The sustain level as a percentage of the peak amplitude
    r : float
        The release time in seconds

    (*) It is not guaranteed that this will remain as such in subsequent versions
    """
    def __init__(self, a, d, s, r):
        """
        Constructs the object

        Parameters
        :param a: The attack time in seconds
        :param d: The decay time in seconds
        :param s: The sustain level as a percentage of the peak amplitude
        :param r: The release time in seconds
        """
        self.a = a
        self.d = d
        self.s = s
        self.r = r

        # TODO: Add exponential envelope type
        # TODO: Refactor to contain a function for amplitude at time t
