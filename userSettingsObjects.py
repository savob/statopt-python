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

    def __init__(self, val: float):
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
    addCoding: bool = False
    gain: valueWithLimits

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
    adapt: bool = False
    
    # Adaption complexity
    totalParents: valueWithLimits
    childrenPerParent: valueWithLimits
    totalMutations: valueWithLimits
    mode1Generations: valueWithLimits # coarse adjustment
    mode2Generations: valueWithLimits # fine adjustment

    knobs: List[str]


@dataclass
class distortionSetting:
    addDistortion: bool = False
    fileName: str = 'distortionTX.mat'

@dataclass
class noiseSettings:
    addNoise: bool = False
    stdDeviation: valueWithLimits   # TX random noise standard diviation [V]
    amplitude: valueWithLimits      # TX deterministic noise amplitude [V]
    frequency: valueWithLimits      # TX deterministic noise frequency [Hz]
    noiseDensity: valueWithLimits   # Noise density [V^2/Hz]

@dataclass
class jitterSettings:
    addJitter: bool = False
    stdDeviation: valueWithLimits # TX random jitter standard diviation [UI]
    amplitude: valueWithLimits    # TX deterministic jitter amplitude [UI]
    DCD: valueWithLimits          # TX duty-cycle distortion jitter [UI]

@dataclass
class equalizerSettings:
    addEqualization: bool = False
    preTaps: List[valueWithLimits]
    mainTap: valueWithLimits 
    postTaps: List[valueWithLimits]


@dataclass
class transmitterSettings:
    # Maximum amplitude [V]
    signalAmplitude: valueWithLimits
    
    # Add source impedance (drop amplitude by half)
    includeSourceImpedance: bool = True
    
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

@dataclass
class preAmpSettings:
    addGain: bool = False
    gain: float

@dataclass
class CTLESettings:
    addEqualization: bool = False    
    zeroFreq: valueWithLimits       # frequency of first zero [Hz]
    zeroNumb: valueWithLimits       # number of zeros
    pole1Freq: valueWithLimits      # frequency of first pole [Hz]
    pole1Numb: valueWithLimits      # number of first poles
    pole2Freq: valueWithLimits      # frequency of additional poles [Hz]
    pole2Numb: valueWithLimits      # number of additional poles

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
    # Apply channel/cross-talk
    addChannel: bool = True
    addCrossTalk: bool = True
    
    # Add notch (must update transfer function)
    addNotch: bool = False
    notchFreq: valueWithLimits      # frequency of notch
    notchAttenuation: valueWithLimits # attenuation at notch [dB]
       
    # Convolve pulse response (convolve all channels with additional transfer function, must update transfer function)
    modelCircuitTF: bool = False
    modelCircuitTFName: str
    
    # Override channel pulse response (must have same over-sampling frequency)
    overrideResponse: bool = False
    overrideFileName: str 
    
    # Approximate cross-talk to speed up simulation
    approximate: bool = True
    
    # Make cross-talk channels asynchronous
    makeAsynchronous: bool = True

    # Channel file names (ensure channel data has same frequency points)
    fileNames: dict

    # Noise
    noise: noiseSettings


# The complete compiled class for all simulation settings
@dataclass
class simulationSettings:
    general: generalSettings
    adaption: adaptionSettings
    transmitter: transmitterSettings
    channel: channelSettings
    receiver: receiverSettings