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
# This function is used to import new keystone (.s4p) files or matfile 
# (.mat) transfer function data into the StatEye program. This function is
# not a part of the main program. It must be run only when importing new 
# channel files. This script finds all .s4p files in the local directory 
# and saves the information into ChannelData.mat. Once this file is 
# generated, the StatEye no longer requires the use of the MathWorks 
# RF-Toolbox(TM). This script also has the option to convolve the channel 
# with an additional transfer function (such as an extracted circuit 
# frequency response) and additionally to add a notch at a particular 
# frequency. This additional data must come from a .mat file containing a 
# structure with directories named "response" and "frequency". Each should 
# be a vector containing the same number of elements. To save structure 
# type: 
# save('<FILENAME>.mat','-struct','<STRUCTURENAME>')
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
#   keystone (.s4p) or matfile (.mat) channel files
#   matfile (.mat) channel files
#
# Outputs:
#   simResults: structure containing simulation results
#   ChannelData.mat file containing channel information
#   
###########################################################################
from userSettingsObjects import simulationSettings
from initializeSimulation import simulationStatus, channelInfluence
import pickle # Used to load and unload Python objects (.pkl)
import os
import skrf as rf # Used to read Touchstone files and nothing else
import numpy as np
from math import isnan
import control.matlab as ml
from loadMatlabFiles import objectFromMat


def generateTransferFunction(simSettings: simulationSettings, simResults: simulationStatus):

    # Check if must update
    update = updateChannelData(simSettings, simResults)
    if not update:
        return 
    
    ml.use_matlab_defaults() # Needed to ensure compatibility with MATLAB expectations for control code

    # Begin importing
    print('----------Importing Channel Data----------')
    
    # Load files
    loadFiles(simSettings, simResults)

    # Update data files
    updateFile(simSettings, simResults)
    
    # Finished importing
    print('----------Importing Finished----------')


###########################################################################
# This function determines if the channel data file should be updated.
###########################################################################
def updateChannelData(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Search for channel data file
    localFiles = os.listdir('.')
    update = True # Assume we need updating unless a proper file is found

    if 'ChannelData.pkl' in localFiles:
        # Ensure required channel data is available if there is a file present

        with open('ChannelData.pkl', 'rb') as f:
            simResults.channelData = pickle.load(f) # If this has issues try deleting the file

        fileNames = list(simResults.channelData.__dict__)
        channels = simSettings.channel.fileNames.__dict__
        for channel in channels:
            # Check that there is an entry with the filename (without file type)
            if channels[channel][:-4] not in fileNames:
                return True # Return with the need to update to fill missing data
            else: 
                setattr(simResults.influenceSources.channel, channel, simResults.channelData.__dict__[channels[channel][:-4]])
                

        # Ask to voluntarily update (since we are not lacking any data)
        answer = input('Would you like to update the channel frequency transfer functions? (Y/N)')
        if answer == 'N' or answer == 'n':
            update = False
        elif answer == 'Y' or answer == 'y':
            update = True
        else:
            print('Invalid response: {:s}\n----------Simulation Canceled----------'.format(answer))
            quit()
    
    return update
        
    

###########################################################################
# This function reads the available keystone files to generate the channel 
# characteristic s-parameters. 
###########################################################################
def loadFiles(simSettings: simulationSettings, simResults: simulationStatus):

    # Import variables
    importChannels      = simSettings.channel.fileNames
    modelCircuitTF      = simSettings.channel.modelCircuitTF
    modelCircuitTFName  = simSettings.channel.modelCircuitTFName
    addNotch            = simSettings.channel.addNotch
    notchFreq           = simSettings.channel.notchFreq.value
    notchAttenuation    = simSettings.channel.notchAttenuation.value
    samplePeriod        = simSettings.general.samplePeriod.value
    
    # Load each channel
    for name in importChannels.__dict__:
        fileName = importChannels.__dict__[name]

        freqs = 0
        tranFunc = 0
        
        # Import keystone (.s4p) channel data
        if fileName[-4:] == '.s4p':
            backplane = rf.Network('./touchstone/'+fileName)

            freqs = backplane.f
            freqPoints = freqs.size

            # Get differential mode transfer function
            # Start by preparing differential S-parameters
            sParamsTemp = np.copy(backplane.s)
            
            sParamsTemp[:,1,:] = np.copy(backplane.s[:,2,:])
            sParamsTemp[:,2,:] = np.copy(backplane.s[:,1,:])
            
            sParamsTemp[:,:,1] = np.copy(backplane.s[:,:,2])
            sParamsTemp[:,:,2] = np.copy(backplane.s[:,:,1])
            
            sParamsTemp[:,1,2] = np.copy(backplane.s[:,1,2])
            sParamsTemp[:,2,1] = np.copy(backplane.s[:,2,1])
            
            sParamsTemp[:,1,1] = np.copy(backplane.s[:,2,2])
            sParamsTemp[:,2,2] = np.copy(backplane.s[:,1,1])
    
            M = np.array([[1,-1,0,0],[0,0,1,-1],[1,1,0,0],[0,0,1,1]])
            invM = np.transpose(M)
            
            smmParams = np.zeros((4,4,freqPoints), dtype = complex)
            
            for i in range(freqPoints):
                smmParams[:,:,i] = (M@sParamsTemp[i,:,:]@invM)/2
            
            sParamsDiff = smmParams[0:2,0:2,:]
            
            # Assume source/load impedances of 50 ohm
            zl = 50.0*np.ones((1,1,freqPoints))
            zs = 50.0*np.ones((1,1,freqPoints))
            z0 = backplane.z0[0,0]*np.ones((1,1,freqPoints))

            # Reflection Coefficients
            gammaL = (zl - z0) / (zl + z0)
            gammaL[zl == np.inf] = 1 
            
            gammaS = (zs - z0) / (zs + z0)
            gammaS[zs == np.inf] = 1
            
            gammaIn = (sParamsDiff[0,0,:] + sParamsDiff[0,1,:] * sParamsDiff[1,0,:] * gammaL) / (1 - sParamsDiff[1,1,:] * gammaL)
            
            tranFunc = sParamsDiff[1,0,:] * (1 + gammaL) * (1 - gammaS) / (1 - sParamsDiff[1,1,:] * gammaL) / (1 - gammaIn * gammaS) 
            tranFunc = tranFunc.reshape(freqPoints,) 
        
       
        # Convolve channel with simulated circuit response
        if modelCircuitTF:
            circuit = objectFromMat(modelCircuitTFName)

            # Convert circuit 
            circuit = np.interp(freqs, circuit.frequency, circuit.response)
            for i in range(len(circuit)):
                if isnan(circuit[i]): circuit[i] = 0

            tranFunc = tranFunc * circuit
        
      
        # Add notch in response
        if addNotch:
            k = 2 * np.pi * notchFreq / 10
            g = 10 ^ (notchAttenuation / 20)
            notchLTI = ml.tf([1, 5*k/g, 100*k^2], [1, 5*k, 100*k^2])
            mag, phase, w = ml.bode(notchLTI, 2*np.pi*freqs, plot=False)
            mag = np.squeeze(mag)
            phase = np.squeeze(phase) * 180 / np.pi
            notchTF = mag * np.exp(np.pi * phase)
            tranFunc = tranFunc * notchTF

        impulseResponse = impulseResponseConvolKernel(tranFunc, freqs, samplePeriod, 20000)

        # Save results
        temp = channelInfluence(tranFunc, freqs, impulseResponse)
        setattr(simResults.influenceSources.channel, name, temp)

        # Notify user
        print('Channel {0} is loaded'.format(fileName))
    
def impulseResponseConvolKernel(frequencyResponse, freqs, samplePeriod: float, window: int = 0):
    '''
    Generates the convolution kernel for an impulse given a transfer function / frequency response.

    Pads discrete time transfer function / frequency response with data in the frequency domain
    to reach the needed step in time domain when an inverse Fourier Transform is performed.

    This kernel is generally quite large so there is the option to have a window around the peak.
    '''
    
    # Get defining frequencies
    fStep = freqs[2] - freqs[1]
    fMax = max(freqs)

    # Max frequency needed to get sample period after IDFT
    fMaxDesired = int(1 / (2 * samplePeriod))

    # Extend frequency vector to desired maximum frequency
    padding = np.linspace(fMax, fMaxDesired, int((fMaxDesired-fMax)/fStep))
    freqsExtended = np.concatenate((freqs, padding))

    # Pad TF with zeros
    freqRespPadded = np.concatenate((frequencyResponse, np.zeros((len(freqsExtended)-len(frequencyResponse),))))
    
    # To create an impulse response the padded frequency response is reflected
    # then put through an inverse Fourier Transform to get the time response
    tempH = np.concatenate((freqRespPadded, np.conj(np.flip(freqRespPadded[1:-1]))))
    impulseResponse = np.real(np.fft.ifft(tempH))

    # Trim this convolution to be centered around the peak response if desired
    if window != 0 and window < len(impulseResponse):
        maxValueIndex = np.argmax(impulseResponse)

        # Ensure we stay within bounds and don't go below zero since the response is usually frontward
        bottomIndex = int(max(0, maxValueIndex - (window / 2)))
        topIndex = int(max(window, maxValueIndex + (window / 2)))

        return impulseResponse[bottomIndex:topIndex]
    else:
        return impulseResponse # Return unchanged response (will be large!)


###########################################################################
# This function updates the channel data file so it can be directly
# imported next time.
###########################################################################
def updateFile(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    fileNames = simSettings.channel.fileNames
    results = simResults.influenceSources.channel
    names = fileNames.__dict__
    
    # Update file data
    for name in names:
        fileName = fileNames.__dict__[name][:-4]
        setattr(simResults.channelData, fileName, results.__dict__[name]) # Maybe use .add() or something
    
    
    #simResults.channelData.(fileName(1:end-4)) = .(name)
    data = simResults.channelData

    '''
    Temporarily disable  saving channel data to simplify start
    
    with open('ChannelData.pkl', 'wb') as f:
        pickle.dump(data, f)
        print('ChannelData.pkl file created')
    '''

