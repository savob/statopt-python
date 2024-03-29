###########################################################################
#
#   StatOpt Simulator
#   by Jeremy Cosson-Martin, Jhoan Salinas of
#   Ali Sheikholeslami's group
#   Ported to Python 3 by Savo Bajic
#   Department of Electrical and Computer Engineering
#   University of Toronto
#   Copyright Material
#   For personal use only
#
###########################################################################
# This is the file that runs the statistical simulation of a wireline link 
# based on a selected set of user specified parameters from a file. In 
# addition to performing an analysis of a given wireline configuration to 
# provide information such as the probability distribution and expected 
# eye dimensions, this system can also work to tune a wireline system using
# a genetic algorithm for optimal performance.
#
# To adjust the simulation, only the simulation settings file needs to be
# adjusted. The simulation system files themselves do not need to be edited
# themselves to enable or disable parts of the system's behaviour. The only 
# exception being the selection of which setting file to use explained below.
#
# To enable quicker swapping between simulation configurations they can be 
# prepared in different files that are then selected by editing where the
# generateUserSettings function is imported from a few lines below.
#   
###########################################################################

from generateUserSettingsExample0 import generateUserSettings # Change the 'from' file to desired file

import time # Used for monitoring execution time
import matplotlib.pyplot as plt
from generateSettingsLimits import generateSettingsLimits
from initializeSimulation import initializeSimulation
from checkSettings import checkSettings
from adaption import displayAdaption, adaptLink
from generateFixedInfluence import generateFixedInfluence
from generateVariableInfluence import generateVariableInfluence
from generatePulseResponse import generatePulseResponse
from generateISI import generateISI
from generatePDF import generatePDF
from generateBER import generateBER
from generateResults import generateResults
from displayResults import displayResults
from displayResponses import displayChannels, displayCTLEResponse, displayPulse
from displayInterferences import displayJitter, displayDistortion, displayNoise
from displayDistributions import displayISI, displayPDF, displayBER

# Begin simulation
print('\n----------Preparing Simulation----------')
startTime = time.time() # Get start clock time

simSettings = generateUserSettings()
generateSettingsLimits(simSettings)
simResults = initializeSimulation(simSettings) # Really just adds a bunch of settings and prepares simulation result object
checkSettings(simSettings)

doneLoadingTime = time.time() # Mark time once data is loaded and verified

# Generate fixed sources of influence
generateFixedInfluence(simSettings, simResults)

doneFixedTime = time.time() # Mark time once fixed influences are prepared

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
    adaptLink(simSettings, simResults)

doneSimTime = time.time() # Mark time once simulations are complete 

# Plot Results
# In MATLAB these were all docked in the main window, however there is no to ensure that with matplotlib

# Display responses
displayChannels(simSettings, simResults)
displayCTLEResponse(simSettings, simResults)
displayPulse(simSettings, simResults)

# Display interferences
displayJitter(simSettings, simResults)
displayNoise(simSettings, simResults)
displayDistortion(simSettings, simResults)

# Display distributions
displayISI(simSettings, simResults)
displayPDF(simSettings, simResults)
displayBER(simSettings, simResults)

# Display final results
displayResults(simSettings, simResults)
displayAdaption(simSettings, simResults)

# End Simulation
print('\a\n----------Simulation Complete----------') # 'Bell' character, '\a', to ring when done
endTime = time.time()

print('{:.3f} seconds elapsed since starting the script:'.format(endTime - startTime))
print('\t{:8.3f} to load in and verify simulation parameters'.format(doneLoadingTime - startTime))
print('\t{:8.3f} to prepare fixed system influences'.format(doneFixedTime - doneLoadingTime))
print('\t{:8.3f} to run simulation and adaption'.format(doneSimTime - doneFixedTime))
print('\t{:8.3f} to output data'.format(endTime - doneSimTime))

plt.show() # Show plots after the timers are posted, it blocks the program and thus messes up timers
