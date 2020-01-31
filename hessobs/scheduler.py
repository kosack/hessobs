from __future__ import with_statement, print_function, absolute_import

"""
Multi-Subarray Scheduling
"""

from . import Darkness
import pickle
from matplotlib import pyplot as plt
import abc

import logging

log = logging.getLogger(__name__)

class Scheduler(object):

    """abstract base class for schedulers

    All schedulers should provide a :func:`schedule` method that takes
    a target list (list of Target dictionaries)
    """
    
    def __init__(self,):
        log.info("Schedule Init")
        self._schedules = dict()

    @abc.abstractmethod
    def schedule(self, targets, combine):
        """ do the scheduling (should be overridden in derived classes) """
        pass

    def diff(self, prevfilename):
        """
        print changes between schedules and previous schedule, which should
        have been stored using save_schedule()
        """
        prev = load_schedule(prevfilename)

        for sched in self._schedules:
            print("-" * 70)
            print("{0} CHANGES SINCE LAST VERSION:".format(sched))
            print("-" * 70)
            self._schedules[sched].diff(prev._schedules[sched])

    def draw(self, **kwargs):
        """Draw all schedule planes
        (see :py:func:`Darkness.draw`) for parameters"""
        for sched in self._schedules.values():
            sched.draw(**kwargs)

    def setColorMap(self, cmap):
        """ Change the color map for all schedule planes """
        for sched in self._schedules.values():
            sched._cmap = cmap

    def printSummary(self, **kwargs):
        """Print a summary of all scheduled objects (see
        :func:`Darkness.printSummary()` for a list of options)
        """
        for sched in self._schedules.values():
            sched.printSummary(**kwargs)
            print(" - - - ")

    def printSchedule(self, period):
        """ Print out the schedule for the given period """
        for sched in self._schedules.values():
            sched.printSchedule(period)

    def drawZenithAngleDist(self, **kwargs):
        """ Draw the zenith angle dist for each schedule plane """
        plt.figure(figsize=(15, 5))
        for ii, sched in enumerate(self._schedules.values()):
            plt.subplot(1, len(self._schedules), ii + 1)
            sched.drawZenithAngleDist(newfig=False, **kwargs)

    def drawTargetPie(self, **kwargs):
        """ Draw the target pie for each schedule plane """
        plt.figure(figsize=(15, 4))
        for ii, sched in enumerate(self._schedules.values()):
            plt.subplot(1, len(self._schedules), ii + 1)
            sched.drawTargetPie(**kwargs)

    def drawPie(self, **kwargs):
        plt.figure(figsize=(15, 5))
        for ii, sched in enumerate(self._schedules.values()):
            plt.subplot(1, len(self._schedules), ii + 1)
            sched.drawPie(**kwargs)

    def setDatesAsUnavailable(self, startdate, enddate):
        for sched in self._schedules.values():
            sched.setDatesAsUnavailable(startdate, enddate)


class HESSIIScheduler(Scheduler):

    """This class inherits all methods from :class:`Scheduler` and
    implements a HESS-II style split-subarray schedule. Internally it
    constructs three `hessobs.darkness.Darkness` objects (single-subarray schedules for
    Mono, Stereo, and Hybrid subarrays), and manages the scheduling of
    a mixed set of targets into all three at once.

    Subarrays are defined as :

    - mono : CT5 Mono 
    - hybrid : CT1-5 Hybrid
    - stereo : CT1-4 Stereo

    the schedule() method takes into account all three subarrays when
    given an ordered target list. 

    example::

      from hessobs.Scheduler import HESSIIScheduler
      from hessobs.Targets import load_targets_from_db

      sched = HESSIIScheduler( "darkness2015.dat" )
      targetlist = load_targets_from_db( where="Year=2015 and Hours_Accepted>0")
      sched.schedule( targetlist ) 

      sched.mono.draw() # draw a single schedule plane
      sched.draw()  # draw all planes

    """

    def __init__(self, darkfile="darkness.dat", **kwargs):
        """
        Set up a Subarray Schedule
        """
        log.info("HESS-II init with ", darkfile)
        super(HESSIIScheduler, self).__init__()

        self._schedules['hybrid'] = Darkness(darkfile, name="CT1-5 Hybrid",
                                             **kwargs)

        self._schedules['mono'] = Darkness(darkfile, name="CT5 Mono",
                                           **kwargs)
        self._schedules['stereo'] = Darkness(darkfile, name="CT1-4 Stereo",
                                             **kwargs)

    @property
    def hybrid(self, ):
        """ access the Hybrid (CT1-5) schedule plane """
        return self._schedules['hybrid']

    @property
    def mono(self, ):
        """ access the Mono (CT5) schedule plane """
        return self._schedules['mono']

    @property
    def stereo(self, ):
        """ access the Stereo (CT1-4) schedule plane """
        return self._schedules['stereo']

    def schedule(self, targets, combine):
        """
        fill all schedules, taking into account previously scheduled
        observations that block one or more subarrays.

        Keyword Arguments:
        targets -- a list of Target objects, in order, to schedule
        """

        for targ in targets:

            if targ.Subarray_Accepted == "CT1-5 Hybrid":
                mask = self.hybrid.fillTarget(targ, combine_close=combine)
                self.mono.maskUnavailable(mask)
                self.stereo.maskUnavailable(mask)

            elif targ.Subarray_Accepted == "CT5 Mono":
                mask = self.mono.fillTarget(targ, combine_close=combine)
                self.hybrid.maskUnavailable(mask)

            elif targ.Subarray_Accepted == "CT1-4 Stereo":
                mask = self.stereo.fillTarget(targ, combine_close=combine)
                self.hybrid.maskUnavailable(mask)

            else:
                log.warning("!!! Target {} has an unknown subarray '{}' and "
                            "could not be scheduled !!!"
                            .format(targ.Target_Name,
                                    targ.Subarray_Accepted))


def save_schedule(schedule, filename):
    """ store a saved schedule in a file """
    with open(filename, "wb") as outfile:
        pickle.dump(schedule, outfile)


def load_schedule(filename):
    """ read a saved schedule from a file """
    with open(filename, "rb") as infile:
        schedule = pickle.load(infile)
    return schedule
