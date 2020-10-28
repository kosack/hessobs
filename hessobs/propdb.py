from __future__ import print_function

import logging

from sqlalchemy import create_engine, and_
from sqlalchemy.ext.declarative import declarative_base, DeferredReflection
from sqlalchemy.orm import sessionmaker

from .hessdb import read_dbtoolsrc

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


# ============================================================================
# Database Mapping
# ============================================================================
Base = declarative_base(cls=DeferredReflection)
engine = None

WRITE = False


class Target(Base):
    __tablename__ = "Observation_Proposals"


class Proposal(Base):
    __tablename__ = "Observation_Proposals_Set"


def get_dbstring_from_config():
    """
    """
    rc = read_dbtoolsrc("proposals")
    return "mysql+pymysql://{user}:{password}@{host}:{port}/{db}".format(
        user=rc["user"],
        password=rc["password"],
        host=rc["host"],
        port=int(rc["port"]),
        db=rc["database"],
    )


def init_engine():
    global engine
    if engine is None:
        print("PREPARE")
        engine = create_engine(get_dbstring_from_config(), echo=False)
        Base.prepare(engine)
    else:
        pass


def session():
    """
    """
    global engine
    print("Loading Session")
    init_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def check_if_exists(session, year, seqno, revision=0):
    """
    check if the proposal is already in the database
    """

    nprops = (
        session.query(Proposal)
        .filter(
            and_(
                Proposal.Seqno == seqno,
                Proposal.Year == year,
                Proposal.Revision == revision,
            )
        )
        .count()
    )

    if nprops > 0:
        raise IndexError(
            "Proposal {0}-{1}-{2} already in database".format(year, seqno, revision)
        )


def add_target_to_db(session, name, targetdict, setnum):
    """
    insert a set of targets into a proposal database. The SetNum should
    correspond to the set returned by add_proposal_to_database()
    """
    global WRITE
    for targ in targetdict:
        print("    {0:23s} : {1:30s}".format(targ, str(targetdict[targ])))

    targ = Target(**targetdict)
    targ.Target_Name = name
    targ.SetNum = setnum

    # execute query:
    if WRITE:
        print("ADD TARGET TO SET", targ.SetNum)
        session.add(targ)
        print("Done")


def add_proposal_to_db(session, propdict, year, seqno, revision=0):
    """
    insert a proposal into the database, and return the SetNum that
    references it
    """
    global WRITE

    propdict["Year"] = year
    propdict["Seqno"] = seqno
    propdict["Revision"] = revision
    propdict["URL"] = (
        "http://www.mpi-hd.mpg.de/hfm/HESS/intern/Proposals"
        "/{year}/{year}-{seqno:03d}-{revision}.pdf"
    ).format(year=year, seqno=int(seqno), revision=revision)

    for prop in propdict:
        print("    {0:20s} : {1:30s}".format(prop, str(propdict[prop])))

    prop = Proposal(**propdict)

    # execute query
    if WRITE:
        session.add(prop)

        # retrieve auto-generated SetNum

        res = (
            session.query(Proposal)
            .filter_by(Year=year, Seqno=seqno, Revision=revision)
            .first()
        )

        return res.SetNum
    else:
        return -1
