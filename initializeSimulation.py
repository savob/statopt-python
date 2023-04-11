from userSettingsObjects import simulationSettings
from numpy import linspace, arange, array
from dataclasses import dataclass

@dataclass
class simulationResults:
    successful: bool = True


class channelInfluence:
    transferFunction: array
    frequencies: array
    impulseResponse: array

    def __init__(self, tf = array((1), dtype='complex128'), freq = array(1,), impResp = array(1,)):
        self.transferFunction = tf
        self.frequencies = freq
        self.impulseResponse = impResp

class channelsThatInfluence:
    thru: channelInfluence

    def __init__(self):
        self.thru = channelInfluence()

class influenceSourcesClass:
    channel: channelsThatInfluence

    def __init__(self):
        self.channel = channelsThatInfluence()

class simulationStatus:

    def __init__(self):
        self.finished: bool = False
        self.results: simulationResults = simulationResults()
        self.influenceSources: influenceSourcesClass = influenceSourcesClass()

        self.channelData = channelsThatInfluence() # will have a 'thru' channel but I think that's fine


        


def initializeSimulation(simSettings: simulationSettings):
    
    # Initialize result structure
    simResults = simulationStatus()
    
    # General settings
    addGeneralSettings(simSettings)
        
    # Transmitter settings
    addTransmitterSettings(simSettings)
    
    # Adaption settings
    addAdaptionSettings(simSettings)

    return simResults

###########################################################################
# This function adds fixed general settings.
###########################################################################
def addGeneralSettings(simSettings: simulationSettings):

    # Determine number of data levels
    match(simSettings.general.signalingMode):
        case '1+D':
            simSettings.general.levelNumb.value = 2*simSettings.general.modulation.value-1
        case '1+0.5D':
            simSettings.general.levelNumb.value = 3*simSettings.general.modulation.value-2
        case 'clock':
            simSettings.general.modulation.value = 2
            simSettings.general.levelNumb.value = simSettings.general.modulation.value
        case _:
            simSettings.general.levelNumb.value = simSettings.general.modulation.value
    
    simSettings.general.samplerNumb.value = simSettings.general.levelNumb.value-1
    
    # Set additional rates
    simSettings.general.symbolPeriod.value = 1/simSettings.general.symbolRate.value
    simSettings.general.sampleRate.value = simSettings.general.symbolRate.value*simSettings.general.samplesPerSymb.value
    simSettings.general.samplePeriod.value = 1/simSettings.general.sampleRate.value
    
    # Define axis
    simSettings.general.yIncrement.value = 2*simSettings.receiver.signalAmplitude.value/(simSettings.general.yAxisLength.value-1)
    simSettings.general.yAxisLength.value = 1 + 2 * int(simSettings.receiver.signalAmplitude.value / simSettings.general.yIncrement.value) # Determine length from increment and add one for zero
    simSettings.general.yAxis.value = linspace(-simSettings.receiver.signalAmplitude.value, simSettings.receiver.signalAmplitude.value, simSettings.general.yAxisLength.value)
    samplesPerSymbol = simSettings.general.samplesPerSymb.value
    simSettings.general.xAxisCenter.value = linspace(-0.5*samplesPerSymbol, 0.5*samplesPerSymbol, samplesPerSymbol + 1)*simSettings.general.samplePeriod.value
    simSettings.general.xAxisLong.value = arange(samplesPerSymbol * simSettings.general.numbSymb.value) * simSettings.general.samplePeriod.value


###########################################################################
# This function adds fixed transmitter settings.
###########################################################################
def addTransmitterSettings(simSettings: simulationSettings):

    simSettings.transmitter.EQ.taps.main.value = 1; # will be adjusted later
    simSettings.transmitter.cursorCount.value = simSettings.transmitter.preCursorCount.value+simSettings.transmitter.postCursorCount.value+1 # pre+post+main


###########################################################################
# This function adds fixed adaption settings.
###########################################################################
def addAdaptionSettings(simSettings: simulationSettings):

    # Add dependent settings
    simSettings.adaption.totalPopulation.value = simSettings.adaption.totalParents.value+simSettings.adaption.childrenPerParent.value*\
        simSettings.adaption.totalParents.value+simSettings.adaption.totalMutations.value   
    simSettings.adaption.totalSimulations.value = simSettings.adaption.totalPopulation.value +\
        (simSettings.adaption.totalPopulation.value-simSettings.adaption.totalParents.value)*\
        (simSettings.adaption.mode1Generations.value+simSettings.adaption.mode2Generations.value-1)
    simSettings.adaption.speedUpSim = False 
    
    # Configure for adaption
    if(simSettings.adaption.adapt):
        
        # Save original settings
        simSettings.adaption.savedSettings.modulation      = simSettings.general.modulation
        simSettings.adaption.savedSettings.samplerNumb     = simSettings.general.samplerNumb
        simSettings.adaption.savedSettings.levelNumb       = simSettings.general.levelNumb
        simSettings.adaption.savedSettings.preCursorCount  = simSettings.transmitter.preCursorCount
        simSettings.adaption.savedSettings.postCursorCount = simSettings.transmitter.postCursorCount
        simSettings.adaption.savedSettings.cursorCount     = simSettings.transmitter.cursorCount
        
        # Set adaption defaults
        match(simSettings.general.signalingMode):
            case '1+D':
                simSettings.general.modulation.value = 2
                simSettings.general.levelNumb.value = 2*simSettings.general.modulation.value-1
            case '1+0.5D':
                simSettings.general.modulation.value = 2
                simSettings.general.levelNumb.value = 3*simSettings.general.modulation.value-2
            case 'clock':
                simSettings.general.modulation.value = 2
                simSettings.general.levelNumb.value = simSettings.general.modulation.value
            case _:
                simSettings.general.modulation.value = 2
                simSettings.general.levelNumb.value = simSettings.general.modulation.value
        
        simSettings.general.samplerNumb.value = simSettings.general.levelNumb.value-1
        simSettings.transmitter.preCursorCount.value = 2 
        simSettings.transmitter.postCursorCount.value = 4
        simSettings.transmitter.cursorCount.value = simSettings.transmitter.preCursorCount.value+simSettings.transmitter.postCursorCount.value+1 # pre+main+post
        
        # Add a knob for the main EQ tap if there isn't one already specified
        if not 'transmitter.EQ.taps.main' in simSettings.adaption.knobs:
            simSettings.adaption.knobs.append('transmitter.EQ.taps.main') # add tap to ensure it is updated correctly
        
        simSettings.channel.approximate = True
