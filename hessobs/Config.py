#
# This file defines all of the necessary configuration variables for
# the scheduling
#

TELESCOPE_LONGITIUDE_DEG = 16.30  # degrees east
TELESCOPE_LATITUDE_DEG = -23.26  # degrees north

DEFAULT_MINIMUM_FILL_FRACTION = 0.50
MINIMUM_HOURS_PER_DAY = 0.5  # don't fill a target into a day if less than this

# List of efficiencies spanning the year. These were the efficiences
# used in previous versions of the schedule. They are quite optimistic
DEFAULT_MONTH_EFFICIENCIES = [0.53,  # Jan
                              0.40,  # Feb
                              0.45,  # Mar
                              0.50,  # Apr
                              0.76,  # May
                              0.8,  # Jun
                              0.88,  # Jul
                              0.81,  # Aug
                              0.79,  # Sep
                              0.80,  # Oct
                              0.55,  # Nov
                              0.53]  # Dec

# from Konrad's measurements, averages over each year with RMS values.
MEASURED_MONTH_EFFICIENCIES = [(0.26, 0.16),  # jan
                               (0.26, 0.23),  # feb
                               (0.37, 0.18),  # mar
                               (0.52, 0.14),  # apr
                               (0.67, 0.08),  # may
                               (0.76, 0.08),  # jun
                               (0.74, 0.06),  # jul
                               (0.74, 0.05),  # aug
                               (0.63, 0.14),  # sep
                               (0.51, 0.11),  # oct
                               (0.50, 0.10),  # nov
                               (0.46, 0.13), ]  # dec


# Resolution of the schedule map
BINS_PER_HOUR = 2  # default is 2=half-hour bins (which prevents
# scheduling any sub-runs)


# define all the required attributes for a source, and their defaults
# if they don't exist in the data:
DEFAULT_TARGET_ATTRIBS = dict(Zenith_Min=0,
                              Zenith_Max=50,
                              Wobble_Offset=0.5,
                              Working_Group_Rank=1000,
                              Approval_Class="C",
                              Year=-1,
                              Seqno=-1,
                              Required_Data_Quality="unknown",
                              Target_Name="No Target Name",
                              Comments="",
                              Special_Requests="",
                              Dec_2000=TELESCOPE_LATITUDE_DEG,
                              RA_2000=-1,
                              Hours_Accepted=0,
                              Hours_Requested=0,
                              Working_Group="All",
                              Start_Date=None,
                              End_Date=None,
                              Observation_Strategy="standard",
                              Observation_Mode="wobble",
                              # zenith (to prefer small zenith) or
                              # time (for quicker observations, but
                              # possibly wider zenith
                              Scheduling_Preference="time",
                              Scheduling_Frequency=0,
                              Scheduling_Efficency='standard',  # vs 'ignore'
                              Scheduling_Zenith_Step=5.0,
                              Scheduling_Min_Fraction=0.5,
                              Subarray="CT1-5 Hybrid",
                              Subarray_worst="CT1-5 Hybrid")
