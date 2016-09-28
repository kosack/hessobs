from __future__ import with_statement, print_function, absolute_import
"""
Tools to work with target lists

Targets are defined as dictionaries containing a set of scheduling
parameters. The parameters are defined by the columns in the
``Observation_Proposals`` database tables.

Normally, one loads targets using :func:`Targets.load_targets_from_db`,
or by creating a new target by hand using :func:`Targets.new_target`
or :func:`Targets._new_target_from_name`. Important parameters to set
are:

    * RA_2000
    * Dec_2000
    * Target_Name
    * Hours_Accepted

For a full set, see the defaults in :mod:`Config`. 

"""

try:
    import configparser
except:
    import ConfigParser as configparser

try:
    import MySQLdb
except:
    import pymysql as MySQLdb
import os
import pickle
from . import config
import numpy.random
from numpy import array
import numpy as np
from operator import itemgetter


class Target(dict):

    """ just a dict that allows tab completion in ipython """

    def __init__(self, **kw):
        dict.__init__(self, kw)
        self.__dict__ = self
        _set_target_defaults(self)

    def __str__(self):
        return "--------\n" +\
            "\n".join(["{0:24s} : {1}".format(key, self.__dict__[key])
                       for key in sorted(self.__dict__)]) + "\n"

    @classmethod
    def from_name(cls, name, hours=10):
        """ Create a new target with all the required fields,
        filling in the RA and DEC using a simbad query by object name."""
        _new_target_from_name(name, hours)


def _query_database(query, dbconfig="proposals", db="HESS_Proposals"):
    """

    """

    dbtoolsrc = read_dbtoolsrc(dbconfig)

    try:
        print("Initiating DB connection: ", dbtoolsrc[
              'user'], "on", dbtoolsrc['host'])
        db = MySQLdb.connect(user=dbtoolsrc['user'],
                             host=dbtoolsrc['host'],
                             port=int(dbtoolsrc['port']),
                             passwd=dbtoolsrc['password'],
                             db=db)

        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query)
        return cursor.fetchall()

    except MySQLdb.Error as err:
        print(("Database connection error: {0}".format(err.args[1])))
        raise err


def _new_target_from_name(name, hours=10):
    """
    Look up name on Simbad and return a new target, ready to have
    other fields filled in.

    Arguments:
    - `name`:
    - 'hours': default number of hours to fill in

    """

    from astropy.coordinates import SkyCoord

    pos = SkyCoord.from_name(name)
    target = new_target(Target_Name=name, Hours_Accepted=hours)
    target['RA_2000'] = pos.ra.hour
    target['Dec_2000'] = pos.dec.deg

    return target


def _set_target_defaults(targetdict):
    """
    Adds keys for all default values if they don't exist to a
    target dictionary.  Also cleans up bad entries.
    """

    for attrib in list(config.DEFAULT_TARGET_ATTRIBS.keys()):
        if attrib not in targetdict or targetdict[attrib] is None:
            targetdict[attrib] = config.DEFAULT_TARGET_ATTRIBS[attrib]


def save_targets(targets, filename="targets.dat"):
    """
    write targets to a pickle file (in case of no DB connection)
    """

    print("Pickling targets to:", filename)
    outf = open(filename, "w")
    pickle.dump(targets, outf)


def target_list_to_dict(targets, key='Target_Name'):
    """ returns dictionary indexed by given key"""
    targdict = dict()
    for targ in targets:
        targdict[targ[key]] = targ
    return targdict


def copy_target_between_sets(source_setnum, dest_setnum, target_name,
                             transform=None):
    """
    Copies a target entry from from proposal1 to proposal2 (which can
    be the same proposal if you want to duplicate the target with some
    minor change)
    """

    query = """ SELECT * FROM Observation_Proposals WHERE
    SetNum={set1} and Target_Name like '{targ}' """

    results = _query_database(
        query.format(set1=source_setnum, targ=target_name))

    print(results)

    for result in results:
        del result['Entry']
        result['SetNum'] = dest_setnum
        if transform:
            transform(result)
        print(result)

        colnames = ",".join(list(result.keys()))
        avals = []
        for val in list(result.values()):
            avals.append("'" + str(val) + "'")
        vals = ",".join(avals)

        sql = "INSERT INTO Observation_Proposals ({colnames}) VALUES ({vals});"

        print(sql)

        _query_database(sql.format(colnames=colnames, vals=vals))


def load_targets_from_db(where="Hours_Accepted>0",
                         order="Working_Group_Rank ASC",
                         fallbackfile=None,
                         normalize=True):
    """
    Loads targets from Observation_Proposals database. If no
    dbconnection, loads a pickled version.

    returns array of target dicts
    """

    try:
        query = """
        SELECT * FROM Observation_Proposals AS P
            LEFT JOIN Observation_Proposals_Set as S
                   ON S.SetNum = P.SetNum WHERE ({where}) ORDER BY {order}
        """

        if where is None:
            where = "1"

        targets = []
        fullwhere = "(" + where + ")"

        results = _query_database(query.format(where=fullwhere, order=order))

        for row in results:
            if 'Working_Group_Rank' not in row:
                row['Working_Group_Rank'] = 0

        if fallbackfile is not None:
            save_targets(results, fallbackfile)

        targets = [Target(**res) for res in results]
        # normalize all targets:
        if normalize:
            for targ in targets:
                _set_target_defaults(targ)

    except MySQLdb.Error as err:
        print(err)
        if fallbackfile is not None:
            print("Reading from pickled version")
            tfile = open(fallbackfile)
            targets = pickle.load(tfile)

    return targets


def read_dbtoolsrc(section, fallback_section="hess"):
    """ returns a dict for the given dbtoolsrc section """

    parser = configparser.SafeConfigParser()
    homedir = os.environ['HOME']
    parser.read("{0}/.dbtoolsrc".format(homedir))

    if (parser.has_section(section)):
        return dict(parser.items(section))
    else:
        return dict(parser.items(fallback_section))


def mutate(arr):
    r = numpy.random.randint(1, len(arr))
    return numpy.append(arr[r - 1:-1], arr[0:r])


def stochastically_optimized_schedule(darkfile, targets, iterations=50):
    """
    permute targets to find optimal schedule based on the score

    uses Darkness.score to measure fitness of schedule and returns the
    schedule with the highest score along with the list of
    efficiencies per trial
    """

    from .darkness import Darkness
    
    maxscore = -1e100
    besttargs = targets

    dark = Darkness(darkfile)

    for targ in targets:
        dark.fillTarget(targetinfo=targ,
                        nhours=float(targ['Hours_Accepted']),
                        verbose=False)
    maxscore = dark.score

    scores = []

    targs = array(targets).copy()

    for ii in range(iterations):

        dark.clear()

        targs = numpy.random.permutation(targets)
#        targs = mutate(targs)

        for targ in targs:
            dark.fillTarget(targetinfo=targ,
                            nhours=float(targ['Hours_Accepted']),
                            verbose=False)
        score = dark.score
        scores.append(score)

        if score > maxscore:
            maxscore = score
            besttargs = targs.copy()

        print("TRIAL:", ii, "SCORE:", score, "BEST = ", maxscore)

    dark = Darkness("../2012/darkness2012.dat")
    for targ in besttargs:
        dark.fillTarget(targetinfo=targ,
                        nhours=float(targ['Hours_Accepted']),
                        verbose=False)

    return dark, scores


def update_target(targets, targname, **kwargs):
    """
    Change parameters for a target in a list without updating the database

    Arguments:
    `targname`
        name of target
    `key`
        keyword to update
    `value`
        value to set
    """

    for targ in targets:
        if targ['Target_Name'].startswith(targname):
            for key in kwargs:
                if key in targ:
                    print("UPDATED: ", targ['Target_Name'], key,
                          ":", targ[key], "-->", kwargs[key])
                else:
                    print("UPDATED: ", targ['Target_Name'], "ADDED",
                          key, "=", kwargs[key])

                targ[key] = kwargs[key]

            break


def find_target(targets, targname):
    """ return the target info, searching by targname """

    for targ in targets:
        if targ['Target_Name'].startswith(targname):
            print("FOUND: ", targ['Target_Name'])
            return targ


def load_targets_using_block_heuristic(blocksize=20, timeweighted=False,
                                       where="1"):
    """
    Loads targets in an order that tries to balance WG time.

    It cycles through WGs, filling blocks of 'blocksize' hours before
    jumping to the next WG. Sources with requested hours larger than
    blocksize are filled in one go (not split up)
    """

    # define the order of WG cycle:
    wgs = ['Galactic',
           'Extragalactic',
           'Astroparticle'
           ]

    ntargs = 0
    targs = dict()

    order = "Working_Group_Rank ASC"
    if timeweighted:
        order = "(Working_Group_Rank * Hours_Accepted) ASC"

    for wg in wgs:
        fallback = "targets-{0}.dat".format(wg)
        targs[wg] = list(load_targets_from_db(where="Working_Group='{0}'"
                                              .format(wg) + " AND (" + where
                                              + ")",
                                              fallbackfile=fallback,
                                              order=order))
        ntargs += len(targs[wg])

    # now build target list by cycling through targets, interleaving
    # working groups

    targets = []

    count = 0
    currhours = 0
    iwg = 0

    print("Loading", ntargs, "targets")

    while count < ntargs:

        if (currhours > blocksize):
            iwg += 1
            currhours = 0

        if (iwg >= len(wgs)):
            iwg = 0

        wg = wgs[iwg]

        if len(targs[wg]) > 0:
            tt = targs[wg].pop(0)
            targets.append(tt)
            count += 1
            currhours += tt['Hours_Accepted']
            # print count, currhours,wg
        else:
            iwg += 1

    return targets


def write_target_order(targets, filename):
    """write target list to text file so the order can be edited easily using
    emacs org-mode to move items around (``M-[uparrow]`` and ``M-[downarrow]``)

    Arguments:

    `targets`
        in-order list of targets
    `filename`
        output filename for the target-order list 

    """

    with open(filename, "w") as outfile:
        outfile.write("|Entry|Subarray|Rank|Class|RA|WG|Name|\n")
        for targ in targets:
            line = '| {0} | {1} | {2} | {3} | {4:5.1f} | "{5}" | "{6}" |\n' \
                .format(targ['Entry'],
                        targ['Subarray'],
                        targ['Working_Group_Rank'],
                        targ['Approval_Class'],
                        targ['RA_2000'],
                        targ['Working_Group'],
                        targ['Target_Name'])
            outfile.write(line)

    print("Wrote:", filename)


def order_targets_from_file(targets, filename):
    """
    read an ordered targetlist from the file, and sort targets by that order

    Arguments:

    `targets`
        unordered list of targets
    `filename`
        file to read order from

    returns an ordered target list
    """

    tdict = target_list_to_dict(targets, key="Entry")
    order = 0
    unknown = 999

    from astropy.table import Table
    tab = Table.read(filename, format="ascii.fixed_width", delimiter="|")
    ordered_entries = tab['Entry']

    for entry in ordered_entries:
        if entry in tdict:
            tdict[entry]['New_Fill_Order'] = order
            order += 1
        else:
            print("!!!! Target", entry, " not found, putting at end")
            tdict[entry] = Target()
            tdict[entry]['New_Fill_Order'] = unknown
            unknown += 1

    print("Ordered targets from", filename)

    # check that all targets received an order number:
    for targ in targets:
        if "New_Fill_Order" not in targ:
            print("!!! No Fill Order found for target: ", targ['Target_Name'])
            targ['New_Fill_Order'] = order
            order += 1

    # now put it back as an ordered list:
    targets = list(tdict.values())
    targets = sorted(targets, key=lambda x: x['New_Fill_Order'])

    return targets


def group_by_ra_band(targetlist, rabins=None, binrange=[0, 24], bins=10):
    """groups targets by RA band (used by :func:`print_conflicting_targets`)

    Arguments:

    `targetlist`
        list of target dicts
    `rabins`
        number of bins, or array of bin lower-edges in RA Hours if you
        want non-equal spacing

    """

    if rabins is None:
        rabins = np.linspace(binrange[0], binrange[1], bins)

    ii, ras = np.array([[ii, targ['RA_2000']]
                        for ii, targ in enumerate(targetlist)]).T
    ii = ii.astype(int)
    bands = np.digitize(ras, rabins)

    tt = np.array(targetlist)

    grouped = dict()
    boundaries = list()

    for iband in range(len(rabins) - 1):
        bandname = "RA {0:02.0f}-{1:02.0f} h".format(
            rabins[iband], rabins[iband + 1])
        targsinband = tt[ii[bands == iband + 1]]
        grouped[bandname] = targsinband
        boundaries.append((rabins[iband], rabins[iband + 1]))

    return grouped, boundaries


def print_conflicting_targets(targetlist, rabins=None, dark=None):
    """

    Arguments:
    - `targets`:
    - `dark`: a Darkness object, to estimate free hours in band (if not None)
    """

    fmt = "{Target_Name:>25s} {RA_2000:4.1f} {Working_Group_Rank:4d} "
    fmt += "{Approval_Class:<2s} {Working_Group:<7s}  "
    fmt += "{Hours_Scheduled:3.0f}/{Hours_Accepted:3.0f}"

    groups, bands = group_by_ra_band(targetlist, rabins)

    for group, band in sorted(zip(list(groups.keys()), bands)):
        print("=" * 70)
        print(group)

        if dark:
            raw, est = dark.hoursForRABand(band[0], band[1])
            print("FREE: {0:.1f} h ".format(est))

        print("          TARGET           RA  RANK CLS  WG      SCH/REQ")

        tothrs = 0

        for targ in sorted(groups[group], key=itemgetter("Working_Group_Rank")):
            targ['Working_Group'] = targ['Working_Group'][0:7]
            targ['Approval_Class'] = targ['Approval_Class'][0:1]
            if 'Hours_Scheduled' not in targ:
                targ['Hours_Scheduled'] = 0
            print(fmt.format(**targ))
            tothrs += targ['Hours_Accepted']

        print("                                     TOTAL REQ:   {0:.1f}"
              .format(tothrs))
