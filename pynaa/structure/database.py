## Reads in the gamma database and neutron xs database
import json                               #To read the db files

class database:
    def __init__(self, dbfile):
        self.dbfile = dbfile
        openfile = open(self.dbfile, 'r')
        self.db = json.load(openfile)
        openfile.close()

    # Specific to the gammadb, TODO: move to gammadb class
    def search(self, key, value):
        return [item for item in self.db if item[key] == value]

    def sortby(self, key, db=None):
        '''
        Returns a sorted copy of the whole db or a subset given
        eg. To sort U238 lines by energy (ascending):
        self.sortby('Energy(keV)',self.search('Nuclide', 'U-238'))
        '''
        if db==None:
            db = self.db
        
        return sorted(db, key=lambda k: k[key])
    
    def energy_range(self, emin, emax, key='Energy(keV)'):
        return [item for item in self.db if (item[key] > emin and item[key] < emax)]    
        
## TODO: Implement these later
class gammadb:
    def __init__(self):
        pass

class xsectiondb:
    def __init__(self):
        pass
