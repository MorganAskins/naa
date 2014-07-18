# Example of how to use pynaa to analyze data
import os, sys
import pynaa

def main():
    listoffiles = [foo for foo in os.listdir('./data/SNO+') if foo.endswith('.npz')]
    dbfile = './database/gammalist.json'
    testfile = './data/SNO+/PPO_ThK_spiked_06112014_000.npz'
    ## config file can be generated either by:
    ## pynaa.tool.setup_expmt.setup() or running python setup_expmt.py
    configfile = 'sample_expmt.json'
    
    # Need to build structure objects first
    datastruct = pynaa.structure.datacollection(listoffiles)
    dbstruct = pynaa.structure.database(dbfile)
    expstruct = pynaa.structure.experiment(configfile)
    # Load the test file (optional, can be done with experiment object)
    #datastruct.add_file(testfile, 'control')

    soul = pynaa.heart(datacollection=datastruct, database=dbstruct, experiment=expstruct)
    # Simple test
    soul.add_modifier(pynaa.modifier.deepthought)
    soul.run_modifier(pynaa.modifier.deepthought)
    soul.output_modifier(pynaa.modifier.deepthought)
    # Radionuclide test
    #soul.add_modifier(pynaa.modifier.radionuclide)
    #soul.run_modifier(pynaa.modifier.radionuclide)
    #soul.output_modifier(pynaa.modifier.radionuclide)
    soul.add_modifier(pynaa.modifier.limitfinder)
    soul.run_modifier(pynaa.modifier.limitfinder)
    soul.output_modifier(pynaa.modifier.limitfinder)
    print('End of Examples')
    
if __name__ == '__main__':
    main()
