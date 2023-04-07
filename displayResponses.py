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

def displayChannels(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Plot only if desired
    if not simSettings.general.plotting.channelResponse: return 
        
    # Import variables
    addCrossTalk = simSettings.channel.addCrossTalk
    channels = simResults.influenceSources.channel

    freqScale = 1e-9 # Use this adjust frequency axis

    # Create figure
    plt.figure(dpi = 200, num='Channel Responses')
    plt.plot(channels.thru.frequencies * freqScale,20*np.log10(abs(channels.thru.transferFunction)), color = "blue", label = "THRU Channel", linewidth = 1)
    plt.ylabel('Attenuation [dB]')
    plt.xlabel('Frequency [GHz]')
    #plt.axvline(x=simSettings.general.symbolRate.value * freqScale / (simSettings.general.modulation.value), color = 'grey', label = "Nyquist Frequency")
    plt.title('Channel Transfer Characteristic')
    plt.grid()

    # Plot channels
    if addCrossTalk and channels.next.channelNumb > 0:
        plt.plot(channels.thru.frequencies * freqScale,20*np.log10(abs(channels.next.transferFunction)), color = "red", label = "NEXT Combined", linewidth = 1)
    
    if addCrossTalk and channels.fext.channelNumb > 0:
        plt.plot(channels.thru.frequencies * freqScale,20*np.log10(abs(channels.fext.transferFunction)), color = "green", label = "FEXT Combined", linewidth = 1)

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
    plt.figure(dpi = 200, num='CTLE Response')
    plt.semilogx(freqScale*CTLE.frequency, 10*np.log10(abs(CTLE.magnitude)), label = "CTLE responsel")
    plt.grid()

    # Plot channel
    plt.semilogx(freqScale*channel.frequencies, 10*np.log10(abs(channel.transferFunction)), label = "Channel response")
    
    # Plot resultant
    resultant = CTLE.magnitude*channel.transferFunction
    plt.semilogx(freqScale*channel.frequencies, 10*np.log10(abs(resultant)), label = "Resultant response")
    
    # Plot Nyquist
    plt.axvline(x=freqScale*simSettings.general.symbolRate.value / (simSettings.general.modulation.value),linestyle='dashed',color = 'red', label = "Nyquist Frequency")

    # Add legend
    plt.legend()
    plt.title('CTLE Response Characteristic')
    plt.ylabel('Attenuation [dB]')
    plt.xlabel('Frequency [GHz]')
    plt.xlim(freqScale*1e9, max(freqScale*CTLE.frequency))

