from dataclasses import dataclass

#@dataclass
class userSettings:
    x: int
    y: int

test = userSettings()

test.x = 8
#test.y.u = 0

print(test)

test.a = lambda:None

setattr(test.a, "p", 16)

print(test.a.p)

quit()

# Begin Simulation
print('----------Begining Simulation----------')

### Define Simulation Settings
# Generate user settings

simSettings = GenerateUserSettingsExample_ECE1392_A1() # Example for Assignment 1 of ECE1392


# Generate settings limits
simSettings = GenerateSettingsLimits(simSettings)

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

# End Simulation
print('----------Simulation Complete----------')
print(['Elapsed time is ',num2str(round(toc,1)),' seconds.'])