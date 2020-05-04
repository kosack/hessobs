from hessobs import coordinates
import numpy as np
from math import pi


def test_coords():
    # crab nebula
    ra_deg = 83.629
    dec_deg = 22.017

    # cena:
    ra_deg = 201.365
    dec_deg = -43.0191

    ra_h = ra_deg * 12.0 / 180.0
    ra_rad = ra_deg * pi / 180.0
    dec_rad = dec_deg * pi / 180.0

    utcs = np.linspace(-24, 24, 400)
    jd = 2456353  # should transit at about -6 UTC, at 45 degrees

    jds = jd + utcs / 24.0

    alt, az = coordinates.radec_to_altaz(ra_h, dec_deg, jds)
    tra, tdec = coordinates.altaz_to_radec(alt, az, jds)
    error = (ra_deg - tra, dec_deg - tdec)

    #    subplot(211)
    #    scatter( (jds-jd)*24, alt)
    #    subplot(212)
    #    scatter( tra,tdec )

    # from astro:
    refjd = 2456353.114
    refaltaz = (48.5759, 25.8249)

    testaltaz = coordinates.radec_to_altaz(ra_h, dec_deg, refjd)

    print(refaltaz)
    print(testaltaz)

    assert np.allclose(refaltaz, testaltaz)
