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
# This function plots all possible ISI signal trajectories onto an eye 
# diagram. This adds considerable time to the simulation! Consider
# commenting out unless required.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
# 
# Outputs:
#   Plot of the ISI signal trajectories
#   
###########################################################################

from userSettingsObjects import simulationSettings
from initializeSimulation import simulationStatus
import matplotlib.pyplot as plt
import matplotlib.colors as colours
import matplotlib as mpl
import numpy as np

class nothing:
    def __init__(self):
        pass

def displayISI(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Plot only if desired
    if not simSettings.general.plotting.ISI: return 
    
    # Import variables
    signalingMode  = simSettings.general.signalingMode
    samplesPerSymb = simSettings.general.samplesPerSymb.value
    samplePeriod   = simSettings.general.samplePeriod.value
    numbSymb       = simSettings.general.numbSymb.value
    supplyVoltage  = simSettings.receiver.signalAmplitude.value
    outputPeak = max(simResults.pulseResponse.receiver.outputs.thru)
    ISI        = simResults.eyeGeneration.ISI.thru

    trajectories = nothing()

    # To reduce the discontinuation visibility, ungroup trajectories from their main cursor
    for mainCursor in ISI:
        for combName in ISI[mainCursor]:
            setattr(trajectories, combName, ISI[mainCursor][combName]['trajectory'])
    
    # Order trajectories
    orderTraj = nothing()
    ordered = sorted(trajectories.__dict__)
    for comb in ordered:
        orderTraj.__dict__[comb] = trajectories.__dict__[comb]
    

    # Plot all trajectories
    plt.figure(dpi = 200, num='ISI Trajectories')
    plt.title('ISI Trajectories')
    plt.ylabel('Amplitude [V]')
    plt.xlabel('Samples')
    plt.grid(True)

    if signalingMode == '1+D':
        limit = min(outputPeak*4,supplyVoltage)
    elif signalingMode == '1+0.5D':
        limit = min(outputPeak*3,supplyVoltage)
    else:
        limit = min(outputPeak*2,supplyVoltage)
    plt.ylim(-limit,limit)

    for comb in ordered:

        # Add additional point to stich eyes together
        trajectory = orderTraj.__dict__[comb]

        trajectory1 = trajectory[int(samplesPerSymb/2)+1:]
        velocity = trajectory1[-1]-trajectory1[-2]
        trajectory1 = np.concatenate((trajectory1, [trajectory1[-1]+velocity]))

        trajectory2 = trajectory[:int(samplesPerSymb/2)-1]
        velocity = trajectory2[1]-trajectory2[0]
        trajectory2 = np.concatenate(([trajectory2[0]-velocity], trajectory2))

        velocity = trajectory[-1]-trajectory[-2]
        trajectory3 = np.concatenate((trajectory, [trajectory[-1]+velocity]))

        # Plot multiple eyes adjacent to oneanother, ensure eye is always in the middle
        for symb in range(numbSymb):
            if np.mod(numbSymb,2) == 0:

                # Plot left half
                xIndex = np.arange(symb*samplesPerSymb, (symb+0.5)*samplesPerSymb, 1)
                xAxis = xIndex*samplePeriod
                plt.plot(xAxis,trajectory1)

                # Plot right half
                xIndex = np.arange((symb+0.5)*samplesPerSymb, (symb+1)*samplesPerSymb, 1)
                xAxis = xIndex*samplePeriod
                plt.plot(xAxis,trajectory2)
            else:
                # Plot full eye
                xIndex = np.arange(symb*samplesPerSymb, (1+symb)*samplesPerSymb, 1)
                xAxis = xIndex*samplePeriod
                plt.plot(xAxis,trajectory3)



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
# This function generates an eye diagram from the probability distribution.
# The post-cross-talk, post-jitter and post-noise probability distribution 
# will also be plotted if they have been added.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
# 
# Outputs:
#   Multiple coloured PDF distrubution in the form of eye diagrams
#   
###########################################################################
def displayPDF(simSettings: simulationSettings, simResults: simulationStatus):

    for plotName in simResults.eyeGeneration.PDF.__dict__:

        if plotName[0:4] == 'main': continue

        title = ''

        match plotName: 
            case 'initial':
                if not simSettings.general.plotting.PDFInitial: continue 
                title = 'Probability Distribution Initial'
            case 'crossTalk':
                if not simSettings.general.plotting.PDFCrossTalk: continue 
                title = 'Probability Distribution after Cross-Talk'
            case 'distorted':
                if not simSettings.general.plotting.PDFDistorted: continue 
                title = 'Probability Distribution after Distortion'
            case 'jitter':
                if not simSettings.general.plotting.PDFJitter: continue 
                title = 'Probability Distribution after Jitter'
            case 'noise':
                if not simSettings.general.plotting.PDFNoise: continue 
                title = 'Probability Distribution after Noise'
            case 'final':
                if not simSettings.general.plotting.PDFFinal: continue 
                title = 'Probability Distribution'
            case 'constellation':
                if not simSettings.general.plotting.PDFConstellation: continue 
                title = 'Constellation Distribution'
            case _:
                print('ERROR: Unknown plot found for probability distribution plot')
                quit()
        
        plotDistribution(simSettings, simResults,simResults.eyeGeneration.PDF.__dict__[plotName].combined, title)


###########################################################################
# This function combines multiple PDF eyes together before plotting them.
###########################################################################
def plotDistribution(simSettings,simResults,distribution,name):

    # Import variables
    samplesPerSymb = simSettings.general.samplesPerSymb.value
    signalingMode  = simSettings.general.signalingMode
    symbolPeriod   = simSettings.general.symbolPeriod.value
    yAxis          = simSettings.general.yAxis.value
    xAxis          = simSettings.general.xAxisLong.value
    numbSymb       = simSettings.general.numbSymb.value
    contLevels     = simSettings.general.contLevels.value
    supplyVoltage  = simSettings.receiver.signalAmplitude.value
    outputPeak    = max(simResults.pulseResponse.receiver.outputs.thru)
    samplerLevels = simResults.results.eyeLocs.level
    
    finalDist = 0

    # Combine multiple eyes, ensure one is always in middle
    if name != 'Constellation Distribution':
        if np.mod(numbSymb, 2) == 0:
            finalDist = distribution[:, int(samplesPerSymb/2):]
            for symbol in range(numbSymb-1):
                finalDist = np.hstack((finalDist, distribution))
            
            finalDist = np.hstack((finalDist, distribution[:, :int(samplesPerSymb/2)]))
        else:
            finalDist=[]
            for symbol in range(numbSymb + 1):
                finalDist = np.hstack((finalDist, distribution))
    else:
        finalDist = distribution
    
    
    # Create figure
    plt.figure(dpi = 200, num='PDF Plot')
    if name == 'Constellation Distribution':
        contLevels = contLevels/2
        X, Y = np.meshgrid(yAxis,yAxis)
    else:
        X, Y = np.meshgrid(xAxis,yAxis)
    
    # Prepare colour map for pl t
    temp_big = mpl.colormaps['hot_r']
    newcmp = colours.ListedColormap(temp_big(np.linspace(0, 0.8, contLevels))) # Remove black since same color as outline
    plt.contourf(X, Y, finalDist, contLevels, cmap=newcmp)
    plt.colorbar()
    plt.contour(X, Y, finalDist, contLevels, colors='black', linewidths=[0.2]) # Need to add outlines manually to 'contourf'
    plt.contour(X,Y,finalDist,[1e-12,1e-9,1e-6,1e-3], edgecolor=[0.8,0.8,0.8], faceColor='none', colors='grey', linewidths=[0.2]) # plot outline
    
    plt.title(name)
    plt.grid(True)
    if name == 'Constellation Distribution':
        plt.ylabel('I Amplitude [V]')
        plt.xlabel('Q Amplitude [V]')
        limit = min(2*outputPeak, supplyVoltage)
        plt.xlim(-limit, limit)
        plt.ylim(-limit, limit)
        
        # Add ticks to seperate constellation bits
        if len(samplerLevels) > 1:
            delta = samplerLevels[-1]-samplerLevels[-2]
            samplerLevels = [-limit, samplerLevels[0]-delta, samplerLevels, samplerLevels[-1]+delta,limit]
        else:
            samplerLevels = [-limit, samplerLevels, limit]
        
        plt.yticks(samplerLevels)
        plt.xticks(samplerLevels)
    else:
        plt.ylabel('Amplitude [V]')
        plt.xlabel('Time [s]')
        match signalingMode:
            case '1+D':
                limit = min(outputPeak*4,supplyVoltage)
            case '1+0.5D':
                limit = min(outputPeak*3,supplyVoltage)
            case _:
                limit = min(outputPeak*2,supplyVoltage)
        
        plt.ylim(-limit, limit)
        plt.xticks(np.linspace(0, symbolPeriod*numbSymb, 7))
    
