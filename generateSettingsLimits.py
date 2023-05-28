###########################################################################
#
#   StatEye Simulator
#   by Jeremy Cosson-Martin, Jhoan Salinas of
#   Ali Sheikholeslami's group
#   Ported to Python 3 by Savo Bajic
#   Department of Electrical and Computer Engineering
#   University of Toronto
#   Copyright Material
#   For personal use only
#
###########################################################################
# These functions are responsible for adding limits to the simulation knobs
# which are used to later verify that the user's configuration is valid for
# the simulation.
#
# Inputs:
#   simSettings: structure containing simulation settings
# 
###########################################################################

from userSettingsObjects import simulationSettings, valueWithLimits

def generateSettingsLimits(simSettings: simulationSettings):
    # Add all limit settings for the entire system

    addGeneralSettings(simSettings)
    addAdaptionSettings(simSettings)
    addTransmitterSettings(simSettings)
    addChannelSettings(simSettings)
    addReceiverSettings(simSettings)


###########################################################################
# This function adds setting requirements to a specific variable.
###########################################################################
def addLimits(targetValue: valueWithLimits,max,min,increment):

    # Set the limits 'inplace' if a value other than '[]' is passed in    
    if(not isinstance(max, list)): targetValue.maxValue = max
    if(not isinstance(min, list)): targetValue.minValue = min
    if(not isinstance(increment, list)): targetValue.increment = increment


###########################################################################
# This function adds general setting limits.
###########################################################################
def addGeneralSettings(simSettings: simulationSettings):

    # Rate limits
    addLimits(simSettings.general.symbolRate,1e12,[],[])
    addLimits(simSettings.general.symbolPeriod,[],1e-12,[])
    addLimits(simSettings.general.sampleRate,1e15,[],[])
    addLimits(simSettings.general.samplePeriod,[],1e-15,[])
    
    # Accuracy limits
    addLimits(simSettings.general.samplesPerSymb,1e3,25,1)
    addLimits(simSettings.general.yAxisLength,1e3,25,2)
    addLimits(simSettings.general.yIncrement,1,1e-4,[])
    addLimits(simSettings.general.contLevels,15,5,1)

    # Other limits
    addLimits(simSettings.general.modulation,16,2,1)
    addLimits(simSettings.general.levelNumb,[],2,1)
    addLimits(simSettings.general.samplerNumb,15,1,1)
    addLimits(simSettings.general.numbSymb,10,1,1)
    addLimits(simSettings.general.targetBER,1e-1,1e-12,[])


###########################################################################
# This function adds adaption setting limits.
###########################################################################
def addAdaptionSettings(simSettings: simulationSettings):

    addLimits(simSettings.adaption.totalSimulations,[],1,1)
    addLimits(simSettings.adaption.totalPopulation,[],1,1)
    addLimits(simSettings.adaption.totalParents,[],1,1)
    addLimits(simSettings.adaption.childrenPerParent,[],1,1)
    addLimits(simSettings.adaption.totalMutations,[],0,1)
    addLimits(simSettings.adaption.mode1Generations,[],0,1)
    addLimits(simSettings.adaption.mode2Generations,[],0,1)


###########################################################################
# This function adds transmitter setting limits.
###########################################################################
def addTransmitterSettings(simSettings: simulationSettings):
    
    # Max amplitude
    addLimits(simSettings.transmitter.signalAmplitude,10,[],[])
    
    # Rise/fall time
    addLimits(simSettings.transmitter.tRise,[],0,[])
    
    # Bandwidth
    addLimits(simSettings.transmitter.TXBandwidth,50e9,1e9,[])
    
    # Cursor count
    addLimits(simSettings.transmitter.preCursorCount,100,1,1)
    addLimits(simSettings.transmitter.postCursorCount,100,1,1)
    addLimits(simSettings.transmitter.cursorCount,100,1,1)
    
    # Pre-emphasis
    addLimits(simSettings.transmitter.EQ.taps.main,1,0,0.05) # add main tap individually
    for tap in simSettings.transmitter.EQ.taps.__dict__:
        if not tap == 'main':
            addLimits(simSettings.transmitter.EQ.taps.__dict__[tap],1,-1,0.05)
    
    # Jitter
    addLimits(simSettings.transmitter.jitter.stdDeviation,[],0,[])
    addLimits(simSettings.transmitter.jitter.amplitude,[],0,[])
    addLimits(simSettings.transmitter.jitter.DCD,1,0,[])
    
    # Noise
    addLimits(simSettings.transmitter.noise.stdDeviation,[],0,[])
    addLimits(simSettings.transmitter.noise.amplitude,[],0,[])
    addLimits(simSettings.transmitter.noise.frequency,[],0,[])


###########################################################################
# This function adds channel settings limits.
###########################################################################
def addChannelSettings(simSettings: simulationSettings):

    addLimits(simSettings.channel.notchFreq,50e9,0.5e9,[])
    addLimits(simSettings.channel.notchAttenuation,100,0,1)
    addLimits(simSettings.channel.noise.noiseDensity,[],0,[])


###########################################################################
# This function adds receiver settings limits.
###########################################################################
def addReceiverSettings(simSettings: simulationSettings):

    # Max amplitude
    addLimits(simSettings.transmitter.signalAmplitude,10,[],[])
    
    # PreAmp
    addLimits(simSettings.receiver.preAmp.gain,100,0.1,0.1)
    
    # CTLE
    addLimits(simSettings.receiver.CTLE.zeroFreq,30e9,0.5e9,0.5e9)
    addLimits(simSettings.receiver.CTLE.zeroNumb,2,1,1)
    addLimits(simSettings.receiver.CTLE.pole1Freq,30e9,0.5e9,0.5e9)
    addLimits(simSettings.receiver.CTLE.pole1Numb,2,1,1)
    addLimits(simSettings.receiver.CTLE.pole2Freq,30e9,0.5e9,0.5e9)
    addLimits(simSettings.receiver.CTLE.pole2Numb,5,1,1)
    
    # FFE
    addLimits(simSettings.receiver.FFE.taps.main, 2, -1, 0.05) # allow for some boosting
    for tap in simSettings.receiver.FFE.taps.__dict__:
        if not tap == 'main':
            addLimits(simSettings.receiver.FFE.taps.__dict__[tap], 1, -1, 0.05)
    
    # DFE
    for tap in simSettings.receiver.DFE.taps.__dict__:
        addLimits(simSettings.receiver.DFE.taps.__dict__[tap], 0, -1, 0.01)

    # Jitter
    addLimits(simSettings.receiver.jitter.stdDeviation,[],0,[])
    addLimits(simSettings.receiver.jitter.amplitude,[],0,[])
    addLimits(simSettings.receiver.jitter.DCD,1,0,[])
    
    # Noise
    addLimits(simSettings.receiver.noise.stdDeviation,[],0,[])
    addLimits(simSettings.receiver.noise.amplitude,[],0,[])

