## This is the modifier base class
from .. import structure

class modifier:
    def __init__(self, database, datacollection, experiment):
        self.database = database
        self.datacollection = datacollection
        self.experiment = experiment
        self.__setup__()
    def __setup__(self):
        self.name = None
    def run(self):
        raise AttributeError('run is not defined in this modifier!!!')
    def output(self):
        raise AttributeError('output is not defined in this modifier!!!')
