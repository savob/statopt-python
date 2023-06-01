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
import matplotlib.cm as cm
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
    for mainCursor in ISI.__dict__:
        for combName in ISI.__dict__[mainCursor].__dict__:
            setattr(trajectories, combName, ISI.__dict__[mainCursor].__dict__[combName].__dict__['trajectory'])
    
    # Order trajectories
    orderTraj = nothing()
    ordered = sorted(trajectories.__dict__)
    for comb in ordered:
        orderTraj.__dict__[comb] = trajectories.__dict__[comb]
    

    # Plot all trajectories
    plt.figure(dpi=200, num='ISI Trajectories', layout="constrained")
    plt.title('ISI Trajectories')
    plt.ylabel('Amplitude [V]')
    plt.xlabel('Time (s)')
    plt.grid(True)

    if signalingMode == '1+D':
        limit = min(outputPeak*4,supplyVoltage)
    elif signalingMode == '1+0.5D':
        limit = min(outputPeak*3,supplyVoltage)
    else:
        limit = min(outputPeak*2,supplyVoltage)
    plt.ylim(-limit,limit)

    xAxis = 0

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

    plt.xlim(0, max(xAxis))


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

        if plotName == 'initial':
            if not simSettings.general.plotting.PDFInitial: continue 
            title = 'Probability Distribution Initial'
        elif plotName == 'crossTalk':
            if not simSettings.general.plotting.PDFCrossTalk: continue 
            title = 'Probability Distribution after Cross-Talk'
        elif plotName == 'distorted':
            if not simSettings.general.plotting.PDFDistorted: continue 
            title = 'Probability Distribution after Distortion'
        elif plotName == 'jitter':
            if not simSettings.general.plotting.PDFJitter: continue 
            title = 'Probability Distribution after Jitter'
        elif plotName == 'noise':
            if not simSettings.general.plotting.PDFNoise: continue 
            title = 'Probability Distribution after Noise'
        elif plotName == 'final':
            if not simSettings.general.plotting.PDFFinal: continue 
            title = 'Probability Distribution'
        elif plotName == 'constellation':
            if not simSettings.general.plotting.PDFConstellation: continue 
            title = 'Constellation Distribution'
        else:
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
    plt.figure(dpi=200, num='PDF Plot', layout="constrained")
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
    plt.contour(X,Y,finalDist,[1e-12,1e-9,1e-6,1e-3], colors=[[0.8,0.8,0.8]], linewidths=[0.2]) # plot outline
    
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
        
        if signalingMode == '1+D':
            limit = min(outputPeak*4,supplyVoltage)
        elif signalingMode == '1+0.5D':
            limit = min(outputPeak*3,supplyVoltage)
        else:
            limit = min(outputPeak*2,supplyVoltage)
        
        plt.ylim(-limit, limit)
        plt.xticks(np.linspace(0, symbolPeriod*numbSymb, 7))
    


###########################################################################
# This function plots the BER distribution. Contour lines are added at BERs
# levels of 1e-3, 1e-6, 1e-9, and 1e-12 if possible. It also plots the
# vertical and horizontal bathtub curves for each eye.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
# 
# Outputs:
#   Contour plot of the BER distribution and eye dimension readouts
#   
###########################################################################
def displayBER(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Plot only if successful
    if not simResults.results.successful: return 
    
    if simSettings.general.plotting.BER:
    
        # Plot colored BER eye diagram
        axd = plotBERDistribution(simSettings, simResults, False)

        # Add eye contour lines
        plotEyeContours(simSettings, simResults, True, axd['top'])
        
        # Add sampler targets
        plotSampleTarget(simSettings, simResults, axd['top'])
        
        # Plot vertical bathtub
        plotVerticalBathtub(simSettings, simResults, axd['lower left'])
        
        # Plot horizontal bathtub
        plotHorizontalBathtub(simSettings, simResults, axd['lower right'])
    
    
    if simSettings.general.plotting.BER2:
    
        # Plot PDF
        axd = plotBERDistribution(simSettings, simResults, True)
        
        # Add eye contour lines
        plotEyeContours(simSettings, simResults, False, axd['top'])
        
        # Add sampler targets
        plotSampleTarget(simSettings, simResults, axd['top'])
        
        # Plot vertical bathtub
        plotVerticalBathtub(simSettings, simResults, axd['lower left'])
        
        # Plot horizontal bathtub
        plotHorizontalBathtub(simSettings, simResults, axd['lower right'])
    

        
###########################################################################
# This function plots the 2d contour of the BER eye diagram. The number of
# adjacent eyes is determined by variable "numbSymb".
###########################################################################
def plotBERDistribution(simSettings: simulationSettings, simResults: simulationStatus, onEyeDiagram: bool) -> plt.Axes:
    
    # Import variables
    signalingMode  = simSettings.general.signalingMode
    yAxis          = simSettings.general.yAxis.value
    xAxisLong      = simSettings.general.xAxisLong.value
    contLevels     = simSettings.general.contLevels.value
    samplesPerSymb = simSettings.general.samplesPerSymb.value
    symbolPeriod   = simSettings.general.symbolPeriod.value
    numbSymb       = simSettings.general.numbSymb.value
    supplyVoltage  = simSettings.receiver.signalAmplitude.value
    outputPeak = max(simResults.pulseResponse.receiver.outputs.thru)
    PDF        = simResults.eyeGeneration.PDF.final.combined
    BER        = simResults.eyeGeneration.BER.contours.combined
    
    # Combine PDF and BER eyes, ensure one is always in middle
    if np.mod(numbSymb,2) == 0:
        combinedPDF = PDF[:, int(samplesPerSymb/2):]
        combinedBER = BER[:, int(samplesPerSymb/2):]
        for symbol in range(numbSymb-1):
            combinedPDF = np.hstack((combinedPDF, PDF))
            combinedBER = np.hstack((combinedBER, BER))
        
        combinedPDF = np.hstack((combinedPDF, PDF[:, :int(samplesPerSymb/2)]))
        combinedBER = np.hstack((combinedBER, BER[:, :int(samplesPerSymb/2)]))
    else:
        combinedPDF = []
        combinedBER = []
        for symbol in range(numbSymb):
            combinedPDF = np.hstack((combinedPDF, PDF))
            combinedBER = np.hstack((combinedBER, BER))
    
    # Generate unique figure number
    # This is needed so both BER charts can be drawn without overlapping on the same figure
    figTitle = 'BER Plot'
    if onEyeDiagram == True:
        figTitle = 'BER Plot (on PDF)'

    # Plot BER
    # https://matplotlib.org/stable/tutorials/intermediate/arranging_axes.html
    fig, axd = plt.subplot_mosaic([['top', 'top'], ['top', 'top'], ['lower left', 'lower right']], layout='constrained', num=figTitle, dpi=200, figsize=(9.6, 6.4))
    X, Y = np.meshgrid(xAxisLong, yAxis)

    # Prepare colour map
    temp_big = mpl.colormaps['gray_r']

    if onEyeDiagram:
        newcmp = colours.ListedColormap(temp_big(np.linspace(0, 0.5, 2*contLevels)))
        axd['top'].contourf(X,Y,combinedPDF, contLevels, cmap=newcmp)
        axd['top'].contour(X,Y,combinedPDF, contLevels, colors=[[0.6, 0.6, 0.6]], linewidths=[0.5])
        axd['top'].contour(X,Y,combinedPDF,[1e-12, 1e-9, 1e-6, 1e-3], colors=[[0.8, 0.8, 0.8]], linewidths=[0.5])

        fig.colorbar(cm.ScalarMappable(norm=colours.Normalize(vmin=0, vmax=np.round(np.max(combinedPDF), 2)), cmap=newcmp), ax=axd['top'])
    else:
        newcmp = colours.ListedColormap(temp_big(np.linspace(0, 1, 2*contLevels)))
        axd['top'].contourf(X,Y,combinedBER,contLevels, cmap=newcmp)

        fig.colorbar(cm.ScalarMappable(norm=colours.Normalize(0, np.round(np.max(combinedBER), 2)), cmap=newcmp), ax=axd['top'])
    
    axd['top'].set_title('BER Plot')
    axd['top'].set_ylabel('Amplitude [V]')
    axd['top'].set_xlabel('Time [s]')
    if signalingMode == '1+D':
        limit = min(outputPeak*4,supplyVoltage)
    elif signalingMode == '1+0.5D':
        limit = min(outputPeak*3,supplyVoltage)
    else:
        limit = min(outputPeak*2,supplyVoltage)
    
    axd['top'].set_ylim(-limit,limit)
    axd['top'].set_yticks(np.linspace(-limit, limit, 11))
    axd['top'].set_xticks(np.linspace(0, symbolPeriod*numbSymb,7))
    axd['top'].grid(True)
    
    return axd


###########################################################################
# This function plots the eye contours at BER levels of 1e-3, 1e-6, 1e-9
# and 1e-12 if possible. It also adds a legend which labels each contour.
###########################################################################
def plotEyeContours(simSettings: simulationSettings, simResults: simulationStatus, darkLegend: bool, curPlot: plt.Axes):

    # Import variables
    yAxis          = simSettings.general.yAxis.value
    xAxisLong      = simSettings.general.xAxisLong.value
    samplesPerSymb = simSettings.general.samplesPerSymb.value
    numbSymb       = simSettings.general.numbSymb.value
    BER           = simResults.eyeGeneration.BER.contours.combined
    
    # Combine eyes
    if np.mod(numbSymb, 2) == 0:
        combinedBER = BER[:, int(samplesPerSymb/2)+1:]
        for symbol in range(numbSymb-1):
            combinedBER = np.hstack((combinedBER, BER)) 
        
        combinedBER = np.hstack((combinedBER, BER[:, :int(samplesPerSymb/2)+1])) 
    else:
        combinedBER=[]
        for symbol in range(numbSymb):
            combinedBER = np.hstack((combinedBER, BER)) 
        
    
    distribution = combinedBER
    X, Y = np.meshgrid(xAxisLong, yAxis)
    
    #handles = []
    labels = []
    breaks = []
    coloursList = []
    proxy = []


    # Plot all contours if possible
    if np.min(distribution)<=1e-12:
        labels.append('BER: 1.0e-12')
        coloursList.append([0, 1, 1])
        breaks.append(1e-12)

    if np.min(distribution)<=1e-9:
        labels.append('BER: 1.0e-9')
        coloursList.append([0, 0.85, 0])
        breaks.append(1e-9)

    if np.min(distribution)<=1e-6:
        labels.append('BER: 1.0e-6')
        coloursList.append([1, 0.8, 0])
        breaks.append(1e-6)

    if np.min(distribution)<=1e-3:
        labels.append('BER: 1.0e-3')
        coloursList.append([1, 0.6, 0])
        breaks.append(1e-3)

        # Plot contours and prepare legend information using proxy artists to record colour
        CS = curPlot.contour(X,Y,distribution, breaks, colors=coloursList, linewidth=1)
        proxy = [plt.Rectangle((0,0),1,1,fc = pc.get_edgecolor()) for pc in CS.collections]

    # Add legend based on style
    if np.min(BER) <= 1e-3:
        if darkLegend:
            curPlot.legend(proxy, labels, facecolor='black', labelcolor='white')
        else:
            curPlot.legend(proxy, labels)


###########################################################################
# This function adds targets showing the optimal position to sample data.
###########################################################################
def plotSampleTarget(simSettings: simulationSettings, simResults: simulationStatus, curPlot: plt.Axes):

    # Import variables
    samplePeriod   = simSettings.general.samplePeriod.value
    samplesPerSymb = simSettings.general.samplesPerSymb.value
    yIncrement     = simSettings.general.yIncrement.value
    yAxisLength    = simSettings.general.yAxisLength.value
    numbSymb       = simSettings.general.numbSymb.value
    eyeLocs = simResults.results.eyeLocs
    
    # Display targets
    xLength = numbSymb*samplesPerSymb*samplePeriod/60
    yLength = yAxisLength*yIncrement/45
    xLoc = eyeLocs.time+(numbSymb/2)*samplesPerSymb*samplePeriod

    if isinstance(eyeLocs.level, list):
        for eye in range(len(eyeLocs.level)):
            yLoc = eyeLocs.level[eye]
            curPlot.plot([xLoc-xLength,xLoc+xLength], [yLoc,yLoc], 'r')
            curPlot.plot([xLoc,xLoc], [yLoc-yLength,yLoc+yLength], 'r')
    else:
        yLoc = eyeLocs.level
        curPlot.plot([xLoc-xLength,xLoc+xLength], [yLoc,yLoc], 'r')
        curPlot.plot([xLoc,xLoc], [yLoc-yLength,yLoc+yLength], 'r')
    


###########################################################################
# This function plots the vertical bathtub curve.
###########################################################################
def plotVerticalBathtub(simSettings: simulationSettings, simResults: simulationStatus, curPlot: plt.Axes):

    # Import variables
    signalingMode = simSettings.general.signalingMode
    yAxis         = simSettings.general.yAxis.value
    supplyVoltage = simSettings.receiver.signalAmplitude.value
    outputPeak = max(simResults.pulseResponse.receiver.outputs.thru)
    bathTub    = simResults.eyeGeneration.BER.bathTubY
    
    # Display bathtub
    bathTub = np.maximum(bathTub,1e-12)
    curPlot.semilogx(bathTub,yAxis, linewidth=1.5)
    curPlot.set_title('Vertical Bathtub')
    curPlot.set_ylabel('Amplitude [V]')
    curPlot.set_xlabel('BER')
    
    if signalingMode == '1+D':
        limit = min(outputPeak*4,supplyVoltage)
    elif signalingMode == '1+0.5D':
        limit = min(outputPeak*3,supplyVoltage)
    else:
        limit = min(outputPeak*2,supplyVoltage)
    
    curPlot.set_ylim(-limit, limit)
    curPlot.grid(True)
    if min(bathTub) == 1e-12:
        curPlot.set_xticks([1e-12, 1e-9, 1e-6, 1e-3, 1e-0]) 
        curPlot.set_xlim(1e-12, 1)
    


###########################################################################
# This function plots the horizontal bathtub curve.
###########################################################################
def plotHorizontalBathtub(simSettings: simulationSettings, simResults: simulationStatus, curPlot: plt.Axes):

    # Import variables
    xAxisCenter = simSettings.general.xAxisCenter.value
    bathTubs = simResults.eyeGeneration.BER.bathTubX
    
    # Display bathtub
    
    legText = []
    tubs = list(bathTubs.__dict__)
    for index in range(len(tubs)-1, -1, -1):
        tubName = tubs[index]
        bathTubs.__dict__[tubName] = np.maximum(bathTubs.__dict__[tubName], 1e-12)
        curPlot.semilogy(xAxisCenter,bathTubs.__dict__[tubName], linewidth=1.5, label=('Eye: ' + str(index)))
        
        if min(bathTubs.__dict__[tubName]) == 1e-12:
            curPlot.set_yticks([1e-12, 1e-9, 1e-6, 1e-3, 1e-0])
            curPlot.set_ylim(1e-12, 1)
    
    curPlot.set_title('Horizontal Bathtub')
    curPlot.set_ylabel('BER')
    curPlot.set_xlabel('Time [s]')
    curPlot.grid(True)
    if len(tubs) > 1:
        curPlot.legend()
    
