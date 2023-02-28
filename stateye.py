import time # Used for timing exectution
from generateUserSettingsExampleECE1392 import generateUserSettings # Change the 'from' file to desired file
from generateSettingsLimits import generateSettingsLimits
from initializeSimulation import initializeSimulation




# Begin simulation
print('----------Preparing Simulation----------')
startTime = time.time() # Get start (clock) time

simSettings = generateUserSettings()
print('Simulation settings Loaded')
generateSettingsLimits(simSettings)
print('Simulation settings limits Set')
simResults = initializeSimulation(simSettings) # Really just adds a bunch of settings and prepares simulation result object
print('User-dependant settings set')



# End Simulation
print('----------Simulation Complete----------')
endTime = time.time()
print('{:.3f} seconds elapsed since starting the script.'.format(endTime - startTime))

quit()


# Ensure settings meet requirements
[simSettings, simResults] = CheckSettings(simSettings, simResults)

## Analyze and Adapt Link

# Update channel
simResults = GenerateTransferFunction(simSettings, simResults)

# Generate fixed sources of influence
simResults = GenerateFixedInfluence(simSettings, simResults)

# Loop during adaption
while (~simResults.finished):
    
    # Generate variable sources of influence
    simResults = GenerateVariableInfluence(simSettings, simResults)
    
    # Generate pulse response
    simResults = GeneratePulseResponse(simSettings, simResults)
    
    # Generate ISI signal trajectories
    simResults = GenerateISI(simSettings, simResults)

    # Generate probability distribution
    simResults = GeneratePDF(simSettings, simResults)

    # Generate BER distribution
    simResults = GenerateBER(simSettings, simResults)

    # Generate simulation results
    simResults = GenerateResults(simSettings, simResults)

    # Update adaption settings (if required)
    [simSettings, simResults] = AdaptLink(simSettings, simResults)


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
