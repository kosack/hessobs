Single-Telescope Scheduling
===========================

.. currentmodule:: hessobs.darkness

The :class:`Darkness` object defines a 2D (day vs hour) map of the
available dark time at the telescope site over a year. It allows
targets to be scheduled (filled) into the available time slots, and
handles a set of heuristics for doing so in an optimal manner, while
staying within the given proposal constraints.


Darkness requires a pre-generated map of free dark time per day, which
can be generated for a specific year from the HESS Astro database
using the following script (which requires the
``$HESSROOT/autoscheduler/bin/Darkness`` program to be accessable and
a database connection to the HESS db):

::code sh

  darknesstable.pl 2015 > darkness.dat

Usage
-----

- :py:func:`Darkness.fillTarget` is used to insert targets into the schedule

- the target info must be given as a dictionary of entries from
  the `Observation_Proposals` database table, giving all necessary
  information about the target, the preferences of the proposers,
  and the time allocated by the OC. The :mod:`hessobs.Targets` module provides
  methods to read the database and extract this information

Scheduling Heuristics:
----------------------

The schedule takes into account the range of allowed zenith angles
in the proposal. It uses the zenith information to find an
acceptable observation window.

There are two methods it uses to fill the target (set globally by
:data:`hessobs.Config.DEFAULT_FILL_METHOD`, or for each object by
the `Scheduling_Preference` field in the :class:`hessobs.Targets.Target`

- **zenith** mode perfers small zenith angles, by scheduling in
  increasing stripes of zenith angle until the maximum is reached
  (so the observations may be spread out in time over the full
  year, but are made at small zenith)

  this mode uses the "Scheduling_Zenith_Step" parameter to
  choose how often to step through the zenith range

- **time** mode schedules the objects as fast as possible, allowing
  the full range of zenith angles, so it is good for observations
  you want to do faster, but perhaps at less optimal zeniths.


API Documentation
-----------------

.. automodule:: hessobs.darkness
   :members:
      






