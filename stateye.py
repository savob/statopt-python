import time # Used for timing exectution
from generateUserSettingsExampleECE1392 import generateUserSettings # Change the 'from' file to desired file
from generateSettingsLimits import generateSettingsLimits





# Begin simulation
print('----------Preparing Simulation----------')
startTime = time.time() # Get start (clock)time

simSettings = generateUserSettings()
print('Simulation Settings Loaded')
generateSettingsLimits(simSettings)
print('Simulation Settings Limits Set')





# End Simulation
print('----------Simulation Complete----------')
endTime = time.time()
print('Elapsed time is {:.3f} seconds.'.format(endTime - startTime))

quit()


# Initialize simulation
[simSettings, simResults] = InitializeSimulation(simSettings)

# Ensure settings meet requirements
[simSettings, simResults] = CheckSettings(simSettings, simResults)

# Analyze and Adapt Link

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
