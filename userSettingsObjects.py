from dataclasses import dataclass
from typing import List

# Generic dataclass for any value that may have an associated increment and limits for both.
@dataclass(init=False)
class valueWithLimits: 
    value: float = float("nan")
    maxValue: float = float("nan")
    minValue: float = float("nan")
    increment: float = float("nan")
    minIncrement: float = float("nan")
    maxIncrement: float = float("nan")

    def __init__(self, val: float = float("nan")):
        self.value = val

@dataclass
class plottingSettings:
    # Display responses
    channelResponse: bool = False
    CTLEResponse: bool    = False
    pulseResponse: bool   = False
    
    # Display inteferences
    jitterSource: bool     = False
    noiseSource: bool      = False
    distortionSource: bool = False
    
    # Display probability distributions
    ISI: bool              = False # CAREFUL: CAN BE SLOW TO PLOT!
    PDFInitial: bool       = False
    PDFCrossTalk: bool     = False
    PDFDistorted: bool     = False
    PDFJitter: bool        = False
    PDFNoise: bool         = False
    PDFFinal: bool         = False
    
    # Display bit-error rate distributions
    BER: bool = False            # plot BER contour over BER
    BER2: bool = False           # plot BER contour over PDF
    
    # Display measurement results
    results: bool = False

@dataclass
class codingGainSettings:
    gain: valueWithLimits
    addCoding: bool = False
    

@dataclass
class generalSettings:
    symbolRate: valueWithLimits #symbol rate [S/s] (or 2x frequency [Hz])
        
    # Signaling mode ('standard','1+D','1+0.5D','clock')
    signalingMode: str
    
    # Coding gain
    codingGain: codingGainSettings
    
    # Modulation (M-PAM)
    modulation: valueWithLimits
    
    # Resolution
    samplesPerSymb: valueWithLimits # horizontal resolution
    yAxisLength: valueWithLimits    # vertical resolution (must be odd)
    
    # General display
    numbSymb: valueWithLimits    # number of symbols to plot
    contLevels: valueWithLimits # number of contour levels
        
    # Target BER
    targetBER: valueWithLimits # used for measurement purposes

    plotting: plottingSettings

@dataclass
class adaptionSettings:

    # Adaption complexity
    totalParents: valueWithLimits
    childrenPerParent: valueWithLimits
    totalMutations: valueWithLimits
    mode1Generations: valueWithLimits # coarse adjustment
    mode2Generations: valueWithLimits # fine adjustment

    knobs: List[str]

    adapt: bool = False


@dataclass
class distortionSetting:
    fileName: str
    addDistortion: bool = False
    

@dataclass
class noiseSettings:
    stdDeviation: valueWithLimits   # TX random noise standard diviation [V]
    amplitude: valueWithLimits      # TX deterministic noise amplitude [V]
    frequency: valueWithLimits      # TX deterministic noise frequency [Hz]
    noiseDensity: valueWithLimits   # Noise density [V^2/Hz]
    addNoise: bool = False

@dataclass
class jitterSettings:
    stdDeviation: valueWithLimits # TX random jitter standard diviation [UI]
    amplitude: valueWithLimits    # TX deterministic jitter amplitude [UI]
    DCD: valueWithLimits          # TX duty-cycle distortion jitter [UI]
    addJitter: bool = False

@dataclass
class equalizerSettings:
    preTaps: List[valueWithLimits]
    mainTap: valueWithLimits 
    postTaps: List[valueWithLimits]
    addEqualization: bool = False


@dataclass
class transmitterSettings:
    # Maximum amplitude [V]
    signalAmplitude: valueWithLimits
    
    # Rise/fall time [s]
    tRise: valueWithLimits
    
    # TX bandwidth [Hz]
    TXBandwidth: valueWithLimits
    
    # Impulse cursor length
    preCursorCount: valueWithLimits 
    postCursorCount: valueWithLimits

    # Pre-emphasis
    EQ: equalizerSettings

    # Jitter
    jitter: jitterSettings
    
    # Noise
    noise: noiseSettings

    # Distortion
    distortion: distortionSetting

    # Add source impedance (drop amplitude by half)
    includeSourceImpedance: bool = True

@dataclass
class preAmpSettings:
    gain: valueWithLimits
    addGain: bool = False

@dataclass
class CTLESettings: 
    zeroFreq: valueWithLimits       # frequency of first zero [Hz]
    zeroNumb: valueWithLimits       # number of zeros
    pole1Freq: valueWithLimits      # frequency of first pole [Hz]
    pole1Numb: valueWithLimits      # number of first poles
    pole2Freq: valueWithLimits      # frequency of additional poles [Hz]
    pole2Numb: valueWithLimits      # number of additional poles
    addEqualization: bool = False   

@dataclass
class receiverSettings:
    # Maximum amplitude [V]
    signalAmplitude: valueWithLimits
    
    # PreAmp
    preAmp: preAmpSettings

    # CTLE
    CTLE: CTLESettings
    
    # FFE
    FFE: equalizerSettings
    
    # DFE
    DFE: equalizerSettings
    
    # Jitter
    jitter: jitterSettings
    
    # Noise
    noise: noiseSettings
    
    # Distortion
    distortion: distortionSetting


@dataclass
class channelSettings:
        # Channel file names (ensure channel data has same frequency points)
    fileNameThru: str
    fileNamesNEXT: List[str]
    fileNamesFEXT: List[str]

    # Noise
    noise: noiseSettings

    overrideFileName: str 

    modelCircuitTFName: str
    

    
    # Add notch (must update transfer function)
    notchFreq: valueWithLimits      # frequency of notch
    notchAttenuation: valueWithLimits # attenuation at notch [dB]
    addNotch: bool = False
       
    # Convolve pulse response (convolve all channels with additional transfer function, must update transfer function)
    modelCircuitTF: bool = False

    # Override channel pulse response (must have same over-sampling frequency)
    overrideResponse: bool = False
    
    
    # Approximate cross-talk to speed up simulation
    approximate: bool = True
    
    # Make cross-talk channels asynchronous
    makeAsynchronous: bool = True

    # Apply channel/cross-talk
    addChannel: bool = True
    addCrossTalk: bool = True



# The complete compiled class for all simulation settings
@dataclass
class simulationSettings:
    general: generalSettings
    adaption: adaptionSettings
    transmitter: transmitterSettings
    channel: channelSettings
    receiver: receiverSettings
