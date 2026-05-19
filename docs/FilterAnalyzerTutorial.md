
# Cohn Filter Analyzer - Sample Usage Tutorial

In this tutorial we will use the FilterAnalyzer to analyze a sample filter that has crystal motional parameter and coupling capacitor store in the **`sample-filter.json`** file for a 12 MHz crystal filter

## Overview
In this tutorial we will:
1. Simulate entering crystal filter parameters
2. View the filter as is
3. Change a few parameters to see the effect on the filter
4. Option 1: Iteratively guess at the termination 
5. Option 2: Use the Dishal/Hayward Synthesis to predict optimum capacitor values
6. Option 3: Use the Optimize Z to arrive at a suitable termination
7. Look at adjusting the BFO to get the optimum carrier suppression and audio passband attenuation


## Step 1: Enter Filter Parameter
As the first step you would enter the crystal motional parameters you identifed for your matched set of crystals.  However, for this tutorial we will open and use an exiting profile that only have crystal motional parameters.

Use File->Open Profile and select **`sample-filter.json`** file.   Once open, crystal motional parameters as well as standard coupling capacitors will be entered.  Start with these capacitor values.

## Step 2: View Filter Bode Plot
1. The next step will be to view the unterminate filter to see how it looks open circuit.  However, you will need to enter the start and end frequencies to sweep the filter.  In this case, we know the filter's center frequency is around 12 MHz, lets sweep between 11 MHz and 13 MHz.  Ensure **Bode Plot** and **Full Plot** are enabled and **Enable Term Z** is disabled.
	**Note:** `Ensure that the BFO frequency is 0 for the time being.  If this is not zero, you will get an error.`
2. Click the **Calculate** button to perform the selected analysis (i.e. generate a bode plot)
3. The plot is too wide an you need to do trial and error to figure out the optimum start and stop frequency.  The plot for the filter should have show about 40 dB down on either side of the skirts.
	**Hint**: `The text output window will show the center frequency.  Since we know the bandwidth of the filter is about 3K, try generating a sweep 3KHz above and below the indicated center frequency`. Adjust to get filter skirts in view.
	**Solution**: The start frequency should be around **11.991 MHz** and end frequency should be around **12.00 MHz**
3. Note that the filter has huge humps.  Why?

### Why are there large peaks? 

A 4-crystal ladder filter is a **4-pole system**. Mathematically, this means it has 4 distinct resonant frequencies.
- **When unterminated (or poorly terminated):** There is no electrical damping in the circuit. The energy bounces back and forth, allowing each of those individual poles to ring at its natural frequency. This creates the sharp, distinct peaks and deep nulls you see in your first screenshot.
- **When properly terminated:** The source and load resistance ($Z_0$) act as electrical "shock absorbers." They damp the circuit, causing those individual sharp poles to widen and merge together. When the damping is just right, the peaks fuse into a single, flat passband with steep skirts—which is exactly what you achieved in your second screenshot!
    
While mismatched crystals will make the passband asymmetrical or lopsided, the existence of those **deep ripples is purely a function of improper termination impedance**.

## Step 3: Experiment with Values
Using the sweep frequencies, let change a few parameter to see the impact on the filter.  
**Note**: At any point you can reload the default values if you can recall what was initially loaded.

1. Change **C1** and **C2** values and plot the graph. Try 1/2 of the values (i.e. 100 pf) and double the values (400 pf).  What happens to the center frequency, bandwidth and insertion loss?
2. Change **C3**, **C4** and **C5**.  What happens?
3. Enable the **Enable Term Z**.  Enter a small Z (e.g. 50), enter a moderate Z (e.g. 200), enter a large Z (e.g. 600) in the  **Z Term Real** input.  What happens to the filter's bandwidth, ripple and insertion loss? Does the center frequency change?
	- Try changes the Z values (i.e. Iteratively guess at the termination) to minimize the ripple in the passband.  Pay attention to the insertion loss and bandwidth.
4. Disable the **Enable Term Z** for the next step.


## Step 4: Dishal/Hayward Optimization
Here we will use the **Dishal/Hayward Synthesis** to determine the optimum coupling capacitor values.
1. By doing Step 3 (i.e. a bode plot), the center frequency will be populated in the **Target Frequency** input. If you need to have it at another center frequency you can enter it here.  Leave it as is.
2. Enter the required bandwidth for the system.  Select 2500 Hz
3. Click the **Synthesize Caps** button. No plot will be displayed.  Note the capacitor values changes and a termination impedance was entered.
4. Note this termination impedance. **Write it down!**
5. Generate a bode plot with the new capacitor values and the termination Z.  How does the filter look?  What is the center frequency, bandwidth, ripple and insertion loss?



## Step 4: Impedance Termination Optimization
Here we will use the **Optimize Term Z**  to try and get a better termination impedance that will produce a better filter.

1. Enable the **Optimize Term Z**.  Ensure that all optimization constraints in Selectable Constraints (For Z Opt) is enabled.  These are **Max IL** (insertion loss), **Max Ripple** and carrier suppression (aka **Skirt Target**)
	**Note**: The values here are **POSITIVE** even through its a loss or attenuation
2. Click the **Calculate** button
3. The program will indicate that it failed to find a termination that will fulfil the the conditions for insertion loss, Maximum ripple and carrier suppression (Skirt Target) that you entered.  
4. Lets, try to minimze ripple.  Deselect all constraints except **Max ripple**.  Enter 1 dB and see if the program can find a termination for 1dB.  Select 2 and try. Rinse and repeat for 3, 4, 5, 6.  What happens? What is the best ripple figure you can get? What is the optimum termination to get the best ripple figure?
5. Repeat for **Max IL** and **Skirt Target**.  Pay attention to insertion loss, bandwidth and ripple. What seems to be the best termination.
6. Compare this termination to the Dishal/Hayward Termination you wrote down previously.  Plot both to determine which is better.  Which has better ripple, insertion loss and bandwidth?  Which has sharper skirts?  Which would you use to terminate your filter?


## Step 5: Optimize the BFO Frequency
Here we will use the **BFO Offset**  with the optimum **Z Term Real** (from above) to try and get a acceptable carrier supression and audio passband attenuation.  First, you need to understand how SSB is generated.

#### BFO Background

This discussion is primary for the transmission of SSB.  For reception of SSB, the BFO Frequency can be closer to the center frequency where you get better audio quality.

You will notice the Full Plot displays USB BFO, LSB BFO as well as 600 Hz and 2400 Hz lines.  For the human ear, 600 Hz is about the lower limit and 2400 Hz is the upper limit (for SSB at least).  This is showing you where these audio frequencies (in the Sidebands) would site on the filter skirts.  

When  **BFO Offset**  is 0, you are telling the program to place the Beat Frequency Oscillator _exactly_ on the -3dB edge of the filter.  This is where the BFO Frequency would typically be on **receive**.  On, receive your parts of your audio may be lowered by 3 dB which your ear cannot tell.  

On transmit, your BFO Frequency needs to be shifted so that the carrier is attenuated by the filter skirt.  You can use the **BFO Offset** to identify the optimum BFO Frequency. 

When you increase the **BFO Offset** the BFO slides further away from the center frequency by the amount specified.  Keep in mind, when **BFO Offset** is 0, the BFO Frequency is at the measured -3dB point of the filter (both for LSB and USB)

The BFO Frequency indicates the starting frequency of the audio passband and for USB the BFO Frequency + 600 Hz will be for 600 Hz audio and BFO Frequency + 2400 Hz will be for 2400 Hz audio.  For LSB, the same applies except the audio frequency is subtracted from the BFO Frequency.  If you don't understand this, use AI and take pen and paper and draw a AM modulated signal with side bands and figure it out.  The carrier is usually about 300 Hz or so below/above the BFO frequency.  

The text output window displays (for USB and LSB), the BFO Frequency, the carrier suppression, and attenuation for audio lows (600 Hz away from the BFO frequency) and audip highs (2400 Hz away from the BFO frequency).  With sideband inversion this will be reversed and audio highs will be closer to the BFO frequency and audio lows will be further away from the BFO frequency.  Again if you don't understand this, use pen and paper and AI to figure it out.
**Note**: **Carrier suppression** (printed in the text window) is the attenuation (of the filter) that is 300 Hz below the BFO. Frequency.  

#### BFO Analysis

1. With **BFO Offset** set to zero and using the **Full Plot**, look at where the BFO frequency will be positioned for LSB and USB.  Do the same for the Audio Lows (i.e. 600 Hz) and Highs (i.e. 2400 Hz).  Can you visually see the lines for BFO Frequency, and the Audio Highs and Lows on the bode plot?
2. Switch to the **Zoom USB** and **Zoom LSB** plots.  Can you visually see the lines for BFO Frequency, and the Audio Highs and Lows on the bode plot?  Correlate the lines and the output in the text window.
3. Next, enter 600 Hz for the **BFO Offset** and see the impact?  What is the BFO Frequency, Carrier Supression and Audio High/Lows in the text window?  Can you visualize what is happening on the bode plots (Full, USB and LSB plots)?
4. Adjust the **BFO Offset**, what happens to the carrier supression and the attenuation of audio highs/lows
5. Adjust the **BFO Offset** until you get a good carrier suppression and half decent audio high/lows attenuation.

## Step 6: Save you parameters
Use **File->Save Profile** to save your analysis.  Use a different name to indicate this is analysis (e.g. sample-filter-complete.json)

## Step 7: Practice
There are several sample filter profiles provide.  Use **File->Oen Profile** to save load the analysis.  Follow the same process outlined in this document to practice optimizing the filter.

| File Name                     | Configuration                                            |
| ----------------------------- | -------------------------------------------------------- |
| perfect-crystals.json         | 4 identical crystals for a 12 MHz filter                 |
| sample-filter.json            | File used in this tutorial for a 12 MHz filter           |
| 4-Mhz-Filter.json             | 4 crystals for a 4 MHz filter                            |
| 12-MHz-Peter-Dueling-612.json | 4 Crystals for a 12 MHz Filter (Dueling 612 Transceiver) |
| 12-MHz-Filter.json            | 4 crystals for a 12 MHz filter                           |
