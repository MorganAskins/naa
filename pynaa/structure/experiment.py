import json

class experiment:
    def __init__(self, configfile):
        self.configfile = configfile
        openfile = open(self.configfile, 'r')
        self.config = json.load(openfile)
        openfile.close()
        self.load_config()

    def load_config(self):
        '''
        This takes the currently set config dictionary and loads the
        variables into class members
        '''
        max_controls = 50
        self.sample_name = self.config['sample name']
        self.sample_mass = self.config['sample mass']
        self.start_time = self.config['exposure start']
        self.exposure = self.config['exposure time']
        self.reactor_power = self.config['reactor power']
        self.neutron_flux = self.config['neutron flux']
        ### Files to be used, these are different than the files
        ### loaded into datacollection
        self.samplelist = self.config['samples']
        self.bkglist = self.config['backgrounds']
        ### Nested configurations
        cname = lambda x: 'control <'+str(x)+'>'
        sname = lambda x: 'spike <'+str(x)+'>'
        cnames_exist = [cname(i) for i in range(max_controls) if cname(i) in self.config]
        self.control_nested_list = [ [] for i in cnames_exist ]
        self.spike_nested_list = []
        self.controlmass = [ (self.config[cname])['mass'] for cname in cnames_exist ]
        self.controlname = [ (self.config[cname])['name'] for cname in cnames_exist ]
        for idx, ctrls in enumerate(cnames_exist):
            ctrl_dict = self.config[ctrls]
            self.control_nested_list[idx] = ctrl_dict['controls']
            snames_exist = [sname(i) for i in range(max_controls) if sname(i) in ctrl_dict]
            self.spike_nested_list.append([ctrl_dict[sname] for sname in snames_exist])
