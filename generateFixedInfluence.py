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
# This function creates all constant sources which influence the resultant 
# signal distribution. This includes transfer functions and disturbance
# probability distributions. This script is performed pre-simulation. Since
# the transmitter and CTLE output-refered noise is equalization setting 
# dependent, it must be calculated in the main program loop.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
# 
# Outputs:
#   simResults: structure containing simulation results
#   
###########################################################################

import numpy as np
import scipy.stats as stats
from scipy import io
from userSettingsObjects import simulationSettings
from initializeSimulation import simulationStatus

class combinedChannel:

    def __init__(self):
        self.transferFunction = 0
        self.stepResponse = 0
        self.channelNumb = 0

def generateFixedInfluence(simSettings: simulationSettings, simResults: simulationStatus):

    # Load channel data
    createChannel(simSettings, simResults)
        
    # Generate TX jitter
    generateTXJitter(simSettings, simResults)
    
    # Generate TX distortion
    generateTXDistortion(simSettings, simResults)
        
    # Generate RX jitter
    generateRXJitter(simSettings, simResults)
    
    # Generate RX distortion
    generateRXDistortion(simSettings, simResults)
    
    # Combine influences
    combineInfluences(simSettings, simResults)


###########################################################################
# This function loads the saved channel data and creates step responses.
###########################################################################
def createChannel(simSettings: simulationSettings, simResults: simulationStatus):

    # Import variables
    samplePeriod     = simSettings.general.samplePeriod.value
    symbolPeriod     = simSettings.general.symbolPeriod.value
    samplesPerSymb   = simSettings.general.samplesPerSymb.value
    tRise            = simSettings.transmitter.tRise.value
    preCursorCount   = simSettings.transmitter.preCursorCount.value
    importChannels   = simSettings.channel.fileNames
    addChannel       = simSettings.channel.addChannel
    addCrossTalk     = simSettings.channel.addCrossTalk
    results = simResults.influenceSources.channel
    
    chNames = {'thru'} # Default (no crosstalk)

    # Remove xtalk channels if not required
    if(addCrossTalk):
        chNames = list(importChannels.__dict__)
        
        # Initialize combined channels structure
        setattr(results, 'next', combinedChannel())
        setattr(results, 'fext', combinedChannel())
        setattr(results, 'xtalk', combinedChannel())

    # Load each channel
    for name in chNames:
        if((name == 'next') or (name == 'fext') or (name =='xtalk')):
            continue 

        # Get file information
        impulseResponse = results.__dict__[name].impulseResponse
        transFunc = results.__dict__[name].transferFunction
        
        # Create ideal step response with rise time
        riseIdx = round(tRise/samplePeriod)
        numSymbols = 1000  # Number of symbols to run step for
        time = np.linspace(0, numSymbols*symbolPeriod-samplePeriod, numSymbols * samplesPerSymb)
        idealStep = np.concatenate((np.linspace(0, 1, riseIdx), np.ones((len(time)-riseIdx,))))

        stepResponse = 0
            
        # Apply ideal step response if not adding channel
        if not addChannel:
            stepResponse = np.concatenate((np.zeros((preCursorCount*samplesPerSymb,)), idealStep))
        
        # Apply step to channel convolution
        else:
            stepResponse = np.convolve(idealStep, impulseResponse)
            stepResponse = stepResponse[:-(len(impulseResponse)-1)] # remove the trailing (falling edge) of the convolution
            
        # Contribute to combined channels based on present channel
        if name[:4] == 'thru':
            results.thru.stepResponse = stepResponse
        elif name[:4] == 'next':
            results.next.transferFunction = np.sqrt(results.next.transferFunction**2+transFunc**2)
            results.next.stepResponse = results.next.stepResponse+stepResponse
            results.next.frequencies = results.__dict__[name].frequencies
            results.next.channelNumb = results.next.channelNumb+1
            results.xtalk.transferFunction = np.sqrt(results.xtalk.transferFunction**2+transFunc**2)
            results.xtalk.stepResponse = results.xtalk.stepResponse+stepResponse
            results.xtalk.frequencies = results.__dict__[name].frequencies
            results.xtalk.channelNumb = results.xtalk.channelNumb+1
        elif name[:4] == 'fext':
            results.fext.transferFunction = np.sqrt(results.fext.transferFunction**2+transFunc**2)
            results.fext.stepResponse = results.fext.stepResponse+stepResponse
            results.fext.frequencies = results.__dict__[name].frequencies
            results.fext.channelNumb = results.fext.channelNumb+1
            results.xtalk.transferFunction = np.sqrt(results.xtalk.transferFunction**2+transFunc**2)
            results.xtalk.stepResponse = results.xtalk.stepResponse+stepResponse
            results.xtalk.frequencies = results.__dict__[name].frequencies
            results.xtalk.channelNumb = results.xtalk.channelNumb+1

# Classes used to easily append jitter and distortion data 
class jitter:
    def __init__(self, rj, sj, dcdj, tj, ts, uis):
        self.random = rj
        self.deterministic = sj
        self.DCD = dcdj
        self.totalJitter = tj
        self.timeScale = ts
        self.UIScale = uis

class distortionClass:
    def __init__(self, input, output):
        self.input = input
        self.output = output

###########################################################################
# This function creates a probability distribution for the transmitter
# jitter. This function adds random as well as deterministic jitter.
###########################################################################
def generateTXJitter(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    samplesPerSymb = simSettings.general.samplesPerSymb.value
    samplePeriod   = simSettings.general.samplePeriod.value
    symbolPeriod   = simSettings.general.symbolPeriod.value
    addJitter      = simSettings.transmitter.jitter.addJitter
    stdDeviation   = simSettings.transmitter.jitter.stdDeviation.value
    amplitude      = simSettings.transmitter.jitter.amplitude.value
    DCD            = simSettings.transmitter.jitter.DCD.value
    
    # Add random jitter
    if addJitter and stdDeviation != 0:
        randJitter = stats.norm.pdf(np.linspace(-0.5, 0.5, samplesPerSymb + 1), loc=0, scale=stdDeviation)
        randJitter = randJitter/np.sum(randJitter) # normalize PDF
    else:
        randJitter = 1
    

    # Add deterministic jitter
    if addJitter and amplitude != 0:
        sine = amplitude*np.sin(2*np.pi*np.linspace(0, 1, 10000))
        sine = sine[:-1] # remove repeated 0 value
        sineJitter = np.histogram(sine, np.linspace(-0.5,0.5,samplesPerSymb+1))
        sineJitter = sineJitter[0]/np.sum(sineJitter[0]) # normalize PDF
    else:
        sineJitter = 1
    
    
    # Add duty-cycle distortion jitter
    if addJitter and DCD != 0:
        DCDJitter = np.concatenate(([0.5], np.zeros((round(DCD*samplesPerSymb-1,))), [0.5]))
    else:
        DCDJitter = 1
    
    
    # Convolve all jitter types
    totalJitter = np.convolve(randJitter,sineJitter)
    totalJitter = np.convolve(totalJitter,DCDJitter)
    if(len(totalJitter)<101):
        totalJitter = np.concatenate((np.zeros((round(samplesPerSymb/2),)), totalJitter, np.zeros((round(samplesPerSymb/2),))))
    
    timeScale = np.linspace(-(len(totalJitter)-1)/2*samplePeriod, (len(totalJitter)-1)/2*samplePeriod, len(totalJitter)+1) # +1 needed for histograms
    UIScale = timeScale/symbolPeriod
    
    # Save results
    temp = jitter(randJitter, sineJitter, DCDJitter, totalJitter, timeScale, UIScale)
    setattr(simResults.influenceSources, 'TXJitter', temp)


###########################################################################
# This function creates a transfer function used to add distortion to
# the pulse response. This represents the non-linearity of the transmit
# driver.
###########################################################################
def generateTXDistortion(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    supplyVoltage   = simSettings.transmitter.signalAmplitude.value
    applyDistortion = simSettings.transmitter.distortion.addDistortion
    fileName        = simSettings.transmitter.distortion.fileName
    
    # Define gain function
    if(applyDistortion):
        distortion = io.loadmat(fileName)
        fields = distortion.__dict__
        if 'input' in fields:
            input  = distortion.input
        else:
            print('Error: TX distortion file missing "input" vector. Exiting.')
            quit()
        
        if 'output' in fields:
            output  = distortion.output
        elif 'out' in fields:
            output  = distortion.out
        else:
            print('Error: TX distortion file missing "output" vector. Exiting.')
            quit()
        
    else:
        input  = [-supplyVoltage, supplyVoltage]
        output = [-supplyVoltage, supplyVoltage]
    

    # Save results
    temp = distortionClass(input, output)
    setattr(simResults.influenceSources, 'TXDistortion', temp)


###########################################################################
# This function creates a probability distribution for the receiver
# clock-data recovery unity jitter. This function adds random aswell as 
# deterministic jitter.
###########################################################################
def generateRXJitter(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    samplesPerSymb = simSettings.general.samplesPerSymb.value
    samplePeriod   = simSettings.general.samplePeriod.value
    symbolPeriod   = simSettings.general.symbolPeriod.value
    addJitter      = simSettings.receiver.jitter.addJitter
    stdDeviation   = simSettings.receiver.jitter.stdDeviation.value
    amplitude      = simSettings.receiver.jitter.amplitude.value
    DCD            = simSettings.receiver.jitter.DCD.value

    # Add random jitter
    if addJitter and stdDeviation != 0:
        randJitter = stats.norm.pdf(np.linspace(-0.5, 0.5, samplesPerSymb + 1), loc=0, scale=stdDeviation)
        randJitter = randJitter/np.sum(randJitter) # normalize PDF
    else:
        randJitter = 1
    

    # Add deterministic jitter
    if addJitter and amplitude != 0:
        sine = amplitude*np.sin(2*np.pi*np.linspace(0, 1, 10000))
        sine = sine[:-1] # remove repeated 0 value
        sineJitter = np.histogram(sine, np.linspace(-0.5,0.5,samplesPerSymb+1))
        sineJitter = sineJitter[0]/np.sum(sineJitter[0]) # normalize PDF
    else:
        sineJitter = 1
    
    
    # Add duty-cycle distortion jitter
    if addJitter and DCD != 0:
        DCDJitter = np.concatenate(([0.5], np.zeros((round(DCD*samplesPerSymb-1,))), [0.5]))
    else:
        DCDJitter = 1
    
    
    # Convolve all jitter types
    totalJitter = np.convolve(randJitter,sineJitter)
    totalJitter = np.convolve(totalJitter,DCDJitter)
    if len(totalJitter) < 101:
        totalJitter = np.concatenate((np.zeros((round(samplesPerSymb/2),)), totalJitter, np.zeros((round(samplesPerSymb/2),))))
    
    timeScale = np.linspace(-(len(totalJitter)-1)/2*samplePeriod, (len(totalJitter)-1)/2*samplePeriod, len(totalJitter)+1) # +1 needed for histograms
    UIScale = timeScale/symbolPeriod
    
    # Save results
    temp = jitter(randJitter, sineJitter, DCDJitter, totalJitter, timeScale, UIScale)
    setattr(simResults.influenceSources, 'RXJitter', temp)

###########################################################################
# This function creates a transfer function used to add distortion to
# the pulse response. This represents the non-linearity of the receiver.
###########################################################################
def generateRXDistortion(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    supplyVoltage   = simSettings.receiver.signalAmplitude.value
    applyDistortion = simSettings.receiver.distortion.addDistortion
    fileName        = simSettings.transmitter.distortion.fileName

    # Define gain function
    if applyDistortion:
        distortion = io.loadmat(fileName)
        fields = distortion.__dict__
        if 'input' in fields:
            input  = distortion.input
        else:
            print('Error: RX distortion file missing "input" vector. Exiting.')
            quit()
        
        if 'output' in fields:
            output  = distortion.output
        elif 'out' in fields:
            output  = distortion.out
        else:
            print('Error: RX distortion file missing "output" vector. Exiting.')
            quit()
        
    else:
        input  = [-supplyVoltage, supplyVoltage]
        output = [-supplyVoltage, supplyVoltage]
    

    # Save results
    temp = distortionClass(input, output)
    setattr(simResults.influenceSources, 'RXDistortion', temp)



###########################################################################
# This function combines both transmitter and receiver sources of influence
# together. Since the noise depends on the CTLE response, it must be
# determined later.
###########################################################################
def combineInfluences(simSettings: simulationSettings, simResults: simulationStatus):

    # Import variables
    samplePeriod = simSettings.general.samplePeriod.value
    symbolPeriod = simSettings.general.symbolPeriod.value
    yAxis        = simSettings.general.yAxis.value
    TXDistInput   = simResults.influenceSources.TXDistortion.input
    TXDistOutput  = simResults.influenceSources.TXDistortion.output
    RXDistInput   = simResults.influenceSources.RXDistortion.input
    RXDistOutput  = simResults.influenceSources.RXDistortion.output
    TXJitter      = simResults.influenceSources.TXJitter.totalJitter
    RXJitter      = simResults.influenceSources.RXJitter.totalJitter

    # Combine distortion
    totalDistortionInput = yAxis
    totalDistortionOutput = yAxis
    
    totalDistortionInput = np.interp(totalDistortionInput, RXDistInput, RXDistOutput)
    totalDistortionOutput = np.interp(totalDistortionOutput, TXDistInput, TXDistOutput)
    
    
    # Combine jitter
    totalJitter = np.convolve(TXJitter,RXJitter)
    timeScale = np.linspace(-(len(totalJitter)-1)/2*samplePeriod, (len(totalJitter)-1)/2*samplePeriod, len(totalJitter)+1) # +1 needed for histograms
    UIScale = timeScale/symbolPeriod
    
    # Save results
    totalDist = distortionClass(totalDistortionInput, totalDistortionOutput)
    setattr(simResults.influenceSources, 'totalDistortion', totalDist)
    totJit = jitter(0, 0, 0, totalJitter, timeScale, UIScale)
    setattr(simResults.influenceSources, 'totalJitter', totJit)
