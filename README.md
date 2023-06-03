# StatOpt

StatOpt is a statistical eye modelling and link optimization tool for wireline communications, originally developed in MATLAB, now ported to Python 3. Uses statistical methods to model various wireline effects to estimate the performance of different link configurations, provides estimates for Bit Error bates, eye dimensions, as well as various plots relating to link performance. 

By default, an equalized PAM-4 link has been created. This link is ready to simulate out of the box. Enjoy!

## Features 

- Reading in Touchstone (`.s4p`) files for channel data
- Simulating and characterizing the performance of different modulation schemes such as PAM-4, with different signalling (including 1+D and 1+0.5D)
- Introducing the impairment effects of cross-talk, jitter, noise, and distortion
- Plotting channel and equalizer behaviour curves
- Optimizing equalizers for a given system configuration using a genetic algorithm

# Operation

Operation of the StatOpt tool is meant to be simple. The majority of user effort is in configuring the simulation to suit one's needs. The general flow for setting up and running a simulation is as follows.

1. Upload desired Touchstone (`.s4p`) files and/or `.mat` files to describe distortion or pulses.
   - Files for channels need to go into the `/channels/` folder. *(Both `.s4p` and `.mat` channel descriptions).* 
   - All others (predefined pulses, distortion, etc.) are to be kept in the base directory, alongside this readme file.
2. Configure simulation settings to match desired parameters. Check the example files for baseline configurations.
   - Refer to desired files for channels
   - Set desired output plots
   - Adjust the amount of taps in equalizers
   - Select the parameters to be adjusted in the adaption process, if enabled
3. Adjust the `statopt.py` script to read the simulation configuration function from the desired simulation file.
4. Run the `statopt.py` script.
   - If the simulation is expected to take a long time, the user will need to confirm that they want the simulation to proceed.
5. Wait for the simulation to complete.
6. Enjoy the results!

*Tip: To increase the speed of the simulation, reduce the number of impulse response pre- and post-cursors. Do note that this will reduce the accuracy of the final results.*

## Example Outputs

The following output plots are generated using the configuration in `generateUserSettingsExample0.py`. *Note: Distortion and ISI Trajectory plots are not plotted by default when executing the example as provided. Distortion is not actually enabled for it (by default) and ISI trajectories takes a very long time to render.*

### System Response characteristics

![Channel responses](./media/Channel_Responses.png)
![CTLE Responses](./media/CTLE_Response.png)
![Pulse Response](./media/Pulse_Response.png)

### Inter-Symbol Interference

Using the pulse response with the different possible data strings to record the different possible inter-symbol interference trajectories for the system to take.

![ISI Trajectories](./media/ISI_Trajectories.png)

### Influences on the System 

![Jitter](./media/Jitter_Distribution.png)
![Noise](./media/Noise_Distribution.png)
![Distortion](./media/Non-Linearity.png)

*Note: in example 0 distortion is not enabled by default, hence the simple distortion curves.*

### Final Probability Density and Bit Error Rate

![PDF](./media/PDF_Plot.png)
![BER](./media/BER_Plot_(on_PDF).png)

# Knob Definitions

There are many knobs that can have an effect on the simulation, here is a complete list with explanations:

## General Settings

| Setting Knob | Explanation |
| --- | --- |
|`general.symbolRate`                 |  The system sampling rate [samples/second] |
|`general.signalingMode`              |  The modulation scheme ('standard': conventional baseband, '1+D' and '1+0.5D': partial signaling, 'clock': a clock signal) **NOTE: Adaption is primarily tuned for standard signaling.** |
|`general.modulation`                 |  Number of modulation levels (2: NRZ, 4: PAM4) |
|`general.samplesPerSymb`             |  Time-domain resolution of the eye diagram |
|`general.yAxisLength`                |  Voltage-domain resolution of the eye diagram |
|`general.numbSymb`                   |  Number of periods to display in the eye diagram |
|`general.contLevels`                 |  Number of contour levels in the eye diagram |
|`general.targetBER`                  |  Bit-error-rate level to perform eye measurements (Verical/horizontal eye opening, COM, also used as target for adaption) |
|`general.plotting.channelResponse`   |  Display channel response |
|`general.plotting.CTLEResponse`      |  Display CTLE response |
|`general.plotting.pulseResponse`     |  Display pulse response |
|`general.plotting.jitterSource`      |  Display jitter distribution |
|`general.plotting.noiseSource`       |  Display noise distribution |
|`general.plotting.distortionSource`  |  Display linear distortion |
|`general.plotting.ISI`               |  Display trace eye diagram **(CAREFUL: THIS CAN TAKE A LONG TIME TO DISPLAY)** |
|`general.plotting.PDFInitial`        |  Display impairment-free eye diagram |
|`general.plotting.PDFCrossTalk`      |  Display eye diagram after adding cross-talk |
|`general.plotting.PDFDistorted`      |  Display eye diagram after adding linear distortion |
|`general.plotting.PDFJitter`         |  Display eye diagram after adding jitter |
|`general.plotting.PDFNoise`          |  Display eye diagram after adding noise |
|`general.plotting.PDFFinal`          |  Display final eye diagram |
|`general.plotting.BER`               |  Display BER contour levels superimposed over BER plot |
|`general.plotting.BER2`              |  Display BER contour levels superimposed over eye diagram (final PDF) |
|`general.plotting.results`           |  Display eye measurement results |

## Adaption

| Setting Knob | Explanation |
| --- | --- |
|`adaption.adapt`                     |  Run adaption algorithm **NOTE: Adaption is primarily tuned for standard signaling.** |
|`adaption.totalParents`              |  Number best candidates to keep from previous generation |
|`adaption.childrenPerParent`         |  Number of new candidates to generate per parent |
|`adaption.totalMutations`            |  Number of randomly generated candidates |
|`adaption.mode1Generations`          |  Number of generations to run while applying coarse adjustment |
|`adaption.mode2Generations`          |  Number of generations to run while applying fine adjustment |
|`adaption.knobs`                     |  Specify which knobs to optimize (must provide full path i.e.: `'transmitter.EQ.taps.pre1'`) |

## Transmitter Settings

| Setting Knob | Explanation |
| --- | --- |
|`transmitter.signalAmplitude`        |  Transmitter supply voltage (peak differential) [V] |
|`transmitter.includeSourceImpedance` |  Include 50ohm source impedance (halves transmit signal voltage). **NOTE: this just scales the output, the simulation does not handle reflections.** |
|`transmitter.tRise`                  |  Signal rise time [s] |
|`transmitter.TXBandwidth`            |  Transmitter analog bandwidth [Hz] |
|`transmitter.preCursorCount`         |  Number of ISI pre-cursors to consider in eye diagram generation |
|`transmitter.postCursorCount`        |  Number of ISI post-cursors to consider in eye diagram generation |
|`transmitter.EQ.addEqualization`     |  Apply FIR equalization |
|`transmitter.EQ.taps`                |  Specify FIR equalization tap values |
|`transmitter.jitter.addJitter`       |  Apply transmitter jitter |
|`transmitter.jitter.stdDeviation`    |  Specify random jitter standard deviation [UI] |
|`transmitter.jitter.amplitude`       |  Specify deterministic jitter amplitude [UI] |
|`transmitter.jitter.DCD`             |  Specify duty-cycle distortion jitter [UI] |
|`transmitter.noise.addNoise`         |  Apply transmitter noise |
|`transmitter.noise.stdDeviation`     |  Specify random noise standard deviation [V] |
|`transmitter.noise.amplitude`        |  Specify deterministic noise amplitude [V] |
|`transmitter.noise.frequency`        |  Specify deterministic noise frequency [Hz] |
|`transmitter.distortion.addDistortion` | Add transmitter linear distortion |
|`transmitter.distortion.fileName`    |  File specifying 1-to-1 voltage mapping (structure containing "input" and "output" vectors of same length) |

## Channel Settings

| Setting Knob | Explanation |
| --- | --- |
|`channel.addChannel`                 |  Apply channel to link |
|`channel.addCrossTalk`               |  Apply crosstalk |
|`channel.addNotch`                   |  Apply a notch to channel transfer function |
|`channel.notchFreq`                  |  Specify notch frequency [Hz] |
|`channel.notchAttenuation`           |  Specify notch attenuation [dB] |
|`channel.modelCircuitTF`             |  Convolve link response with an additional pulse response to model a circuit who's response is known |
|`channel.modelCircuitTFName`         |  Specify additional pulse response file |
|`channel.overrideResponse`           |  Override transmitter and channel response with a custom pulse response (can still apply receiver equalization) |
|`channel.overrideFileName`           |  Specify custom pulse response file |
|`channel.approximate`                |  Approximate cross-talk as a noise source to speed up simulation |
|`channel.makeAsynchronous`           |  Assume aggressor channels are not synchronized with victim channel and thus impairment is applyed to all sampling phases equally ||
|`channel.fileNames`                  |  Specify channel files (includes THRU, NEXT and FEXT channels) |
|`channel.noise.addNoise`             |  Apply thermal noise |
|`channel.noise.noiseDensity`         |  Specify thermal noise density [V^2/Hz] |

## Receiver Settings

| Setting Knob | Explanation |
| --- | --- |
|`receiver.signalAmplitude`           |  Specify receiver supply voltage [V] (Y-limits of receiver plots) |
|`receiver.preAmp.addGain`            |  Apply pre-amplification |
|`receiver.preAmp.gain`               |  Specify pre-amplification gain |
|`receiver.CTLE.addEqualization`      |  Apply continuous-time linear equalization |
|`receiver.CTLE.zeroFreq`             |  Specify CTLE transfer function zero frequency [Hz] |
|`receiver.CTLE.zeroNumb`             |  Specify number of zeros to apply to CTLE transfer function  |
|`receiver.CTLE.pole1Freq`            |  Specify primary CTLE transfer function pole frequency [Hz] |
|`receiver.CTLE.pole1Numb`            |  Specify number of primary poles to apply to CTLE transfer function |
|`receiver.CTLE.pole2Freq`            |  Specify secondary CTLE transfer function pole frequency [Hz] |
|`receiver.CTLE.pole2Numb`            |  Specify number of secondary poles to apply to CTLE transfer function |
|`receiver.FFE.addEqualization`       |  Apply FFE equalization |
|`receiver.FFE.taps`                  |  Specify FFE tap values |
|`receiver.DFE.addEqualization`       |  Apply DFE equalization |
|`receiver.DFE.taps`                  |  Specify DFE tap values |
|`receiver.jitter.addJitter`          |  Apply receiver jitter |
|`receiver.jitter.stdDeviation`       |  Specify random jitter standard deviation [UI] |
|`receiver.jitter.amplitude`          |  Specify deterministic jitter amplitude [UI] |
|`receiver.jitter.DCD`                |  Specify duty-cycle distortion jitter [UI] |
|`receiver.noise.addNoise`            |  Apply receiver noise |
|`receiver.noise.stdDeviation`        |  Specify random noise standard deviation [V] |
|`receiver.noise.amplitude`           |  Specify deterministic noise amplitude [V] |
|`receiver.noise.frequency`           |  Specify deterministic noise frequency [Hz] |
|`receiver.distortion.addDistortion`  |  Add receiver linear distortion |
|`receiver.distortion.fileName`       |  File specifying 1-to-1 voltage mapping (structure containing "input" and "output" vectors of same length) |

# Future Work

- [ ] Investigate the use of an alternative, more interactive graphics library for figures like [pyqt](https://www.pyqtgraph.org/) or [Altair](https://altair-viz.github.io/index.html)
- [ ] Consider allowing the chaining of `.s4p` files to allow systems to be more flexible. For example allowing one to change the transmission line but keeping the same die-to-pad channel.
- [ ] Speed up simulation of RX CTLE step. **Currently `lsim` is responsible for 90% of run time during adaption.**
  - Attempt to parallelize its operation across all channels in a given link configuration
  - Consider replacing `lsim` with a covolution operation like what is done for pulse response generation. This is probably what goes on inside `lsim` but we could avoid repeatly calculating this repsonse by recording it the first time for a given CTLE. Then whenever the response is needed, read it from memory and convole which is much faster than recalculating the impulse reponse repeatedly.

# Dependancies

In addition to running Python 3.10 or newer, the following libraries are needed to run this code:

- [NumPy](https://numpy.org/install/)
- [SciPy](https://scipy.org/install/)
- [matplotlib](https://matplotlib.org/stable/users/getting_started/index.html#installation-quick-start)
- [scikit-rf](https://github.com/scikit-rf/scikit-rf)
- [Python Control Library](https://python-control.readthedocs.io/en/0.9.3.post2/intro.html)

These can all be automatically installed/verified to be the right versions using the following command in the project directory:

`pip install -r requirements.txt`

*NOTE: This may run on earlier versions of the packages and Python, but it has only been extensively tested on Python 3.10 with the package versions specified as the minimums in `requirements.txt`.*

# Credit

Originally written in MATLAB by Jeremy Cosson-Martin and Jhoan Salinas for Ali Sheikholeslami's research group. Porting to Python was done by Savo Bajic as a project for Ali Sheikholeslami's wireline course, ECE1392, based on version 1.11 in MATLAB, although it has been updated since in parallel with the MATLAB version.

The Touchstone files used for examples were provided by Samtec as part of the IEEE 802.3ck 100 Gb/s per Lane Electrical Study Group. More information is available in the [Touchstone folder readme](/touchstone/readme.md).