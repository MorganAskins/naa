:: PyNaa (Python Neutron Activation Analysis) ::

pynaa is used for simulation and analysis of 'neutron activation analysis'
experiments.

Dependencies:
-- python (with numpy, scipy, matplotlib)
-- pyne ( for reading of endf files and obtaining cross sections )
	https://github.com/pyne/pyne
-- json (python version)
-- hdf5 (eventually, python version)
(optional)
-- root (Not Yet Added ... )

Current Features:
Forward and backward simulation of sample activation

Future Features: (ordered by importance)
Peak finding
Matching of peaks to gamma emissions (in a smart way)
Spectrum energy correction based on 511 keV
Use of full reactor neutron spectrum

For root, will add spe2root.cpp (not making pyroot a dependency)
