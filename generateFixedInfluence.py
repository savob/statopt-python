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
###########################################################################

import numpy as np
import scipy.stats as stats
from userSettingsObjects import simulationSettings
from initializeSimulation import simulationStatus
from loadMatlabFiles import objectFromMat
import control.matlab as ml
from math import isnan
import os
import skrf as rf # Used to read Touchstone files and nothing else

class combinedChannel:

    def __init__(self):
        self.transferFunction = 0
        self.pulseResponse = 0
        self.channelNumb = 0

def generateFixedInfluence(simSettings: simulationSettings, simResults: simulationStatus):

    ml.use_matlab_defaults() # Needed to ensure compatibility with MATLAB expectations for control code

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
    samplesPerSymb   = simSettings.general.samplesPerSymb.value
    tRise            = simSettings.transmitter.tRise.value
    preCursorCount   = simSettings.transmitter.preCursorCount.value
    postCursorCount  = simSettings.transmitter.postCursorCount.value
    importChannels   = simSettings.channel.fileNames
    addChannel       = simSettings.channel.addChannel
    addCrossTalk     = simSettings.channel.addCrossTalk
    overrideResponse = simSettings.channel.overrideResponse
    overrideFileName = simSettings.channel.overrideFileName
    modelCircuitTF     = simSettings.channel.modelCircuitTF
    modelCircuitTFName = simSettings.channel.modelCircuitTFName
    addNotch           = simSettings.channel.addNotch
    notchFreq          = simSettings.channel.notchFreq.value
    notchAttenuation   = simSettings.channel.notchAttenuation.value
    results = simResults.influenceSources.channel
    
    chNames = {'thru'} # Default (no crosstalk)

    # Add xtalk channels if required
    if addCrossTalk:
        chNames = list(importChannels.__dict__)
        
        # Initialize combined channels structure
        setattr(results, 'next', combinedChannel())
        setattr(results, 'fext', combinedChannel())
        setattr(results, 'xtalk', combinedChannel())


    # Apply custom pulse response
    if overrideResponse:
        # Load data
        data = objectFromMat(overrideFileName)
        fields = data.__dict__
        if 'amp' in fields:
            amplitude = data.amp
        elif 'amplitude' in fields:
            amplitude = data.amplitude
        elif 'amplitudes' in fields:
            amplitude = data.amplitudes

        time = data.time

        # Override pulse response
        pulseResponse = np.interp(np.arange(0,time[-1] + samplePeriod,samplePeriod), time, amplitude)
        pulseResponse = np.concatenate((np.zeros((preCursorCount*samplesPerSymb,)), pulseResponse, np.zeros((postCursorCount*samplesPerSymb,))))

        # Create frequency response
        tranFunc = np.fft.fft(pulseResponse)
        freqs = np.linspace(0, 1/samplePeriod, len(tranFunc)+1)
        endIndex = int(len(tranFunc) / 2)
        tranFunc = tranFunc[:endIndex]
        freqs = freqs[0:endIndex]

        # Save results
        results.thru.pulseResponse = pulseResponse
        results.thru.transferFunction = tranFunc
        results.thru.frequencies = freqs

    else:
        # Get frequency responses from channel descriptions
        for name in chNames:
            fileName = importChannels.__dict__[name]

            freqs = 0
            tranFunc = 0

            # Import keystone (.s4p) channel data
            if fileName[-4:] == '.s4p':
                fileAddress = os.path.join('.', 'channels', fileName)
                backplane = rf.Network(fileAddress)

                freqs = backplane.f
                freqPoints = freqs.size

                # Get differential mode transfer function
                # Start by preparing differential S-parameters
                sParamsTemp = np.copy(backplane.s)
                
                sParamsTemp[:,1,:] = np.copy(backplane.s[:,2,:])
                sParamsTemp[:,2,:] = np.copy(backplane.s[:,1,:])
                
                sParamsTemp[:,:,1] = np.copy(backplane.s[:,:,2])
                sParamsTemp[:,:,2] = np.copy(backplane.s[:,:,1])
                
                sParamsTemp[:,1,2] = np.copy(backplane.s[:,1,2])
                sParamsTemp[:,2,1] = np.copy(backplane.s[:,2,1])
                
                sParamsTemp[:,1,1] = np.copy(backplane.s[:,2,2])
                sParamsTemp[:,2,2] = np.copy(backplane.s[:,1,1])
        
                M = np.array([[1,-1,0,0],[0,0,1,-1],[1,1,0,0],[0,0,1,1]])
                invM = np.transpose(M)
                
                smmParams = np.zeros((4,4,freqPoints), dtype = complex)
                
                for i in range(freqPoints):
                    smmParams[:,:,i] = (M@sParamsTemp[i,:,:]@invM)/2
                
                sParamsDiff = smmParams[0:2,0:2,:]
                
                # Assume source/load impedances of 50 ohm
                zl = 50.0*np.ones((1,1,freqPoints))
                zs = 50.0*np.ones((1,1,freqPoints))
                z0 = backplane.z0[0,0]*np.ones((1,1,freqPoints))

                # Reflection Coefficients
                gammaL = (zl - z0) / (zl + z0)
                gammaL[zl == np.inf] = 1 
                
                gammaS = (zs - z0) / (zs + z0)
                gammaS[zs == np.inf] = 1
                
                gammaIn = (sParamsDiff[0,0,:] + sParamsDiff[0,1,:] * sParamsDiff[1,0,:] * gammaL) / (1 - sParamsDiff[1,1,:] * gammaL)
                
                tranFunc = sParamsDiff[1,0,:] * (1 + gammaL) * (1 - gammaS) / (1 - sParamsDiff[1,1,:] * gammaL) / (1 - gammaIn * gammaS) 
                tranFunc = tranFunc.reshape(freqPoints,) 
            
            elif fileName[-4:] == '.mat':
                # If it's a .MAT file check for frequency points
                
                temp = objectFromMat(fileName)
                try:
                    tranFunc = temp.response
                    freqs = temp.frequency
                except AttributeError:
                    print('ERROR: "{:s}" is lacking one or both of "frequency" and/or "response" as fields for defining a channel\'s response.\n----------------SIMULATION ABORTING----------------'.format(fileName))
                    quit()  

    
            # Convolve channel with simulated circuit response
            if modelCircuitTF:
                circuit = objectFromMat(modelCircuitTFName)

                # Convert circuit 
                circuit = np.interp(freqs, circuit.frequency, circuit.response)
                for i in range(len(circuit)):
                    if isnan(circuit[i]): circuit[i] = 0

                tranFunc = tranFunc * circuit

            
            # Add notch in response
            if addNotch:
                k = 2 * np.pi * notchFreq / 10
                g = 10 ^ (notchAttenuation / 20)
                notchLTI = ml.tf([1, 5*k/g, 100*k^2], [1, 5*k, 100*k^2])
                mag, phase, _ = ml.bode(notchLTI, 2*np.pi*freqs, plot=False, deg=False) # Return phase in radians
                mag = np.squeeze(mag)
                phase = np.squeeze(phase)*np.pi/180
                notchTF = mag * np.exp(np.pi * phase)
                tranFunc = tranFunc * notchTF

                
            # Combine xtalk responses
            if name[:4] == 'thru':
                results.thru.transferFunction = tranFunc
                results.thru.frequencies = freqs
            elif name[:4] == 'next':
                results.next.transferFunction = np.sqrt(results.next.transferFunction**2+tranFunc**2)
                results.next.frequencies = freqs

                results.next.channelNumb = results.next.channelNumb+1
                results.xtalk.transferFunction = np.sqrt(results.xtalk.transferFunction**2+tranFunc**2)
                results.xtalk.frequencies = freqs
                results.xtalk.channelNumb = results.xtalk.channelNumb+1
            elif name[:4] == 'fext':
                results.fext.transferFunction = np.sqrt(results.fext.transferFunction**2+tranFunc**2)
                results.fext.frequencies = freqs
                results.fext.channelNumb = results.fext.channelNumb+1
                results.xtalk.transferFunction = np.sqrt(results.xtalk.transferFunction**2+tranFunc**2)
                results.xtalk.frequencies = freqs
                results.xtalk.channelNumb = results.xtalk.channelNumb+1

        # Create pulse response for all the combined channels
        for name in results.__dict__:

            freqs = results.__dict__[name].frequencies
            tranFunc = results.__dict__[name].transferFunction
    
            # Create impulse response
            
            pulseResponse = impulseResponseConvolKernel(tranFunc, freqs, samplePeriod)
        
            # Create ideal pulse response with rise time
            riseIdx = round(tRise/samplePeriod)
            idealPulse = np.concatenate((np.zeros((preCursorCount*samplesPerSymb,)),np.linspace(0,1,riseIdx),np.ones((samplesPerSymb-riseIdx,)),np.linspace(1,0,riseIdx),np.zeros((postCursorCount*samplesPerSymb-riseIdx,))))
        
            # Apply pulse response to channel
            if not addChannel:
                if name[0:3] == 'thru':
                    pulseResponse = np.convolve(np.concatenate((1, np.zeros((len(pulseResponse),)))), idealPulse, 'same')
                else:
                    pulseResponse = np.zeros((len(idealPulse),))
            else:
                pulseResponse = np.convolve(pulseResponse,idealPulse,'same')
    
            # Save pulse response
            results.__dict__[name].pulseResponse = pulseResponse


###########################################################################
# Generates the convolution kernel for an impulse given a system's 
# frequency response.
#
# Pads discrete time transfer frequency response with data in the frequency
# domain to reach the needed step in time domain when an inverse Fourier
# Transform is performed.
#
# This kernel is generally quite large so there is the option to have a 
# window around the peak.
###########################################################################
def impulseResponseConvolKernel(frequencyResponse, freqs, samplePeriod: float) -> np.ndarray:
    
    # Get defining frequencies
    fStep = freqs[1] - freqs[0]
    fstep2 = freqs[2] - freqs[1]
    fMin = min(freqs)
    fMax = max(freqs)
    fSteps = len(freqs)
    workFrequencyResponse = 0

    # Check that the frequency steps are linear
    if fStep != fstep2:
        print('\n------------------------------\nWARNING: Frequency response data not linearly spaced; linearizing for pulse response.\nTHIS MAY REDUCE THE ACCURACY OF RESULTS.\n------------------------------\n')
        workFreqs = np.linspace(fMin, fMax, fSteps)
        workFrequencyResponse = np.interp(workFreqs, freqs, frequencyResponse)

        fStep = workFreqs[1] - workFreqs[0]
    else:
        # Use data as it came in
        workFreqs = freqs
        workFrequencyResponse = frequencyResponse


    # Find oversampling factor to pad frequency response with
    samplePeriod0 = 1 / (2*freqs[-1])
    upConvert = int(np.ceil(samplePeriod0/samplePeriod))

    # Pad response with zeros
    freqRespPadded = np.concatenate((workFrequencyResponse, np.zeros((len(workFrequencyResponse)*(upConvert-1),))))

    # To create an impulse response the padded frequency response is reflected
    # then put through an inverse Fourier Transform to get the time response
    tempH = np.concatenate((freqRespPadded, np.conj(np.flip(freqRespPadded[1:-1]))))
    impulseResponse = np.real(np.fft.ifft(tempH))


    # Center pulse
    maxValueIndex = np.argmax(impulseResponse)
    impulseResponse = np.concatenate((impulseResponse[maxValueIndex:],impulseResponse[:maxValueIndex]))
    midPoint = int(len(impulseResponse) / 2)
    impulseResponse = np.concatenate((impulseResponse[midPoint:],impulseResponse[:midPoint]))


    # Ensure exact same sampling rate
    time = np.linspace(0, 1/(2*freqs[-1]*upConvert), len(impulseResponse))
    time2 = np.linspace(0, samplePeriod, len(impulseResponse))
    impulseResponse = np.interp(time, time2, impulseResponse, left=0, right=0)
    
    return impulseResponse # Return unchanged response (will be large!)


# Classes used to easily append jitter and distortion data 
class jitter:
    def __init__(self, rj, sj, dcdj, hist, ts, uis):
        self.random = rj
        self.deterministic = sj
        self.DCD = dcdj
        self.histogram = hist
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
        distortion = objectFromMat(fileName)
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
        distortion = objectFromMat(fileName)
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
    TXJitter      = simResults.influenceSources.TXJitter.histogram
    RXJitter      = simResults.influenceSources.RXJitter.histogram

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
