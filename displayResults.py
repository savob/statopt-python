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
        print('Data level {0:d}: {1:.3f}V\n'.format(index, dLevs[index]))


###########################################################################
# This function displays ideal sampler locations
###########################################################################
def displaySamplerLocs(simResults: simulationStatus):

    # Import variables
    eyeLocs = simResults.results.eyeLocs
    
    # Display eye locations
    print('----------Sampler Location Results----------')
    if type(eyeLocs.level) == int:
        print('Sampler {0:d}: level: {1:.3f}V, phase: {2:3.1f}deg\n'.format(0, eyeLocs.level, eyeLocs.phase)) # Case for single eye
    else:
        for index in range(len(eyeLocs.level)-1, -1, -1):
            print('Sampler {0:d}: level: {1:.3f}V, phase: {2:3.1f}deg\n'.format(index, eyeLocs.level[index], eyeLocs.phase))


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

    for index, eye in enumerate(eyeDims.__dict__):
        print('Eye {0:d} height: {1:.3f}V, width: {2:.2f}UI for BER: {3:.1e}\n'.format(index, eyeDims.__dict__[eye].height, eyeDims.__dict__[eye].widthUI, bestBER))


###########################################################################
# This function displays the channel operating margin
###########################################################################
def displayCOM(simResults: simulationStatus):

    # Import variables
    com = simResults.results.com
    ber = simResults.results.BER
    
    # Display eye locations
    print('----------Channel Operating Margin----------')
    print('COM: {0:1f}dB for BER: {1:.1e}\n'.format(com, ber))
