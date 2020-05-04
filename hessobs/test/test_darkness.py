from hessobs.darkness import Darkness
from hessobs.targets import Target
import pkg_resources


def test_schedule():

    filename = pkg_resources.resource_filename("hessobs", "test/darkness2017.dat")
    dark = Darkness(filename)

    total, effcorrected = dark.hoursOfFreeDarkTime()
    assert (total - 1672.5) < 0.1

    dark.generateZenithAngleMapByTarget()

    targ = Target(Target_Name="Test", RA_2000=17.5, Dec_2000=-29, Hours_Accepted=100)

    targ2 = Target(Target_Name="Test2", RA_2000=10.5, Dec_2000=-29, Hours_Accepted=50)

    dark.fillTarget(targ)
    dark.fillTarget(targ2)

    assert len(dark.targets) == 2
    assert dark.hoursOfFreeDarkTime()[0] < 1600

    target_ids = dark.search("Test")
    assert len(target_ids) == 2

    zamap = dark.generateZenithAngleMapByTarget()
    assert zamap.sum() > 0

    dark.printSummary()
    dark.printSchedule(5)
    assert dark.periodName(3) == "2017-03"
