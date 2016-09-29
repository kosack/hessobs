import numpy as np
from matplotlib import pyplot as plt


def plot_available_time_vs_zmax(dark, target, **kwargs):
    """
    Draw a plot of the available time in a schedule (as defined by a
    :class:`Darkness` object) for a given RA/Dec position as a function of
    maximum zenith angle (useful for determining the maximum amount of
    time available to observe an object over a year)

    dark 
         a Darkness object, already initialized
    target
         a Target dictionary containing at least RA_2000 and Dec_2000 keys

    usage:

    >>> t1 = Target.from_name( "Crab" )
    >>> t2 = Target.from_name( "Sgr A*" )
    >>> plot_available_time_vs_zmax( dark, t1 )
    >>> plot_available_time_vs_zmax( dark, t2 )
    >>> legend(loc="best")

    """

    ra_h = target['RA_2000']
    dec_deg = target['Dec_2000']
    name = target['Target_Name']

    zeniths = np.linspace(0, 70, 100)

    mask = dark.map == dark.UNAVAILABLE
    zen = dark._generateZenithAngleMap(ra_h, dec_deg)
    zen[mask] = -1  # mark regions where we can't even observe

    h_avail = np.array([np.sum(dark.effmap[(zen > 0) & (zen < zmax)])
                        for zmax in zeniths]) * dark.hours_per_map_bin

    plt.plot(zeniths, h_avail, label=name, **kwargs)
    plt.xlabel("Maximum Allowed Zenith Angle (deg)")
    plt.ylabel("Estimated Available Time (h)")
    plt.grid(True)
    plt.legend(loc="best")
