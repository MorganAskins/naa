from . import modifier
#from . import tools
from . import structure

class heart:
    '''
    TODO: write docstring
    '''
    def __init__(self, database=None, datacollection=None, experiment=None):
        if (type(database) != structure.database) and database != None:
            raise TypeError('Database given is not valid')
        if (type(datacollection) != structure.datacollection) and datacollection != None:
            raise TypeError('Datacollection given is not valid')
        if (type(experiment) != structure.experiment) and experiment != None:
            raise TypeError('Experiment given is not valid')
        self.database = database
        self.datacollection = datacollection
        self.experiment = experiment
        self.load_experiment()
        self.mods = []

    def load_experiment(self):
        if self.experiment == None:
            return
        xp = self.experiment
        for sample in xp.samplelist:
            self.datacollection.add_file(sample, 'sample')
        for control_nest in xp.control_nested_list:
            for control in control_nest:
                self.datacollection.add_file(control, 'control')
        for background in xp.bkglist:
            self.datacollection.add_file(background, 'background')
        
    def add_modifier(self, mod):
        if issubclass(mod, modifier.modifier):
            self.mods.append(mod(self.database, self.datacollection, self.experiment))
        else:
            print(type(mod), 'is not a subclass of modifier')
            
    def run_modifier(self, mod):
        modObj = [foo for foo in self.mods if type(foo) is mod][0]
        modObj.run()

    def output_modifier(self, mod):
        modObj = [foo for foo in self.mods if type(foo) is mod][0]
        modObj.output()
            
    def run_all_modifiers(self):
        for mod in self.mods:
            mod.run()
