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
# This function generates the final simulation results. It determines the
# data levels and measures the eye openings.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
#   
###########################################################################

from userSettingsObjects import simulationSettings, nothing
from initializeSimulation import simulationStatus
import numpy as np
import scipy.signal as spsig

def generateResults(simSettings: simulationSettings, simResults: simulationStatus):

    # Measure data levels
    measureDataLevs(simSettings, simResults)
    
    # Measure eye openning
    measureEyeSizes(simSettings, simResults)
    
    # Measure eye position
    measureEyePositions(simSettings, simResults)
    
    # Measure channel operating margin
    measureCOM(simResults)


###########################################################################
# This function finds the location of each data level. It does so by
# setting the minimum peak spacing at 2. This spacing is increased until
# the correct number of data peaks is observed.
###########################################################################
def measureDataLevs(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    yAxis       = simSettings.general.yAxis.value
    yAxisLength = simSettings.general.yAxisLength.value
    levelCount  = simSettings.general.levelNumb.value
    successful = simResults.results.successful
    
    if successful:
        
        PDF = simResults.eyeGeneration.PDF.final.combined
        BER = simResults.eyeGeneration.BER
    
        # Find data levels
        try:
            spacing = 2
            locations, prop = spsig.find_peaks(PDF[:,BER.eyeLocs.X], distance=spacing)
            while(len(locations)>levelCount):
                spacing = spacing+2
                locations, prop = spsig.find_peaks(PDF[:,BER.eyeLocs.X], distance=spacing)
            
            if len(locations) != levelCount:
               print('Warning: Cannot find data levels!')
               successful = False
            
        except:
            locations = np.ceil(np.ones((levelCount,))*yAxisLength/2)
            successful = False
        
    else:
        locations = np.ceil(np.ones((levelCount,))*yAxisLength/2)
    
    
    # Get values
    dLevs = np.zeros_like(locations, dtype=float)
    for interation, loc in enumerate(locations):
        dLevs[interation] = yAxis[int(loc)]

    # Save results
    simResults.results.dLevs = dLevs
    simResults.results.successful = successful


###########################################################################
# This function determines the eye dimensions.
###########################################################################
def measureEyeSizes(simSettings: simulationSettings, simResults: simulationStatus):

    # Import variables
    samplePeriod = simSettings.general.samplePeriod.value
    symbolPeriod = simSettings.general.symbolPeriod.value
    yIncrement   = simSettings.general.yIncrement.value
    targetBER    = simSettings.general.targetBER.value
    eyeLocs    = simResults.eyeGeneration.BER.eyeLocs
    bathTubX   = simResults.eyeGeneration.BER.bathTubX
    bathTubY   = simResults.eyeGeneration.BER.bathTubY
    successful = simResults.results.successful
    
    BER = targetBER
    eyeDims = nothing()

    if successful:
       
        # Find worst BER eye
        BER = targetBER
        for index in range(len(eyeLocs.Y)):
            BER = np.maximum(BER, bathTubY[eyeLocs.Y[index]])
        

        # Find height and width of each eye
        for eye in range(len(eyeLocs.Y)):

            # Get labels for common datapoints
            tubLabel = 'tub' + str(eye)
            eyeLabel = 'eye' + str(eye)

            # Set in middle of eye
            top = eyeLocs.Y[eye]
            bottom = eyeLocs.Y[eye]
            right = eyeLocs.X
            left = eyeLocs.X

            # Find size of each eye
            while bathTubY[top]<BER and top<(len(bathTubY)-1): top = top+1 
            while bathTubY[bottom]<BER and bottom>0: bottom = bottom-1 
            while bathTubX.__dict__[tubLabel][right]<BER and right<(len(bathTubX.__dict__[tubLabel])-1): right = right+1 
            while bathTubX.__dict__[tubLabel][left]<BER and left>0: left = left-1 
            height = (top-bottom)*yIncrement
            width = (right-left)*samplePeriod
            widthUI = width/symbolPeriod
            area = height*width
            eyeDims.__dict__[eyeLabel] = nothing()
            eyeDims.__dict__[eyeLabel].height = height
            eyeDims.__dict__[eyeLabel].width = width
            eyeDims.__dict__[eyeLabel].widthUI = widthUI
            eyeDims.__dict__[eyeLabel].area = area

            # Ensure not a false reading
            if top == len(bathTubY) or bottom==0:
                successful = False
                print('Warning: Cannot determine eye limits.')

    else:
        # Default eyedims
        eyeDims.eye0 = nothing()
        eyeDims.eye0.height = 0
        eyeDims.eye0.width = 0
        eyeDims.eye0.widthUI = 0
        eyeDims.eye0.area = 0
        
    

    # Save results
    simResults.results.BER = BER
    simResults.results.eyeDimensions = eyeDims
    simResults.results.successful = successful


###########################################################################
# This function takes the pre-calculated eye positions and converts the
# vales to voltage, time and phase
###########################################################################
def measureEyePositions(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    yAxis          = simSettings.general.yAxis.value
    xAxis          = simSettings.general.xAxisCenter.value
    samplePeriod   = simSettings.general.samplePeriod.value
    samplesPerSymb = simSettings.general.samplesPerSymb.value
    successful = simResults.results.successful
    
    # Calculate position
    level = 0
    time = 0
    phase = 0

    if successful:
        eyeLocs = simResults.eyeGeneration.BER.eyeLocs
        level = np.zeros_like(eyeLocs.Y, dtype=float)
        for iter, loc in enumerate(eyeLocs.Y):
            level[iter] = yAxis[loc]
        time = xAxis[eyeLocs.X]
        phase = round(time/(samplePeriod*samplesPerSymb)*360, 1)
    
    # Save results
    simResults.results.eyeLocs = nothing()
    simResults.results.eyeLocs.level = level
    simResults.results.eyeLocs.time = time
    simResults.results.eyeLocs.phase = phase


###########################################################################
# This function measures the channel operating margin. The BER is set from
# setting.
###########################################################################
def measureCOM(simResults: simulationStatus):

    # Import variables
    dLevs = simResults.results.dLevs
    eyes = simResults.results.eyeDimensions
    successful = simResults.results.successful

    # Calculate only if successful
    com = -1e3 # set default very negative (no eye openning)
    if successful:
        eyeNames = eyes.__dict__
        
        # Loop through eyes
        for index in range(len(eyeNames)):
            
            # Calculate COM for eye
            signalHeight = dLevs[index+1]-dLevs[index]
            eyeHeight = eyes.__dict__['eye' + str(index)].height
            noiseHeight = signalHeight-eyeHeight
            comTmp = 20*np.log10(signalHeight/noiseHeight)
            
            # Save worst COM
            if index == 0 or comTmp < com: com = comTmp 
    
    # Save results
    simResults.results.com = com
