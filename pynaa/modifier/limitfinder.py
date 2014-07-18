#from naafile import naafile
import math
import numpy as np
#import json
from .modifier import modifier
from ..tool import mfit as mf

## For reading half lives:
US=1/1000.0
S=1
M=60*S
H=60*M
D=24*H
Y=365.25*D


class limitfinder(modifier):
    '''
    Limit finder compares control runs with sample runs for naa
    and set limits on the corresponding peaks using the ratio
    Limit finder inherits from modifier with:
    self.database, self.datacollection, self.experiment
    '''
    def __setup__(self):
        '''
        Match the list of named files in self.experiment with
        open data files in self.datacollection
        '''
        self.name = 'limitfinder'
        xp = self.experiment
        dataC = self.datacollection
        # Build lists of pynaa.structure.datafiles, these are one-to-one with the names list
        self.samplefiles = [[dfile for dfile in dataC.openfiles if dfile.name==samplename][0]
                            for samplename in xp.samplelist]
        self.bkgfiles = [[dfile for dfile in dataC.openfiles if dfile.name==samplename][0]
                         for samplename in xp.bkglist]
        self.control_nested_files = [[[dfile for dfile in dataC.openfiles if dfile.name==samplename][0]
                                       for samplename in namelist] for namelist in xp.control_nested_list]
                 
    def run(self):
        #self.set_backgrounds()
        xp = self.experiment
        # Store results in a list of result dictionaries
        self.results = []
        for spike_dict, ctrl in zip(xp.spike_nested_list, self.control_nested_files):
            for spikes in spike_dict:
                self.results.append(self.find_spike(spikes, ctrl))
        # Save the results to the experiment
        self.experiment.results = self.results
                
    # def set_backgrounds(self):
    #     if len(self.bkglist) == 0:
    #         return                        #no backgrounds
    #     self.bkgnaafile = sum(self.bkglist)

    def find_spike(self, spike, ctrl):
        # For now, just look for highest intensity peak
        # Here are some potential problems that need to be solved:
        # (Can be solved from the fits, needs a goodness of fit...)
        # peaks too close, peaks overlapping
        spike_name = spike['isotope']
        result_dict = {'isotope': spike_name}
        spike_energy = self.__max_intensity_energy__(spike_name)
        result_dict.update({'energy': spike_energy})
        halflife = eval(self.database.search('Nuclide',spike_name)[0]['Half life(s)'])
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
            start_time = nfile.tstart - self.experiment.start_time
            stop_time = nfile.tstop - self.experiment.start_time
            ## Only include files with 2 sigma over bkg
            areasum = integral - (bkg_left+bkg_right)*(steps/(steps_left+steps_right))
            areaerr_sq = integral
            if areasum >= 3*math.sqrt(areaerr_sq):
                control_time_sum += correction(start_time, stop_time)
                control_area_sum += areasum
                control_err_sq += areaerr_sq

        result_dict.update({'control area': control_area_sum})
        result_dict.update({'control area err': math.sqrt(control_err_sq)})
        
        for nfile in self.samplefiles:
            graph = mf.graph(nfile.x, nfile.y)
            integral, steps = graph.integrate(spike_energy-halfwidth, spike_energy+halfwidth)
            bkg_left, steps_left = graph.integrate(spike_energy-halfwidth-pastwidth, spike_energy-halfwidth)
            bkg_right, steps_right = graph.integrate(spike_energy+halfwidth, spike_energy+halfwidth+pastwidth)
            start_time = nfile.tstart - self.experiment.start_time
            stop_time = nfile.tstop - self.experiment.start_time
            ## Only include files with 2 sigma over bkg
            areasum = integral - (bkg_left+bkg_right)*(steps/(steps_left+steps_right))
            areaerr_sq = math.sqrt(integral)
            if areasum >= 3*math.sqrt(areaerr_sq):
                sample_time_sum += correction(start_time, stop_time)
                sample_area_sum += areasum
                sample_err_sq += areaerr_sq

        result_dict.update({'sample area': sample_area_sum})
        result_dict.update({'sample area err': math.sqrt(sample_err_sq)})
        result = (sample_area_sum*spike['mass']*control_time_sum)/(control_area_sum*
                                                                   sample_time_sum*self.experiment.sample_mass)
        result_err = result*math.sqrt(sample_err_sq/sample_area_sum**2 + control_err_sq/control_area_sum**2)
        result_dict.update({'result': result})
        result_dict.update({'result err': result_err})
        return result_dict

    def peak_info(self, spike, ctrl):
        ffunc = lambda p, x: p[0]*mf.compshoulder(x, p[1], p[2], p[3])+p[4]

        spike_energy = self.__max_intensity_energy__(spike['isotope'])
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

    def output(self):
        for result in self.results:
            print('___________________________________________________________')
            print('Looking for ',result['isotope'],'at',result['energy'],'keV')
            print('control area:', '{:.3e}'.format(result['control area']),
                  '+/-', '{:.3e}'.format(result['control area err']))
            print('sample area:', '{:.3e}'.format(result['sample area']),
                  '+/-', '{:.3e}'.format(result['sample area err']))
            print('Results:', '{:.3e}'.format(result['result']),
                  '+/-','{:.3e}'.format(result['result err']), 'g/g', result['isotope'])
            print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

    def __max_intensity_energy__(self, isotope):
        sorted_list = self.database.sortby('Intensity',self.database.search('Nuclide', isotope))
        return (sorted_list[-1])['Energy(keV)']
