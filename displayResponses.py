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
# This function plots the channel characteristic transfer function for each
# available channel. The power of all cross-talk channels is combined
# before being displayed.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
# 
# Outputs:
#   A plot of the channel transfer function
#   
###########################################################################
from userSettingsObjects import simulationSettings
from initializeSimulation import simulationStatus
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as spsig

def displayChannels(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Plot only if desired
    if not simSettings.general.plotting.channelResponse: return 
        
    # Import variables
    addCrossTalk = simSettings.channel.addCrossTalk
    channels = simResults.influenceSources.channel

    freqScale = 1e-9 # Use this adjust frequency axis

    # Create figure
    plt.figure(dpi=100, num='Channel Responses', layout='constrained')
    plt.plot(channels.thru.frequencies * freqScale,20*np.log10(abs(channels.thru.transferFunction)), color = "blue", label = "THRU Channel", linewidth = 0.5)
    plt.ylabel('Attenuation [dB]')
    plt.xlabel('Frequency [GHz]')
    #plt.axvline(x=simSettings.general.symbolRate.value * freqScale / (simSettings.general.modulation.value), color = 'grey', label = "Nyquist Frequency")
    plt.title('Channel Transfer Characteristic')
    plt.grid()

    # Plot channels
    if addCrossTalk and channels.next.channelNumb > 0:
        plt.plot(channels.thru.frequencies * freqScale,20*np.log10(abs(channels.next.transferFunction)), color = "red", label = "NEXT Combined", linewidth = 0.5)
    
    if addCrossTalk and channels.fext.channelNumb > 0:
        plt.plot(channels.thru.frequencies * freqScale,20*np.log10(abs(channels.fext.transferFunction)), color = "green", label = "FEXT Combined", linewidth = 0.5)

    plt.xlim(0, freqScale*max(channels.thru.frequencies))
    plt.legend()
    

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
# This function plots the transfer function of the CTLE. It also
# superimposes the channel plot to use as comparison. Finally, it plots the
# location of the Nyquist frequency.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
#   
# Outputs:
#   A plot of the CTLE transfer function
#
###########################################################################

from userSettingsObjects import simulationSettings
from initializeSimulation import simulationStatus
import matplotlib.pyplot as plt
import numpy as np

def displayCTLEResponse(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Plot only if desired
    if not simSettings.general.plotting.CTLEResponse: return 

    # Import variables
    symbolRate = simSettings.general.symbolRate.value
    zeroFreq   = simSettings.receiver.CTLE.zeroFreq.value
    pole1Freq  = simSettings.receiver.CTLE.pole1Freq.value
    zeroName     = ('z' + str(zeroFreq/1e9)).replace('.', '_')
    poleName     = ('z' + str(pole1Freq/1e9)).replace('.', '_')
    CTLE    = simResults.influenceSources.RXCTLE.__dict__[zeroName].__dict__[poleName]
    channel = simResults.influenceSources.channel.thru
    
    freqScale = 1e-9 # Use this adjust frequency axis


    # Plot CTLE
    plt.figure(dpi=100, num='CTLE Response', layout='constrained')
    plt.semilogx(freqScale*CTLE.frequency, 10*np.log10(abs(CTLE.magnitude)), linewidth=0.5, label = "CTLE response")
    plt.grid()

    # Plot channel
    plt.semilogx(freqScale*channel.frequencies, 10*np.log10(abs(channel.transferFunction)), linewidth=0.5, label = "Channel response")
    
    # Plot resultant
    resultant = CTLE.magnitude*channel.transferFunction
    plt.semilogx(freqScale*channel.frequencies, 10*np.log10(abs(resultant)), linewidth=0.5, label = "Resultant response")
    
    # Plot Nyquist
    plt.axvline(x=freqScale*simSettings.general.symbolRate.value / (simSettings.general.modulation.value),linestyle='dashed',color = 'red', label = "Nyquist Frequency")

    # Add legend
    plt.legend()
    plt.title('CTLE Response Characteristic')
    plt.ylabel('Attenuation [dB]')
    plt.xlabel('Frequency [GHz]')
    plt.xlim(freqScale*1e9, max(freqScale*CTLE.frequency))


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
# This function plots the transmitter output, channel output and receiver
# output. The TX response is post equalization. All responses are not 
# applied to sources of inteference. This function also plots the location 
# of each cursor, representing the number of symbol which the response 
# covers.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
#   
# Outputs:
#   A plot of the un-intefered pulse response post-FFE equalization
#
###########################################################################
def displayPulse(simSettings: simulationSettings, simResults: simulationStatus):
    
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
        
    # Add fake rise/fall-time
    TXOutput = addRiseFallSlope(TXOutput, tRise, sampleRate)

    # Adjust the length of each signal to display only desired cursors
    TXOutput,timeAxis = limitLength(TXOutput, signalingMode, preCursorCount, postCursorCount, samplesPerSymb, samplePeriod, True)
    chanOutput, _ = limitLength(chanOutput, signalingMode, preCursorCount, postCursorCount, samplesPerSymb, samplePeriod, False)
    RXOutput, _ = limitLength(RXOutput, signalingMode, preCursorCount, postCursorCount, samplesPerSymb, samplePeriod, False)

    # Plot transmitter output
    fig, axs = plt.subplots(nrows=3, ncols=1, dpi=100, num='Pulse Response', sharex='all', layout='constrained')
    fig.suptitle('Pulse Responses')
    plotResponse(axs[0], TXOutput, timeAxis, True, 'Transmitter Output', samplesPerSymb, samplePeriod, cursorCount, preCursorCount, postCursorCount)

    # Plot channel output
    plotResponse(axs[1], chanOutput, timeAxis, False, 'Channel Output', samplesPerSymb, samplePeriod, cursorCount, preCursorCount, postCursorCount)

    # Plot receiver output
    plotResponse(axs[2], RXOutput, timeAxis, False, 'Receiver Output', samplesPerSymb, samplePeriod, cursorCount, preCursorCount, postCursorCount)


###########################################################################
# This function artificially adds rise and fall slope to the signal. This
# is infact added when the signal passes through the channel, however
# allows for a visual representation.
###########################################################################
def addRiseFallSlope(TXOutput, tRise, sampleRate):

    diffSignal = np.diff(TXOutput)
    riseSamples = int(tRise * sampleRate)
    for index in range(len(diffSignal)):
        change = diffSignal[index]
        if change != 0:
            for rise in range(index, index+riseSamples+1):
                TXOutput[rise] = TXOutput[index-1]+change/riseSamples*(rise-index)

    return TXOutput


###########################################################################
# This function adjusts the length of the signal to display only desired
# cursors. If the TX output is being plotted, a slight offset is added to
# allow for the signal to apear in the middle of the symbol period, even
# with its exponential slope.
###########################################################################
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


###########################################################################
# This function plots the response. It also adds cursors at each symbol
# location.
###########################################################################
def plotResponse(subplot: plt.Axes, response,timeAxis,addLegend,name,samplesPerSymb,samplePeriod,cursorCount,preCursorCount,postCursorCount):
   
    # Add response
    subplot.plot(timeAxis, response, linewidth=1.5)
    subplot.set_title(name)
    subplot.set_ylabel('Amplitude [V]')
    subplot.set_xlabel('Time [s]')
    subplot.grid(True)
    subplot.set_xticks(np.arange(0, samplesPerSymb*cursorCount*samplePeriod,samplesPerSymb*samplePeriod))
    amplitude = max(response)-min(response)
    subplot.set_xlim(0, timeAxis[-1])
    subplot.set_ylim(min(response)-0.2*amplitude, max(response)+0.2*amplitude)
        
    # Add pre-cursors
    for index in range(preCursorCount, 0, -1):
        loc = int((preCursorCount-index+0.5) * samplesPerSymb)
        subplot.plot([loc*samplePeriod, loc*samplePeriod], [0, response[loc]], linewidth=2, label=('Pre-Cursor ' + str(index)))

    # Add main-cursor(s)
    subplot.plot([(preCursorCount+0.5)*samplesPerSymb*samplePeriod, (preCursorCount+0.5)*samplesPerSymb*samplePeriod], [0, response[int((preCursorCount+0.5)*samplesPerSymb)]], linewidth=2, label='Main Cursor')
    
    # Add post-cursors
    for index in range(1, postCursorCount+1):
        loc = int((preCursorCount+index+0.5)*samplesPerSymb)
        subplot.plot([loc*samplePeriod, loc*samplePeriod], [0, response[loc]], linewidth=2, label=('Post-Cursor ' + str(index)))

    # Add legend
    if addLegend:
        subplot.legend()
    
