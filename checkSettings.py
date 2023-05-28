###########################################################################
#
#   StatEye Simulator
#   by Jeremy Cosson-Martin, Jhoan Salinas of
#   Ali Sheikholeslami's group
#   Ported to Python 3 by Savo Bajic
#   Department of Electrical and Computer Engineering
#   University of Toronto
#   Copyright Material
#   For personal use only
#
###########################################################################
# Checks the user's settings to verify if they fall within the expected 
# limits for given values as well as if they match the prescribed 
# increments for said value. Should any be found out of range an error is 
# raised detailing the issue and the simulation is halted.
#
# Inputs:
#   simSettings: structure containing simulation settings
#   
###########################################################################

from userSettingsObjects import simulationSettings, valueWithLimits
from initializeSimulation import simulationStatus
from warnings import warn
from math import pow, isnan

differenceTolerance = 0.00001 # Accepable deviation (absolute) between values to be considered equal (to deal with representation)

class badSettingException(Exception):
    def __str__(self):
        return 'An invalid setting has been encountered'

    def __repr__(self):
        return str(type(self))
    
def error(message: str):
    print('{:s}'.format(message))
    raise badSettingException

def checkSettings(simSettings: simulationSettings):

    # Check speed settings
    checkGeneralSettings(simSettings)
    
    # Check adaption settings
    checkAdaptionSettings(simSettings)
    
    # Check transmitter settings
    checkTransmitterSettings(simSettings)
    
    # Check channel settings
    checkChannelSettings(simSettings)
    
    # Check receiver settings
    checkReceiverSettings(simSettings)

    # Print confirmation of setting validity
    print('Settings are all verified to fall within specified limits')
    
    # Estimate simulation time
    checkSimTime(simSettings)


###########################################################################
# This function checks all general simulation settings.
###########################################################################
def checkGeneralSettings(simSettings: simulationSettings):

    # Rate limits
    checkLimits(simSettings.general.symbolRate, 'general.symbolRate')
    checkLimits(simSettings.general.symbolPeriod, 'general.symbolPeriod')
    checkLimits(simSettings.general.sampleRate, 'general.sampleRate')
    checkLimits(simSettings.general.samplePeriod, 'general.samplePeriod')
    
    # Accuracy limits
    checkLimits(simSettings.general.samplesPerSymb, 'general.samplesPerSymb')
    checkLimits(simSettings.general.yAxisLength, 'general.yAxisLength')
    checkLimits(simSettings.general.yIncrement, 'general.yIncrement')
    checkLimits(simSettings.general.contLevels, 'general.contLevels')
    
    # Other limits
    checkLimits(simSettings.general.modulation, 'general.modulation')
    checkLimits(simSettings.general.levelNumb, 'general.levelNumb')
    checkLimits(simSettings.general.samplerNumb, 'general.samplerNumb')
    checkLimits(simSettings.general.numbSymb, 'general.numbSymb')

    allowedSignalingModes = ['standard', '1+D', '1+0.5D', 'clock']
    if not simSettings.general.signalingMode in allowedSignalingModes:
        print('Allowed signalling modes:')
        print(allowedSignalingModes)
        error('unrecognized signaling mode!')
    


###########################################################################
# This function checks all adaption simulation settings.
###########################################################################
def checkAdaptionSettings(simSettings: simulationSettings):

    checkLimits(simSettings.adaption.totalSimulations, 'adaption.totalSimulations')
    checkLimits(simSettings.adaption.totalPopulation, 'adaption.totalPopulation')
    checkLimits(simSettings.adaption.totalParents, 'adaption.totalParents')
    checkLimits(simSettings.adaption.childrenPerParent, 'adaption.childrenPerParent')
    checkLimits(simSettings.adaption.totalMutations, 'adaption.totalMutations')
    checkLimits(simSettings.adaption.mode1Generations, 'adaption.mode1Generations')
    checkLimits(simSettings.adaption.mode2Generations, 'adaption.mode2Generations')
    adaption=simSettings.adaption

    if (adaption.totalParents.value + adaption.childrenPerParent.value * adaption.totalParents.value + adaption.totalMutations.value != adaption.totalPopulation.value):
        error('adaption population groups must add up to total population!')
    
    if (adaption.mode1Generations.value==0 and adaption.mode2Generations.value == 0):
        error('adaption must have at least one generation!')
    
    if (simSettings.adaption.adapt):
        if simSettings.adaption.knobs == False: # Empty lists are False
            error('adaption is desired however no knobs are specified!')
        
        for knobName in simSettings.adaption.knobs:
            if knobName[0:14] == 'transmitter.EQ' and not simSettings.transmitter.EQ.addEqualization:
                warn('adaption cannot adjust TX EQ because it is not enabled!')
            
            if knobName[0:15] =='receiver.preAmp' and not simSettings.receiver.preAmp.addGain:
                warn('adaption cannot adjust RX gain because it is not enabled!')
            
            if knobName[0:13] == 'receiver.CTLE' and not simSettings.receiver.CTLE.addEqualization:
                warn('adaption cannot adjust RX CTLE because it is not enabled!')
            
            if knobName[0:12] == 'receiver.FFE' and not simSettings.receiver.FFE.addEqualization:
                warn('adaption cannot adjust RX FFE because it is not enabled!')
            
            if knobName[0:12] == 'receiver.DFE' and not simSettings.receiver.DFE.addEqualization:
                warn('adaption cannot adjust RX DFE because it is not enabled!')
            
        # Check if exclusively one of zeroFreq and pole1Freq are getting tuned
        pole1Tuned = 'receiver_CTLE_pole1Freq' in simSettings.adaption.knobs
        zeroTuned = 'receiver_CTLE_zeroFreq' in simSettings.adaption.knobs
        if pole1Tuned ^ zeroTuned: # XOR
            error('if adapting CTLE settings, must add both zero and pole1 frequency knobs!')
        
        if(simSettings.channel.overrideResponse):
            error('equalization has no effect when overwriting pulse response!')
        
    


###########################################################################
# This function checks all transmitter settings.
###########################################################################
def checkTransmitterSettings(simSettings: simulationSettings):
    
    # Input voltage
    checkLimits(simSettings.transmitter.signalAmplitude, 'transmitter.signalAmplitude')
    
    # TX rise/fall time
    checkLimits(simSettings.transmitter.tRise, 'transmitter.tRise')
    
    # TX bandwidth
    checkLimits(simSettings.transmitter.TXBandwidth, 'transmitter.TXBandwidth')
    
    # Impulse cursor length
    checkLimits(simSettings.transmitter.preCursorCount, 'transmitter.preCursorCount')
    checkLimits(simSettings.transmitter.postCursorCount, 'transmitter.postCursorCount')
    checkLimits(simSettings.transmitter.cursorCount, 'transmitter.cursorCount')
    
    # Pre-emphasis
    for tap in simSettings.transmitter.EQ.taps.__dict__:
        checkLimits(simSettings.transmitter.EQ.taps.__dict__[tap], 'transmitter.EQ.taps.{0}'.format(tap))
    
    
    # Jitter
    checkLimits(simSettings.transmitter.jitter.stdDeviation, 'transmitter.jitter.stdDeviation')
    checkLimits(simSettings.transmitter.jitter.amplitude, 'transmitter.jitter.amplitude')
    checkLimits(simSettings.transmitter.jitter.DCD, 'transmitter.jitter.DCD')
    
    # Noise
    checkLimits(simSettings.transmitter.noise.stdDeviation, 'transmitter.noise.stdDeviation')
    checkLimits(simSettings.transmitter.noise.amplitude, 'transmitter.noise.amplitude')
    checkLimits(simSettings.transmitter.noise.frequency, 'transmitter.noise.frequency')


###########################################################################
# This function checks all channel settings.
###########################################################################
def checkChannelSettings(simSettings: simulationSettings):

    if(simSettings.channel.overrideResponse and simSettings.channel.addChannel):
        warn('pulse override desired, removing all channels!')
        simSettings.channel.addChannel = False        
    
    if not simSettings.channel.addChannel:
        if simSettings.channel.addCrossTalk:
            warn('channel is not applied, thus removing all cross-talk!')
            simSettings.channel.addCrossTalk = False
    
        if simSettings.transmitter.noise.addNoise:
            warn('channel is not applied, thus cannot calculate TX-noise!')
            simSettings.transmitter.noise.addNoise = False
    
        if simSettings.channel.noise.addNoise:
            warn('channel is not applied, thus removing all channel-noise!')
            simSettings.channel.noise.addNoise = False
        
        if simSettings.general.plotting.channelResponse or simSettings.general.plotting.CTLEResponse:
            warn('frequency response and CTLE not used and thus is not displayed!')
            simSettings.general.plotting.channelResponse = False
            simSettings.general.plotting.CTLEResponse = False
    
    # Check channel files for allowed extensions
    for channel in simSettings.channel.fileNames.__dict__:
        if not ((simSettings.channel.fileNames.__dict__[channel][-4:] == '.s4p') or (simSettings.channel.fileNames.__dict__[channel][-4:] == '.mat')):
            print('Invalid file extension for channel file with filename of "{0}"'.format(simSettings.channel.fileNames.__dict__[channel]))
            error('unknown channel file type detected, please ensure using .mat or .s4p files!')
        
    
    if simSettings.channel.fileNames.thru == False:
        error('must have file for thruough channel!')
        
    numberOfChannelFiles = len(simSettings.channel.fileNames.__dict__)
    if simSettings.channel.addCrossTalk and (numberOfChannelFiles < 2):
        warn('to have cross-talk, must add references to more than one channel!')
    
    
    checkLimits(simSettings.channel.noise.noiseDensity, 'channel.noise.noiseDensity')


###########################################################################
# This function checks all receiver settings.
###########################################################################
def checkReceiverSettings(simSettings: simulationSettings):

    # Maximum amplitude
    checkLimits(simSettings.receiver.signalAmplitude, 'receiver.signalAmplitude')
    
    # Pre-amp
    checkLimits(simSettings.receiver.preAmp.gain, 'receiver.preAmp.gain')
    
    # CTLE
    checkLimits(simSettings.receiver.CTLE.zeroFreq, 'receiver.CTLE.zeroFreq')
    checkLimits(simSettings.receiver.CTLE.zeroNumb, 'receiver.CTLE.zeroNumb')
    checkLimits(simSettings.receiver.CTLE.pole1Freq, 'receiver.CTLE.pole1Freq')
    checkLimits(simSettings.receiver.CTLE.pole1Numb, 'receiver.CTLE.pole1Numb')
    checkLimits(simSettings.receiver.CTLE.pole2Freq, 'receiver.CTLE.pole2Freq')
    checkLimits(simSettings.receiver.CTLE.pole2Numb, 'receiver.CTLE.pole2Numb')
    if simSettings.receiver.CTLE.zeroFreq.value > simSettings.receiver.CTLE.pole1Freq.value:
        error('receiver CTLE zero frequency must be less than its poles!')
    
    if simSettings.receiver.CTLE.pole1Freq.value > simSettings.receiver.CTLE.pole2Freq.value:
        error('receiver CTLE additional pole frequencies must be greater than its first poles!')
    
    
    # FFE
    for tap in simSettings.receiver.FFE.taps.__dict__:
        checkLimits(simSettings.receiver.FFE.taps.__dict__[tap], 'receiver.FFE.taps.{0}'.format(tap))
    
    # DFE
    for tap in simSettings.receiver.DFE.taps.__dict__:
        checkLimits(simSettings.receiver.DFE.taps.__dict__[tap], 'receiver.DFE.taps.{0}'.format(tap))
    
    
    # Jitter
    checkLimits(simSettings.receiver.jitter.stdDeviation, 'receiver.jitter.stdDeviation')
    checkLimits(simSettings.receiver.jitter.amplitude, 'receiver.jitter.amplitude')
    checkLimits(simSettings.receiver.jitter.DCD, 'receiver.jitter.DCD')
    
    # Noise
    checkLimits(simSettings.receiver.noise.stdDeviation, 'receiver.noise.stdDeviation')
    checkLimits(simSettings.receiver.noise.amplitude, 'receiver.noise.amplitude')


###########################################################################
# This function checks the boundary conditions. It ensures it within the
# limits and a multiple of the minimum increment if desired. If a violation
# is made, an error message is displayed.
###########################################################################
def checkLimits(setting: valueWithLimits, nameOfsetting: str):

    # Check requirements if they're defined (not NaN, the default)
    if isnan(setting.value):
        return # Do not check values for undefined values
    elif (not isnan(setting.maxValue)) and setting.value > setting.maxValue:
        error('{0} ({2:f}) must not excede {1:f}!'.format(nameOfsetting, setting.maxValue, setting.value))
    elif (not isnan(setting.minValue)) and setting.value < setting.minValue:
        error('{0} ({2:f}) must be larger than {1:f}!'.format(nameOfsetting, setting.minValue, setting.value))
    elif (not isnan(setting.increment)):

        # Check if the value meets some specific increment from a baseline
        baseline = 0
        if not isnan(setting.minValue):
            baseline = setting.minValue
        adjustedValue = setting.value-baseline # Find value relative to baseline

        # Do both checks since sometimes mod on it's own doesn't like floats. E.g. "1 % 0.05" is 0.005, but "1 / 0.05" is 20.0  
        modulus = adjustedValue % setting.increment
        divisionNormal = adjustedValue / setting.increment
        divisionRounded = round(divisionNormal)

        # Given the representation in Python for floats and division/mutliplication we may not get nice divisions.
        # We can check if our results are approximately equal if all else fails
        # A case which needs this is checking if -0.3 falls between -1 and 1, with increments of 0.05.
        if divisionRounded != divisionNormal:
            differenceFromRounded = abs(divisionRounded - divisionNormal)
        else:
            differenceFromRounded = 0

        if (modulus != 0) and (differenceFromRounded > differenceTolerance):
            error('{0} ({3:f}) must be a multiple of the minimum increment {1:f} starting from {2:f}!'.format(nameOfsetting, setting.increment, baseline, setting.value))
    


###########################################################################
# This function warns the user if the expected simulation time exceeds 5
# minutes. The user is prompted with the option to continue or cancel
# the simulation.
###########################################################################
def checkSimTime(simSettings: simulationSettings):
    
    # Import variables
    signalingMode    = simSettings.general.signalingMode
    samplesPerSymb   = simSettings.general.samplesPerSymb.value
    yAxisLength      = simSettings.general.yAxisLength.value
    channels         = simSettings.channel
    addCrossTalk     = simSettings.channel.addCrossTalk
    modulation       = simSettings.general.modulation
    cursorCount      = simSettings.transmitter.cursorCount
    xTalkApprox      = simSettings.channel.approximate
    adapt            = simSettings.adaption.adapt
    totalSimulations = simSettings.adaption.totalSimulations
    
    # Determine number of channels
    if addCrossTalk:
        if xTalkApprox:
            chanNumb = 2
        else:
            chanNumb = len(channels.fileNames)
    else:
        chanNumb = 1
    
        
    # Determine number of calculations
    if signalingMode == 'clock':
        calculations = 2*modulation.value
    else:
        calculations = pow(modulation.value, cursorCount.value)
    
    
    # Determine approximate simulation time
    # TODO: #1 Update these coefficients with tests from Python (these are the ones taken from MATLAB)
    simTime = []
    simTime.append(0.8 * chanNumb)                                     # Generate sources
    simTime.append(2e-2 * chanNumb)                                    # Generate pulse response
    simTime.append(3.2e-4 * chanNumb * calculations)                   # Generate ISI
    simTime.append(0.6 * chanNumb * modulation.value)                  # Generate PDF
    simTime.append(0.5)                                                # Generate BER
    simTime.append(0.7 * chanNumb * totalSimulations.value * adapt)    # Adaption
    simTime.append(2.0)                                                # Plotting (assumes plotting channel, impulse, CTLE, PDF and BER)
    
    # Total the time
    totalTime = sum(simTime)
    totalTime = totalTime*5e-5*samplesPerSymb*yAxisLength # Accuracy
    
    # Warn user if required
    if totalTime > 5*60 :
        print('\a') # Print bell character to try triggering a notification on the user's end
        answer = input('The simulation is expected to take {:.0f} minutes. Are you sure you would like to continue? (Y/N) '.format(totalTime/60))
        if not (answer == 'y' or answer == 'Y'):
            print('\n----------Simulation Canceled----------')
            quit()
        
    print('Expected simulation time {:.0f} seconds.\n'.format(totalTime))

