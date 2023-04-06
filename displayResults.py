###########################################################################
#
#   StatEye Simulator
#   by Jeremy Cosson-Martin, Jhoan Salinas
#   Ali Sheikholeslami's group
#   Department of Electrical and Computer Engineering
#   University of Toronto
#   Copyright Material
#   For personal use only
#
###########################################################################
# This function displays the final simulation results. It displays the
# data level and eye dimension results to the command window.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
# 
# Outputs:
#   Data levels, ideal sampling locations and eye dimension results to 
#   command window
#   
###########################################################################

from userSettingsObjects import simulationSettings
from initializeSimulation import simulationStatus

def displayResults(simSettings: simulationSettings,simResults: simulationStatus):

    if simSettings.general.plotting.results and simResults.results.successful:
        
        # Display data levels
        displayDLevs(simResults)
        
        # Display sampler locations
        displaySamplerLocs(simResults)
        
        # Display eye opening
        displayEyeOpening(simSettings, simResults)
        
        # Display channel operating margin
        displayCOM(simResults)


###########################################################################
# This function displays data levels
###########################################################################
def displayDLevs(simResults: simulationStatus):

    # Import variables
    dLevs = simResults.results.dLevs
    
    # Display data levels
    print('----------Data Level Results----------')
    for index in range(len(dLevs)-1, -1, -1):
        print('Data level %i: %.2fV\n'% {index, dLevs[index]})


###########################################################################
# This function displays ideal sampler locations
###########################################################################
def displaySamplerLocs(simResults: simulationStatus):

    # Import variables
    eyeLocs = simResults.results.eyeLocs
    
    # Display eye locations
    print('----------Sampler Location Results----------')
    for index in range(len(eyeLocs.level)-1, -1, -1):
        print('Sampler %i: level: %.2fV, phase: %0.1fdeg\n'% {index, eyeLocs.level[index], eyeLocs.phase})


###########################################################################
# This function displays the eye size results.
###########################################################################
def displayEyeOpening(simSettings: simulationSettings, simResults: simulationStatus):

    # Import variables
    target = simSettings.general.targetBER.value
    eyeDims = simResults.results.eyeDimensions
    bestBER = simResults.results.BER
    
    # Display eye quality
    print('----------Opening Results----------')

    if bestBER > target:
        print('WARNING: Target BER not met!')

    for index, eye in enumerate(eyeDims):
        print('Eye %i height: %.3fV, width: %.2fUI for BER: %.1e\n'% {index, eyeDims.__dict__[eye].height, eyeDims.__dict__[eye].widthUI, bestBER})


###########################################################################
# This function displays the channel operating margin
###########################################################################
def displayCOM(simResults: simulationStatus):

    # Import variables
    com = simResults.results.com
    ber = simResults.results.BER
    
    # Display eye locations
    print('----------Channel Operating Margin----------')
    print('COM: %.1fdB for BER: %.1e\n' % {com, ber})
