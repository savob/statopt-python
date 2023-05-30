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
# This function determines the system pulse response. An ideal pulse is
# created, fed through transmitter equalization, channel attenuation and 
# receiver equalization. The length of the pulse response is kept long
# regardless of the cursor count. It is shortenned later before generating
# the ISI eye diagram.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
#   
###########################################################################

from userSettingsObjects import simulationSettings
from initializeSimulation import simulationStatus
import numpy as np
import control.matlab as ml
from loadMatlabFiles import objectFromMat
import scipy.signal as spsig

class nothing:
    def __init__(self):
        pass

def generatePulseResponse(simSettings: simulationSettings, simResults: simulationStatus):

    # Apply TX pulse
    applyPulse(simSettings, simResults) 

    # Apply TX equalization
    applyTXEQ(simSettings, simResults)

    # Apply channel characteristics
    applyChannel(simSettings, simResults)
    
    # Apply RX gain
    applyRXGain(simSettings, simResults)
    
    # Apply RX CTLE
    applyRXCTLE(simSettings, simResults)
    
    # Apply RX FFE
    applyRXFFE(simSettings, simResults)
    
    # Apply RX DFE
    applyRXDFE(simSettings, simResults)

    # Limit length of pulse
    limitLength(simSettings, simResults)
    

###########################################################################
# This function generates an ideal pulse with a total length of 3 symbols 
# and a predetermined height. The added symbols are required to ensure the 
# pulse begins and returns to zero.
###########################################################################
def applyPulse(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    pulseVoltage    = simSettings.transmitter.signalAmplitude.value
    preCursorCount  = simSettings.transmitter.preCursorCount.value
    postCursorCount = simSettings.transmitter.postCursorCount.value
    includeSourceImpedance = simSettings.transmitter.includeSourceImpedance
    
    # Create pulse
    if (includeSourceImpedance):
        pulse = np.concatenate((np.zeros((preCursorCount,)), [pulseVoltage/2], np.zeros((postCursorCount,))))
    else:
        pulse = np.concatenate((np.zeros((preCursorCount,)), [pulseVoltage], np.zeros((postCursorCount,))))
    
    
    # Save results
    setattr(simResults.pulseResponse, 'transmitter', nothing())
    simResults.pulseResponse.transmitter.pulse = pulse


###########################################################################
# This function convolves the pulse signal with the TX equalization 
# response in the time domain to add pre-emphasis to the signal. The length 
# of the FIR filter is defined by the number of taps. The main cursor level
# is reduced automatically to ensure the maximum output level is never
# grater than the normalized supply level. 
###########################################################################
def applyTXEQ(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    samplesPerSymb  = simSettings.general.samplesPerSymb.value
    taps            = simSettings.transmitter.EQ.taps
    addEqualization = simSettings.transmitter.EQ.addEqualization
    inputSignal = simResults.pulseResponse.transmitter.pulse
    
    if addEqualization:
    
        # Calculate main tap height
        main = 1
        for tapName in taps.__dict__:
            if tapName != 'main':
                main = main - abs(taps.__dict__[tapName].value)
        
        simSettings.transmitter.EQ.taps.main.value = main

        # Ensure summation adds up to supply
        if main <= 0:
            successful = False
        else:
            successful = True
        

        # Ensure main tap is largest
        for tapName in taps.__dict__:
            if tapName != 'main' and abs(taps.__dict__[tapName].value) >= abs(main):
                successful = False
            
        
        simResults.results.successful = successful

        # Order taps        
        tapNames = list(taps.__dict__)
        tapNames.sort()
        response = [main]
        pre = 1
        post = 1
        for tapName in tapNames:
            tapValue = taps.__dict__[tapName].value
            if tapName == ('pre' + str(pre)):
                response.insert(0, tapValue)
                pre = pre + 1
            elif tapName == ('post' + str(post)):
                response.append(tapValue)
                post = post + 1

        # Convolve input with response
        discreteSignal = np.convolve(inputSignal, response)
    else:
        discreteSignal = inputSignal
    
    
    # Change signal to continuous time
    outputSignal= np.zeros((samplesPerSymb*len(discreteSignal),))
    for index in range(len(discreteSignal)):
       outputSignal[index*samplesPerSymb:(index+1)*samplesPerSymb-1] = discreteSignal[index]
    
    
    # Save results
    setattr(simResults.pulseResponse.transmitter, 'EQ', nothing())
    simResults.pulseResponse.transmitter.EQ.input = inputSignal 
    simResults.pulseResponse.transmitter.EQ.output = outputSignal
    simResults.pulseResponse.transmitter.output = outputSignal


###########################################################################
# This function applies the channel attenuation to the transmitter signal.
# If cross-talk is desired, it also creates the channel response for those
# channels. It can also override the channel pulse response with a custom 
# one defined by the user.
###########################################################################
def applyChannel(simSettings: simulationSettings, simResults: simulationStatus):
        
    # Import variables
    signalingMode    = simSettings.general.signalingMode
    samplePeriod     = simSettings.general.samplePeriod.value
    samplesPerSymb   = simSettings.general.samplesPerSymb.value
    preCursorCount   = simSettings.transmitter.preCursorCount.value
    postCursorCount  = simSettings.transmitter.postCursorCount.value
    approximate      = simSettings.channel.approximate
    overrideResponse = simSettings.channel.overrideResponse
    overrideFileName = simSettings.channel.overrideFileName
    inputSignal = simResults.pulseResponse.transmitter.output  
    channels    = simResults.influenceSources.channel

    # Needed for output
    setattr(simResults.pulseResponse, 'channel', nothing())
    setattr(simResults.pulseResponse.channel, 'outputs', nothing())
    
    # Loop through each channel
    for chName in channels.__dict__:
    
        # Skip required channels
        if approximate:
            if chName != 'thru' and chName != 'xtalk':
                continue
        else:
            if chName == 'next' or chName == 'fext' or chName == 'xtalk':
                continue


        # Apply custom step response
        if overrideResponse:
            
            # Only apply to thru channel
            if chName != 'thru': continue 
            
            # Load data
            data = objectFromMat(overrideFileName)
            fields = data.__dict__
            if 'amp' in fields:
                amplitude = data.amp
            elif 'amplitude' in fields:
                amplitude = data.amplitude
            
            time = data.time

            # Override pulse response
            channelPulse = np.interp(np.arange(0,time[len(time)-1],samplePeriod), time, amplitude)
            channelPulse = np.concatenate((np.zeros((preCursorCount*samplesPerSymb,)), channelPulse, np.zeros((postCursorCount*samplesPerSymb,))))

            # Apply pulse response
            maxLoc = np.argmax(inputSignal)
            inputPulses = np.zeros((len(inputSignal),))
            locs = np.arange(maxLoc-preCursorCount*samplesPerSymb, maxLoc+postCursorCount*samplesPerSymb, samplesPerSymb)
            inputPulses[locs] = inputSignal[locs]
            outputSignal = np.convolve(inputPulses,channelPulse)
            
        # Apply channel response
        else:
            diffSignal = np.diff(inputSignal)
            signalLength = len(channels.__dict__[chName].pulseResponse)+len(diffSignal)-1
            outputSignal = np.zeros((signalLength,))
            for index in range(len(diffSignal)):
                if(diffSignal[index]==0): continue 
                tailLength = signalLength-len(channels.__dict__[chName].pulseResponse)-index
                tailAmplitude = channels.__dict__[chName].pulseResponse[-1]*diffSignal[index]
                outputSignal = outputSignal + np.concatenate((np.zeros((index,)), channels.__dict__[chName].pulseResponse*diffSignal[index], np.ones((tailLength,))*tailAmplitude))
            

        # Limit signal length
        outputSignal = limitPulse(outputSignal,signalingMode,samplesPerSymb,preCursorCount,postCursorCount)
       
        # Save results
        simResults.pulseResponse.channel.input = inputSignal
        simResults.pulseResponse.channel.outputs.__dict__[chName] = outputSignal


###########################################################################
# This function limits the pulse response length. It either keeps signal
# content greater than 1% of the maximum, or keeps the required number of
# cursors, which ever longer.
###########################################################################
def limitPulse(signal,signalingMode,samplesPerSymb,preCursorCount,postCursorCount):

    # Locate signal content greater than 1% of maximum
    minVal = 0.01 * max(abs(signal))
    start1P = 0
    end1P = len(signal) - 1
    while(abs(signal[start1P]) < minVal):
        start1P = start1P + 1
    
    while(abs(signal[end1P]) < minVal):
        end1P = end1P-1
    

    # Locate peak pulse
    peakLoc = findPeakPulse(signal)
    
    # Chop signal ensuring all desired cursors are included
    if signalingMode == '1+D' or signalingMode == '1+0.5D':
        startC = round(peakLoc-(preCursorCount+1)*samplesPerSymb)-1
        endC = round(peakLoc+(postCursorCount+2)*samplesPerSymb) # add additional symbol to allow for delay
    else:
        startC = round(peakLoc-(preCursorCount+0.5)*samplesPerSymb)-1
        endC = round(peakLoc+(postCursorCount+1.5)*samplesPerSymb) # add additional symbol to allow for delay
    
    signal = signal[min(start1P,startC):max(end1P,endC)]  

    return signal


###########################################################################
# This function is to find the peak in a signal
###########################################################################
def findPeakPulse(signal):
    signal = np.nan_to_num(signal) # Set NaN's to 0. This prevents issues with peak finder
    peaks, prop = spsig.find_peaks(abs(signal), height=0)

    # Break if empty
    if len(peaks) == 0:
        return 0
    
    maxPeak = np.argmax(prop['peak_heights'])
    peakLoc = peaks[maxPeak]

    return peakLoc


###########################################################################
# This function increases the gain of the received signal by a constant.
###########################################################################
def applyRXGain(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    signalingMode   = simSettings.general.signalingMode
    samplesPerSymb  = simSettings.general.samplesPerSymb.value
    adapt           = simSettings.adaption.adapt
    knobs           = simSettings.adaption.knobs
    preCursorCount  = simSettings.transmitter.preCursorCount.value
    postCursorCount = simSettings.transmitter.postCursorCount.value
    approximate     = simSettings.channel.approximate
    addGain         = simSettings.receiver.preAmp.addGain
    gain            = simSettings.receiver.preAmp.gain
    distortion   = simResults.influenceSources.totalDistortion.output
    inputSignals = simResults.pulseResponse.channel.outputs

    # Needed for output
    setattr(simResults.pulseResponse.receiver, 'preAmp', nothing())
    setattr(simResults.pulseResponse.receiver.preAmp, 'inputs', nothing())
    setattr(simResults.pulseResponse.receiver.preAmp, 'outputs', nothing())
    setattr(simResults.pulseResponse.receiver.preAmp, 'outputPeak', nothing())

    # Calculate gain automatically
    if addGain and adapt and 'receiver.preAmp.gain' in knobs:
        
        # Estimate signal height
        peakLoc = findPeakPulse(abs(inputSignals.thru))

        if signalingMode == '1+D':
            startIdx = round(peakLoc-(preCursorCount+0.5)*samplesPerSymb)
            endIdx = round(peakLoc+(postCursorCount-0.5)*samplesPerSymb)
        elif signalingMode == '1+0.5D':
            startIdx = round(peakLoc-(preCursorCount+1/6)*samplesPerSymb)
            endIdx = round(peakLoc+(postCursorCount-1/6)*samplesPerSymb)
        else:
            startIdx = round(peakLoc-preCursorCount*samplesPerSymb)
            endIdx = round(peakLoc+postCursorCount*samplesPerSymb)
        
        startIdx = max(round(startIdx),1)
        endIdx = min(round(endIdx),len(inputSignals.thru))
        section = np.arange(startIdx, endIdx, samplesPerSymb)
        cursorSum = np.sum(abs(inputSignals.thru[section]))

        # Calculate required gain
        saturation = max(abs(distortion))
        gain.value = saturation/cursorSum
        gain.value = round(gain.value/gain.increment)*gain.increment # round to closest multiple of increment
        gain.value = max(min(gain.value,gain.maxValue), gain.minValue) # keep within limits

        # Update current adaption setting
        simSettings.receiver.preAmp.gain.value = gain.value
        if 'adaption' in simResults.__dict__:
            simResults.adaption.currentResult.knobs.__dict__['receiver_preAmp_gain'] = gain.value
            print('receiver_preAmp_gain: {0:.2f}'.format(gain.value))
        
        
    # Remove gain
    elif not addGain:
        gain.value = 1
    
    
    # Loop through each channel
    for chName in inputSignals.__dict__:
        
        # Skip required channels
        if approximate:
            if chName != 'thru' and chName != 'xtalk':
                continue
        else:
            if chName == 'next' or chName == 'fext' or chName == 'xtalk':
                continue
            
        
        
        # Amplify signal
        inputSignal = inputSignals.__dict__[chName]
        outputSignal = inputSignal*gain.value

        # Retrieve main pulse peak
        amplitude = max(abs(outputSignal))

        # Save results
        simResults.pulseResponse.receiver.preAmp.inputs.__dict__[chName] = inputSignal
        simResults.pulseResponse.receiver.preAmp.outputs.__dict__[chName] = outputSignal       
        simResults.pulseResponse.receiver.preAmp.outputPeak.__dict__[chName] = amplitude


###########################################################################
# This function adds equalization by putting the impuse through the CTLE
# transfer function. The response is a third order low-pass filter with 
# peaking. The peaking frequency and amount can be specified. Additional 
# poles can be added at a higher specified frequency.
###########################################################################
def applyRXCTLE(simSettings: simulationSettings, simResults: simulationStatus):

    # Import variables
    samplePeriod    = simSettings.general.samplePeriod.value
    approximate     = simSettings.channel.approximate
    addEqualization = simSettings.receiver.CTLE.addEqualization
    zeroFreq        = simSettings.receiver.CTLE.zeroFreq.value
    pole1Freq       = simSettings.receiver.CTLE.pole1Freq.value
    zeroName     = ('z' + str(zeroFreq/1e9)).replace('.', '_')
    poleName     = ('z' + str(pole1Freq/1e9)).replace('.', '_')
    transferFunc = simResults.influenceSources.RXCTLE.__dict__[zeroName].__dict__[poleName].transferFunc
    inputSignals = simResults.pulseResponse.receiver.preAmp.outputs
    
    # Needed for outputs
    setattr(simResults.pulseResponse.receiver, 'CTLE', nothing())
    setattr(simResults.pulseResponse.receiver.CTLE, 'inputs', nothing())
    setattr(simResults.pulseResponse.receiver.CTLE, 'outputs', nothing())

    # Loop through each channel
    for chName in inputSignals.__dict__:
        
        # Skip required channels
        if approximate:
            if chName != 'thru' and chName != 'xtalk':
                continue
        else:
            if chName == 'next' or chName == 'fext' or chName == 'xtalk':
                continue
        
        # Apply CTLE
        inputSignal = inputSignals.__dict__[chName]
        if addEqualization:
            times = np.arange(len(inputSignals.__dict__[chName]))*samplePeriod
            outputSignal, times, _ = ml.lsim(transferFunc, inputSignal, times)
        else:
            outputSignal = inputSignal
        
        
        # Save results
        simResults.pulseResponse.receiver.CTLE.inputs.__dict__[chName] = inputSignal
        simResults.pulseResponse.receiver.CTLE.outputs.__dict__[chName] = outputSignal
    


###########################################################################
# This function convolves the RX FFE equalization response with the pulse 
# signal in the time domain to add equalization to the signal. The length 
# of the FIR filter is defined by the number of taps.
###########################################################################
def applyRXFFE(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    signalingMode   = simSettings.general.signalingMode
    samplesPerSymb  = simSettings.general.samplesPerSymb.value
    adapt           = simSettings.adaption.adapt
    knobs           = simSettings.adaption.knobs
    preCursorCount  = simSettings.transmitter.preCursorCount.value
    postCursorCount = simSettings.transmitter.postCursorCount.value
    approximate     = simSettings.channel.approximate
    taps            = simSettings.receiver.FFE.taps
    addEqualization = simSettings.receiver.FFE.addEqualization
    distortion   = simResults.influenceSources.totalDistortion.output
    inputSignals = simResults.pulseResponse.receiver.CTLE.outputs

    if addEqualization:
        
        # Automatically calculate main-tap value
        if adapt and ('receiver.FFE.taps.main' in knobs):

            # Estimate signal height
            peakLoc = findPeakPulse(abs(inputSignals.thru))

            if signalingMode == '1+D':
                startIdx = round(peakLoc-(preCursorCount+0.5)*samplesPerSymb)
                endIdx = round(peakLoc+(postCursorCount-0.5)*samplesPerSymb)
            elif signalingMode == '1+0.5D':
                startIdx = round(peakLoc-(preCursorCount+1/6)*samplesPerSymb)
                endIdx = round(peakLoc+(postCursorCount-1/6)*samplesPerSymb)
            else:
                startIdx = round(peakLoc-preCursorCount*samplesPerSymb)
                endIdx = round(peakLoc+postCursorCount*samplesPerSymb)
            
            startIdx = max(round(startIdx),1)
            endIdx = min(round(endIdx),len(inputSignals.thru))
            section = np.arange(startIdx, endIdx, samplesPerSymb)
            cursorSum = np.sum(abs(inputSignals.thru[section]))

            # Calculate required gain
            saturation = max(abs(distortion))
            taps.main.value = saturation/cursorSum
            taps.main.value = round(taps.main.value/taps.main.increment)*taps.main.increment # round to closest multiple of increment
            taps.main.value = max(min(taps.main.value,taps.main.maxValue),taps.main.minValue) # keep within limits

            # Update current adaption setting
            simSettings.receiver.FFE.taps.main.value = taps.main.value
            if 'adaption' in simResults.__dict__:
                simResults.adaption.currentResult.knobs.__dict__['receiver_FFE_taps_main'] = taps.main.value
                print('receiver_FFE_taps_main: {0:.2f}\n'.format(taps.main.value))
            
        

        # Order taps
        tapNames = list(taps.__dict__)
        tapNames.sort()
        response = [taps.main.value]
        pre = 1
        post = 1
        for tapName in tapNames:
            if tapName == ('pre' + str(pre)):
                response.insert(0, taps.__dict__[tapName].value)
                pre = pre + 1
            elif tapName == ('post' + str(post)):
                response.append(taps.__dict__[tapName].value)
                post = post + 1
            
        

        # Perform equalization on each channel
        outputSignals = nothing()
        for chName in inputSignals.__dict__:
            inputSignals.__dict__[chName] = inputSignals.__dict__[chName] # This is likely redundant

            # Skip required channels
            if (approximate):
                if chName != 'thru' and chName != 'xtalk':
                    continue
                
            else:
                if chName == 'next' or chName == 'fext' or chName == 'xtalk':
                    continue

            # Convolve signal with equalizer (why wasn't 'convole' used here? Will keep as it was for now)
            symbol = 1
            numbCursors = len(tapNames)
            outputSignals.__dict__[chName] = np.zeros((len(inputSignals.__dict__[chName])+(numbCursors-1)*samplesPerSymb,))
            for index in range(len(response)):
                outputSignals.__dict__[chName] = outputSignals.__dict__[chName] + response[index] * np.concatenate((np.zeros(((symbol-1)*samplesPerSymb,)), inputSignals.__dict__[chName], np.zeros(((numbCursors-symbol)*samplesPerSymb),)))
                symbol = symbol+1
        
    else:
        outputSignals = inputSignals
    

    # Save results
    setattr(simResults.pulseResponse.receiver, 'FFE', nothing())
    setattr(simResults.pulseResponse.receiver.FFE, 'inputs', nothing())
    setattr(simResults.pulseResponse.receiver.FFE, 'outputs', nothing())
    simResults.pulseResponse.receiver.FFE.inputs = inputSignals
    simResults.pulseResponse.receiver.FFE.outputs = outputSignals


###########################################################################
# This function applies the receiver DFE to the pulse response. Since a
# DFE is not LTI, this function approximates the effect by sutracting the
# specified post-cursor. Due to any delay accumulated in the FFE, the peak
# of the pulse must be re-measured to ensure the DFE is applied in the 
# correct location.
###########################################################################
def applyRXDFE(simSettings: simulationSettings, simResults: simulationStatus):

    # Import variables
    signalingMode   = simSettings.general.signalingMode
    samplesPerSymb  = simSettings.general.samplesPerSymb.value
    approximate     = simSettings.channel.approximate
    supplyVoltage   = simSettings.receiver.signalAmplitude.value
    taps            = simSettings.receiver.DFE.taps
    addEqualization = simSettings.receiver.DFE.addEqualization
    inputSignals = simResults.pulseResponse.receiver.FFE.outputs
    
    # Needed for output
    setattr(simResults.pulseResponse.receiver, 'DFE', nothing())
    setattr(simResults.pulseResponse.receiver.DFE, 'inputs', nothing())
    setattr(simResults.pulseResponse.receiver.DFE, 'outputs', nothing())

    # Perform equalization on each channel
    for chName in inputSignals.__dict__:
        
        # Skip required channels
        if approximate:
            if chName != 'thru' and chName != 'xtalk':
                continue
        else:
            if chName == 'next' or chName == 'fext' or chName == 'xtalk':
                continue
        
        # Find pulse peak location
        inputSignal = inputSignals.__dict__[chName]
        peakLoc = findPeakPulse(abs(inputSignal))
        
        # Apply DFE
        outputSignal = inputSignal
        if addEqualization:

            # Order taps
            tapNames = list(taps.__dict__)
            tapNames.sort()
            response = []
            post = 1
            for tapName in tapNames:
                if tapName == ('post' + str(post)):
                    response.append(taps.__dict__[tapName].value)
                    post = post+1

            
            # Apply equalization
            for index in range(len(response)):
                tapName = list(tapNames)[index]
                position = float(tapName[-1])

                if signalingMode == '1+D' or signalingMode == '1+0.5D':
                    startIdx = round(peakLoc+(position-1)*samplesPerSymb)
                    endIdx = round(peakLoc+position*samplesPerSymb-1)
                else:
                    startIdx = round(peakLoc+(position-0.5)*samplesPerSymb)
                    endIdx = round(peakLoc+(position+0.5)*samplesPerSymb-1)
                
                startIdx = max(min(startIdx,len(outputSignal)-samplesPerSymb),1)
                endIdx = max(min(endIdx,len(outputSignal)),samplesPerSymb)
                outputSignal[startIdx:endIdx] = outputSignal[startIdx:endIdx]+response[index]*supplyVoltage
    
        # Save results
        simResults.pulseResponse.receiver.DFE.inputs.__dict__[chName] = inputSignal
        simResults.pulseResponse.receiver.DFE.outputs.__dict__[chName] = outputSignal


###########################################################################
# This function limits the length of the pulses to only include the
# required cursors. By doing so, it also ensures that the symbols are
# centered within the symbol period. Allignment is required due to delay in
# equalization devices.
###########################################################################
def limitLength(simSettings,simResults):

    # Import variables
    signalingMode   = simSettings.general.signalingMode
    samplesPerSymb  = simSettings.general.samplesPerSymb.value
    preCursorCount  = simSettings.transmitter.preCursorCount.value
    postCursorCount = simSettings.transmitter.postCursorCount.value
    approximate     = simSettings.channel.approximate
    pulses     = simResults.pulseResponse.receiver.DFE.outputs
    successful = simResults.results.successful
    
    # Perform to each channel
    for chName in pulses.__dict__:
        
        # Skip required channels
        if approximate:
            if chName != 'thru' and chName != 'xtalk':
                continue
        else:
            if chName == 'next' or chName == 'fext' or chName == 'xtalk':
                continue
        
        # Locate pulse peak
        pulse = np.round(pulses.__dict__[chName],4)

        # I feel like this logic just results in finding the middle of the pulse everytime but it is like this in StatEye, since 
        peakLoc1 = findPeakPulse(pulse)
        peakLoc2 = findPeakPulse(np.flip(pulse))

        peakLoc2 = len(pulse)-peakLoc2+1
        peakLoc = round(np.mean([peakLoc1, peakLoc2]))

        # Limit length
        if signalingMode == '1+D':
            startIdx = round(peakLoc-(preCursorCount+1)*samplesPerSymb)
            endIdx = round(peakLoc+(postCursorCount)*samplesPerSymb)
        elif signalingMode == '1+0.5D':
            startIdx = round(peakLoc-(preCursorCount+2/3)*samplesPerSymb)
            endIdx = round(peakLoc+(postCursorCount+1/3)*samplesPerSymb)
        else:
            startIdx = round(peakLoc-(preCursorCount+0.5)*samplesPerSymb)
            endIdx = round(peakLoc+(postCursorCount+0.5)*samplesPerSymb)
        

        # Adjust 
        if endIdx > len(pulses.__dict__[chName]):
            pulses.__dict__[chName] = np.concatenate((pulses.__dict__[chName], np.zeros((endIdx-len(pulses.__dict__[chName]),))))
        else:
            pulses.__dict__[chName] = pulses.__dict__[chName][0:endIdx]
        
        
        # Adjust beginning
        if startIdx < 1:
            diff = 1-startIdx
            pulses.__dict__[chName] = np.concatenate((np.zeros((diff,)), pulses.__dict__[chName][0:endIdx]))
            print('Having trouble finding main cursor!\n')
            #successful = False
        else:
            pulses.__dict__[chName] = pulses.__dict__[chName][startIdx:]
    
    # Save results
    simResults.pulseResponse.receiver.outputs = pulses
    simResults.results.successful = successful

