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
# This function generates an eye diagram due to ISI in the pulse 
# response. It does this by first splitting up the pulse response into 
# individual cursors, it then determine all combinations of pre, main and 
# post cursor data levels and multiplies the pulse response by the
# combination, finally it superimposes the summation of each combination,
# creating several signal traces resembling an eye diagram. 
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

def generateISI(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    signalingMode   = simSettings.general.signalingMode
    samplesPerSymb  = simSettings.general.samplesPerSymb.value
    modulation      = simSettings.general.modulation.value
    levelNumb       = simSettings.general.levelNumb.value
    preCursorCount  = simSettings.transmitter.preCursorCount.value
    postCursorCount = simSettings.transmitter.postCursorCount.value
    cursorCount     = simSettings.transmitter.cursorCount.value  
    approximate     = simSettings.channel.approximate
    speedUpSim      = simSettings.adaption.speedUpSim
    pulses = simResults.pulseResponse.receiver.outputs

    result = nothing()
    transitions = 0

    # Break if simulation has already failed
    if not simResults.results.successful: return 
    
    if speedUpSim:
        # Take previous results if repeat simulation
        transitions = simResults.eyeGeneration.ISI.thru
    else:
        # Determine all cursor combinations
        combinations = generateCursorCombinations(cursorCount,signalingMode,modulation,levelNumb)
        
        # Clasify ISI trajectories classified by transition
        transitions = clasifyTrajectories(combinations,preCursorCount,signalingMode)
    
    
    # Loop through each available channel file
    for chName in pulses.__dict__:
        
        # Skip required channels
        if approximate:
            if chName != 'thru' and chName != 'xtalk':
                continue
        else:
            if chName == 'next' or chName == 'fext' or chName == 'xtalk':
                continue
            
        
        # Split pulse into symbol portions
        splitPul = splitPulse(pulses.__dict__[chName],preCursorCount,postCursorCount,samplesPerSymb)

        # Apply cursor combinations to the split pulse response
        result.__dict__[chName] = applyCursorCombination(transitions,splitPul,samplesPerSymb)
    
    
    # Save results
    simResults.eyeGeneration.ISI = result


###########################################################################
# The following functions returns a structure containing all possible 
# cursor combinations. The number of levels is dictated by the modulation 
# scheme and the number of cursors. If a signaling mode such as QAM is
# selected, combinations which do not have DC components will be created.
###########################################################################
def generateCursorCombinations(cursorCount,signalingMode,modulation,levelNumb):
    ISI = nothing()

    # Create combinations with DC component
    if signalingMode == 'standard' or signalingMode == '1+D' or signalingMode == '1+0.5D':
        for combination in range(modulation**cursorCount):
            baseM = np.base_repr(combination, base=modulation) # create base-M value from combination

            vector = np.zeros((cursorCount-len(baseM),))
            for number in baseM:
                vector = np.concatenate((vector, [float(number)]))

            symbolName = 'c'
            for number in vector:
                symbolName = '{0:s}{1:d}'.format(symbolName, int(number))

            polar = np.interp(vector, [0, modulation-1], [-1,1]) # gets polar [-1 1] base-M vector
            setattr(ISI, symbolName, nothing())
            ISI.__dict__[symbolName].cursors = polar
        
            
    # Create combinations without DC component
    else:
        for level in range(levelNumb):
            vector = np.ones((cursorCount,))*level
            for index in np.arange(1,cursorCount, 2):
                vector[index] = levelNumb-1-vector[index] # invert every other bit
            
            polar = np.interp(vector, [0,levelNumb-1],[-1,1]) # gets polar [-1 1] base-M vector

            symbolName = 'c'
            for number in vector:
                symbolName = '{0:s}{1:d}'.format(symbolName, int(number))

            setattr(ISI, symbolName, nothing())
            ISI.__dict__[symbolName].cursors = polar
        
    return ISI


###########################################################################
# This function classifies all trajectories based on the pre, main and post
# cursor transitions. All three are required for generating edge BER plots.
# It should be noted that the order of cursors is reversed to account for
# time.
###########################################################################
def clasifyTrajectories(ISI,preCursorCount,signalingMode):
    
    classifiedISI = nothing()

    for name in ISI.__dict__:
        preCursor  = name[preCursorCount+1]
        mainCursor = name[preCursorCount+2]
        postCursor = name[preCursorCount+3]
        if signalingMode == '1+D' or signalingMode == '1+0.5D':
            if not ('trans'+postCursor+mainCursor) in classifiedISI.__dict__:
                setattr(classifiedISI, ('trans'+postCursor+mainCursor), nothing())
            if not name in classifiedISI.__dict__[('trans'+postCursor+mainCursor)].__dict__:
                setattr(classifiedISI.__dict__[('trans'+postCursor+mainCursor)], name, nothing())
            classifiedISI.__dict__[('trans'+postCursor+mainCursor)].__dict__[name].cursors = ISI.__dict__[name].cursors
        else:
            if not ('trans'+postCursor+mainCursor+preCursor) in classifiedISI.__dict__:
                setattr(classifiedISI, ('trans'+postCursor+mainCursor+preCursor), nothing())
            if not name in classifiedISI.__dict__[('trans'+postCursor+mainCursor+preCursor)].__dict__:
                setattr(classifiedISI.__dict__[('trans'+postCursor+mainCursor+preCursor)], name, nothing())
            classifiedISI.__dict__[('trans'+postCursor+mainCursor+preCursor)].__dict__[name].cursors = ISI.__dict__[name].cursors
        
    return classifiedISI


###########################################################################
# This function splits the pulse response into symbols and returns them
# in a structure categorized by name.
###########################################################################
def splitPulse(pulse,preCursorCount,postCursorCount,samplesPerSymb):

    splitPulse = nothing()
    # Split pre-cursors
    index = 0
    for cursor in np.arange(preCursorCount, 0, -1):
        splitPulse.__dict__['pre' + str(cursor)] = pulse[index:index+samplesPerSymb]
        index = index+samplesPerSymb
    
    
    # Split main-cursor(s)
    splitPulse.__dict__['main'] = pulse[index:index+samplesPerSymb]
    index = index+samplesPerSymb
    
    # Split post-cursors
    for cursor in range(postCursorCount):
        splitPulse.__dict__['post'+str(cursor)] = pulse[index:index+samplesPerSymb]
        index = index+samplesPerSymb
    
    return splitPulse


###########################################################################
# This function applies the cursor combinations to the split pulse 
# response. This creates all possible signal trajectories due to ISI.
###########################################################################
def applyCursorCombination(ISI,splitPulse,samplesPerSymb):

    # Loop through transitions
    cursors = list(splitPulse.__dict__)
    for transName in ISI.__dict__:

        # Loop through combinations
        for comb in ISI.__dict__[transName].__dict__:
            
            # Loop through cursors while superimposing transformation
            vector = ISI.__dict__[transName].__dict__[comb].cursors
            ISI.__dict__[transName].__dict__[comb].trajectory = np.zeros((samplesPerSymb,))
            
            for pos in range(len(vector)):
                offset = splitPulse.__dict__[cursors[pos]]*vector[pos] # multiply cursor by data levels
                ISI.__dict__[transName].__dict__[comb].trajectory = ISI.__dict__[transName].__dict__[comb].trajectory+offset
            
    return ISI    
    
