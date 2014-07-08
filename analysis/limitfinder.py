from naafile import naafile
import math
import numpy as np
import json
import mfit as mf

## For reading half lives:
US=1/1000.0
S=1
M=60*S
H=60*M
D=24*H
Y=365.25*D


class limitfinder:
    def __init__(self, config):
        self.config = config
        self.load_config()

    def load_config(self):
        '''
        This takes the currently set config dictionary and loads the variables
        into class members
        '''
        max_controls = 50
        self.sample_name = self.config['sample name']
        self.sample_mass = self.config['sample mass']
        self.start_time = self.config['exposure start']
        self.exposure = self.config['exposure time']
        self.reactor_power = self.config['reactor power']
        self.neutron_flux = self.config['neutron flux']
        ## Files
        self.samplelist, self.bkglist = [], []
        for fnames in self.config['samples']:
            self.add_file(fnames, self.samplelist)
        for fnames in self.config['backgrounds']:
            self.add_file(fnames, self.bkglist)
        ## Nested configurations
        cname = lambda x: 'control <'+str(x)+'>'
        sname = lambda x: 'spike <'+str(x)+'>'
        cnames_exist = [cname(i) for i in range(max_controls) if cname(i) in self.config]
        self.controllist = [ [] for i in cnames_exist ]
        self.topspikelist = []
        self.controlmass = [ (self.config[cname])['mass'] for cname in cnames_exist ]
        self.controlname = [ (self.config[cname])['name'] for cname in cnames_exist ]
        # spike list will be [num controls][(spikes in each)]
        
        for idx, ctrls in enumerate(cnames_exist):
            ctrl_dict = self.config[ctrls]
            for fnames in ctrl_dict['controls']:
                self.add_file(fnames, self.controllist[idx])
            snames_exist = [sname(i) for i in range(max_controls) if sname(i) in ctrl_dict]
            subspikelist = [ ctrl_dict[sname] for sname in snames_exist ]
            self.topspikelist.append(subspikelist)

        ## Grab database from first sample naafile
        opendb = open((self.samplelist[0]).gammadb, 'r')
        self.gammadb = json.load(opendb)
                 
    def run(self):
        self.set_backgrounds()
        for spike_dict, ctrl in zip(self.topspikelist, self.controllist):
            for spikes in spike_dict:
                self.find_spike(spikes, ctrl)
            

    def set_backgrounds(self):
        if len(self.bkglist) == 0:
            return                        #no backgrounds
        self.bkgnaafile = sum(self.bkglist)

    def find_spike(self, spike, ctrl):
        # For now, just look for highest intensity peak
        # Here are some potential problems that need to be solved:
        # (Can be solved from the fits, needs a goodness of fit...)
        # 
        spike_name = spike['isotope']
        spike_energy = maxIenergy(self.gammadb, spike_name)
        print('Looking for', spike_name, 'at', spike_energy)
        halflife = eval(searchdb(self.gammadb,'Nuclide',spike_name)[0]['Half life(s)'])
        L = math.log(2)/halflife
        correction = lambda ti, tf: np.exp(-L*ti)-np.exp(-L*tf)
        control_area_sum, sample_area_sum = 0, 0
        control_time_sum, sample_time_sum = 0, 0
        ## Errors:
        control_err_sq, sample_err_sq = 0, 0
        
        ## Use fits to set these magic numbers TODO
        halfwidth, pastwidth = self.peak_info(spike, ctrl)
        #halfwidth = 5
        #pastwidth = 5
        print('halfwidth:', halfwidth, 'pastwidth:', pastwidth)
        if halfwidth < 1:
            halfwidth = 1
        if pastwidth < 1:
            pastwidth = 1
            
        for nfile in ctrl:
            graph = mf.graph(nfile.x, nfile.y)
            integral, steps = graph.integrate(spike_energy-halfwidth, spike_energy+halfwidth)
            bkg_left, steps_left = graph.integrate(spike_energy-halfwidth-pastwidth, spike_energy-halfwidth)
            bkg_right, steps_right = graph.integrate(spike_energy+halfwidth, spike_energy+halfwidth+pastwidth)
            start_time = nfile.tstart - self.start_time
            stop_time = nfile.tstop - self.start_time
            ## Only include files with 2 sigma over bkg
            areasum = integral - (bkg_left+bkg_right)*(steps/(steps_left+steps_right))
            areaerr_sq = integral
            if areasum >= 3*math.sqrt(areaerr_sq):
                control_time_sum += correction(start_time, stop_time)
                control_area_sum += areasum
                control_err_sq += areaerr_sq
        print('control area:', '{:.3e}'.format(control_area_sum), '+/-', '{:.3e}'.format(math.sqrt(control_err_sq)))
        
        for nfile in self.samplelist:
            graph = mf.graph(nfile.x, nfile.y)
            integral, steps = graph.integrate(spike_energy-halfwidth, spike_energy+halfwidth)
            bkg_left, steps_left = graph.integrate(spike_energy-halfwidth-pastwidth, spike_energy-halfwidth)
            bkg_right, steps_right = graph.integrate(spike_energy+halfwidth, spike_energy+halfwidth+pastwidth)
            start_time = nfile.tstart - self.start_time
            stop_time = nfile.tstop - self.start_time
            ## Only include files with 2 sigma over bkg
            areasum = integral - (bkg_left+bkg_right)*(steps/(steps_left+steps_right))
            areaerr_sq = math.sqrt(integral)
            if areasum >= 3*math.sqrt(areaerr_sq):
                sample_time_sum += correction(start_time, stop_time)
                sample_area_sum += areasum
                sample_err_sq += areaerr_sq
        print('sample area:', '{:.3e}'.format(sample_area_sum), '+/-', '{:.3e}'.format(math.sqrt(sample_err_sq)))
        print('sample mass:', '{:.3e}'.format(self.sample_mass))
        print('spike mass:', '{:.3e}'.format(spike['mass']))
        result = (sample_area_sum*spike['mass']*control_time_sum)/(control_area_sum*sample_time_sum*self.sample_mass)
        result_err = result*math.sqrt(sample_err_sq/sample_area_sum**2 + control_err_sq/control_area_sum**2)
        print('!! Results:', '{:.3e}'.format(result), '+/-','{:.3e}'.format(result_err), 'g/g', spike_name)
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

    def peak_info(self, spike, ctrl):
        ffunc = lambda p, x: p[0]*mf.compshoulder(x, p[1], p[2], p[3])+p[4]
        spike_energy = maxIenergy(self.gammadb, spike['isotope'])
        fit_distance = 40
        fits=[]
        # Fit each control file at the specified peak
        for nfile in ctrl:
            x,y = nfile.x, nfile.y
            gr = mf.graph(x, y)
            peak = np.where(x <= spike_energy)[0][-1]
            xmin, xmax = (peak-fit_distance), (peak+fit_distance)
            bwidth = (x[xmax]-x[xmin])/len(x[xmin:xmax])
            p0 = [(sum(y[xmin:xmax])-len(y[xmin:xmax])*min(y[xmin:xmax]))*bwidth/math.pi,
                  spike_energy, 1, 0.5, min(y[xmin:xmax])]
            fitter = mf.function(ffunc, p0, x[xmin], x[xmax])
            gr.fit(fitter)
            fits.append(fitter)
        # Determine which peak is the cleanest, and what width to integrate
        best_fit = 0
        peakbgratio = 0
        for idx, fit in enumerate(fits):
            ratio = fit.p0[0] / fit.p0[4]
            if ratio > peakbgratio:
                peakbgratio = ratio
                best_fit = idx
            
        halfwidth = (fits[best_fit].p0)[3]*math.log(20)
        pastwidth = halfwidth
        return halfwidth, pastwidth
            
                
    def add_file(self, filename, filelist):
        try:
            filelist.append(naafile(filename))
        except (NameError, FileNotFoundError, OSError) as er:
            print(er)


##
def searchdb(db, key, value):
    return [item for item in db if item[key] == value]

def maxIenergy(db, nuclide):
    nuc = searchdb(db, 'Nuclide', nuclide)
    top_energy, intense = 0, 0
    for gamma in nuc:
        if gamma['Intensity'] > intense:
            intense = gamma['Intensity']
            top_energy = gamma['Energy(keV)']
    return top_energy
