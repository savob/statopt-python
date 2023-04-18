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
# This function updates the adaption simulation. This algorithm has three 
# modes. The first allows for a wide range of random children. The second 
# restricts the randomness to likely candidates. The third resets general 
# settings to the user's specifications and run the optimal solution.
#
# IMPORTANT: to increase adaption speed, the modulation scheme and cursor
# count is temporarily reduced. As a result, the optimal log results may
# not coincide with the final result.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
#
# Outputs:
#   simSettings: structure containing simualation settings
#   simResults: structure containing simulation results
#   
###########################################################################

from userSettingsObjects import simulationSettings
from initializeSimulation import simulationStatus
import matplotlib.pyplot as plt
import numpy as np
import random
import copy
import functools

class nothing:
    def __init__(self):
        pass


def adaptLink(simSettings, simResults):

    # Determine whether to adapt
    if simSettings.adaption.adapt:

        # Add adaption structure if first run
        initializeAdaptionStructure(simSettings, simResults)
        
        # Generate new results
        extractNewResults(simSettings, simResults)
        
        # Compare results
        simResults.adaption.optimalResult, isOptimal = compareResults(simResults.adaption.currentResult,simResults.adaption.optimalResult)
        
        # Log result
        logResults(simResults)
        
        # Decide next action
        decideNextAction(simSettings, simResults)
        
        # Display results
        displayResult(simSettings, simResults, isOptimal)
    else:
        simResults.finished = True

###########################################################################
# This function is used to set a nested field in an object based on a 
# string broken by periods to describe fields. 
###########################################################################
def rsetattr(obj, attr, val):
    # Using partition to check if we are at the base or not
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val) # Get the attribute tree if there is a pre section

# using wonder's beautiful simplification: https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-objects/31174427?noredirect=1#comment86638618_31174427

###########################################################################
# This function is used to retirieve values from an object based on a 
# string broken by periods to describe fields
###########################################################################
def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))

###########################################################################
# This function initializes the adaption results structure in memory.
###########################################################################
def initializeAdaptionStructure(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Initialize structure only if it does not already exist
    if 'adaption' in simResults.__dict__: return

    simResults.adaption = nothing()
    
    # Chose a new random seed
    random.seed()

    # Initialize the log structure
    #generateNewLog(simSettings,simResults)
    simResults.adaption.log = []
    
    # Initialize optimal result
    simResults.adaption.optimalResult = nothing()
    simResults.adaption.optimalResult.name = 'default'
    simResults.adaption.optimalResult.results = nothing()
    simResults.adaption.optimalResult.results.BER = 1
    simResults.adaption.optimalResult.results.minEyeHeight = 0
    simResults.adaption.optimalResult.results.minEyeWidth = 0
    simResults.adaption.optimalResult.results.minEyeArea = 0
    simResults.adaption.optimalResult.successful = False
    
    # Get current knob settings
    knobs = simSettings.adaption.knobs
    knobValues = nothing()
    for knobPath in knobs:
        validName = str(knobPath).replace('.', '_')
        knobValues.__dict__[validName] = rgetattr(simSettings, str(knobPath)+'.value')
    
    
    # Initialize current result
    simResults.adaption.currentResult = nothing()
    simResults.adaption.currentResult.name = 'initialCandidate'
    simResults.adaption.currentResult.knobs = knobValues
    
    # Initialize generation structure
    simResults.adaption.generations = nothing()
    simResults.adaption.generationNumb = 1
    
    # Initialize other parameters
    simResults.adaption.adaptMode = 1
    simResults.adaption.simNumb = 1
    
# Class used for log entries
class logEntry:
    simNumb: int
    adaptMode: int
    generationNumb: int
    candidateName: str
    currentBER: float
    currentEyeHeight: float
    optimalBER: float
    optimalEyeHeight: float
    successful: bool
    
    
    def __init__(self, sn: int, am: int, gn:int, cn: str, cber: float, ceh: float, ober: float, oeh: float, suc: bool):
        self.simNumb = sn
        self.adaptMode = am
        self.generationNumb = gn
        self.candidateName = cn
        self.currentBER = cber
        self.currentEyeHeight = ceh
        self.optimalBER = ober
        self.optimalEyeHeight = oeh
        self.successful = suc

###########################################################################
# This function creates a new log file by defining headings with empty
# values.
###########################################################################
def generateNewLog(simSettings: simulationSettings, simResults: simulationStatus):

    # Create sim number headings
    log = logEntry(0,0,0,'',0,0,0,0,False)
    
    # Create knob headings
    knobs = simSettings.adaption.knobs
    for knobPath in knobs:
        validName = str(knobPath).replace('.', '_')
        log.__dict__[validName] = ''

    # Save results
    simResults.adaption.log = log


###########################################################################
# This function extracts important data from the simulation results. It
# also determines solution health criteria such as BER and minimum eye 
# height.
###########################################################################
def extractNewResults(simSettings: simulationSettings, simResults: simulationStatus):

    # Import variables
    samplesPerSymb  = simSettings.general.samplesPerSymb.value
    signalingMode   = simSettings.general.signalingMode
    preCursorCount  = simSettings.transmitter.preCursorCount.value
    postCursorCount = simSettings.transmitter.postCursorCount.value
    supplyVoltage   = simSettings.receiver.signalAmplitude.value
    successful    = simResults.results.successful
    pulse         = simResults.pulseResponse.receiver.outputs.thru
    results       = simResults.results
    generations   = simResults.adaption.generations
    currentResult = simResults.adaption.currentResult
    genNumb       = simResults.adaption.generationNumb

    if successful:
        
        # Estimate signal height
        peakLoc = np.argmax(np.abs(pulse))
        match signalingMode: 
            case '1+D':
                startIdx = round(peakLoc-(preCursorCount+0.5)*samplesPerSymb)
                endIdx = round(peakLoc+(postCursorCount-0.5)*samplesPerSymb)
            case '1+0.5D':
                startIdx = round(peakLoc-(preCursorCount+1/6)*samplesPerSymb)
                endIdx = round(peakLoc+(postCursorCount-1/6)*samplesPerSymb)
            case _:
                startIdx = round(peakLoc-preCursorCount*samplesPerSymb)
                endIdx = round(peakLoc+postCursorCount*samplesPerSymb)
        
        startIdx = np.max([startIdx, 0])
        endIdx = np.min([endIdx, len(pulse)-1])
        cursorSum = 0
        for index in np.arange(startIdx, endIdx, samplesPerSymb):
            cursorSum = cursorSum + np.abs(pulse[index])
        
        # Ensure signal not saturated
        if cursorSum>supplyVoltage:
            print('WARNING: input amplitude too large!')
            successful = False
        
        
        # Ensure 1+0.5D scheme is not 0.5+D
        if signalingMode == '1+0.5D':
            main1 = pulse((preCursorCount+0.5)*samplesPerSymb)
            main2 = pulse((preCursorCount+1.5)*samplesPerSymb)
            if np.abs(main2)>np.abs(main1):
                print('WARNING: second main-cursor larger than first!')
                successful = False
            
        
        
        # Ensure no excessive phase offset
        if np.abs(results.eyeLocs.phase)>45:
            print('WARNING: phase offset too large!')
            successful = False
        
        
        # Determine min eye size
        eyes = list(results.eyeDimensions.__dict__)
        results.minEyeHeight = results.eyeDimensions.__dict__[eyes[0]].height
        results.minEyeWidth = results.eyeDimensions.__dict__[eyes[0]].width
        results.minEyeArea = results.eyeDimensions.__dict__[eyes[0]].area
        for eye in range(2, len(eyes)+1):
            eyeName = eyes[eye]
            results.minEyeHeight = np.min(results.minEyeHeight,results.eyeDimensions.__dict__[eyeName].height)
            results.minEyeWidth = np.min(results.minEyeWidth,results.eyeDimensions.__dict__[eyeName].width)
            results.minEyeArea = np.min(results.minEyeArea,results.eyeDimensions.__dict__[eyeName].area)
    
    # Set worst case result if unsuccessful
    if not successful:
        results.minEyeHeight = 0
        results.minEyeWidth = 0
        results.minEyeArea = 0
        results.BER = 1
    

    # Update current setting
    currentResult.results = results
    currentResult.successful = successful
    currentResult.simulated = True
    
    # Update generation
    if 'generation' + str(genNumb) not in generations.__dict__:
        generations.__dict__['generation' + str(genNumb)] = nothing()
    generations.__dict__['generation' + str(genNumb)].__dict__[currentResult.name] = currentResult
    
    # Save results
    simResults.adaption.currentResult = currentResult
    simResults.adaption.generations = generations


###########################################################################
# This function compares the new results to the previous optimal one. If
# the new result is better, the optimal result will be replaced. The
# solution with the lowest BER is selected. If both have the same BER, the
# solution with the tallest minimum eye will be selected.
###########################################################################
def compareResults(newResult, oldResult):
    
    # Load results
    newBER        = newResult.results.BER
    newHeight     = newResult.results.minEyeHeight
    newSuccessful = newResult.successful
    oldBER        = oldResult.results.BER
    oldHeight     = oldResult.results.minEyeHeight
    oldSuccessful = oldResult.successful
    
    # Compare results
    if newSuccessful and ((not oldSuccessful) or newBER<oldBER or (newBER==oldBER and newHeight>oldHeight)):
        bestResult = copy.deepcopy(newResult)
        isBetter = True
    else:
        bestResult = copy.deepcopy(oldResult)
        isBetter = False
    
    return bestResult, isBetter


###########################################################################
# This function saves the current adaption settings and status to the log
# structure.
###########################################################################
def logResults(simResults):

    # Import variables
    currentResult  = simResults.adaption.currentResult
    log            = simResults.adaption.log
    simNumb        = simResults.adaption.simNumb
    generationNumb = simResults.adaption.generationNumb
    optimalResult  = simResults.adaption.optimalResult
    adaptMode      = simResults.adaption.adaptMode

    # Add other results
    row = logEntry(simNumb, adaptMode, generationNumb, currentResult.name, \
                currentResult.results.BER, currentResult.results.minEyeHeight, \
                optimalResult.results.BER, optimalResult.results.minEyeHeight, currentResult.successful)

    # Add knob settings
    knobs = currentResult.knobs.__dict__
    for name in knobs:
        row.__dict__[name] = currentResult.knobs.__dict__[name]

    # Save to log
    simResults.adaption.log.append(row)
    


###########################################################################
# This function displays the current state of all knob settings for the 
# transmitter and receiver. If a new optimal is discovered, this also
# notifies the user.
###########################################################################
def displayResult(simSettings: simulationSettings, simResults: simulationStatus, newOptimal: bool):

    # Import variables
    totalSimulations = simSettings.adaption.totalSimulations.value
    finished         = simResults.finished
    currentResult    = simResults.adaption.currentResult
    optimalResult    = simResults.adaption.optimalResult
    simNumb          = simResults.adaption.simNumb    
            
    # Notify user of new optimal from previous round (colored red)
    if newOptimal:
        print('--New Optimal Found!--')
        print('Optimal BER: {0:.1e}'.format(optimalResult.results.BER))
        print('Optimal Eye height: {0:.2f}'.format(optimalResult.results.minEyeHeight))
    
    
    # Display current setting
    if not finished:
        if currentResult.name == 'finalCandidate':
            print('----------Generating Final Plots----------')
        else:
            print('\n----------Adaption {0:d}/~{1:d}----------'.format(simNumb, totalSimulations))
        
        headings = currentResult.knobs.__dict__
        for heading in headings:
            if heading != 'receiver_preAmp_gain' and heading != 'receiver_FFE_taps_main':
                value = currentResult.knobs.__dict__[heading]
                if value > 1e3:
                    print('{0:s}: {1:.2e}'.format(heading,value))
                else:
                    print('{0:s}: {1:.2f}'.format(heading,value))

        
###########################################################################
# This function determines the next course of action for the adaption
# algorithm. It will either chose a new set generation child or will create
# a new generation. For the final pass, the optimal solution will be run 
# and the simulation will be terminated.
###########################################################################
def decideNextAction(simSettings: simulationSettings, simResults: simulationStatus):
    
    # First pass through
    if simResults.adaption.simNumb == 1:
        checkIncrementMode(simSettings, simResults)
        createNewGeneration(simSettings, simResults)
        displayResult(simSettings, simResults, False)
        if 'receiver_preAmp_gain' in simResults.adaption.currentResult.knobs.__dict__:
            print('receiver_preAmp_gain: {0:.2f}'.format(simResults.adaption.currentResult.knobs.receiver_preAmp_gain))
        
        simSettings.adaption.speedUpSim = True
        
        # Initial condition unsuccessful, ask if to try again
        if not simResults.adaption.currentResult.successful:
            #beep
            answer = input('Would you like the adaption to continue without an initial condition? (Y/N) ')
            if not (answer == 'y' or answer == 'Y'):
                print('----------Simulation Canceled----------')
                quit()
    
    # Increment simulation run count
    simResults.adaption.simNumb = simResults.adaption.simNumb + 1
    
    # Running adaption while not mode 3
    if not simResults.adaption.adaptMode == 3:
        
        # Pick a new candidate
        finished = pickNewCandidate(simSettings, simResults)

        # Current generation finished
        if finished:
            simResults.adaption.generationNumb = simResults.adaption.generationNumb+1
            checkIncrementMode(simSettings, simResults)
            
            # Create new generation
            if not simResults.adaption.adaptMode == 3:
                createNewGeneration(simSettings, simResults) 
                pickNewCandidate(simSettings, simResults)
                
            # Run once more to set optimal result
            else:
                setOptimal(simSettings, simResults)
                simSettings.adaption.speedUpSim = False
        
        # Reset success flag
        simResults.results.successful = True
    else:
        simResults.finished = True
    


###########################################################################
# This function checks to see if the adaption mode should be incremented.
###########################################################################
def checkIncrementMode(simSettings: simulationSettings, simResults: simulationStatus):

    # Import variables
    mode1Generations  = simSettings.adaption.mode1Generations.value
    mode2Generations  = simSettings.adaption.mode2Generations.value
    generationNumb = simResults.adaption.generationNumb
    adaptMode      = simResults.adaption.adaptMode
        
    # Determine mode change
    if adaptMode == 1 and generationNumb > mode1Generations:
        adaptMode = 2
    
    if adaptMode == 2 and generationNumb > mode1Generations+mode2Generations:
        adaptMode = 3

    # Save results
    simResults.adaption.adaptMode = adaptMode


###########################################################################
# This function kills the previous generation while keeping the desired
# amount of optimal parents. It then creates a new set of children and
# mutations.
###########################################################################
def createNewGeneration(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    totalPopulation   = simSettings.adaption.totalPopulation.value
    totalParents      = simSettings.adaption.totalParents.value
    childrenPerParent = simSettings.adaption.childrenPerParent.value
    adaptMode      = simResults.adaption.adaptMode
    generations    = simResults.adaption.generations
    generationNumb = simResults.adaption.generationNumb
    log            = simResults.adaption.log
    
    # Kill unsuccessfull simulations
    generations = killUnsuccessfullSims(generations, generationNumb)

    # Remove duplicate solutions
    generations = killDuplicates(simSettings, generations, generationNumb)
    
    # Kill all but optimal solutions
    generations = killOldGeneration(generations, generationNumb, totalParents)
    
    # Change survivors to parents
    generations = renameSurvivors(generations, generationNumb)
    
    # Add children to generation
    generations = createChildren(simSettings, generations,generationNumb, childrenPerParent, totalParents, adaptMode, log)
    
    # Add mutations to generation
    generations = createMutations(simSettings, generations, generationNumb, totalPopulation, log)
    
    # Save results
    simResults.adaption.generations = generations


###########################################################################
# This function kills all solutions which did not simulate successfully.
###########################################################################
def killUnsuccessfullSims(generations, genNumb):

    newGeneration = nothing()
    oldGeneration = generations.__dict__['generation' + str(np.max([genNumb-1, 1]))]
    oldPeople = list(oldGeneration.__dict__)
    for oldPersonName in oldPeople:
        if oldGeneration.__dict__[oldPersonName].successful:
            newGeneration.__dict__[oldPersonName] = oldGeneration.__dict__[oldPersonName]
    
    generations.__dict__['generation' + str(genNumb)] = newGeneration

    return generations


###########################################################################
# This fuction checks all solutions to ensure no two have the same knob 
# settings. If so, it removes one of them.
###########################################################################
def killDuplicates(simSettings,generations,genNumb):
    
    currGeneration = generations.__dict__['generation'+str(genNumb)]
    people = list(currGeneration.__dict__)
    if len(people) > 1:
        
        # Create remove list
        removeList = []
        knobs = simSettings.adaption.knobs
        for reference, refName in enumerate(people):
            refName = people[reference]
            different = False
            for compare in range(reference+1, len(people)):
                compName = people[compare]

                for knobName in knobs:
                    knobName = str(knobName).replace('.','_')
                    if currGeneration.__dict__[refName].knobs.__dict__[knobName] \
                            != currGeneration.__dict__[compName].knobs.__dict__[knobName]:
                        different = True
                        break

                if different: break 
            
            if not different: removeList.append(refName)

        # Remove people on list
        for name in removeList:
            delattr(currGeneration, name)
    
    generations.__dict__['generation' + str(genNumb)] = currGeneration

    return generations


###########################################################################
# This function keeps only the required number of top solutions.
###########################################################################
def killOldGeneration(generations,genNumb,totalParents):
    
    currGeneration = generations.__dict__['generation'+str(genNumb)]
    people = list(currGeneration.__dict__)
    while len(people)>totalParents:
        worstPersonName = people[0]
        worstResult = currGeneration.__dict__[worstPersonName]
        for index in range(1, len(people)):
            newPersonName = people[index]
            isBetter = compareResults(currGeneration.__dict__[newPersonName],worstResult)
            if not isBetter: worstResult = currGeneration.__dict__[newPersonName]
        
        delattr(currGeneration, worstResult.name)
        people = list(currGeneration.__dict__)
    
    generations.__dict__['generation'+str(genNumb)] = currGeneration # Might not be needed due to passing by reference

    return generations


###########################################################################
# This function renames all remaining people to ensure they are all parents
# and are listed in order. To ensure solutions are not overwritten, all are
# renamed first to 'instance' and then 'parent'.
###########################################################################
def renameSurvivors(generations,genNumb):

    # Rename all to 'instance'
    currGeneration = generations.__dict__['generation'+str(genNumb)]
    people = list(currGeneration.__dict__)
    for index, personName in enumerate(people):
        currGeneration.__dict__['instance'+str(index)] = currGeneration.__dict__[personName]
        delattr(currGeneration, personName)
    
    
    # Rename all to 'parent'
    people = list(currGeneration.__dict__)
    for index, personName in enumerate(people):
        currGeneration.__dict__['parent'+str(index)] = currGeneration.__dict__[personName]
        currGeneration.__dict__['parent'+str(index)].name = 'parent'+str(index)
        delattr(currGeneration, personName)
    
    generations.__dict__['generation'+str(genNumb)] = currGeneration # Might not be needed due to passing by reference

    return generations


###########################################################################
# This function will create a new child. If a minimum increment is 
# specified, mode 1 will chose a new setting within three values and mode 
# 2 will be within one. To ensure the same knob combination is not 
# resimulated, each combination is compared with previous simulations.
###########################################################################
def createChildren(simSettings,generations,genNumb,childrenPerParent,totalParents,adaptMode,log):
    
    # Determine number of children to add
    currGeneration = generations.__dict__['generation'+str(genNumb)]
    parents = currGeneration.__dict__
    addNumber = childrenPerParent*totalParents+totalParents-len(parents)
    
    # Add children
    knobs = simSettings.adaption.knobs
    for child in range(addNumber):
        
        # Allocate a parent else ignore
        givenParent = int(np.ceil((child+1)/childrenPerParent))
        if ('parent'+str(givenParent)) in currGeneration.__dict__:
            currGeneration.__dict__['child'+str(child)] = nothing()
            currGeneration.__dict__['child'+str(child)].knobs = currGeneration.__dict__['parent'+str(givenParent)].knobs
        
            # Randomize knobs
            for attempt in range(100):
                for knobName in knobs:
                    validName = str(knobName).replace('.','_')

                    # Retrieve knob limits
                    minValue = rgetattr(simSettings, (knobName + '.minValue'))
                    maxValue = rgetattr(simSettings, (knobName + '.maxValue'))
                    increment = rgetattr(simSettings, (knobName + '.increment'))

                    # Set new knob value
                    if knobName == 'receiver.preAmp.gain' or knobName == 'receiver.FFE.taps.main':
                        value = 1 # set automatically
                    else:
                        currentValue = currGeneration.__dict__['child'+str(child)].knobs.__dict__[validName]
                        if adaptMode == 1:
                            value = currentValue + increment * random.randint(-3, 3)
                        else:
                            value = currentValue + increment * random.randint(-1, 1)
                        
                        value = round(value/increment)*increment
                        value = max(min(value,maxValue),minValue)
                    
                    currGeneration.__dict__['child'+str(child)].knobs.__dict__[validName] = value
                
                
                # Ensure knobs meet requirements
                currGeneration.__dict__['child'+str(child)].knobs, goodChild = checkKnobs(currGeneration.__dict__['child'+str(child)].knobs)
            
                # Check knob uniqueness
                goodChild = goodChild & checkUniqueness(currGeneration.__dict__['child'+str(child)].knobs,log)
                
                # Exit condition
                if goodChild: break 
            
            currGeneration.__dict__['child'+str(child)].simulated = False
            currGeneration.__dict__['child'+str(child)].name = 'child' + str(child)
        
    
    generations.__dict__['generation'+str(genNumb)] = currGeneration # Might not be needed due to passing by reference

    return generations


###########################################################################
# This function will randomly select a new set of settings. It the
# limitRandomness input is set to True, the randomness will be restricted.
# To ensure the same knob combination is not resimulated, each combination 
# is compared with previous simulations.
###########################################################################
def createMutations(simSettings,generations,genNumb,totalPopulation,log):
    
    # Determine number of mutations to add
    currGeneration = generations.__dict__['generation'+str(genNumb)]
    population = currGeneration.__dict__
    addNumber = totalPopulation-len(population)
    
    # Randomize all knobs
    knobs = simSettings.adaption.knobs
    for mutation in range(addNumber):

        # Prepare fields for mutation
        mutationName = 'mutation'+str(mutation)
        currGeneration.__dict__[mutationName] = nothing()
        currGeneration.__dict__[mutationName].knobs = nothing()

        for attempt in range(100):
            for knobName in knobs:

                validName = str(knobName).replace('.','_')

                # Retrieve knob limits
                minValue = rgetattr(simSettings, (knobName + '.minValue'))
                maxValue = rgetattr(simSettings, (knobName + '.maxValue'))
                increment = rgetattr(simSettings, (knobName + '.increment'))

                # Set new knob value
                if knobName == 'receiver.preAmp.gain' or knobName == 'receiver.FFE.taps.main':
                    value = 1 # set automatically
                else:
                    value = random.uniform(minValue, maxValue)
                    value = np.round(value/increment)*increment
                    value = max(min(value,maxValue),minValue)
                
                currGeneration.__dict__[mutationName].knobs.__dict__[validName] = value
            
            
            # Ensure knobs meet requirements
            currGeneration.__dict__[mutationName].knobs, goodMutant = checkKnobs(currGeneration.__dict__[mutationName].knobs)
    
            # Check knob uniqueness
            goodMutant = goodMutant & checkUniqueness(currGeneration.__dict__[mutationName].knobs,log)
            
            # Exit condition
            if goodMutant: break 
        
        currGeneration.__dict__[mutationName].simulated = False
        currGeneration.__dict__[mutationName].name = mutationName
    
    generations.__dict__['generation'+str(genNumb)] = currGeneration # Might not be needed due to passing by reference

    return generations


###########################################################################
# This function ensures all taps meet requirements. It also sets the TX EQ 
# main tap height.
###########################################################################
def checkKnobs(knobs):

    # Calculate TX main tap height
    main = 1
    knobNames = knobs.__dict__
    for knobName in knobNames:
        if knobName[:14] == 'transmitter_EQ' and knobName[-4:] != 'main':
            main = main - abs(knobs.__dict__[knobName])
    
    knobs.transmitter_EQ_taps_main = main # update

    # Ensure summation adds up to supply
    good = True
    if main <= 0:
        good = False
    else:
        good = True
    

    # Ensure main tap is largest
    for knobName in knobNames:
        if knobName[:14] == 'transmitter_EQ' and knobName != 'transmitter_EQ_taps_main' and \
                abs(knobs.__dict__[knobName])>=np.abs(main):
            good = False
        
    # Ensure CTLE zero is lower than its frequency
    knobNames = knobs.__dict__
    if ('receiver_CTLE_zeroFreq' in knobNames) and ('receiver_CTLE_pole1Freq' in knobNames):
        if (knobs.receiver_CTLE_zeroFreq>knobs.receiver_CTLE_pole1Freq):
            good = False
    
    # Save results
    knobs.transmitter_EQ_taps_main = main

    return knobs, good


###########################################################################
# This function ensures the specific combination of settings has not 
# already been simulated, eliminating repeated simulations. It also ensures
# simple setting are respected such as the TX pre-emphasis summing no
# larger than the supply.
###########################################################################
def checkUniqueness(knobs, log):

    unique = True
    knobNames = knobs.__dict__
    for index in range(len(log)):
        similarities = 0
        for name in knobNames:
            if log[index].__dict__[name] == knobs.__dict__[name]:
                similarities = similarities + 1
        
        if similarities == len(knobNames):
            unique = False

    return unique


###########################################################################
# This function selects a new candidate to simulate.
###########################################################################
def pickNewCandidate(simSettings: simulationSettings, simResults: simulationStatus):

    # Import variables
    totalPopulation = simSettings.adaption.totalPopulation.value
    knobs = simSettings.adaption.knobs
    genNumb = simResults.adaption.generationNumb
    currGeneration = simResults.adaption.generations.__dict__['generation'+str(genNumb)]
    
    # Pick candidate that has not been similated yet
    people = list(currGeneration.__dict__)
    candNumb = 0
    candidateName = people[candNumb]
    while currGeneration.__dict__[candidateName].simulated:
        candNumb = candNumb+1
        if candNumb >= totalPopulation:
            finished = True
            return finished
        
        candidateName = people[candNumb]
    
    finished = False
    
    # Add value to settings structure
    for knobName in knobs:
        knobPath = str(knobName) + '.value'
        validName = str(knobName).replace('.','_')
        rsetattr(simSettings, knobPath, currGeneration.__dict__[candidateName].knobs.__dict__[validName])
    
    currentResult = currGeneration.__dict__[candidateName]
    
    # Save results
    simResults.adaption.currentResult = currentResult

    return finished


###########################################################################
# This function sets the settings to the previously determined optimal
# solution. It also sets the modulation scheme and pulse cursor count to
# the original user selection.
###########################################################################
def setOptimal(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    optimalResult = simResults.adaption.optimalResult
    genNumb = simResults.adaption.generationNumb
    generations = simResults.adaption.generations
    
    # See if adaption failed
    if not optimalResult.successful:
        print('ERROR: Adaption has failed! Consider increasing the number of generations.') 
    
        
    # Set settings to optimal
    knobs = optimalResult.knobs.__dict__
    for knobName in knobs:
        knobPath = str(str(knobName) + '.value').replace('_','.')
        rsetattr(simSettings, knobPath, optimalResult.knobs.__dict__[knobName])
    
    currentResult = optimalResult
    currentResult.name = 'finalCandidate'
    generations.__dict__['generation'+str(genNumb)] = nothing()
    generations.__dict__['generation'+str(genNumb)].__dict__[currentResult.name] = optimalResult
    
    # Add original user settings
    simSettings.general.modulation          = simSettings.adaption.savedSettings.modulation
    simSettings.general.samplerNumb         = simSettings.adaption.savedSettings.samplerNumb
    simSettings.general.levelNumb           = simSettings.adaption.savedSettings.levelNumb
    simSettings.transmitter.preCursorCount  = simSettings.adaption.savedSettings.preCursorCount
    simSettings.transmitter.postCursorCount = simSettings.adaption.savedSettings.postCursorCount
    simSettings.transmitter.cursorCount     = simSettings.adaption.savedSettings.cursorCount
    
    # Save results
    simResults.adaption.currentResult = currentResult
    simResults.adaption.generations = generations


###########################################################################
# Plot the adaption process's results across attempts/generations
###########################################################################
def displayAdaption(simSettings: simulationSettings, simResults: simulationStatus):

    # Do not plot if not adapting
    if not simSettings.adaption.adapt: return 
    
    # Import variables
    log = simResults.adaption.log

    BER = np.zeros((len(log),))
    eyeHeight = np.zeros((len(log),))
    
    for index in range(len(log)):
        BER[index]= log[index].optimalBER
        eyeHeight[index]= log[index].optimalEyeHeight
    
    
    # Plot single result
    fig, axs = plt.subplots(nrows=2, ncols=1, dpi = 200, num='Adaption Results')
    axs[0].semilogy(np.arange(len(BER)), BER, linewidth=1)
    axs[0].set_title('Optimal BER vs. Adaption Attempt')
    axs[0].set_ylabel('BER (NRZ)')
    axs[0].set_xlabel('Adaption Number')
    axs[0].grid(True)

    axs[1].plot(np.arange(len(eyeHeight)), eyeHeight, linewidth=1)
    axs[1].set_title('Optimal Eye Height vs. Adaption Attempt')
    axs[1].set_ylabel('Eye Height (NRZ)')
    axs[1].set_xlabel('Adaption Number')
    axs[1].set_ylim(0, max(max(eyeHeight)*1.2, 0.1))
    axs[1].grid(True)
    
    # Tell use to update settings
    print('The adaption has finished! If you like the results, update your settings to match those in the command window.')
