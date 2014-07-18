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

%% TODO %%
Future Features: (ordered by importance)
Peak finding
Matching of peaks to gamma emissions (in a smart way)
Spectrum energy correction based on 511 keV
Use of full reactor neutron spectrum
Feldman-Cousins Analysis

%%%% --- Structure Of Analysis--- %%%%

The main library is pynaa, analysis code calls from this library
pynaa has one class: pynaa.heart
pynaa.heart loads in three classes in the library pynaa.structure
pynaa.structures (which include data, databases, and config files)
can be modified through heart by classes derived from
pynaa
$$ pynaa.structure


        |       < structure
        |       
 pynaa <  heart < modifier
        |      
        |       < tool


