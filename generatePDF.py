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
# This function generates the PDF of the channel eye diagram. It combines
# the pulse response which has passed through the channel and
# equalization elements, ISI from adjacent symbols, cross-talk from
# adjacent wires, distortion from both TX and RX, jitter from both
# TX and CDR, and noise from both TX and RX to creates an accurate 
# probability distribution.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
# 
# Outputs:
#   simResults: structure containing simulation results
#   
###########################################################################

from userSettingsObjects import simulationSettings
from initializeSimulation import simulationStatus
import numpy as np

class nothing:
    def __init__(self):
        pass

def generatePDF(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Break if simulation has already failed
    if not simResults.results.successful: return 
    
    # Create PDF from ISI
    generateHist(simSettings, simResults)

    # Add cross-talk
    applyCrossTalk(simSettings, simResults)
    
    # Add distortion
    applyDistortion(simSettings, simResults)
       
    # Add jitter
    applyJitter(simSettings, simResults)
            
    # Add noise
    applyNoise(simSettings, simResults)
    
    # Combine PDF together
    combinePDFs(simResults)


###########################################################################
# This function creates a probability distribution histogram based on the
# classified ISI trajectories. It first combines all ISI trajectories
# pertaining to the same main-cursor into a single array and then turns the 
# trajectories into a histograms.
###########################################################################
def generateHist(simSettings: simulationSettings, simResults: simulationStatus):

    # Import variables
    samplesPerSymb = simSettings.general.samplesPerSymb.value
    yAxis          = simSettings.general.yAxis.value
    yIncrement     = simSettings.general.yIncrement.value
    approximate    = simSettings.channel.approximate
    ISI = simResults.eyeGeneration.ISI

    trajectories = nothing()
    PDF = nothing()
    PDF.initial = nothing()
    
    # Loop through each available channel file
    for chName in ISI.__dict__:
        setattr(PDF.initial, chName, nothing())
        setattr(trajectories, chName, nothing())

        # Skip required channels
        if approximate:
            if chName != 'thru' and chName != 'xtalk':
                continue
            
        else:
            if chName == 'next' or chName == 'fext' or chName == 'xtalk':
                continue
        
        # Combine trajectories into a single matrix
        transitions = ISI.__dict__[chName].__dict__
        for transName in transitions:
            setattr(PDF.initial.__dict__[chName], transName, [])

            trajectories.__dict__[chName].__dict__[transName]=[]
            cursorComb = ISI.__dict__[chName].__dict__[transName].__dict__
            for comb in cursorComb:
                if trajectories.__dict__[chName].__dict__[transName] == []:
                    trajectories.__dict__[chName].__dict__[transName] = ISI.__dict__[chName].__dict__[transName].__dict__[comb].trajectory 
                else:
                    trajectories.__dict__[chName].__dict__[transName] = np.vstack((trajectories.__dict__[chName].__dict__[transName], ISI.__dict__[chName].__dict__[transName].__dict__[comb].trajectory))
        
        # Create transition-classified histogram from matrix
        for transName in transitions:
            for index in range(samplesPerSymb):
                # Not that in MATLAB the bins are defined by center-points, while in Python they are the edges.
                yAxisLong = np.concatenate((yAxis, [yAxis[-1] + yIncrement])) - yIncrement/2 # add additional bin to remove clipping
                if trajectories.__dict__[chName].__dict__[transName].ndim > 1:
                    histogram, edges = np.histogram(trajectories.__dict__[chName].__dict__[transName][:,index], yAxisLong)
                else:
                    histogram, edges = np.histogram(trajectories.__dict__[chName].__dict__[transName][index], yAxisLong)
                normalized = histogram / len(transitions) # Normalize for all transitions

                if PDF.initial.__dict__[chName].__dict__[transName] == []:
                    PDF.initial.__dict__[chName].__dict__[transName] = normalized
                else:
                    PDF.initial.__dict__[chName].__dict__[transName] = np.vstack((PDF.initial.__dict__[chName].__dict__[transName], normalized))
        
            PDF.initial.__dict__[chName].__dict__[transName] =  np.transpose(PDF.initial.__dict__[chName].__dict__[transName])
                
    # Save results
    simResults.eyeGeneration.PDF = PDF # reset previous PDF


###########################################################################
# This function applies cross-talk to the probability distribution by
# convolving each channel together vertically. The cross-talk channels
# must first combine all levels together before performing the convolution.
###########################################################################
def applyCrossTalk(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    samplesPerSymb   = simSettings.general.samplesPerSymb.value
    yAxisLength      = simSettings.general.yAxisLength.value
    makeAsynchronous = simSettings.channel.makeAsynchronous
    approximate      = simSettings.channel.approximate
    PDF = simResults.eyeGeneration.PDF
    
    # Save initial PDF
    newPDF = nothing()
    newPDF.initial = PDF.initial.thru

    # Don't cross-talk if desired
    if simSettings.channel.addCrossTalk:
        newPDF.crossTalk = nothing()
            
        # Loop through each transition
        transitions = PDF.initial.thru.__dict__
        for transName in transitions:

            # Set main channel distribution
            newPDF.crossTalk.__dict__[transName] = PDF.initial.thru.__dict__[transName]

            # Loop through each channel except main channel
            for chName in PDF.initial.__dict__:

                # Skip required channels
                if(approximate):
                    if chName != 'xtalk':
                        continue
                    
                else:
                    if chName == 'thru' or chName == 'next' or chName == 'fext' or chName == 'xtalk':
                        continue

        
                # Combine all main cursor levels of inteference channel
                disturbance = np.zeros((yAxisLength,samplesPerSymb))
                for levelName in transitions:
                    disturbance = disturbance + PDF.initial.__dict__[chName].__dict__[levelName]
                
                
                # Make channel asnychronous if desired
                if makeAsynchronous:
                    disturbance = makeAsynch(disturbance,samplesPerSymb,yAxisLength)
                

                # Loop through each sample
                temp = []
                for time in range(samplesPerSymb):

                    # Convolute channels together
                    tmpDist = np.convolve(newPDF.crossTalk.__dict__[transName][:,time], disturbance[:,time])

                    # Normalize distribution
                    total = np.sum(tmpDist)
                    if total!=0:
                        tmpDist = tmpDist/total
                    
                    
                    # Size convolution to match yAxis length
                    if temp == []:
                        temp = tmpDist[int((len(tmpDist)-yAxisLength)/2) : int(-(len(tmpDist)-yAxisLength)/2)] 
                    else:
                        temp = np.vstack((temp, tmpDist[int((len(tmpDist)-yAxisLength)/2) : int(-(len(tmpDist)-yAxisLength)/2)]))
                
                newPDF.crossTalk.__dict__[transName] = np.transpose(temp)
        

    # Save results
    simResults.eyeGeneration.PDF = newPDF


###########################################################################
# This function turns a channel distribution into an asynchronous 
# distribution. For each level, it sums the probability at each time 
# instance, normalizes the summation and then sets all time instance to the
# same distribution.
###########################################################################
def makeAsynch(syncChannel,samplesPerSymb,yAxisLength):

    # Sum all time instance probabilities
    asyncChannel = np.zeros((yAxisLength,samplesPerSymb))
    for level in range(yAxisLength):
        for time in range(samplesPerSymb):
            asyncChannel[level,1] = asyncChannel[level,1] + syncChannel[level,time]
    
    # Normalize the new distribution
    asyncChannel[:,1] = asyncChannel[:,1]/np.sum(asyncChannel[:,1])
    
    # Set the same distribution at all time instances
    for time in range(samplesPerSymb):
        asyncChannel[:,time] = asyncChannel[:,1]
    
    return asyncChannel

###########################################################################
# This function adds distortion to the probability distribution which
# models non-linear transfer functions and saturates high amplitude
# levels. If the output mapping lies between two levels, a portion is
# distributed between both levels.
###########################################################################
def applyDistortion(simSettings: simulationSettings, simResults: simulationStatus):

    # Apply distortion only if desired
    if not simSettings.transmitter.distortion.addDistortion and not simSettings.receiver.distortion.addDistortion: return 
        
    # Import variables
    samplesPerSymb = simSettings.general.samplesPerSymb.value
    yAxis          = simSettings.general.yAxis.value
    yAxisLength    = simSettings.general.yAxisLength.value
    distortion = simResults.influenceSources.totalDistortion.output
    PDF        = simResults.eyeGeneration.PDF

    # Chose last created plot
    plots = list(PDF.__dict__)
    plotName = plots[-1]

    PDF.distorted = nothing()

    # Loop through each transition
    transitions = list(PDF.__dict__[plotName].__dict__)
    for transName in transitions:

        # Initialize distorted PDF
        PDF.distorted.__dict__[transName] = np.zeros((yAxisLength,samplesPerSymb))

        # Apply distortion
        for level in range(yAxisLength):
            newLevel = distortion[level]
            newLevel = max([newLevel,min(yAxis)])
            newLevel = min([newLevel,max(yAxis)])
            newIdx = np.interp(newLevel, yAxis, np.arange(yAxisLength))
            upper = np.mod(newIdx,1)
            lower = 1-upper
            PDF.distorted.__dict__[transName][int(np.ceil(newIdx)),:] = \
                PDF.distorted.__dict__[transName][int(np.ceil(newIdx)),:] + \
                PDF.__dict__[plotName].__dict__[transName][level,:] * upper
            PDF.distorted.__dict__[transName][int(np.floor(newIdx)),:] = \
                PDF.distorted.__dict__[transName][int(np.floor(newIdx)),:] + \
                PDF.__dict__[plotName].__dict__[transName][level,:] * lower

    # Save results
    simResults.eyeGeneration.PDF = PDF


###########################################################################
# This function applies jitter to the distribution histogram by convolving
# the distribution with a jitter PDF horizontally.
###########################################################################
def applyJitter(simSettings: simulationSettings, simResults: simulationStatus):

    # Add jitter only if desired
    if not simSettings.transmitter.jitter.addJitter and \
            not simSettings.receiver.jitter.addJitter:
        return 
    
    
    # Import variables
    samplesPerSymb = simSettings.general.samplesPerSymb.value
    yAxisLength    = simSettings.general.yAxisLength.value
    xAxis          = simSettings.general.xAxisCenter.value
    jitter = simResults.influenceSources.totalJitter.totalJitter
    PDF    = simResults.eyeGeneration.PDF
    
    # Use last created plot
    plots = list(PDF.__dict__)
    plotName = plots[-1]

    PDF.jitter = nothing()

    # Loop through each transition
    transitions = PDF.__dict__[plotName].__dict__
    for transName in transitions:

        # Convolve PDF with total jitter
        combPDF = np.hstack((PDF.__dict__[plotName].__dict__[transName], PDF.__dict__[plotName].__dict__[transName], PDF.__dict__[plotName].__dict__[transName])) # add adjacent PDFs to ensure no discontinuities
        
        temp = np.convolve(combPDF[0,:], jitter) # Used for sizing
        PDF.jitter.__dict__[transName] = np.zeros((yAxisLength, len(temp)))

        for index in range(yAxisLength):
            PDF.jitter.__dict__[transName][index,:] = np.convolve(combPDF[index,:], jitter)

        # Limit length to 1 symbol length
        lengthDiff = np.size(PDF.jitter.__dict__[transName],1)-samplesPerSymb
        if lengthDiff != 0:
            # Trim to middle section
            trimmedRegionStart = int(lengthDiff/2)
            trimmedRegionEnd = int(np.size(PDF.jitter.__dict__[transName],1)-lengthDiff/2)
            PDF.jitter.__dict__[transName] = PDF.jitter.__dict__[transName][:, trimmedRegionStart:trimmedRegionEnd]
        

        # Ensure distribution adds up to 1 in vertical axis
        for index in range(len(xAxis)-1):
            total = np.sum(PDF.jitter.__dict__[transName][:,index])
            if total !=0:
                PDF.jitter.__dict__[transName][:,index] = PDF.jitter.__dict__[transName][:,index]/total

    # Save results
    simResults.eyeGeneration.PDF = PDF


###########################################################################
# This function applies noise to the distribution by convolving it with
# the noise PDF vertically.
###########################################################################
def applyNoise(simSettings: simulationSettings, simResults: simulationStatus):
 
    # Add noise only if desired
    if not simSettings.transmitter.noise.addNoise and\
            not simSettings.channel.noise.addNoise and\
            not simSettings.receiver.noise.addNoise:
        return 
    
    
    # Import variables
    samplesPerSymb = simSettings.general.samplesPerSymb.value
    yAxisLength    = simSettings.general.yAxisLength.value
    xAxis          = simSettings.general.xAxisCenter.value
    noise = simResults.influenceSources.totalNoise.histogram
    PDF   = simResults.eyeGeneration.PDF
    
    # Chose last created plot
    plots = list(PDF.__dict__)
    plotName = plots[-1]

    PDF.noise = nothing()
        
    # Loop through each transition
    transitions = PDF.__dict__[plotName].__dict__
    for transName in transitions:

        # Convolve PDF with noise
        temp = np.convolve(PDF.__dict__[plotName].__dict__[transName][:,0], noise) # Used for sizing
        PDF.noise.__dict__[transName] = np.zeros((len(temp), samplesPerSymb))

        for index in range(samplesPerSymb):
            PDF.noise.__dict__[transName][:,index] = np.convolve(PDF.__dict__[plotName].__dict__[transName][:,index], noise)
        

        # Limit height to y-axis limits
        heightDiff = np.size(PDF.noise.__dict__[transName],0)-yAxisLength
        if heightDiff != 0:
            # Trim to middle section
            trimmedRegionStart = int(heightDiff/2)
            trimmedRegionEnd = int(np.size(PDF.noise.__dict__[transName],0)-heightDiff/2)
            PDF.noise.__dict__[transName] = PDF.noise.__dict__[transName][trimmedRegionStart:trimmedRegionEnd, :]
        

        # Ensure distribution adds up to 1 in vertical axis
        for index in range(len(xAxis)-1):
            total = np.sum(PDF.noise.__dict__[transName][:,index])
            if total != 0:
                PDF.noise.__dict__[transName][:,index] = PDF.noise.__dict__[transName][:,index]/total


    # Save results
    simResults.eyeGeneration.PDF = PDF


###########################################################################
# This function combines all main-cursor level PDFs together, used later
# for plotting.
###########################################################################
def combinePDFs(simResults: simulationStatus):

    # Import variables
    PDF = simResults.eyeGeneration.PDF
    
    # Loop through each available plot
    for plotName in PDF.__dict__:
        transitions = list(PDF.__dict__[plotName].__dict__)
        
        if len(transitions) == 0:
            continue # skip any states without transitions
        PDF.__dict__[plotName].combined = np.zeros_like(PDF.__dict__[plotName].__dict__[transitions[0]])
        for transName in transitions:
            PDF.__dict__[plotName].combined = PDF.__dict__[plotName].combined + (PDF.__dict__[plotName].__dict__[transName]/len(transitions))

    # Generate final distribution
    PDF.final = PDF.__dict__[plotName]
    
    # Save results
    simResults.eyeGeneration.PDF = PDF
