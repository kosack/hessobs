from __future__ import with_statement, print_function, absolute_import

from numpy import sin, cos, tan, arctan2, arcsin
from numpy import mod, radians, degrees, array, sqrt
from . import config
from math import pi

"""
A set of simple functions to convert between ground-based and
space-based coordinates.  This does not take into account effects such
as Earth's precession, nutation, or atmospheric refraction, so the precision
is limited.  They are fine for schedule calculation, however.

Author: Karl Kosack (from `hessobs` scheduling software)
"""

MJD_OFFSET = 2400000.5  # conversion from Julian Date to MJD
MJD_2000 = 51544.5  # time base for GMST: 2000-01-01T12:00:00
JD_2000 = MJD_2000 + MJD_OFFSET


def jd_to_mjd(jd):
    """
    convert Julian date to a Modified Julian Date
    """
    global MJD_OFFSET
    return jd - MJD_OFFSET


def mjd_to_jd(jd):
    """
    convert Modified Julian Date to julian date
    """
    global MJD_OFFSET
    return jd + MJD_OFFSET


def hourangle_from_ra(ra_hours, jd):
    """ returns hour angle in radians """

    lon = -config.TELESCOPE_LONGITIUDE_DEG * pi / 180.0

    return jd_to_gmst_angle(jd) - lon - ra_hours * pi / 12.0


def ra_from_hourangle(hourangle_rad, jd):
    """
    return Right accensions in hours
    """
    lon = -config.TELESCOPE_LONGITIUDE_DEG * pi / 180.0

    return jd_to_gmst_angle(jd) - lon - hourangle_rad


def jd_to_gmst_angle(jd):
    """
    Returns GMST (Greenwich Mean Sidereal Time) angle in radians from
    a JD (julian date), Accuracy: ~ 0.1 s
    """
    gmst_hours = mod(18.697374558 + 24.06570982441908 * (jd - JD_2000), 24.0)
    return gmst_hours * pi / 12.0  # in radians


def radec_to_altaz(ra_hours, dec_deg, jd):
    """ returns alt,az in degrees """
    lat = -config.TELESCOPE_LATITUDE_DEG * pi / 180.
    ha = hourangle_from_ra(ra_hours, jd)
    cosha = cos(ha)
    dec = (dec_deg * pi / 180.)

    az = -arctan2(sin(ha),
                  cosha * sin(lat) - tan(dec) * cos(lat))

    alt = -arcsin(sin(lat) * sin(dec)
                  + cos(lat) * cos(dec) * cosha)

    return alt * 180. / pi, az * 180. / pi


def altaz_to_radec(alt_deg, az_deg, jd):
    """ returns ra_hours, dec_deg """

    lat = -config.TELESCOPE_LATITUDE_DEG * pi / 180.

    az = -az_deg * pi / 180.
    alt = -alt_deg * pi / 180.

    ha = arctan2(sin(az),
                 cos(az) * sin(lat) + tan(alt) * cos(lat))

    ra = ra_from_hourangle(ha, jd)
    dec = arcsin(sin(lat) * sin(alt) - cos(lat) * cos(alt) * cos(az))

    return mod(ra * 12.0 / pi + 24, 24), dec * 180. / pi


def ang_sep_deg(lambda0, beta0, lambda1, beta1):
    """ calculate angular separation between two spherical coordinates
    using the Vincenti formula (accurate for large and small
    separations).  lambda = longitudinal coordinates (e.g. RA or gall)
    and beta=latitudinal coordinate (e.g. dec or galb). These must be
    in degrees already.

    EXAMPLE:
        ra = arange(100)*0.1
        dec = ones(100)*-20.0
        center_radec = (120.0,15.0) # distance to a single point (can be array)
        dists = ang_sep_deg( ra, dec, center_radec[0], center_radec[1] )

    Arguments:
    - `lambda0,beta0`: first ra/dec coordinate in deg (or arrays)
    - `lambda1, beta1`: second ra/dec coordinates in deg (or arrays)
    """

    l0 = radians(array(lambda0))
    l1 = radians(array(lambda1))
    b0 = radians(array(beta0))
    b1 = radians(array(beta1))

    cosb0 = cos(b0)
    cosb1 = cos(b1)
    sinb0 = sin(b0)
    sinb1 = sin(b1)
    cosdl = cos(l1 - l0)

    numer = sqrt((cosb1 * sin(l1 - l0)) ** 2 +
                 (cosb0 * sinb1 - sinb0 * cosb1 * cosdl) ** 2)

    denom = sinb0 * sinb1 + cosb0 * cosb1 * cosdl

    return degrees(arctan2(numer, denom))
