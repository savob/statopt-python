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
# This function plots all possible ISI signal trajectories onto an eye 
# diagram. This adds considerable time to the simulation! Consider
# commenting out unless required.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
# 
# Outputs:
#   Plot of the ISI signal trajectories
#   
###########################################################################

from userSettingsObjects import simulationSettings
from initializeSimulation import simulationStatus
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import loadmat

class nothing:
    def __init__(self):
        pass

def displayISI(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Plot only if desired
    if not simSettings.general.plotting.ISI: return 
    
    # Import variables
    signalingMode  = simSettings.general.signalingMode
    samplesPerSymb = simSettings.general.samplesPerSymb.value
    samplePeriod   = simSettings.general.samplePeriod.value
    numbSymb       = simSettings.general.numbSymb.value
    supplyVoltage  = simSettings.receiver.signalAmplitude.value
    outputPeak = max(simResults.pulseResponse.receiver.outputs.thru)
    ISI        = simResults.eyeGeneration.ISI.thru

    trajectories = nothing()

    # To reduce the discontinuation visibility, ungroup trajectories from their main cursor
    for mainCursor in ISI:
        for combName in ISI[mainCursor].__dict__:
            setattr(trajectories, combName, ISI[mainCursor].__dict__[combName].trajectory)
    
    # Order trajectories
    orderTraj = nothing()
    ordered = sorted(trajectories.__dict__)
    for comb in ordered:
        orderTraj.__dict__[comb] = trajectories.__dict__[comb]
    

    # Plot all trajectories
    plt.figure(dpi = 200, num='ISI Trajectories')
    plt.title('ISI Trajectories')
    plt.ylabel('Amplitude [V]')
    plt.xlabel('Samples')
    plt.grid(True)

    if signalingMode == '1+D':
        limit = min(outputPeak*4,supplyVoltage)
    elif signalingMode == '1+0.5D':
        limit = min(outputPeak*3,supplyVoltage)
    else:
        limit = min(outputPeak*2,supplyVoltage)
    plt.ylim(-limit,limit)

    for comb in ordered:

        # Add additional point to stich eyes together
        trajectory = orderTraj.__dict__[comb]
        trajectory1 = trajectory[:,int(samplesPerSymb/2)+1:]
        velocity = trajectory1[-1]-trajectory1[-2]
        trajectory1 = [trajectory1, trajectory1[-2]+velocity] 
        trajectory2 = trajectory[:,:int(samplesPerSymb/2)]
        velocity = trajectory2[2]-trajectory2[1]
        trajectory2 = [trajectory2(1)-velocity,trajectory2] 
        velocity = trajectory[-1]-trajectory[-2]
        trajectory3 = [trajectory, trajectory[-1]+velocity] 

        # Plot multiple eyes adjacent to oneanother, ensure eye is always in the middle
        for symb in range(numbSymb):
            if np.mod(numbSymb,2) == 0:

                # Plot left half
                xIndex = np.arange(symb*samplesPerSymb, (symb+0.5)*samplesPerSymb, 1)
                xAxis = xIndex*samplePeriod
                plt.plot(xAxis,trajectory1)

                # Plot right half
                xIndex = np.arange((symb+0.5)*samplesPerSymb, (symb+1)*samplesPerSymb, 1)
                xAxis = xIndex*samplePeriod
                plt.plot(xAxis,trajectory2)
            else:
                # Plot full eye
                xIndex = np.arange(symb*samplesPerSymb, (1+symb)*samplesPerSymb, 1)
                xAxis = xIndex*samplePeriod
                plt.plot(xAxis,trajectory3)