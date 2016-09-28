from kapteyn import maputils
from kapteyn import wcs
from matplotlib import pyplot as plt
import matplotlib.patheffects as PathEffects
import numpy as np


# ====== FROM SERVICE.py

__version__ = '1.91'


epsilon = 0.0000000001


def radians(a):
    return a * np.pi / 180.0


def degrees(a):
    return a * 180.0 / np.pi


def cylrange():
    X = np.arange(0, 400.0, 30.0)
    # Replace last two (dummy) values by two values around 180 degrees
    X[-1] = 180.0 - epsilon
    X[-2] = 180.0 + epsilon
    return X


def polrange():
    X = np.arange(0, 380.0, 15)
    # Replace last two (dummy) values by two values around 180 degrees
    X[-1] = 180.0 - epsilon
    X[-2] = 180.0 + epsilon
    return X


def getperimeter(grat):
    # Calculate perimeter of QUAD projection
    xlo, y = grat.gmap.topixel((-45.0 - epsilon, 0.0))
    xhi, y = grat.gmap.topixel((315 + epsilon, 0.0))
    x, ylo = grat.gmap.topixel((180, -45))
    x, yhi = grat.gmap.topixel((180, 45))
    x1, y = grat.gmap.topixel((45 - epsilon, 0.0))
    x, ylolo = grat.gmap.topixel((0, -135 + epsilon))
    x, yhihi = grat.gmap.topixel((0, 135 - epsilon))
    perimeter = [(xlo, ylo), (x1, ylo), (x1, ylolo), (xhi, ylolo), (xhi, yhihi),
                 (x1, yhihi), (x1, yhi), (xlo, yhi), (xlo, ylo)]
    return perimeter


# Set defaults which can be overwritten by the allskyfxx.py scripts
title = ''
titlepos = 1.02
dec0 = 89.9999999999
fsize = 10
figsize = (7, 6)
drawgrid = False
grat = None
smallversion = False
plotbox = (0.1, 0.05, 0.8, 0.8)
markerpos = "120 deg 60 deg"


def doplot(frame, annim, grat, title,
           lon_world=None, lat_world=None,
           lon_constval=None, lat_constval=None,
           lon_fmt=None, lat_fmt=None,
           markerpos=None,
           plotdata=False, perimeter=None, drawgrid=None,
           smallversion=False, addangle0=0.0, addangle1=0.0,
           framebgcolor=None, deltapx0=0.0, deltapy0=0.0,
           deltapx1=0.0, deltapy1=0.0,
           labkwargs0={'color': 'r'}, labkwargs1={'color': 'b'}):
    # Apply some extra settings

    if framebgcolor != None:
        frame.set_axis_bgcolor(framebgcolor)

    if lon_constval == None:
        lon_constval = 0.0    # Reasonable for all sky plots
    if lat_constval == None:
        lat_constval = 0.0    # Reasonable for all sky plots
    if lon_fmt == None:
        lon_fmt = 'Dms'
    if lat_fmt == None:
        lat_fmt = 'Dms'
    # Plot labels inside graticule if required
    # labkwargs0.update({'fontsize':fsize})
    # labkwargs1.update({'fontsize':fsize})
    ilabs1 = grat.Insidelabels(wcsaxis=0,
                               world=lon_world, constval=lat_constval,
                               deltapx=deltapx0, deltapy=deltapy0,
                               addangle=addangle0, fmt=lon_fmt, **labkwargs0)
    ilabs2 = grat.Insidelabels(wcsaxis=1,
                               world=lat_world, constval=lon_constval,
                               deltapx=deltapx1, deltapy=deltapy1,
                               addangle=addangle1, fmt=lat_fmt, **labkwargs1)

    # Plot just 1 pixel c.q. marker
    if markerpos != None:
        annim.Marker(pos=markerpos, marker='o', color='red')

    if drawgrid:
        pixellabels = annim.Pixellabels(plotaxis=(2, 3))

    # Plot the title
    if smallversion:
        t = frame.set_title(title, color='g', fontsize=10)
    else:
        t = frame.set_title(title, color='g', fontsize=13, linespacing=1.5)
    t.set_y(titlepos)

    # Plot alternative borders. Do this after the graticule is plotted
    # Only then you know the frame of the graticule and plotting in that
    # frame will overwrite graticule lines so that the borders look better
    if perimeter != None:
        p = plt.Polygon(perimeter, facecolor='#d6eaef', lw=2)
        frame.add_patch(p)     # Must be in frame specified by user
        Xp, Yp = list(zip(*perimeter))
        grat.frame.plot(Xp, Yp, color='r')

    annim.interact_toolbarinfo()


#-------- END SERVICE

def label_objects(annim, objects, fontsize=10, radius=None,
                  align="top", **kwargs):
    from astropy.coordinates import SkyCoord

    for obj in objects:
        cc = SkyCoord.from_name(obj)
        label_object(annim, (cc.galactic.l.deg, cc.galactic.b.deg),
                     obj, fontsize=fontsize, radius=radius,
                     align=align, **kwargs)


def label_object(annim, pos, text, fontsize=10, radius=None,
                 align="bottom", **kwargs):
    lx, ly = annim.projection.topixel(pos)
    if (text != ""):
        txt = plt.text(lx, ly, text + "  ", fontsize=fontsize, rotation=90,
                       horizontalalignment='left', verticalalignment=align,
                       **kwargs)

        txt.set_path_effects([PathEffects.withStroke(linewidth=3,
                                                     foreground="w")])
        annim.Marker(x=pos[0], y=pos[1],  marker='o', markersize=2,
                     color='black', mode="world")

    if radius:
        annim.Beam(radius * 2, radius * 2, xc=pos[0], yc=pos[1],
                   fc="black", color='black', fill=False,  lw=2)

    print("Plotted", text, " at ", pos)


def plotobs(annim, obs, color='r'):
    for xx, yy in obs:
        annim.Beam(5.0, 5.0, xc=xx, yc=yy,
                   fc=color, fill=True, alpha=0.1, lw=0)


def plot_targets_on_sky(dark, radec=False, proj='AIT', withlabels=True):

    # note all coords are specified in galactic coordinates, and are
    # transformed to the final system via tran().
    # ======================================================================

    # plotbox = (0.0,0.05,0.9,0.9)
    figsize = (15, 8)
    fig = plt.figure(figsize=figsize)
    frame = fig.add_axes(plotbox)
    title = "({0} projection)".format(proj)

    # ======================================================================
    tran = wcs.Transformation(wcs.fk5, wcs.galactic)
    if radec:
        tran = wcs.Transformation(wcs.fk5, wcs.fk5)

    header = {'NAXIS': 2, 'NAXIS1': 100, 'NAXIS2': 80,
              'CTYPE1': 'GLON-{0}'.format(proj),
              'CRVAL1': 0.0, 'CRPIX1': 50, 'CUNIT1': 'deg', 'CDELT1': -4.0,
              'CTYPE2': 'GLAT-{0}'.format(proj),
              'CRVAL2': 0.0, 'CRPIX2': 40, 'CUNIT2': 'deg', 'CDELT2': 4.0,
              }
    if radec:
        header = {'NAXIS': 2, 'NAXIS1': 100, 'NAXIS2': 80,
                  'CTYPE1': 'RA---{0}'.format(proj),
                  'CRVAL1': 0.0, 'CRPIX1': 50, 'CUNIT1': 'deg', 'CDELT1': -4.0,
                  'CTYPE2': 'DEC--{0}'.format(proj),
                  'CRVAL2': 0.0, 'CRPIX2': 40, 'CUNIT2': 'deg', 'CDELT2': 4.0,
                  }

    X = cylrange()
    Y = np.arange(-60, 90, 30.0)
    f = maputils.FITSimage(externalheader=header)
    annim = f.Annotatedimage(frame)
    grat = annim.Graticule(axnum=(1, 2), wylim=(-90, 90.0), wxlim=(0, 360),
                           startx=X, starty=Y)
    grat.setp_lineswcs0(0, lw=2)
    grat.setp_lineswcs1(0, lw=2)
    lat_world = [-60, -30, -20, -10, 0, 10, 20, 30, 60]
    # Remove the left 180 deg and print the right 180 deg instead
    w1 = np.arange(0, 151, 10.0)
    w2 = np.arange(210, 360, 10.0)
    lon_world = concatenate((w1, w2))
    labkwargs0 = {'color': 'b', 'va': 'bottom', 'ha': 'right'}
    labkwargs1 = {'color': 'b', 'va': 'bottom', 'ha': 'right'}

    doplot(frame, annim, grat, title,
           lon_world=lon_world, lat_world=lat_world,
           labkwargs0=labkwargs0, labkwargs1=labkwargs1,
           markerpos=None)

    if radec:
        grat2 = annim.Graticule(skyout=wcs.galactic)
    else:
        grat2 = annim.Graticule(skyout=wcs.fk5)
    grat2.setp_gratline(wcsaxis=1, position=0, linestyle=':', lw=3, color='k')
    grat2.setp_gratline(
        wcsaxis=1, position=-60, linestyle=':', lw=3, color='k')
    grat2.setp_gratline(wcsaxis=1, position=60, linestyle=':', lw=3, color='k')
    grat2.setp_gratline(wcsaxis=0, lw=0)
    grat2.setp_ticklabel(visible=False)
    grat2.setp_axislabel(visible=False)
    inswcs1 = grat2.Insidelabels(wcsaxis=1)
    # display CTA pointings

    wobble = array([(xx, yy) for xx in [-1.0, 1.0, 0.0, 0.0]
                    for yy in [0.0, 0.0, -1.0, 1.0]]) * 0.7

    for targ in list(dark.targets.values()):
        hrs, corrected_hours = dark.hoursForTarget(targ.INDEX)
        color = 'red'
        if corrected_hours > 1.0:
            color = 'cornflowerblue'
        if corrected_hours > 20:
            color = 'darkblue'
        pos = (targ.RA_2000 * 180.0 / 12.0, targ.Dec_2000)
        if withlabels is True:
            label_object(annim, tran(pos), targ.Target_Name)
        plotobs(annim, tran(np.array(pos) + wobble), color=color)

    # ======================================================================
    annim.plot()
    plt.show()
    return annim
