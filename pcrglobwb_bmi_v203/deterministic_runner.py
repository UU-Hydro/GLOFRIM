#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging

from pcraster.framework import DynamicModel
from pcraster.framework import DynamicFramework

from configuration import Configuration
from currTimeStep import ModelTime
from reporting import Reporting
from spinUp import SpinUp

import pcraster as pcr

from pcrglobwb import PCRGlobWB

logger = logging.getLogger(__name__)

class DeterministicRunner(DynamicModel):

    def __init__(self, configuration, modelTime, initialState = None, system_argument = None):
        DynamicModel.__init__(self)

        self.modelTime = modelTime        
        self.model = PCRGlobWB(configuration, modelTime, initialState)
        self.reporting = Reporting(configuration, self.model, modelTime)
        
        # the model will set paramaters based on global pre-multipliers given in the argument:
        self.adusting_parameters(configuration, system_argument)

        # make the configuration available for the other method/function
        self.configuration = configuration
            
    def adusting_parameters(self, configuration, system_argument): 
        
        # it is also possible to define prefactors via the ini/configuration file: 
        # - this will be overwrite any previous given pre-multipliers
        if 'prefactorOptions' in configuration.allSections:
            
            logger.info("Adjusting some model parameters based on given values in the ini/configuration file.")

            self.multiplier_for_refPotET    = float(configuration.prefactorOptions['linear_multiplier_for_refPotET'        ])  # linear scale  # Note that this one does NOT work for the changing WMIN or Joyce land cover options.
            multiplier_for_degreeDayFactor  = float(configuration.prefactorOptions['linear_multiplier_for_degreeDayFactor' ])  # linear scale
            multiplier_for_minSoilDepthFrac = float(configuration.prefactorOptions['linear_multiplier_for_minSoilDepthFrac'])  # linear scale
            multiplier_for_kSat             = float(configuration.prefactorOptions['log_10_multiplier_for_kSat'            ])  # log scale
            multiplier_for_storCap          = float(configuration.prefactorOptions['linear_multiplier_for_storCap'         ])  # linear scale
            multiplier_for_recessionCoeff   = float(configuration.prefactorOptions['log_10_multiplier_for_recessionCoeff'  ])  # log scale
        
        # saving global pre-multipliers to the log file:
        msg  = "\n" 
        msg += "\n" 
        msg += "Multiplier values used: "+"\n" 
        msg += "For minSoilDepthFrac           : "+str(multiplier_for_minSoilDepthFrac)+"\n"
        msg += "For kSat (log-scale)           : "+str(multiplier_for_kSat            )+"\n"
        msg += "For recessionCoeff (log-scale) : "+str(multiplier_for_recessionCoeff  )+"\n"
        msg += "For storCap                    : "+str(multiplier_for_storCap         )+"\n"
        msg += "For degreeDayFactor            : "+str(multiplier_for_degreeDayFactor )+"\n"
        msg += "For refPotET                   : "+str(self.multiplier_for_refPotET   )+"\n"
        logger.info(msg)
        # - also to a txt file 
        f = open("multiplier.txt","w") # this will be stored in the "map" folder of the 'outputDir' (as we set the current working directory to this "map" folder, see configuration.py)
        f.write(msg)
        f.close()

        # set parameter "recessionCoeff" based on the given pre-multiplier
        # - also saving the adjusted parameter maps to pcraster files
        # - these will be stored in the "map" folder of the 'outputDir' (as we set the current working directory to this "map" folder, see configuration.py)
        # "recessionCoeff"
        # minimum value is zero and using log-scale
        self.model.groundwater.recessionCoeff = pcr.max(0.0, (10**(multiplier_for_recessionCoeff)) * self.model.groundwater.recessionCoeff)
        self.model.groundwater.recessionCoeff = pcr.min(1.0, self.model.groundwater.recessionCoeff)
        # report the map
        pcr.report(self.model.groundwater.recessionCoeff, "recessionCoeff.map")
        
        # set parameters "kSat", "storCap", "minSoilDepthFrac", and "degreeDayFactor" based on the given pre-multipliers
        for coverType in self.model.landSurface.coverTypes:

            # "degreeDayFactor"
            self.model.landSurface.landCoverObj[coverType].degreeDayFactor  = pcr.max(0.0, multiplier_for_degreeDayFactor  *\
                                                           self.model.landSurface.landCoverObj[coverType].degreeDayFactor)
            # report the map
            pcraster_filename = "degreeDayFactor" + "_" + coverType + ".map" 
            pcr.report(self.model.landSurface.landCoverObj[coverType].degreeDayFactor , pcraster_filename)

        # "kSat" and "storCap" for 2 layer model
        if self.model.landSurface.numberOfSoilLayers == 2:

            # "kSat"
			    # minimum value is zero and using-log-scale
            self.model.landSurface.parameters.kSatUpp = \
                   pcr.max(0.0, (10**(multiplier_for_kSat)) * self.model.landSurface.parameters.kSatUpp)
            self.model.landSurface.parameters.kSatLow = \
                   pcr.max(0.0, (10**(multiplier_for_kSat)) * self.model.landSurface.parameters.kSatLow)
            
            # report the maps (for debugging)
            #pcraster_filename = "kSatUpp"+ "_" + coverType + ".map" 
            #pcr.report(self.model.landSurface.parameters.kSatUpp, pcraster_filename)
            #pcraster_filename = "kSatLow"+ "_" + coverType + ".map" 
            #pcr.report(self.model.landSurface.parameters.kSatLow, pcraster_filename)

            # "storCap"
            # minimum value is zero
            self.model.landSurface.parameters.storCapUpp = pcr.max(0.0, multiplier_for_storCap*\
                                                                                                self.model.landSurface.parameters.storCapUpp)
            self.model.landSurface.parameters.storCapLow = pcr.max(0.0, multiplier_for_storCap*\
                                                                                                self.model.landSurface.parameters.storCapLow)
            # report the maps (for debugging)
            #pcraster_filename = "storCapUpp"+ "_" + coverType + ".map" 
            #pcr.report(self.model.landSurface.parameters.storCapUpp, pcraster_filename)
            #pcraster_filename = "storCapLow"+ "_" + coverType + ".map" 
            #pcr.report(self.model.landSurface.parameters.storCapLow, pcraster_filename)
            
        # "kSat" and "storCap" for 3 layer model
        if self.model.landSurface.numberOfSoilLayers == 3:

            # "kSat"
			    # minimum value is zero and using-log-scale
            self.model.landSurface.landCoverObj[coverType].parameters.kSatUpp000005 = \
                   pcr.max(0.0, (10**(multiplier_for_kSat)) * self.model.landSurface.landCoverObj[coverType].parameters.kSatUpp000005)
            self.model.landSurface.landCoverObj[coverType].parameters.kSatUpp005030 = \
                   pcr.max(0.0, (10**(multiplier_for_kSat)) * self.model.landSurface.landCoverObj[coverType].parameters.kSatUpp005030)
            self.model.landSurface.landCoverObj[coverType].parameters.kSatLow030150 = \
                   pcr.max(0.0, (10**(multiplier_for_kSat)) * self.model.landSurface.landCoverObj[coverType].parameters.kSatLow030150)
            # report the maps
            pcraster_filename = "kSatUpp000005"+ "_" + coverType + ".map" 
            pcr.report(self.model.landSurface.landCoverObj[coverType].parameters.kSatUpp000005, pcraster_filename)
            pcraster_filename = "kSatUpp005030"+ "_" + coverType + ".map" 
            pcr.report(self.model.landSurface.landCoverObj[coverType].parameters.kSatUpp005030, pcraster_filename)
            pcraster_filename = "kSatLow030150"+ "_" + coverType + ".map" 
            pcr.report(self.model.landSurface.landCoverObj[coverType].parameters.kSatLow030150, pcraster_filename)

            # "storCap"
            # minimum value is zero
            self.model.landSurface.landCoverObj[coverType].parameters.storCapUpp000005 = pcr.max(0.0, multiplier_for_storCap*\
                                                                                                      self.model.landSurface.landCoverObj[coverType].parameters.storCapUpp000005)
            self.model.landSurface.landCoverObj[coverType].parameters.storCapUpp005030 = pcr.max(0.0, multiplier_for_storCap*\
                                                                                                      self.model.landSurface.landCoverObj[coverType].parameters.storCapUpp005030)
            self.model.landSurface.landCoverObj[coverType].parameters.storCapLow030150 = pcr.max(0.0, multiplier_for_storCap*\
                                                                                                      self.model.landSurface.landCoverObj[coverType].parameters.storCapLow030150)
            # report the maps
            pcraster_filename = "storCapUpp000005"+ "_" + coverType + ".map" 
            pcr.report(self.model.landSurface.landCoverObj[coverType].parameters.storCapUpp000005, pcraster_filename)
            pcraster_filename = "storCapUpp005030"+ "_" + coverType + ".map" 
            pcr.report(self.model.landSurface.landCoverObj[coverType].parameters.storCapUpp005030, pcraster_filename)
            pcraster_filename = "storCapLow030150"+ "_" + coverType + ".map" 
            pcr.report(self.model.landSurface.landCoverObj[coverType].parameters.storCapLow030150, pcraster_filename)


        # re-calculate rootZoneWaterStorageCap as the consequence of the modification of "storCap"
        # This is WMAX in the oldcalc script.
        if self.model.landSurface.numberOfSoilLayers == 2:
            self.model.landSurface.parameters.rootZoneWaterStorageCap = self.model.landSurface.parameters.storCapUpp +\
                                                                                                self.model.landSurface.parameters.storCapLow
        if self.model.landSurface.numberOfSoilLayers == 3:
            self.model.landSurface.landCoverObj[coverType].parameters.rootZoneWaterStorageCap = self.model.landSurface.landCoverObj[coverType].parameters.storCapUpp000005 +\
                                                                                                self.model.landSurface.landCoverObj[coverType].parameters.storCapUpp005030 +\
																									self.model.landSurface.landCoverObj[coverType].parameters.storCapLow030150
        # report the map
        #pcraster_filename = "rootZoneWaterStorageCap"+ "_" + coverType + ".map" 
        #pcr.report(self.model.landSurface.parameters.rootZoneWaterStorageCap, pcraster_filename)
        
        # "minSoilDepthFrac"
        if multiplier_for_minSoilDepthFrac != 1.0:
            
            for coverType in self.model.landSurface.coverTypes:            
            
                # minimum value is zero
                self.model.landSurface.landCoverObj[coverType].minSoilDepthFrac = pcr.max(0.0, multiplier_for_minSoilDepthFrac*\
                                                               self.model.landSurface.landCoverObj[coverType].minSoilDepthFrac)
                # for minSoilDepthFrac - values will be limited by maxSoilDepthFrac
                self.model.landSurface.landCoverObj[coverType].minSoilDepthFrac = pcr.min(\
                                                               self.model.landSurface.landCoverObj[coverType].minSoilDepthFrac,\
                                                               self.model.landSurface.landCoverObj[coverType].maxSoilDepthFrac)
                # maximum value is 1.0
                self.model.landSurface.landCoverObj[coverType].minSoilDepthFrac = pcr.min(1.0, self.model.landSurface.landCoverObj[coverType].minSoilDepthFrac)
                # report the map
                pcraster_filename = "minSoilDepthFrac"+ "_" + coverType + ".map" 
                pcr.report(self.model.landSurface.landCoverObj[coverType].minSoilDepthFrac, pcraster_filename)
                
                # re-calculate arnoBeta (as the consequence of the modification of minSoilDepthFrac)
                self.model.landSurface.landCoverObj[coverType].arnoBeta = pcr.max(0.001,\
                     (self.model.landSurface.landCoverObj[coverType].maxSoilDepthFrac-1.)/(1.-self.model.landSurface.landCoverObj[coverType].minSoilDepthFrac)+\
                                               self.model.landSurface.parameters.orographyBeta-0.01)
                self.model.landSurface.landCoverObj[coverType].arnoBeta = pcr.cover(pcr.max(0.001,\
                      self.model.landSurface.landCoverObj[coverType].arnoBeta), 0.001)
                # report the map
                pcraster_filename = "arnoBeta"+ "_" + coverType + ".map" 
                pcr.report(self.model.landSurface.landCoverObj[coverType].arnoBeta, pcraster_filename)
                
                # re-calculate rootZoneWaterStorageMin (as the consequence of the modification of minSoilDepthFrac)
                # This is WMIN in the oldcalc script.
                # WMIN (unit: m): minimum local soil water capacity within the grid-cell
                self.model.landSurface.landCoverObj[coverType].rootZoneWaterStorageMin = self.model.landSurface.landCoverObj[coverType].minSoilDepthFrac *\
                                                                                         self.model.landSurface.parameters.rootZoneWaterStorageCap 
                # report the map
                pcraster_filename = "rootZoneWaterStorageMin"+ "_" + coverType + ".map" 
                pcr.report(self.model.landSurface.landCoverObj[coverType].rootZoneWaterStorageMin, pcraster_filename)
                
                # re-calculate rootZoneWaterStorageRange (as the consequence of the modification of rootZoneWaterStorageRange and minSoilDepthFrac)
                # WMAX - WMIN (unit: m)
                self.model.landSurface.landCoverObj[coverType].rootZoneWaterStorageRange = self.model.landSurface.parameters.rootZoneWaterStorageCap -\
                                                                                           self.model.landSurface.landCoverObj[coverType].rootZoneWaterStorageMin
                # report the map
                #pcraster_filename = "rootZoneWaterStorageRange"+ "_" + coverType + ".map" 
                #pcr.report(self.model.landSurface.landCoverObj[coverType].rootZoneWaterStorageRange, pcraster_filename)
        
    def initial(self): 
        pass

    def dynamic(self):

        # re-calculate current model time using current pcraster timestep value
        self.modelTime.update(self.currentTimeStep())

        # update model (will pick up current model time from model time object)
        
        self.model.read_forcings()
        self.model.update(report_water_balance=True)
        

        #do any needed reporting for this time step        
        self.reporting.report()

def main():
	
    initial_state = None
    configuration = Configuration()
    
    spin_up = SpinUp(configuration)                   # object for spin_up
    
    currTimeStep = ModelTime() # timeStep info: year, month, day, doy, hour, etc
    
    # spinningUp
    noSpinUps = int(configuration.globalOptions['maxSpinUpsInYears'])
    if noSpinUps > 0:
        
        logger.info('Spin-Up #Total Years: '+str(noSpinUps))

        spinUpRun = 0 ; has_converged = False
        while spinUpRun < noSpinUps and has_converged == False:
            spinUpRun += 1
            currTimeStep.getStartEndTimeStepsForSpinUp(
                    configuration.globalOptions['startTime'],
                    spinUpRun, noSpinUps)
            logger.info('Spin-Up Run No. '+str(spinUpRun))
            deterministic_runner = DeterministicRunner(configuration, currTimeStep, initial_state)
            
            all_state_begin = deterministic_runner.model.getAllState() 
            
            dynamic_framework = DynamicFramework(deterministic_runner,currTimeStep.nrOfTimeSteps)
            dynamic_framework.setQuiet(True)
            dynamic_framework.run()
            
            all_state_end = deterministic_runner.model.getAllState() 
            
            has_converged = spin_up.checkConvergence(all_state_begin, all_state_end, spinUpRun, deterministic_runner.model.routing.cellArea)
            
            initial_state = deterministic_runner.model.getState()
    #
    # Running the deterministic_runner (excluding DA scheme)
    currTimeStep.getStartEndTimeSteps(configuration.globalOptions['startTime'],
                                      configuration.globalOptions['endTime'])
    
    logger.info('Transient simulation run started.')
    deterministic_runner = DeterministicRunner(configuration, currTimeStep, initial_state)
    
    dynamic_framework = DynamicFramework(deterministic_runner,currTimeStep.nrOfTimeSteps)
    dynamic_framework.setQuiet(True)
    dynamic_framework.run()

if __name__ == '__main__':
    sys.exit(main())

