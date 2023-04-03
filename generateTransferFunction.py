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
from scipy import signal, optimize


def generateTransferFunction(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Check if must update
    update = updateChannelData(simSettings, simResults)
    if not update:
        return 
    
    # Begin importing
    print('----------Importing Channel Data----------')
    
    # Load files
    loadFiles(simSettings, simResults)

    # Create step response
    #simResults = generateNumDen(simResults) # Going to try and use the actual step response

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
            circuit = pickle.load(modelCircuitTFName)

            # Convert circuit 
            circuit = np.interp(freqs, circuit.frequency, circuit.response)
            for i in range(len(circuit)):
                if isnan(circuit[i]): circuit[i] = 0

            tranFunc = tranFunc * circuit
        
      
        # Add notch in response
        if addNotch:
            k = 2 * np.pi * notchFreq / 10
            g = 10 ^ (notchAttenuation / 20)
            notchLTI = signal.lti([1, 5*k/g, 100*k^2], [1, 5*k, 100*k^2])
            w, mag, phase = signal.bode(notchLTI, 2*np.pi*freqs)
            mag = np.squeeze(mag)
            phase = np.squeeze(phase) * 180 / np.pi
            notchTF = mag * np.exp(np.pi * phase)
            tranFunc = tranFunc * notchTF
        
        
        '''
        Perform rational fitting

        In the original StatEye tool, it made use of the 'rationalfit' function to find a
        decent fit for the modified frequency response data stored in 'tranFunc', so that
        it could be described as a polynomial so that the pulse responses of channels can
        be easily determined using the built in functions to do so with arbitrary transfer 
        polynomials. However this function doesn't seem to have any readily found 
        equivalents, nor is it something easily replicated.

        In place of this polynomial fitting, I have elected to derive the impulse response 
        of our system using Discrete Fourier Transform techniques and use that as a part 
        of a convolution in realtime instead.

        It seems that skrf.vectorFitting.VectorFitting should be able to do a decent job
        of the linear fitting, but it only acts on networks. I attepted using 'curve_fit' 
        but that doesn't seem to work well when trying to tune complex parameters.

        I have left the partially ported MATLAB code here to be referred to in the future if needed
        '''

        '''
        fitTollerence = -50  # rational fitting tolerance in dB
        initialGuess = np.full((97) ,1 + 1j)
        initialGuess[-1]= 0
        rationalFuncCoeffs, convergence = optimize.curve_fit(rationalTestFcn, freqs, tranFunc, p0=initialGuess)
        nPoles = 48 # Always 48 given function definition
        '''

        impulseResponse = impulseResponseConvolKernel(tranFunc, freqs, samplePeriod, 6000)

        # Save results
        temp = channelInfluence(tranFunc, freqs, impulseResponse)
        setattr(simResults.influenceSources.channel, name, temp)
        #simResults.influenceSources.channel.__dict__[name].nPoles = nPoles
        #simResults.influenceSources.channel.__dict__[name].rationalFunc = rationalFunc

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
    freqRespPadded = np.concatenate((frequencyResponse, np.zeros((freqsExtended.size-frequencyResponse.size))))
    
    # To create an impulse response the padded frequency response is reflected
    # then put through an inverse Fourier Transform to get the time response
    tempH = np.concatenate((freqRespPadded, np.conj(np.flip(freqRespPadded[1:freqRespPadded.size-1]))))
    impulseResponse = np.real(np.fft.ifft(tempH))

    # Trim this convolution to be centered around the peak response if desired
    if window != 0:
        maxValueIndex = np.argmax(impulseResponse)

        # Ensure we stay within bounds and don't go below zero since the response is usually frontward
        bottomIndex = int(max(0, maxValueIndex - (window / 2)))
        topIndex = int(max(window, maxValueIndex + (window / 2)))

        return impulseResponse[bottomIndex:topIndex]
    else:
        return impulseResponse # Return unchanged response (will be large!)


'''

These are additional functions used as part of the polynomial fitting system

###########################################################################
# This function is used to find the rational fit
###########################################################################
def rationalTestFcn(f, a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12,a13,a14,a15,a16,a17,a18,a19,a20,a21,a22,a23,
                    a24,a25,a26,a27,a28,a29,a30,a31,a32,a33,a34,a35,a36,a37,a38,a39,a40,a41,a42,a43,a44,a45,a46,a47,
                    c0,c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13,c14,c15,c16,c17,c18,c19,c20,c21,c22,c23,
                    c24,c25,c26,c27,c28,c29,c30,c31,c32,c33,c34,c35,c36,c37,c38,c39,c40,c41,c42,c43,c44,c45,c46,c47,d):
    s = 2*np.pi*f
    

    result = d
    
    for x in range(48):
        result = result + (locals()['c'+str(x)] / (s - locals()['a'+str(x)] ))

    result = result * np.exp(-s*delayFactor)
    return result

###########################################################################
# This function creates the numerators and denominators for the channel
# transfer functions.
###########################################################################
def generateNumDen(simResults: simulationStatus):

    # Loop through each channel
    for channel in simResults.influenceSources.channel.__dict__:
        name = simResults.influenceSources.channel.__dict__[channel]
        
        # Import variables
        nPoles = simResults.influenceSources.channel.__dict__[name].nPoles
        A = simResults.influenceSources.channel.__dict__[name].rationalFunc[0:47]
        C = simResults.influenceSources.channel.__dict__[name].rationalFunc[48:-1]
        D = simResults.influenceSources.channel.__dict__[name].rationalFunc[-1]
        #delay = simResults.influenceSources.channel.__dict__[name].rationalFunc.Delay
        
        # Create numerators and denominators
        numerator = np.array([1])
        denominator = np.array([1])

        index1 = 1 # index of poles and residues
        index2 = 0 # index of numerators and denominators
        while index1 <= nPoles:
            
            # Real pole
            if np.isreal(A(index1)):
                index2 = index2 + 1
                numerator[index2] = C(index1)
                denominator[index2] = [1, -A(index1)]
                index1 = index1 + 1
                
            # Complex pole
            else:
                index2 = index2 + 1
                real_a = np.real(A(index1))
                imag_a = np.imag(A(index1))
                real_c = np.real(C(index1))
                imag_c = np.imag(C(index1))
                numerator[index2] = [2*real_c, -2*(real_a*real_c+imag_a*imag_c)]
                denominator[index2] = [1, -2*real_a, real_a^2+imag_a^2]
                index1 = index1 + 2
            
        
        
        # Remove proprietary RF Toolbox variables
        # Although not applicable, kept to maintain compatibility with the remainder of the codebase
        del simResults.influenceSources.channel.__dict__[name].rationalFunc
        
        # Save results
        simResults.influenceSources.channel.__dict__[name].A = A
        simResults.influenceSources.channel.__dict__[name].C = C
        simResults.influenceSources.channel.__dict__[name].D = D
        simResults.influenceSources.channel.__dict__[name].delay = delayFactor
        simResults.influenceSources.channel.__dict__[name].numerator = numerator
        simResults.influenceSources.channel.__dict__[name].denominator = denominator
'''    


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

