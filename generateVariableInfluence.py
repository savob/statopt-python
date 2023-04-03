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
# This function creates all variable sources which influence the resultant 
# signal distribution. This is to say, sources which may change based on
# settings. For example, the receiver output refered noise will depend on 
# the receiver gain and equalization.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   simResults: structure containing simulation results
# 
# Outputs:
#   simResults: structure containing simulation results
#   
###########################################################################
from userSettingsObjects import simulationSettings
from initializeSimulation import simulationStatus
import numpy as np
import scipy.stats as stats
import scipy.signal as signal
from scipy import io
import scipy as sp

def generateVariableInfluence(simSettings: simulationSettings, simResults: simulationStatus):

    # Generate CTLE responses
    generateCTLE(simSettings, simResults)

    # Calculate RMS of RX FFE tap values
    #calculateFFERMS(simSettings, simResults)

    # Generate transmitter noise distribution
    #generateTXNoise(simSettings, simResults)

    # Generate channel noise distribution
    #generateChannelNoise(simSettings, simResults)

    # Generate receiver noise distribution
    #generateRXNoise(simSettings, simResults)

    # Combine influences
    combineInfluences(simSettings, simResults)


###########################################################################
# This function determines if the CTLE response for the given knob settings
# has already been calculated. If not it calculates the transfer function.
###########################################################################
def generateCTLE(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    addEqualization = simSettings.receiver.CTLE.addEqualization
    zeroFreq        = simSettings.receiver.CTLE.zeroFreq.value
    zeroNumb        = simSettings.receiver.CTLE.zeroNumb.value
    pole1Freq       = simSettings.receiver.CTLE.pole1Freq.value
    pole1Numb       = simSettings.receiver.CTLE.pole1Numb.value
    pole2Freq       = simSettings.receiver.CTLE.pole2Freq.value
    pole2Numb       = simSettings.receiver.CTLE.pole2Numb.value
    channelFreqs = simResults.influenceSources.channel.thru.frequencies
    zeroName     = ('z' + str(zeroFreq/1e9)).replace('.', '_')
    poleName     = ('z' + str(pole1Freq/1e9)).replace('.', '_')
    
    # Define CTLE transfer function
    if(addEqualization):

        # Determine if TF already calculated
        if 'RXCTLE' in simResults.influenceSources.__dict__:
            CTLEs = simResults.influenceSources.RXCTLE
        else:
            CTLEs = []
        
        calculated = True
        if CTLEs == []:
            calculated = False
        elif not zeroName in CTLEs.__dict__:
            calculated = False
        elif not poleName in CTLEs.__dict__[zeroName]:
            calculated = False
        
        
        # Return if CTLE already calculated
        if (calculated): return
        
        # Calculate new TF
        else:
            
            # Add first zero
            wz = 2*np.pi*zeroFreq
            listWz = np.ones((zeroNumb,)) * wz
            gain = (1/wz) ** zeroNumb
            
            # Add first pole
            wp1 = 2*np.pi*pole1Freq
            listWp1 = np.ones((pole1Numb,)) * wp1
            gain = gain * ((wp1) ** pole1Numb)

            # Add additional poles
            wp2 = 2*np.pi*pole2Freq
            listWp2 = np.ones((pole2Numb,)) * wp2
            gain = gain * ((wp2) ** pole2Numb)

            # Combine pole lists
            listWp = np.concatenate((listWp1, listWp2))

            # Combine transfer functions
            transferFunc = signal.ZerosPolesGain(listWz, listWp, gain)
        
    else:
        transferFunc = signal.TransferFunction([1],[1])
    

    # Save results
    w, magnitude, phase = signal.bode(transferFunc, 2*np.pi*channelFreqs) # force frequencies to be same as channel
    #simResults.influenceSources.RXCTLE.(zeroName).(poleName).transferFunc = transferFunc
    #simResults.influenceSources.RXCTLE.(zeroName).(poleName).magnitude = magnitude
    #simResults.influenceSources.RXCTLE.(zeroName).(poleName).phase = phase
    #simResults.influenceSources.RXCTLE.(zeroName).(poleName).frequency = channelFreqs

'''
###########################################################################
# This function calculates the RMS value of the RX FFE tap settings. This
# value is required later for output-refering noise.
###########################################################################
def calculateFFERMS(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    taps = simSettings.receiver.FFE.taps
    
    # Calculate RMS of taps (used for noise analysis)
    FFESum = 0
    tapNames = fieldnames(taps)
    for index=1:length(tapNames):
        tapName = tapNames{index}
        FFESum = FFESum+taps.(tapName).value^2
    
    tapRMS = sqrt(FFESum)
    
    # Save results
    simResults.pulseResponse.receiver.FFE.tapRMS = tapRMS


###########################################################################
# This function creates a probability distribution for the transmitter
# noise. This function adds random aswell as deterministic noise. Since the
# noise is created at the transmitter, it is attenuated by the channel,
# amplified by the CTLE, and amplitied by the FFE. Thus the equivalent 
# noise must first be calculated. To do so, it is assumed that the gaussian
# noise is white noise up to the bandwidth of the transmitter. The power of
# this white distribution is sent through the channel and CTLE power 
# transfer function. The equivalent power at the receiver is calculated and
# a corresponding gaussian distribution is created.
###########################################################################
def generateTXNoise(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    addCoding     = simSettings.general.codingGain.addCoding
    codingGain    = simSettings.general.codingGain.gain.value
    yAxis         = simSettings.general.yAxis.value
    yAxisLength   = simSettings.general.yAxisLength.value
    yIncrement    = simSettings.general.yIncrement.value
    TXBandwidth   = simSettings.transmitter.TXBandwidth.value
    addNoise      = simSettings.transmitter.noise.addNoise
    stdDeviation  = simSettings.transmitter.noise.stdDeviation.value
    sineAmp       = simSettings.transmitter.noise.amplitude.value
    sineFreq      = simSettings.transmitter.noise.frequency.value
    supplyVoltage = simSettings.receiver.signalAmplitude.value
    usePreAmp     = simSettings.receiver.preAmp.addGain
    gain          = simSettings.receiver.preAmp.gain.value
    useCTLE       = simSettings.receiver.CTLE.addEqualization
    zeroFreq      = simSettings.receiver.CTLE.zeroFreq.value
    pole1Freq     = simSettings.receiver.CTLE.pole1Freq.value
    useFFE        = simSettings.receiver.FFE.addEqualization
    
    FFERMS        = simResults.pulseResponse.receiver.FFE.tapRMS
    channelFreqs  = simResults.influenceSources.channel.thru.frequencies
    channelTF     = simResults.influenceSources.channel.thru.transferFunction  
    zeroName      = strrep(['z',num2str(zeroFreq/1e9)],'.','_')
    poleName      = strrep(['z',num2str(pole1Freq/1e9)],'.','_')
    CTLEMagnitude = simResults.influenceSources.RXCTLE.(zeroName).(poleName).magnitude
    
    # Add random noise
    if addNoise and stdDeviation != 0:

        # Create noise frequency distribution in transmitter
        power = stdDeviation^2
        maxIndex = floor(interp1(channelFreqs,1:length(channelFreqs),TXBandwidth))
        if(isnan(maxIndex)):
            maxIndex=length(channelFreqs) 
        
        powerDistribution = [ones(maxIndex,1)*power/TXBandwidthzeros(length(channelFreqs)-maxIndex,1)]

        # Calculate equivalent noise at receiver output
        powerDistribution = powerDistribution.*(abs(channelTF).^2)
        if(usePreAmp):
            powerDistribution = powerDistribution*gain^2
        
        if(useCTLE):
            powerDistribution = powerDistribution.*CTLEMagnitude.^2
        
        if(useFFE):
            powerDistribution = powerDistribution*FFERMS^2
        
        freqIncrement = channelFreqs(2)-channelFreqs(1)
        outputPower = sum(powerDistribution)*freqIncrement
        stdDeviationOutput = sqrt(outputPower)

        # Apply coding gain
        if(addCoding):
            stdDeviationOutput = stdDeviationOutput/10^(codingGain/10) 
        
        
        # Create noise distribution
        randNoise = normpdf(yAxis,0,stdDeviationOutput)
        randNoise = randNoise/sum(randNoise) # normalize PDF
    else:
        randNoise = 1 # perfect impulse
    

    # Add deterministic noise   
    if addNoise and sineAmp != 0:

        # Calculate equivalent noise at receiver output
        freqIndex = interp1(channelFreqs,1:length(channelFreqs),sineFreq)
        sineAmp = sineAmp*abs(interp1(1:length(channelTF),channelTF,freqIndex))
        if(usePreAmp):
            sineAmp = sineAmp*gain
        
        if(useCTLE):
            sineAmp = sineAmp*abs(interp1(1:length(channelTF),CTLEMagnitude,freqIndex))
        
        if(useFFE):
            sineAmp = sineAmp*FFERMS^2
        
        
        # Apply coding gain
        if(addCoding):
            sineAmp = sineAmp/10^(codingGain/10)
        
        
        # Generate sine distribution
        sine = sineAmp*sin(2*pi*(0:0.0001:1))
        sine = sine(1:-1) # remove repeated 0 value
        sineNoise = hist(sine,yAxis)
        sineNoise = sineNoise/sum(sineNoise) # normalize PDF
    else:
        sineNoise = 1 # perfect impulse
    

    # Convolve both noise types
    totalNoise = np.convolve(randNoise,sineNoise)
    if(len(totalNoise)<2*supplyVoltage/yIncrement):
       totalNoise = [zeros(1,round(yAxisLength/2)),totalNoise,zeros(1,round(yAxisLength/2))]
    
    voltageScale = -(length(totalNoise)-1)/2*yIncrement:yIncrement:length(totalNoise)/2*yIncrement

    # Save results
    simResults.influenceSources.TXNoise.random = randNoise
    simResults.influenceSources.TXNoise.deterministic = sineNoise
    simResults.influenceSources.TXNoise.totalNoise = totalNoise
    simResults.influenceSources.TXNoise.voltageScale = voltageScale


###########################################################################
# This function creates a probability distribution for the channel noise. 
# This function adds only random noise. Since the noise is defined at the 
# output of the channel, it is amplified by the CTLE and FFE. Thus the 
# equivalent noise must first be calculated. From there, a corresponding 
# gaussian distribution is created.
###########################################################################
def generateChannelNoise(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    addCoding     = simSettings.general.codingGain.addCoding
    codingGain    = simSettings.general.codingGain.gain.value
    yAxis         = simSettings.general.yAxis.value
    yAxisLength   = simSettings.general.yAxisLength.value
    addNoise      = simSettings.channel.noise.addNoise
    noiseDensity  = simSettings.channel.noise.noiseDensity.value
    usePreAmp     = simSettings.receiver.preAmp.addGain
    gain          = simSettings.receiver.preAmp.gain.value
    useCTLE       = simSettings.receiver.CTLE.addEqualization
    zeroFreq      = simSettings.receiver.CTLE.zeroFreq.value
    pole1Freq     = simSettings.receiver.CTLE.pole1Freq.value
    useFFE        = simSettings.receiver.FFE.addEqualization
    FFERMS   = simResults.pulseResponse.receiver.FFE.tapRMS
    zeroName = strrep(['z',num2str(zeroFreq/1e9)],'.','_')
    poleName = strrep(['z',num2str(pole1Freq/1e9)],'.','_')
    CTLE     = simResults.influenceSources.RXCTLE.(zeroName).(poleName)
        
    # Add random noise
    if addNoise and noiseDensity != 0: 

        # Create noise frequency distribution before amplification
        freqIncrement = CTLE.frequency(2)-CTLE.frequency(1)
        powerDistribution = noiseDensity*freqIncrement*ones(length(CTLE.frequency),1)

        # Calculate equivalent noise at receiver output
        if(usePreAmp):
            powerDistribution = powerDistribution*gain^2
        
        if(useCTLE):
            powerDistribution = powerDistribution.*CTLE.magnitude.^2
        
        if(useFFE):
            powerDistribution = powerDistribution*FFERMS^2
        
        outputPower = sum(powerDistribution)
        stdDeviationOutput = sqrt(outputPower)

        # Apply coding gain
        if(addCoding):
            stdDeviationOutput = stdDeviationOutput/10^(codingGain/10)
        
        
        # Create noise distribution
        randNoise = normpdf(yAxis,0,stdDeviationOutput)
        randNoise = randNoise/sum(randNoise) # normalize PDF
    else:
        randNoise = [zeros(1,floor(yAxisLength/2)),1,zeros(1,floor(yAxisLength/2))] # perfect impulse
    

    # Save results
    simResults.influenceSources.CHNoise.totalNoise = randNoise
    simResults.influenceSources.CHNoise.voltageScale = yAxis


###########################################################################
# This function creates a probability distribution for the receiver
# noise. This function adds random aswell as deterministic noise. It is
# assumed that the receiver noise is input refered and thus is affected by
# the pre-amp, CTLE and FFE.
###########################################################################
def generateRXNoise(simSettings: simulationSettings, simResults: simulationStatus):
    
    # Import variables
    addCoding     = simSettings.general.codingGain.addCoding
    codingGain    = simSettings.general.codingGain.gain.value
    yAxis         = simSettings.general.yAxis.value
    yAxisLength   = simSettings.general.yAxisLength.value
    yIncrement    = simSettings.general.yIncrement.value
    addNoise      = simSettings.receiver.noise.addNoise
    stdDeviation  = simSettings.receiver.noise.stdDeviation.value
    sineAmp       = simSettings.transmitter.noise.amplitude.value
    sineFreq      = simSettings.transmitter.noise.frequency.value
    supplyVoltage = simSettings.receiver.signalAmplitude.value
    usePreAmp     = simSettings.receiver.preAmp.addGain
    gain          = simSettings.receiver.preAmp.gain.value
    useCTLE       = simSettings.receiver.CTLE.addEqualization    
    zeroFreq      = simSettings.receiver.CTLE.zeroFreq.value
    pole1Freq     = simSettings.receiver.CTLE.pole1Freq.value
    useFFE        = simSettings.receiver.FFE.addEqualization
    FFERMS   = simResults.pulseResponse.receiver.FFE.tapRMS
    zeroName = strrep(['z',num2str(zeroFreq/1e9)],'.','_')
    poleName = strrep(['z',num2str(pole1Freq/1e9)],'.','_')
    CTLE     = simResults.influenceSources.RXCTLE.(zeroName).(poleName)
    
    # Add random noise
    if(addNoise and stdDeviation !=0):
        
        # Create noise frequency distribution before amplification
        power = stdDeviation^2
        powerDistribution = ones(length(CTLE.frequency),1)*power/length(CTLE.frequency)
        
        # Calculate output refered noise output
        if(useCTLE):
            powerDistribution = powerDistribution.*CTLE.magnitude.^2
        
        if(usePreAmp):
            powerDistribution = powerDistribution*gain^2
        
        if(useFFE):
            powerDistribution = powerDistribution*FFERMS^2
        
        outputPower = sum(powerDistribution)
        stdDeviationOutput = sqrt(outputPower)

        # Apply coding gain
        if(addCoding):
            stdDeviationOutput = stdDeviationOutput/10^(codingGain/10)
        
        
        # Create noise distribution
        randNoise = normpdf(yAxis,0,stdDeviationOutput)
        randNoise = randNoise/sum(randNoise) # normalize PDF
    else:
        randNoise = 1 # perfect impulse
    

    # Add deterministic noise   
    if addNoise and sineAmp != 0:
        
        # Calculate equivalent noise at receiver output
        freqIndex = interp1(CTLE.frequency,1:length(CTLE.frequency),sineFreq)
        sineAmp = sineAmp*abs(interp1(1:length(CTLE.magnitude),CTLE.magnitude,freqIndex))
        if(usePreAmp):
            sineAmp = sineAmp*gain
        
        if(useCTLE):
            sineAmp = sineAmp*abs(interp1(1:length(CTLE.magnitude),CTLE.magnitude,freqIndex))
        
        if(useFFE):
            sineAmp = sineAmp*FFERMS^2
        
    
        # Apply coding gain
        if(addCoding):
            sineAmp = sineAmp/10^(codingGain/10)
        
        
        # Generate sine distribution
        sine = sineAmp*np.sin(2*np.pi*(0:0.0001:1))
        sine = sine(1:-1) # remove repeated 0 value
        sineNoise = hist(sine,yAxis)
        sineNoise = sineNoise/np.sum(sineNoise) # normalize PDF
    else:
        sineNoise = 1 # perfect impulse
    
    
    # Convolve both noise types
    totalNoise = np.convolve(randNoise,sineNoise)
    if len(totalNoise) < 2*supplyVoltage/yIncrement:
       totalNoise = np.concatenate((np.zeros((round(yAxisLength/2),)), totalNoise, np.zeros((round(yAxisLength/2),))))
    
    voltageScale = np.linspace(-(len(totalNoise)-1)/2*yIncrement, (len(totalNoise)-1)/2*yIncrement, len(totalNoise) + 1)
    
    # Save results
    simResults.influenceSources.RXNoise.random = randNoise
    simResults.influenceSources.RXNoise.deterministic = sineNoise
    simResults.influenceSources.RXNoise.totalNoise = totalNoise
    simResults.influenceSources.RXNoise.voltageScale = voltageScale  
'''

###########################################################################
# This function combines all sources of noise together.
###########################################################################
def combineInfluences(simSettings: simulationSettings, simResults: simulationStatus):

    # Import variables
    yIncrement = simSettings.general.yIncrement.value
    TXNoise = simResults.influenceSources.TXNoise.totalNoise
    CHNoise = simResults.influenceSources.CHNoise.totalNoise
    RXNoise = simResults.influenceSources.RXNoise.totalNoise
    
    # Combine noise
    totalNoise = np.convolve(TXNoise,CHNoise)
    totalNoise = np.convolve(totalNoise,RXNoise)
    voltagescale = np.linspace(-(len(totalNoise)-1)/2*yIncrement, (len(totalNoise)-1)/2*yIncrement, len(totalNoise) + 1)

    # Save results
    simResults.influenceSources.totalNoise.histogram = totalNoise
    simResults.influenceSources.totalNoise.voltageScale = voltagescale
