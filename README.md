# hessobs
Tools for HESS observation planning

## Command-line Tools:

The following works anywhere
- `hessobs-visplot`: show altitide and azimuth plot of object at HESS, MAGIC, VERITAS for a given night
- `hessobs-animate`: make animated visplot


The following requrire read access to the HESS internal database:
- `hessobs-summary`: produce summary plot and data of observations for a given time period 
- `hessobs-ingestproposal`: add a proposal to the proposal db
- `hessobs-verifyprop`: check a proposal in the db

## Scheduling Example

```python
import time
from datetime import datetime

from PySched.Scheduler import HESSIIScheduler, save_schedule, load_schedule
from PySched import Config, load_targets_from_db

#====================================================================
# choose efficencies
#====================================================================
eff_avg, eff_rms = array(Config.MEASURED_MONTH_EFFICIENCIES).T
too_reserve_frac = 0.15  # how much to reserve for TOOs
optimism_frac = 0.5  # add 50% RMS due to speedup of daq
eff = (eff_avg + eff_rms * optimism_frac) - too_reserve_frac

#====================================================================
# Create the schedules, one for each subarray type
#====================================================================

sched = HESSIIScheduler("darkness2015.dat", efficiencies=eff, binsperhour=16)

#====================================================================
# first load all HESS-II targets, ordered by the approval
# class and schedule those:
#====================================================================

where = """
  Year=2014 
  AND Hours_Accepted > 0
  AND Observation_Strategy in ("coordinated","standard") 
"""

targets = load_targets_from_db(where=where)

if os.path.exists("target-order.org"):
    targets = order_targets_from_file(targets, "target-order.org")

sched.schedule(targets)


#====================================================================
# show differences and ask to save:
#====================================================================

if os.path.exists("sched.pickle"):
    sched.diff("sched.pickle")


answer = raw_input("Save this schedule? [y/n] ")
if answer == "y" or answer == "Y":
    save_schedule(sched, "sched.pickle")


```
