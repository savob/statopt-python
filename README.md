# StatEye Simulation

Statistical eye modelling tool, StatEye, ported to Python 3. Uses statistical methods to model various wireline effects to estimate the performance of different wireline link configurations, provides estimates for Bit Error Rates, Eye dimensions, as well as various plots relating to link performance. 

By default, an equalized PAM-4 link has been created. This link is ready to simulate out of the box. Enjoy!

## Features 

- Reading in Touchstone (`.s4p`) files for channel data
- Simulating and characterizing the performance of different modulation schemes such as PAM-4, with different signalling (including 1+D and 1+0.5D)
- Introducing the impairment effects of cross-talk, jitter, noise, and distortion
- Plotting channel and equalizer behaviour curves
- Optimizing equalizers for a given system configuration using a genetic algorithm

# Operation

Operation of the StatEye tool is meant to be simple. The majority of user effort is in configuring the simulation to suit one's needs. The general flow for setting up and running a simulation is as follows.

1. Upload desired Touchstone (`.s4p`) files and/or `.mat` files to describe distortion or pulses. *Note: Touchstone files for channels need to go into the `/touchstone/` folder.*
2. Configure simulation settings to match desired parameters. Check the example files for baseline configurations.
   - Refer to desired files for channels
   - Set desired output plots
   - Adjust the amount of taps in equalizers
   - Select the parameters to be adjusted in the adaption process, if enabled
3. Adjust the `stateye.py` script to read the simulation configuration function from the desired simulation file.
4. Run the `stateye.py` script.
   - Users may be asked whether or not to update the previously saved channel information. **This is needed if the Touchstone files are updated**, but can be skipped in most cases.
   - If the simulation is expected to take a long time, the user will need to confirm that they want the simulation to proceed.
5. Wait for the simulation to complete.
6. Enjoy the results!

*Tip: To increase the speed of the simulation, reduce the number of impulse response pre and postcursors. This will reduce the accuracy of the final results.*

## Example Outputs

The following output plots are generated using the configuration in `generateUserSettingsExample0.py`.

Plots related to the system's characteristics

![Channel responses](./media/Channel_Responses.png)
![CTLE Responses](./media/CTLE_Response.png)

The pulse response of the system, there are some slight deviations from the MATLAB version due to the different approaches taken to model it. In MATLAB a polynomial was fit to the frequency resonse, however in Python the discrete time response based on frequency response was used with no curve fitting.

![Pulse Response](./media/Pulse_Response.png)

Using the pulse response with the different possible data strings to record the different possible inter-symbol interference trajectories for the system, to take.

![ISI Trajectories](./media/ISI_Trajectories.png)

Plots of the various influences on the system.

![Jitter](./media/Jitter_Distribution.png)
![Noise](./media/Noise_Distribution.png)
![Distortion](./media/Non-Linearity.png)

The final probability density distribution and analysis.

![PDF](./media/PDF_Plot.png)
![BER](./media/BER_Plot.png)

# Knob Definitions

There are many knobs that can have an effect on the simulation, here is a complete list with explanations:

## General Settings

| Setting Knob | Explanation |
| --- | --- |
|`General.SymbolRate`                 |  The system sampling rate [samples/second] |
|`General.SignalingMode`              |  The modulation scheme ('standard': conventional baseband, '1+D' and '1+0.5D': partial signaling, 'clock': a clock signal) **NOTE: Adaption is primarily tuned for standard signaling.** |
|`General.Modulation`                 |  Number of modulation levels (2: NRZ, 4: PAM4) |
|`General.SamplesPerSymb`             |  Time-domain resolution of the eye diagram |
|`General.yAxisLength`                |  Voltage-domain resolution of the eye diagram |
|`General.NumbSymb`                   |  Number of periods to display in the eye diagram |
|`General.ContLevels`                 |  Number of contour levels in the eye diagram |
|`General.TargetBER`                  |  Bit-error-rate level to perform eye measurements (Verical/horizontal eye opening, COM, also used as target for adaption) |
|`General.Plotting.ChannelResponse`   |  Display channel response |
|`General.Plotting.CTLEResponse`      |  Display CTLE response |
|`General.Plotting.PulseResponse`     |  Display pulse response |
|`General.Plotting.JitterSource`      |  Display jitter distribution |
|`General.Plotting.NoiseSource`       |  Display noise distribution |
|`General.Plotting.DistortionSource`  |  Display linear distortion |
|`General.Plotting.ISI`               |  Display trace eye diagram (CAREFUL: THIS CAN TAKE A LONG TIME TO DISPLAY) |
|`General.Plotting.PDFInitial`        |  Display impairment-free eye diagram |
|`General.Plotting.PDFCrossTalk`      |  Display eye diagram after adding cross-talk |
|`General.Plotting.PDFDistorted`      |  Display eye diagram after adding linear distortion |
|`General.Plotting.PDFJitter`         |  Display eye diagram after adding jitter |
|`General.Plotting.PDFNoise`          |  Display eye diagram after adding noise |
|`General.Plotting.PDFFinal`          |  Display final eye diagram |
|`General.Plotting.BER`               |  Display BER contour levels superimposed over BER plot |
|`General.Plotting.BER2`              |  Display BER contour levels superimposed over eye diagram (final PDF) |
|`General.Plotting.Results`           |  Display eye measurement results |

## Adaption

| Setting Knob | Explanation |
| --- | --- |
|`Adaption.Adapt`                     |  Run adaption algorithm **NOTE: Adaption is primarily tuned for standard signaling.** |
|`Adaption.TotalParents`              |  Number best candidates to keep from previous generation |
|`Adaption.ChildrenPerParent`         |  Number of new candidates to generate per parent |
|`Adaption.TotalMutations`            |  Number of randomly generated candidates |
|`Adaption.Mode1Generations`          |  Number of generations to run while applying coarse adjustment |
|`Adaption.Mode2Generations`          |  Number of generations to run while applying fine adjustment |
|`Adaption.Knobs`                     |  Specify which knobs to optimize (must provide full path i.e.: `'transmitter.EQ.taps.pre1'`) |

## Transmitter Settings

| Setting Knob | Explanation |
| --- | --- |
|`Transmitter.SignalAmplitude`        |  Transmitter supply voltage (peak differential) [V] |
|`Transmitter.IncludeSourceImpedance` |  Include 50ohm source impedance (halves transmit signal voltage). **NOTE: this just scales the output, the simulation does not handle reflections.** |
|`Transmitter.TRise`                  |  Signal rise time [s] |
|`Transmitter.TXBandwidth`            |  Transmitter analog bandwidth [Hz] |
|`Transmitter.PreCursorCount`         |  Number of ISI pre-cursors to consider in eye diagram generation |
|`Transmitter.PostCursorCount`        |  Number of ISI post-cursors to consider in eye diagram generation |
|`Transmitter.EQ.AddEqualization`     |  Apply FIR equalization |
|`Transmitter.EQ.Taps`                |  Specify FIR equalization tap values |
|`Transmitter.Jitter.AddJitter`       |  Apply transmitter jitter |
|`Transmitter.Jitter.STDDeviation`    |  Specify random jitter standard deviation [UI] |
|`Transmitter.Jitter.Amplitude`       |  Specify deterministic jitter amplitude [UI] |
|`Transmitter.Jitter.DCD`             |  Specify duty-cycle distortion jitter [UI] |
|`Transmitter.Noise.AddNoise`         |  Apply transmitter noise |
|`Transmitter.Noise.StdDeviation`     |  Specify random noise standard deviation [V] |
|`Transmitter.Noise.Amplitude`        |  Specify deterministic noise amplitude [V] |
|`Transmitter.Noise.Frequency`        |  Specify deterministic noise frequency [Hz] |
|`Transmitter.Distortion.AddDistortion` | Add transmitter linear distortion |
|`Transmitter.Distortion.FileName`    |  File specifying 1-to-1 voltage mapping (structure containing "input" and "output" vectors of same length) |

## Channel Settings

| Setting Knob | Explanation |
| --- | --- |
|`Channel.AddChannel`                 |  Apply channel to link |
|`Channel.AddCrossTalk`               |  Apply crosstalk |
|`Channel.AddNotch`                   |  Apply a notch to channel transfer function |
|`Channel.NotchFreq`                  |  Specify notch frequency [Hz] |
|`Channel.NotchAttenuation`           |  Specify notch attenuation [dB] |
|`Channel.ModelCircuitTF`             |  Convolve link response with an additional pulse response to model a circuit who's response is known |
|`Channel.ModelCircuitTFName`         |  Specify additional pulse response file |
|`Channel.OverrideResponse`           |  Override transmitter and channel response with a custom pulse response (can still apply receiver equalization) |
|`Channel.OverrideFileName`           |  Specify custom pulse response file |
|`Channel.Approximate`                |  Approximate cross-talk as a noise source to speed up simulation |
|`Channel.MakeAsynchronous`           |  Assume aggressor channels are not synchronized with victim channel and thus impairment is applyed to all sampling phases equally ||
|`Channel.FileNames`                  |  Specify channel files (includes THRU, NEXT and FEXT channels) |
|`Channel.Noise.AddNoise`             |  Apply thermal noise |
|`Channel.Noise.NoiseDensity`         |  Specify thermal noise density [V^2/Hz] |

## Receiver Settings

| Setting Knob | Explanation |
| --- | --- |
|`Receiver.SignalAmplitude`           |  Specify receiver supply voltage [V] (Y-limits of receiver plots) |
|`Receiver.PreAmp.AddGain`            |  Apply pre-amplification |
|`Receiver.PreAmp.Gain`               |  Specify pre-amplification gain |
|`Receiver.CTLE.AddEqualization`      |  Apply continuous-time linear equalization |
|`Receiver.CTLE.ZeroFreq`             |  Specify CTLE transfer function zero frequency [Hz] |
|`Receiver.CTLE.ZeroNumb`             |  Specify number of zeros to apply to CTLE transfer function  |
|`Receiver.CTLE.Pole1Freq`            |  Specify primary CTLE transfer function pole frequency [Hz] |
|`Receiver.CTLE.Pole1Numb`            |  Specify number of primary poles to apply to CTLE transfer function |
|`Receiver.CTLE.Pole2Freq`            |  Specify secondary CTLE transfer function pole frequency [Hz] |
|`Receiver.CTLE.Pole2Numb`            |  Specify number of secondary poles to apply to CTLE transfer function |
|`Receiver.FFE.AddEqualization`       |  Apply FFE equalization |
|`Receiver.FFE.Taps`                  |  Specify FFE tap values |
|`Receiver.DFE.AddEqualization`       |  Apply DFE equalization |
|`Receiver.DFE.Taps`                  |  Specify DFE tap values |
|`Receiver.Jitter.AddJitter`          |  Apply receiver jitter |
|`Receiver.Jitter.STDDeviation`       |  Specify random jitter standard deviation [UI] |
|`Receiver.Jitter.Amplitude`          |  Specify deterministic jitter amplitude [UI] |
|`Receiver.Jitter.DCD`                |  Specify duty-cycle distortion jitter [UI] |
|`Receiver.Noise.AddNoise`            |  Apply receiver noise |
|`Receiver.Noise.StdDeviation`        |  Specify random noise standard deviation [V] |
|`Receiver.Noise.Amplitude`           |  Specify deterministic noise amplitude [V] |
|`Receiver.Noise.Frequency`           |  Specify deterministic noise frequency [Hz] |
|`Receiver.Distortion.AddDistortion`  |  Add receiver linear distortion |
|`Receiver.Distortion.FileName`       |  File specifying 1-to-1 voltage mapping (structure containing "input" and "output" vectors of same length) |

# Remaining Work

- [x] Fix up and validate the adaption system
- [x] Perform more varied tests of the system
- [x] Polish up the figure formatting. E.g. prevent axes labels overlapping adjacent plots when the window is sized smaller.
- [x] Port more example configurations for users
- [x] Update and upload documentation for operation based on the "readme"s from MATLAB
- [x] Clean up comments and disclaimers in files
- [ ] Verify accuracy of system simulation (pulse and CTLE responses)
- [ ] Investigate the use of an alternative, more interactive graphics library like [pyqt](https://www.pyqtgraph.org/) or [Altair](https://altair-viz.github.io/index.html)
- [x] Improve installation process. Perhaps preparing this as a package for Anaconda or pip.

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

Originally written in MATLAB by Jeremy Cosson-Martin and Jhoan Salinas for Ali Sheikholeslami's research group. Porting to Python was done by Savo Bajic as a project for Ali Sheikholeslami's wireline course, ECE1392, based on version 1.11 of StatEye in MATLAB.

The Touchstone files used for examples were provided by Samtec as part of the IEEE 802.3ck 100 Gb/s per Lane Electrical Study Group. More information is available in the [Touchstone folder readme](/touchstone/readme.md).