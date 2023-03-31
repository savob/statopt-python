from dataclasses import dataclass, field
from typing import List
from numpy import ndarray, empty

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
class valueList:
    value: ndarray = empty(0)

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
    gain: valueWithLimits = valueWithLimits()
    

@dataclass
class generalSettings:
    symbolRate: valueWithLimits = valueWithLimits() #symbol rate [S/s] (or 2x frequency [Hz])
    symbolPeriod: valueWithLimits = valueWithLimits()
    sampleRate: valueWithLimits = valueWithLimits()
    samplePeriod: valueWithLimits = valueWithLimits()

    # Signaling mode ('standard','1+D','1+0.5D','clock')
    signalingMode: str = 'standard'
    
    # Coding gain
    codingGain: codingGainSettings = codingGainSettings()
    
    # Modulation (M-PAM)
    modulation: valueWithLimits = valueWithLimits()
    
    # Resolution
    samplesPerSymb: valueWithLimits = valueWithLimits() # horizontal resolution
    yAxis: valueList = valueList()
    yAxisLength: valueWithLimits = valueWithLimits()    # vertical resolution (must be odd)
    yIncrement: valueWithLimits = valueWithLimits()
    xAxisCenter: valueList = valueList()
    xAxisLong: valueList = valueList()
    
    # General display
    numbSymb: valueWithLimits = valueWithLimits()    # number of symbols to plot
    contLevels: valueWithLimits = valueWithLimits() # number of contour levels
    levelNumb: valueWithLimits = valueWithLimits()
    samplerNumb: valueWithLimits = valueWithLimits()
        
    # Target BER
    targetBER: valueWithLimits = valueWithLimits() # used for measurement purposes

    plotting: plottingSettings = plottingSettings()

@dataclass
class originalSettings:
    modulation: valueWithLimits = valueWithLimits()
    levelNumb: valueWithLimits = valueWithLimits()
    samplerNumb: valueWithLimits = valueWithLimits()
    preCursorCount: valueWithLimits = valueWithLimits()
    postCursorCount: valueWithLimits = valueWithLimits()
    cursorCount: valueWithLimits = valueWithLimits()

@dataclass
class adaptionSettings:

    adapt: bool = False
    knobs: list = field(default_factory=lambda : [])

    # Adaption complexity
    totalParents: valueWithLimits = valueWithLimits()
    childrenPerParent: valueWithLimits = valueWithLimits()
    totalMutations: valueWithLimits = valueWithLimits()
    mode1Generations: valueWithLimits = valueWithLimits()# coarse adjustment
    mode2Generations: valueWithLimits = valueWithLimits() # fine adjustment

    totalSimulations: valueWithLimits = valueWithLimits()
    totalPopulation: valueWithLimits = valueWithLimits()

    speedUpSim: bool = False
    savedSettings: originalSettings = originalSettings()

@dataclass
class distortionSetting:
    addDistortion: bool = False
    fileName: str = ''
    

class noiseSettings:
    def __init__(self):
        self.addNoise: bool = False
        self.stdDeviation: valueWithLimits = valueWithLimits()   # TX random noise standard diviation [V]
        self.amplitude: valueWithLimits = valueWithLimits()      # TX deterministic noise amplitude [V]
        self.frequency: valueWithLimits = valueWithLimits()      # TX deterministic noise frequency [Hz]
        self.noiseDensity: valueWithLimits = valueWithLimits()   # Noise density [V^2/Hz]

@dataclass
class jitterSettings:
    addJitter: bool = False
    stdDeviation: valueWithLimits = valueWithLimits() # TX random jitter standard diviation [UI]
    amplitude: valueWithLimits = valueWithLimits()    # TX deterministic jitter amplitude [UI]
    DCD: valueWithLimits = valueWithLimits()          # TX duty-cycle distortion jitter [UI]


class equalizerSettings:
    def __init__(self):
        self.addEqualization = False
        self.preTaps = []
        self.mainTap = valueWithLimits() 
        self.postTaps = []


@dataclass
class transmitterSettings:
    
    signalAmplitude: valueWithLimits = valueWithLimits() # Maximum amplitude [V]
    TXBandwidth: valueWithLimits = valueWithLimits() # TX bandwidth [Hz]
    
    # Impulse cursor length
    preCursorCount: valueWithLimits = valueWithLimits()
    postCursorCount: valueWithLimits = valueWithLimits()
    cursorCount: valueWithLimits = valueWithLimits()
    tRise: valueWithLimits = valueWithLimits() # Rise/fall time [s]

    EQ: equalizerSettings = equalizerSettings() # Pre-emphasis
    jitter: jitterSettings = jitterSettings()
    noise: noiseSettings = noiseSettings()
    distortion: distortionSetting = distortionSetting()
    includeSourceImpedance: bool = True # Add source impedance (drop amplitude by half)

@dataclass
class preAmpSettings:
    addGain: bool = False
    gain: valueWithLimits = valueWithLimits()

@dataclass
class CTLESettings: 
    zeroFreq: valueWithLimits = valueWithLimits()      # frequency of first zero [Hz]
    zeroNumb: valueWithLimits = valueWithLimits()       # number of zeros
    pole1Freq: valueWithLimits = valueWithLimits()      # frequency of first pole [Hz]
    pole1Numb: valueWithLimits = valueWithLimits()      # number of first poles
    pole2Freq: valueWithLimits = valueWithLimits()      # frequency of additional poles [Hz]
    pole2Numb: valueWithLimits = valueWithLimits()      # number of additional poles
    addEqualization: bool = False   

@dataclass
class receiverSettings:
    
    signalAmplitude: valueWithLimits = valueWithLimits() # Maximum amplitude [V]
    preAmp: preAmpSettings = preAmpSettings()
    CTLE: CTLESettings = CTLESettings()
    FFE: equalizerSettings = equalizerSettings()
    DFE: equalizerSettings = equalizerSettings()
    jitter: jitterSettings = jitterSettings()
    noise: noiseSettings = noiseSettings()
    distortion: distortionSetting = distortionSetting()

@dataclass
class fileNamesHolder:
    pass

@dataclass
class channelSettings:

    # Apply channel/cross-talk
    addChannel: bool = True
    addCrossTalk: bool = True

    # Noise
    noise: noiseSettings = noiseSettings()

    # Add notch (must update transfer function)
    notchFreq: valueWithLimits = valueWithLimits()     # frequency of notch
    notchAttenuation: valueWithLimits = valueWithLimits() # attenuation at notch [dB]
    addNotch: bool = False
       
    # Convolve pulse response (convolve all channels with additional transfer function, must update transfer function)
    modelCircuitTF: bool = False
    modelCircuitTFName: str = ''

    # Override channel pulse response (must have same over-sampling frequency)
    overrideResponse: bool = False
    overrideFileName: str = ''
    
    # Approximate cross-talk to speed up simulation
    approximate: bool = True
    
    # Make cross-talk channels asynchronous
    makeAsynchronous: bool = True

    # Channel file names (ensure channel data has same frequency points)
    fileNames: fileNamesHolder = fileNamesHolder()


# The complete compiled class for all simulation settings
@dataclass
class simulationSettings:
    general: generalSettings = generalSettings()
    adaption: adaptionSettings = adaptionSettings()
    transmitter: transmitterSettings = transmitterSettings()
    channel: channelSettings = channelSettings()
    receiver: receiverSettings = receiverSettings()
