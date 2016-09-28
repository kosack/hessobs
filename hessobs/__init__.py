"""Tools for creating HESS Schedules

This module can be used to create Long-Term schedules from a list of
targets, including many constraints (e.g. on zenith angle, time, etc).
Long-term schedules are used to plan the observation time for a full
year at once, and are not intended to respresent the exact day-to-day
or hour-to-hour observation schedule. Thus the design of this
scheduling system tries to take a global view that at least accurately
represents the time division of sources.

Generally scheduling proceeds as follows:

 1) Edit the Observation_Proposal database to set all parameters
 2) use the :mod:`Targets` module to load the database table into a list of target dictionaries (each one contains all target scheduling parameters) 
 3) Construct a :class:`Scheduler.Scheduler` subclass (like :class:`Scheduler.HESSIIScheduler`), specifying the expected dark time and data taking efficiencies.
 4) call the :func:`schedule` method of the scheduler on the list of targets

"""

from .Darkness import *
from .Targets import *
from .Coordinates import *
from .Utils import *
from .Scheduler import *

