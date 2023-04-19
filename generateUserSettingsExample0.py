from userSettingsObjects import simulationSettings, valueWithLimits
from math import sqrt, pow

# Generate pulse response from channel response for a PAM-4 system

def generateUserSettings() -> simulationSettings:
    simSettings = simulationSettings()

    ########################################
    # General settings
    ########################################
    # Frequency
    simSettings.general.symbolRate.value = 32e9 # symbol rate [S/s] (or 2x frequency [Hz])
        
    # Signaling mode ('standard','1+D','1+0.5D','clock')
    simSettings.general.signalingMode = 'standard'
    
    # Coding gain
    simSettings.general.codingGain.addCoding = False
    simSettings.general.codingGain.gain.value = 0 # coding gain [dB]
    
    # Modulation (M-PAM)
    simSettings.general.modulation.value = 4
    
    # Resolution
    simSettings.general.samplesPerSymb.value = 100 # horizontal resolution
    simSettings.general.yAxisLength.value = 201    # vertical resolution (must be odd)
    
    # General display
    simSettings.general.numbSymb.value = 2    # number of symbols to plot
    simSettings.general.contLevels.value = 10 # number of contour levels
        
    # Target BER
    simSettings.general.targetBER.value = 1e-6 # used for measurement purposes

    # Display responses
    simSettings.general.plotting.channelResponse = True
    simSettings.general.plotting.CTLEResponse    = True
    simSettings.general.plotting.pulseResponse   = True
    
    # Display inteferences
    simSettings.general.plotting.jitterSource     = True
    simSettings.general.plotting.noiseSource      = True
    simSettings.general.plotting.distortionSource = False
    
    # Display probability distributions
    simSettings.general.plotting.ISI              = False # CAREFUL: CAN BE SLOW TO PLOT!
    simSettings.general.plotting.PDFInitial       = False
    simSettings.general.plotting.PDFCrossTalk     = False
    simSettings.general.plotting.PDFDistorted     = False
    simSettings.general.plotting.PDFJitter        = False
    simSettings.general.plotting.PDFNoise         = False
    simSettings.general.plotting.PDFFinal         = True
    
    # Display bit-error rate distributions
    simSettings.general.plotting.BER  = False            # plot BER contour over BER
    simSettings.general.plotting.BER2 = True             # plot BER contour over PDF
    
    # Display measurement results
    simSettings.general.plotting.results = True
    
    ########################################
    # Adaption settings
    ########################################
    # Run adaption algorithm
    simSettings.adaption.adapt = False
    
    # Adaption complexity
    simSettings.adaption.totalParents.value = 2
    simSettings.adaption.childrenPerParent.value = 10
    simSettings.adaption.totalMutations.value = 2
    simSettings.adaption.mode1Generations.value = 20 # coarse adjustment
    simSettings.adaption.mode2Generations.value = 55 # fine adjustment

    # Define knobs to optimize
    simSettings.adaption.knobs = ['transmitter.EQ.taps.pre1',\
        'transmitter.EQ.taps.post1',\
        'receiver.preAmp.gain',\
        'receiver.CTLE.zeroFreq',\
        'receiver.CTLE.pole1Freq',\
        'receiver.FFE.taps.pre2',\
        'receiver.FFE.taps.pre1',\
        'receiver.FFE.taps.main',\
        'receiver.FFE.taps.post1',\
        'receiver.FFE.taps.post2',\
        'receiver.DFE.taps.post1',\
        'receiver.DFE.taps.post2']
        
    ########################################
    # Transmitter settings 
    ########################################    
    # Maximum amplitude [V]
    simSettings.transmitter.signalAmplitude.value = 1.5
    
    # Add source impedance (drop amplitude by half)
    simSettings.transmitter.includeSourceImpedance = True
    
    # Rise/fall time [s]
    simSettings.transmitter.tRise.value = 1e-12
    
    # TX bandwidth [Hz]
    simSettings.transmitter.TXBandwidth.value = 30e9
    
    # Impulse cursor length
    simSettings.transmitter.preCursorCount.value = 2 
    simSettings.transmitter.postCursorCount.value = 4

    # Pre-emphasis
    simSettings.transmitter.EQ.addEqualization = True
    simSettings.transmitter.EQ.taps.pre3  = valueWithLimits(-0.00)
    simSettings.transmitter.EQ.taps.pre2  = valueWithLimits(-0.00)
    simSettings.transmitter.EQ.taps.pre1  = valueWithLimits(-0.10)
    simSettings.transmitter.EQ.taps.main  = valueWithLimits( 1.00) # calculated automatically
    simSettings.transmitter.EQ.taps.post1 = valueWithLimits(-0.00)
    simSettings.transmitter.EQ.taps.post2 = valueWithLimits(-0.00)
    simSettings.transmitter.EQ.taps.post3 = valueWithLimits(-0.00)
    simSettings.transmitter.EQ.taps.post4 = valueWithLimits(-0.00)
    simSettings.transmitter.EQ.taps.post5 = valueWithLimits(-0.00)

    # Jitter
    simSettings.transmitter.jitter.addJitter = False
    simSettings.transmitter.jitter.stdDeviation.value = 0 # TX random jitter standard diviation [UI]
    simSettings.transmitter.jitter.amplitude.value = 0    # TX deterministic jitter amplitude [UI]
    simSettings.transmitter.jitter.DCD.value = 0          # TX duty-cycle distortion jitter [UI]
    
    # Noise
    simSettings.transmitter.noise.addNoise = True
    simSettings.transmitter.noise.stdDeviation.value = sqrt(simSettings.transmitter.signalAmplitude.value**2/2/pow(10, (6*6.01+1.76)/10)) # TX random noise standard diviation [V]
    simSettings.transmitter.noise.amplitude.value = 0    # TX deterministic noise amplitude [V]
    simSettings.transmitter.noise.frequency.value = 1e6  # TX deterministic noise frequency [Hz]

    # Distortion
    simSettings.transmitter.distortion.addDistortion = False
    simSettings.transmitter.distortion.fileName = 'distortionTX.mat'
    
    ########################################
    # Channel settings
    ########################################
    # Apply channel/cross-talk
    simSettings.channel.addChannel = True
    simSettings.channel.addCrossTalk = True
    
    # Add notch (must update transfer function)
    simSettings.channel.addNotch = False
    simSettings.channel.notchFreq.value = 20e9      # frequency of notch
    simSettings.channel.notchAttenuation.value = 20 # attenuation at notch [dB]
       
    # Convolve pulse response (convolve all channels with additional transfer function, must update transfer function)
    simSettings.channel.modelCircuitTF = False
    simSettings.channel.modelCircuitTFName = "LNATransferFunction.mat"
    
    # Override channel pulse response (must have same over-sampling frequency)
    simSettings.channel.overrideResponse = False
    simSettings.channel.overrideFileName = 'LNAPulseResponse.mat'  
    
    # Approximate cross-talk to speed up simulation
    simSettings.channel.approximate = True
    
    # Make cross-talk channels asynchronous
    simSettings.channel.makeAsynchronous = True

    # Channel file names (ensure channel data has same frequency points)
    simSettings.channel.fileNames.thru = 'C2M__Z100_IL14_WC_BOR_H_L_H_THRU.s4p'
    simSettings.channel.fileNames.next1 = 'C2M__Z100_IL14_WC_BOR_H_L_H_NEXT1.s4p'
    simSettings.channel.fileNames.next2 = 'C2M__Z100_IL14_WC_BOR_H_L_H_NEXT2.s4p'
    simSettings.channel.fileNames.next3 = 'C2M__Z100_IL14_WC_BOR_H_L_H_NEXT3.s4p'
    simSettings.channel.fileNames.next4 = 'C2M__Z100_IL14_WC_BOR_H_L_H_NEXT4.s4p'
    simSettings.channel.fileNames.fext1 = 'C2M__Z100_IL14_WC_BOR_H_L_H_FEXT1.s4p'
    simSettings.channel.fileNames.fext2 = 'C2M__Z100_IL14_WC_BOR_H_L_H_FEXT2.s4p'
    simSettings.channel.fileNames.fext3 = 'C2M__Z100_IL14_WC_BOR_H_L_H_FEXT3.s4p'

    # Noise
    simSettings.channel.noise.addNoise = True
    simSettings.channel.noise.noiseDensity.value = 5.2e-17*3 # channel noise density [V^2/Hz]
    
    ########################################
    # Receiver settings
    ########################################
    # Maximum amplitude [V]
    simSettings.receiver.signalAmplitude.value = 0.2
    
    # PreAmp
    simSettings.receiver.preAmp.addGain = True
    simSettings.receiver.preAmp.gain.value = 0.5

    # CTLE
    simSettings.receiver.CTLE.addEqualization = True    
    simSettings.receiver.CTLE.zeroFreq.value  = 20.5e9 # frequency of first zero [Hz]
    simSettings.receiver.CTLE.zeroNumb.value  = 1      # number of zeros
    simSettings.receiver.CTLE.pole1Freq.value = 29.0e9 # frequency of first pole [Hz]
    simSettings.receiver.CTLE.pole1Numb.value = 1      # number of first poles
    simSettings.receiver.CTLE.pole2Freq.value = 30.0e9 # frequency of additional poles [Hz]
    simSettings.receiver.CTLE.pole2Numb.value = 3      # number of additional poles
    
    # FFE
    simSettings.receiver.FFE.addEqualization = True
    simSettings.receiver.FFE.taps.pre3  = valueWithLimits(-0.00)
    simSettings.receiver.FFE.taps.pre2  = valueWithLimits(-0.00)
    simSettings.receiver.FFE.taps.pre1  = valueWithLimits( 0.05)
    simSettings.receiver.FFE.taps.main  = valueWithLimits( 1.10)
    simSettings.receiver.FFE.taps.post1 = valueWithLimits(-0.30)
    simSettings.receiver.FFE.taps.post2 = valueWithLimits(-0.05)
    simSettings.receiver.FFE.taps.post3 = valueWithLimits(-0.00)
    simSettings.receiver.FFE.taps.post4 = valueWithLimits(-0.00)
    simSettings.receiver.FFE.taps.post5 = valueWithLimits(-0.00)
    
    # DFE
    simSettings.receiver.DFE.addEqualization = False
    simSettings.receiver.DFE.taps.post1 = valueWithLimits(-0.00)
    simSettings.receiver.DFE.taps.post2 = valueWithLimits(-0.00)
    simSettings.receiver.DFE.taps.post3 = valueWithLimits(-0.00)
    simSettings.receiver.DFE.taps.post4 = valueWithLimits(-0.00)
    simSettings.receiver.DFE.taps.post5 = valueWithLimits(-0.00)
    
    # Jitter
    simSettings.receiver.jitter.addJitter = True
    simSettings.receiver.jitter.stdDeviation.value = 0.02 # CDR random jitter standard diviation [UI]
    simSettings.receiver.jitter.amplitude.value = 0    # CDR deterministic jitter amplitude [UI]
    simSettings.receiver.jitter.DCD.value = 0          # CDR duty-cycle distortion jitter [UI]
    
    # Noise
    simSettings.receiver.noise.addNoise = True
    simSettings.receiver.noise.stdDeviation.value = 1e-3 #sqrt((2.4e-3)^2+(1.5e-3)^2) # RX random noise standard diviation [V]
    simSettings.receiver.noise.amplitude.value = 0    # RX deterministic noise amplitude [V]
    simSettings.receiver.noise.frequency.value = 1e6  # RX deterministic noise frequency [Hz]
    
    # Distortion
    simSettings.receiver.distortion.addDistortion = False
    simSettings.receiver.distortion.fileName = 'distortionRX.mat'

    return simSettings