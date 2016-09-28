Working With Targets
====================

.. currentmodule:: hessobs.Targets

The target data structure
-------------------------

Targets are expressed as a python dict containing a set of required fields (that
are identical to the HESS Proposal database fields)

You can create this dictionary using the `Target` class:

.. code-block:: python

    t = Target()
    t.Target_Name = 'MyTarget'
    t.Hours_Accepted = 10
    print(t)

by using the `Target.from_name(name)` constructor

.. code-block:: python

    t = Target.from_name("Sgr A*")

Finally, you can create a list of targets by querying the HESS_Proposals
database using one of the helper functions like `load_targets_from_db()`

.. code-block:: python

    where = """
      Year=2015
      AND Hours_Accepted > 0
      AND Observation_Strategy in ("coordinated","standard")
    """

    targets = load_targets_from_db(where=where, order='Science_Grade DESC')


Functions for manipulating target lists
---------------------------------------

.. automodule:: hessobs.Targets
   :members: 
