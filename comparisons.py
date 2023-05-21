'''
This file was prepared to compare the pulse responses between the MATLAB and Python
versions of the tool since they are calculated using different methods. The MATLAB 
version uses the fitted version of the transfer function, while the Python 
implementation uses zero-padding and discrete time analysis.

To compare the results, the results object from MATLAB needs to be saved as a .mat
object to be then read by this function. It is assumed that the pusles are from an
identical simulation configuration.

This code is a modified version of the functions used for displaying the pulse 
responses, so that the two pulses are imposed over one another.
'''

from userSettingsObjects import simulationSettings
from initializeSimulation import simulationStatus
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as spsig

def comparePulse(simSettings: simulationSettings, simResults: simulationStatus, simResults2: simulationStatus):
    
    # Plot only if desired
    if not simSettings.general.plotting.pulseResponse: return 
    
    # Import variables
    signalingMode   = simSettings.general.signalingMode
    samplesPerSymb  = simSettings.general.samplesPerSymb.value
    samplePeriod    = simSettings.general.samplePeriod.value
    sampleRate      = simSettings.general.sampleRate.value
    tRise           = simSettings.transmitter.tRise.value
    preCursorCount  = simSettings.transmitter.preCursorCount.value
    postCursorCount = simSettings.transmitter.postCursorCount.value
    cursorCount     = simSettings.transmitter.cursorCount.value
    TXOutput   = simResults.pulseResponse.transmitter.output
    chanOutput = simResults.pulseResponse.channel.outputs.thru
    RXOutput   = simResults.pulseResponse.receiver.outputs.thru

    chanOutput2 = simResults2.pulseResponse.channel.outputs.thru
    RXOutput2   = simResults2.pulseResponse.receiver.outputs.thru
        
    # Add fake rise/fall-time
    TXOutput = addRiseFallSlope(TXOutput, tRise, sampleRate)

    # Adjust the length of each signal to display only desired cursors
    TXOutput,timeAxis = limitLength(TXOutput, signalingMode, preCursorCount, postCursorCount, samplesPerSymb, samplePeriod, True)
    chanOutput, _ = limitLength(chanOutput, signalingMode, preCursorCount, postCursorCount, samplesPerSymb, samplePeriod, False)
    RXOutput, _ = limitLength(RXOutput, signalingMode, preCursorCount, postCursorCount, samplesPerSymb, samplePeriod, False)
    
    chanOutput2, _ = limitLength(chanOutput2, signalingMode, preCursorCount, postCursorCount, samplesPerSymb, samplePeriod, False)
    RXOutput2, _ = limitLength(RXOutput2, signalingMode, preCursorCount, postCursorCount, samplesPerSymb, samplePeriod, False)

    # Plot transmitter output
    fig, axs = plt.subplots(nrows=3, ncols=1, dpi = 100, num='Pulse Response Comparison', sharex='all')
    fig.suptitle('Pulse Responses')
    fig.set_tight_layout(True)
    plotResponse(axs[0], chanOutput, chanOutput2, timeAxis, True, 'Channel Output', samplesPerSymb, samplePeriod, cursorCount, preCursorCount, postCursorCount)

    # Plot channel output
    plotResponse(axs[1], RXOutput, RXOutput2, timeAxis, True, 'Receiver Output', samplesPerSymb, samplePeriod, cursorCount, preCursorCount, postCursorCount)

    absolute = np.abs(RXOutput - RXOutput2)
    relative = absolute / np.abs(RXOutput2)
    # Plot receiver output
    plotResponse2(axs[2], relative, absolute, timeAxis, True, 'Comparison of RX Output (Relative)', samplesPerSymb, samplePeriod, cursorCount, preCursorCount, postCursorCount)


def addRiseFallSlope(TXOutput, tRise, sampleRate):

    diffSignal = np.diff(TXOutput)
    riseSamples = int(tRise * sampleRate)
    for index in range(len(diffSignal)):
        change = diffSignal[index]
        if change != 0:
            for rise in range(index, index+riseSamples+1):
                TXOutput[rise] = TXOutput[index-1]+change/riseSamples*(rise-index)

    return TXOutput


def limitLength(signal,signalingMode,preCursorCount,postCursorCount,samplesPerSymb,samplePeriod,isTX):

    # Locate pulse peak location
    # In MATLAB it went from both ends to find the center of a plateau
    # SciPy's Signal library already returns any such plateau center as the peak for the plateau
    peakLoc, prop = spsig.find_peaks(signal, height=0) # Set height to zero to get peak heights in properties
    peakLoc = peakLoc[np.argmax(prop['peak_heights'])] # Get the highest peak's index within the peak array

    # Shorten signal
    if isTX:
        startIdx = round(peakLoc-(preCursorCount+0.5)*samplesPerSymb)
        endIdx = round(peakLoc+(postCursorCount+0.5)*samplesPerSymb)
    else:
        if signalingMode == '1+D':
            startIdx = round(peakLoc-(preCursorCount+1)*samplesPerSymb)
            endIdx = round(peakLoc+(postCursorCount)*samplesPerSymb)
        elif signalingMode == '1+0.5D':
            startIdx = round(peakLoc-(preCursorCount+2/3)*samplesPerSymb)
            endIdx = round(peakLoc+(postCursorCount+1/3)*samplesPerSymb)
        else:
            startIdx = round(peakLoc-(preCursorCount+0.5)*samplesPerSymb)
            endIdx = round(peakLoc+(postCursorCount+0.5)*samplesPerSymb)

    
    if endIdx > len(signal):
        signal = np.concatenate((signal, np.zeros((endIdx-len(signal),))))
    else:
        signal = signal[:endIdx]
    
    if startIdx < 0:
        signal = np.concatenate((np.zeros((abs(startIdx),)), signal))
    else:
        signal = signal[startIdx:]
    
    timeAxis = np.arange(len(signal)) * samplePeriod

    return signal,timeAxis


def plotResponse(subplot: plt.Axes, response, response2, timeAxis,addLegend,name,samplesPerSymb,samplePeriod,cursorCount,preCursorCount,postCursorCount):
   
    # Add response
    subplot.plot(timeAxis, response, linewidth=1.5, label='Python')
    subplot.plot(timeAxis, response2, linewidth=1.5, label='MATLAB')
    subplot.set_title(name)
    subplot.set_ylabel('Amplitude [V]')
    subplot.set_xlabel('Time [s]')
    subplot.grid(True)
    subplot.set_xticks(np.arange(0, samplesPerSymb*cursorCount*samplePeriod,samplesPerSymb*samplePeriod))
    amplitude = max(response)-min(response)
    subplot.set_xlim(0, timeAxis[-1])
    subplot.set_ylim(min(response)-0.2*amplitude, max(response)+0.2*amplitude)
        
    # Add legend
    subplot.legend()
    
def plotResponse2(subplot: plt.Axes, response, response2, timeAxis,addLegend,name,samplesPerSymb,samplePeriod,cursorCount,preCursorCount,postCursorCount):
   
    # Add response
    subplot.plot(timeAxis, response, linewidth=1.5, label='Relative')
    #subplot.plot(timeAxis, response2, linewidth=1.5, label='Absolute')
    subplot.set_title(name)
    subplot.set_ylabel('Value')
    subplot.set_xlabel('Time [s]')
    subplot.grid(True)
    subplot.set_xticks(np.arange(0, samplesPerSymb*cursorCount*samplePeriod,samplesPerSymb*samplePeriod))
    subplot.set_xlim(0, timeAxis[-1])
    subplot.set_ylim(0, 0.1)
    