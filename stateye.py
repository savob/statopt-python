import time # Used for timing exectution
import matplotlib.pyplot as plt
from generateUserSettingsExampleECE1392 import generateUserSettings # Change the 'from' file to desired file
from generateSettingsLimits import generateSettingsLimits
from initializeSimulation import initializeSimulation
from checkSettings import checkSettings
from generateTransferFunction import generateTransferFunction
from generateFixedInfluence import generateFixedInfluence
from generateVariableInfluence import generateVariableInfluence
from generatePulseResponse import generatePulseResponse
from generateISI import generateISI
from generatePDF import generatePDF
from generateBER import generateBER
from generateResults import generateResults
from displayResults import displayResults
from displayChannels import displayChannels
from displayCTLEResponse import displayCTLEResponse
from displayInterferences import displayJitter, displayDistortion, displayNoise

# Begin simulation
print('----------Preparing Simulation----------')
startTime = time.time() # Get start (clock) time

simSettings = generateUserSettings()
print('Simulation settings Loaded')
generateSettingsLimits(simSettings)
print('Simulation settings limits set')
simResults = initializeSimulation(simSettings) # Really just adds a bunch of settings and prepares simulation result object
print('User-dependant settings generated')
checkSettings(simSettings, simResults)

doneLoadingTime = time.time() # Mark time once data was loaded

# Start preconditioning the simulation
generateTransferFunction(simSettings, simResults)

# Generate fixed sources of influence
generateFixedInfluence(simSettings, simResults)

doneFixedTime = time.time() # Mark time once data was loaded

# Analyze and Adapt Link
while not simResults.finished:
    
    # Generate variable sources of influence
    generateVariableInfluence(simSettings, simResults)

    # Generate pulse response
    generatePulseResponse(simSettings, simResults)

    # Generate ISI signal trajectories
    generateISI(simSettings, simResults)

    # Generate probability distribution
    generatePDF(simSettings, simResults)

    # Generate BER distribution
    generateBER(simSettings, simResults)

    # Generate simulation results
    generateResults(simSettings, simResults)

    # Update adaption settings (if required)
    #AdaptLink(simSettings, simResults)
    simResults.finished = True # Not doing adaptions for now

doneSimTime = time.time() # Mark time once data was loaded

# Display responses
displayChannels(simSettings, simResults)
displayCTLEResponse(simSettings, simResults)


# Display interferences
displayJitter(simSettings, simResults)
displayNoise(simSettings, simResults)
displayDistortion(simSettings, simResults)

# Display final results
displayResults(simSettings, simResults)
#DisplayAdaption(simSettings, simResults)

# End Simulation
print('----------Simulation Complete----------')
endTime = time.time()

print('{:.3f} seconds elapsed since starting the script:'.format(endTime - startTime))
print('\t{:6.3f} to load and verify in simulation parameters'.format(doneLoadingTime - startTime))
print('\t{:6.3f} to prepare fixed system influences'.format(doneFixedTime - doneLoadingTime))
print('\t{:6.3f} to run simulation and adaption'.format(doneSimTime - doneFixedTime))
print('\t{:6.3f} to output data'.format(endTime - doneSimTime))

plt.show() # Show plots after the timers are posted, it blocks the program

quit()

    



# Plot Results
# Dock all figures in one window
#set(0,'DefaultFigureWindowStyle','docked')

DisplayPulse(simSettings, simResults)


# Display distributions
DisplayISI(simSettings, simResults)
DisplayPDF(simSettings, simResults)
DisplayBER(simSettings, simResults)

