from hessobs.targets import Target


def test_custom_target():

    t = Target(Target_Name="bob")
    assert t.Target_Name == "bob"
    assert t.Hours_Accepted == 0


def test_target_from_name():

    t = Target.from_name("Crab")
    assert (t.RA_2000 - 5.575547493333334) < 0.1
