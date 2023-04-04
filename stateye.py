import time # Used for timing exectution
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

# Begin simulation
print('----------Preparing Simulation----------')
startTime = time.time() # Get start (clock) time

simSettings = generateUserSettings()
print('Simulation settings Loaded')
generateSettingsLimits(simSettings)
print('Simulation settings limits Set')
simResults = initializeSimulation(simSettings) # Really just adds a bunch of settings and prepares simulation result object
print('User-dependant settings generated')
checkSettings(simSettings, simResults)


# Start preconditioning the simulation
generateTransferFunction(simSettings, simResults)

## Analyze and Adapt Link

# Generate fixed sources of influence
generateFixedInfluence(simSettings, simResults)

# Loop during adaption
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
    #GenerateBER(simSettings, simResults)

    # Generate simulation results
    #GenerateResults(simSettings, simResults)

    # Update adaption settings (if required)
    #AdaptLink(simSettings, simResults)
    simResults.finished = True # Not doing adaptions for now



# End Simulation
print('----------Simulation Complete----------')
endTime = time.time()
print('{:.3f} seconds elapsed since starting the script.'.format(endTime - startTime))

quit()

    



# Plot Results
# Dock all figures in one window
#set(0,'DefaultFigureWindowStyle','docked')

# Display responses
DisplayChannel(simSettings, simResults)
DisplayCTLEResponse(simSettings, simResults)
DisplayPulse(simSettings, simResults)

# Display interferences
DisplayJitter(simSettings, simResults)
DisplayNoise(simSettings, simResults)
DisplayDistortion(simSettings, simResults)

# Display distributions
DisplayISI(simSettings, simResults)
DisplayPDF(simSettings, simResults)
DisplayBER(simSettings, simResults)

# Display final results
DisplayResults(simSettings, simResults)
DisplayAdaption(simSettings, simResults)
