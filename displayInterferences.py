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
# This function plots the jitter source distributions. Sources include the
# TX jitter and RX CDR jitter.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
# 
# Outputs:
#   A PDF distribution of the two jitter sources.
#   
###########################################################################
from userSettingsObjects import simulationSettings
from initializeSimulation import simulationStatus
import matplotlib.pyplot as plt

def displayJitter(simSettings: simulationSettings, simResults: simulationStatus):

    # Plot only if desired
    if not simSettings.general.plotting.jitterSource: return 
    
    # Import variables
    TXJitter    = simResults.influenceSources.TXJitter.totalJitter
    TXTime      = simResults.influenceSources.TXJitter.UIScale
    RXJitter    = simResults.influenceSources.RXJitter.totalJitter
    RXTime      = simResults.influenceSources.RXJitter.UIScale  
    totalJitter = simResults.influenceSources.totalJitter.totalJitter
    totalTime   = simResults.influenceSources.totalJitter.UIScale  
    
    # Plot jitter PDF
    # Something is off about the width of bars, this current configuration makes decent looking graphs though.
    fig, axs = plt.subplots(nrows=3, ncols=1, sharex='all', dpi=100, num='Jitter Distribution', layout='constrained')
    fig.suptitle('Jitter Histograms')
    axs[0].hist(TXTime[:-1], TXTime, weights=TXJitter)
    axs[0].set_title('TX')
    axs[0].set_ylabel('Normalized\nProbability')
    axs[0].set_xlim(TXTime[0], TXTime[-1])
    axs[0].grid()

    axs[1].hist(RXTime[:-1], RXTime, weights=RXJitter)
    axs[1].set_title('Clock Data Recovery (RX CDR)')
    axs[1].set_ylabel('Normalized\nProbability')
    axs[1].grid()

    axs[2].hist(totalTime[:-1], totalTime, weights=totalJitter)
    axs[2].set_title('Combined')
    axs[2].set_ylabel('Normalized\nProbability')
    axs[2].set_xlabel('Time [UI]')
    axs[2].grid()


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
# This function plots the noise source distributions. Sources include the
# TX noise and RX noise.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
# 
# Outputs:
#   A PDF distribution of the two jitter sources.
#   
###########################################################################
def displayNoise (simSettings: simulationSettings, simResults: simulationStatus):

    # Plot only if desired
    if not simSettings.general.plotting.noiseSource: return 
    
    # Import variables
    yAxis     = simSettings.general.yAxis.value
    TXNoise      = simResults.influenceSources.TXNoise.totalNoise
    TXVoltage    = simResults.influenceSources.TXNoise.voltageScale
    CHNoise      = simResults.influenceSources.CHNoise.totalNoise
    CHVoltage    = simResults.influenceSources.CHNoise.voltageScale
    RXNoise      = simResults.influenceSources.RXNoise.totalNoise
    RXVoltage    = simResults.influenceSources.RXNoise.voltageScale
    totalNoise   = simResults.influenceSources.totalNoise.histogram
    totalVoltage = simResults.influenceSources.totalNoise.voltageScale  
    
    # Plot noise PDF
    fig, axs = plt.subplots(nrows=1, ncols=4, sharey='all', dpi=100, num='Noise Distribution', layout='constrained')
    fig.suptitle('Noise Histograms')
    axs[0].hist(TXVoltage[:-1], TXVoltage, weights=TXNoise, orientation='horizontal')
    axs[0].set_title('TX')
    axs[0].set_xlabel('Normalized\nProbability') 
    axs[0].set_ylabel('Amplitude [V]')
    axs[0].grid()
    axs[0].set_ylim(yAxis[0], yAxis[-1])
    
    axs[1].hist(CHVoltage[:-1], CHVoltage, weights=CHNoise, orientation='horizontal')
    axs[1].set_title('Channel')
    axs[1].set_xlabel('Normalized\nProbability')
    axs[1].set_ylabel('Amplitude [V]')
    axs[1].grid()

    axs[2].hist(RXVoltage[:-1], RXVoltage, weights=RXNoise, orientation='horizontal')
    axs[2].set_title('RX')
    axs[2].set_xlabel('Normalized\nProbability')
    axs[2].set_ylabel('Amplitude [V]')
    axs[2].grid()
    
    axs[3].hist(totalVoltage[:-1], totalVoltage, weights=totalNoise, orientation='horizontal')
    axs[3].set_title('Combined')
    axs[3].set_xlabel('Normalized\nProbability')
    axs[3].set_ylabel('Amplitude [V]')
    axs[3].grid()


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
# This function plots the distortion transfer functions for the transmitter
# and receiver.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
# 
# Outputs:
#   Two transfer functions displaying non-linearity.
#   
###########################################################################
def displayDistortion(simSettings: simulationSettings, simResults: simulationStatus):

    # Plot only if desired
    if not simSettings.general.plotting.distortionSource: return 
    
    # Import variables
    supplyVoltage = simSettings.receiver.signalAmplitude.value
    TXInput     = simResults.influenceSources.TXDistortion.input
    TXOutput    = simResults.influenceSources.TXDistortion.output
    RXInput     = simResults.influenceSources.RXDistortion.input
    RXOutput    = simResults.influenceSources.RXDistortion.output
    totalInput  = simResults.influenceSources.totalDistortion.input
    totalOutput = simResults.influenceSources.totalDistortion.output
    
    # Plot distortion

    fig, axs = plt.subplots(nrows=1, ncols=3, dpi=100, num='Non-Linearity', layout='constrained')
    fig.suptitle('Distortion')
    axs[0].plot(TXInput, TXOutput, linewidth=2)
    axs[0].set_title('TX')
    axs[0].set_ylabel('Output [V]') 
    axs[0].set_xlabel('Input [V]')
    axs[0].set_ylim(min(TXOutput), max(TXOutput))
    axs[0].set_xlim(min(TXInput), max(TXInput))
    axs[0].grid()
    
    axs[1].plot(RXInput, RXOutput, linewidth=2)
    axs[1].set_title('RX')
    axs[1].set_ylabel('Output [V]') 
    axs[1].set_xlabel('Input [V]')
    axs[1].set_ylim(-supplyVoltage, supplyVoltage)
    axs[1].set_xlim(min(RXInput), max(RXInput))
    axs[1].grid()

    axs[2].plot(totalInput, totalOutput, linewidth=2)
    axs[2].set_title('Combined')
    axs[2].set_ylabel('Output [V]') 
    axs[2].set_xlabel('Input [V]')
    axs[2].set_ylim(-supplyVoltage, supplyVoltage)
    axs[2].set_xlim(min(totalInput), max(totalInput))
    axs[2].grid()

    
