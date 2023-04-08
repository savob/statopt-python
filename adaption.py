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
# This function displays the progress of the adaption algorithm over time.
# It can be used to ensure the global optimal solution has been reached.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
# 
# Outputs:
#   Plot showing adaption result versus attempt
#   
###########################################################################
from userSettingsObjects import simulationSettings
from initializeSimulation import simulationStatus
import matplotlib.pyplot as plt
import numpy as np

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
