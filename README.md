# StatEye Simulation

Statistical eye modelling tool, StatEye, ported to Python 3. Uses statistical methods to model various wireline effects to estimate the performance of different wireline link configurations, provides estimates for Bit Error Rates, Eye dimensions, as well as various plots relating to link performance. 

By default, an equalized PAM-4 link has been created. This link is ready to simulate out of the box. Enjoy!

## Features 

- Reading in Touchstone (.s4p) files for channel data
- Simulating and characterizing the performance of different modulation schemes such as PAM-4, with different signalling (including 1+D and 1+0.5D)
- Introducing the impairment effects of cross-talk, jitter, noise, and distortion
- Plotting channel and equalizer behaviour curves
- Optimizing equalizers for a given system configuration using a genetic algorithm

# Operation

Operation of the StatEye tool is meant to be simple. The majority of user effort is in configuring the simulation to suit one's needs. The general flow for setting up and running a simulation is as follows.

1. Upload desired Touchstone (.s40) files and/or .mat files to describe distortion or pulses. *Note: Touchstone files for channels need to go into the `/touchstone/` folder.*
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

Polots related to the system's characteristics

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

# Remaining Work

- [x] Fix up and validate the adaption system
- [x] Perform more varied tests of the system
- [x] Polish up the figure formatting. E.g. prevent axes labels overlapping adjacent plots when the window is sized smaller.
- [x] Port more example configurations for users
- [ ] Update and upload documentation for operation based on the "readme"s from MATLAB
- [ ] Clean up comments and disclaimers in files
- [ ] Verify accuracy of system simulation (pulse and CTLE responses)
- [ ] Investigate the use of an alternative, more interactive graphics library like [pyqt](https://www.pyqtgraph.org/) or [Altair](https://altair-viz.github.io/index.html)

# Dependancies

In addition to Python 3, the following libraries are needed to run this code:

- [NumPy](https://numpy.org/install/)
- [SciPy](https://scipy.org/install/)
- [matplotlib](https://matplotlib.org/stable/users/getting_started/index.html#installation-quick-start)
- [scikit-rf](https://github.com/scikit-rf/scikit-rf)
- [Python Control Library](https://python-control.readthedocs.io/en/0.9.3.post2/intro.html)

# Credit

Originally written in MATLAB by by Jeremy Cosson-Martin and Jhoan Salinas for Ali Sheikholeslami's research group. Porting to Python was done by Savo Bajic as a projects for Ali Sheikholeslami's wireline course (ECE1392).
