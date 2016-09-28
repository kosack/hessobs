import sys
import pymysql as mysql
from pymysql import cursors

try:
    import ConfigParser as configparser
except:
    import configparser
import os
import datetime
import logging

logger = logging.getLogger(__name__)


def read_dbtoolsrc(section, fallback_section="hess"):
    """ returns a dict for the given dbtoolsrc section """

    parser = configparser.SafeConfigParser()
    homedir = os.environ['HOME']
    parser.read("{0}/.dbtoolsrc".format(homedir))

    if (parser.has_section(section)):
        return dict(parser.items(section))
    else:
        return dict(parser.items(fallback_section))


def query_database(query, dbconfig="hess", db="HD_tables"):
    """

    Arguments:
    - `query`:
    """

    ver = 2 if sys.version_info.major <= 2 else 3

    dbtoolsrc = read_dbtoolsrc(dbconfig)

    try:
        logger.debug("Initiating DB connection: %s on %s for query (%s)",
                     dbtoolsrc['user'], dbtoolsrc['host'], query)

        if ver == 3:
            dbh = mysql.connect(user=dbtoolsrc['user'],
                                host=dbtoolsrc['host'],
                                port=int(dbtoolsrc['port']),
                                passwd=dbtoolsrc['password'],
                                db=db)

            cursor = dbh.cursor(cursors.DictCursor)

        else:
            dbh = mysql.connect(user=dbtoolsrc['user'],
                                host=dbtoolsrc['host'],
                                port=int(dbtoolsrc['port']),
                                passwd=dbtoolsrc['password'],
                                db=db)
            cursor = dbh.cursor(cursors.DictCursor)

        logger.debug("QUERY: {}".format(query))
        cursor.execute(query)
        logger.debug("DONE")
        return cursor.fetchall()

    except mysql.Error as err:
        logger.exception("Database connection error: {0}".format(err.args[1]))
        raise err


def get_date_range_for_period(period):
    """
    Returns the run-range for the given period name (e.g. 
    "P2014-02")
    """

    if not period.lower().startswith("p"):
        raise RuntimeError("Period '{}' should start with P".format(period))

    query = """ 
    SELECT * FROM Astro_Shifts WHERE
    Period like '{0}';
    """

    result = query_database(query.format(period),
                            dbconfig="hess", db="HESS_AstroParam")

    return (result[0]['StartDate'], result[0]['EndDate'])


def get_run_range_for_dates(startdate, enddate):
    """Returns (run_min, run_max) for given date range. Dates should be
    passed as :class:`datetime.datetime` objects.
    """

    query = \
        """
    SELECT MIN(RunNumber) as rmin ,MAX(RunNumber) as rmax FROM Run_Start 
    WHERE TimeOfStart>'{0}' AND TimeOfStart < '{1}'
    """
    sstart = startdate.isoformat()
    send = (enddate + datetime.timedelta(days=2)).isoformat()

    result = query_database(query.format(sstart, send), db="HESS_History")
    return result[0]['rmin'], result[0]['rmax']


def get_run_range_for_period(period):
    drange = get_date_range_for_period(period)
    return get_run_range_for_dates(drange[0], drange[1])


def get_run_range_for_year(year):
    year = int(year)
    p0 = "P{0}-01".format(year)
    p1 = "P{0}-01".format(year + 1)

    drange0 = get_date_range_for_period(p0)
    drange1 = get_date_range_for_period(p1)

    return get_run_range_for_dates(drange0[0], drange1[0])
