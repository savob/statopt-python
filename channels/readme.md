# Channel Data Folder

This is the folder that will be searched for the channel files specified in configurations, these can either be Touchstone (`.s4p`) files or MATLAB data files (`.mat`). There is no need to specify this folder when setting a filename in a simulation configuration, so if one wants to use "A.s4p" from this folder as the through channel then use the following setting in the function:

```
simSettings.channel.fileNames.thru = 'A.s4p'
```

For NEXT and FEXT channels the scheme is similar but appended with an index starting from 1, examples are below. *Note: the order of NEXT/FEXT channels has no effect on simulation.*

```
simSettings.channel.fileNames.fext1 = 'C2M__Z100_IL14_WC_BOR_H_L_H_FEXT1.s4p'
simSettings.channel.fileNames.next4 = 'C2M__Z100_IL14_WC_BOR_H_L_H_NEXT4.s4p'
simSettings.channel.fileNames.next3 = 'C2M__Z100_IL14_WC_BOR_H_L_H_NEXT3.s4p'
simSettings.channel.fileNames.fext2 = 'C2M__Z100_IL14_WC_BOR_H_L_H_FEXT2.s4p'
```

## Using Touchstone Files

No special preparations need to be taken to use standard Touchstone (`.s4p`) files with this program; provided the files contain valid data in the correct format.

## Using MATLAB Data Files

Although not the usual method of describing a channel's properties, MATLAB-style data files can be used to describe the frequency responce of a channel from one end to the other. If one chooses to use this method to describe the behaviour of a channel then it needs to contain two vectors of equal length: 

1. `frequency` - Marks down the frequency value for a given response. **Specified in Hz.**
2. `response` - Describes the response of the channel for a given frequency as a complex number.

*(If either of these are missing or misspelled then the program will inform the user and close.)*

The motivation for having this feature is to allow for the easy importing and tailoring of arbitrary channels using MATLAB or Octave to plot a response to a simple structure instead of synthesizing a complete Touchstone file.

# Credit for Provided Channels

The channel descriptions distributed with this program and used in the examples were provided for research use by other researchers, credit for them is as follows.

## "C2M_Z100_IL14_WC_BOR_H_L_H_" Files

*Used in examples 0, 1, 3 and 4.*

Samtec from their work: "100 GEL C2M Flyover Host Files: Tp0 to Tp2, with and without manufacturing variations, for losses of 9, 10, 11, 12, 13, and 14 dB Losses." IEEE 802.3ck 100 Gb/s per Lane Electrical Study Group. 18-May-2018.

The presentation itself is available [here](https://grouper.ieee.org/groups/802/3/ck/public/18_05/mellitz_3ck_02_0518.pdf), all the channel files we used and the others they prepared for that presentation are in [this dataset](https://grouper.ieee.org/groups/802/3/ck/public/tools/c2m/mellitz_3ck_01_0518_C2M.zip). They have additional channel file sets available on their [group's page](https://grouper.ieee.org/groups/802/3/ck/public/tools/index.html).

## "TEC_Whisper27in_" Files

*Used in example 2.*

TE Connectivity from their work: "100 Gb/s Measured Backplane Channels" for the March 2011 IEEE 802 LMSC Plenary Session presented by Megha Shanbhag.

The presentation itself is available [here](http://www.ieee802.org/3/100GCU/public/mar11/shanbhag_01a_0311.pdf), the channel files originate from [this dataset](https://www.ieee802.org/3/100GCU/public/ChannelData/TEC_11_0401/shanbhag_01_0411.zip). They are posted alongside other channel datasets as part of their [task force's page](https://www.ieee802.org/3/100GCU/public/channel.html).