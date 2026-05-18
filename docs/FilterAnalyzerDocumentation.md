
```toc
```

# Cohn Filter Analyzer - User Guide

## 1. Installation and Prerequisites

This application is written in Python. To run it cleanly without interfering with your other embedded development tools (like PlatformIO), it is strictly recommended to run it inside an isolated Virtual Environment (`venv`).

### Why use a Virtual Environment (`venv`)?

Python relies on a global library system. If you install data-science libraries globally, they might conflict with or bloat the specific versions of Python required by other software on your PC. A `venv` acts as a sealed bubble. Any libraries you install inside the bubble stay in the bubble, keeping your global system safe and clean.

### Setup Instructions (VS Code / Windows)

1. **Install Python:** Ensure Python 3 is installed (downloadable via the Microsoft Store).
2. Visit the github repo (https://github.com/drajnauth/FilterAnalyzerPy) and get the FilterAnalyzerpy repo on your system.  Place the code in a suitable directory.  You **MUST** run the program from this directory.
3. **Create the Environment:** Open a command prompt and navagate to the folder with the FilterAnalyzer.py software, and type:
```cmd
python -m venv .venv

```

3. **Activate the Environment:** * Open the VS Code Command Palette (`Ctrl+Shift+P`).
* Type **Python: Select Interpreter** and select the path ending in `('.venv': venv)`.
* Close your terminal and open a New Terminal. You should see `(.venv)` in green at the start of your command prompt.


4. **Install Libraries:** In that active terminal, run:
```cmd
pip install numpy matplotlib pillow

```
5. Tkinter
- The python program using tkinter.  On Microsoft Windows, tkinter is probably installed and the software will work. If you get a tkinter error you will need to manually install tkinter on Windows.  This is done by selecting a python installed that includes tkinter.  Look at using python from the Microsoft Store.

- In linux, tkinter needs to be installed from the command line.
```	 sudo apt update 
	 sudo apt install python3-tk
```


### Running the Program

- You will first need to active the virtual environment.  This is done by entering the following command within the directory with the FilterAnalyzer.py and the .venv directory.
```
.venv\Scripts\activate.bat
```

- Ensure your terminal shows the `(.venv)` prompt. Run the program by typing:
```
python FilterAnalyzer.py
```

---

## 2. General Usage Workflow



### Step A: Enter Crystal Parameters

Begin by characterizing your physical crystals using a SNA, VNA or an oscillator test fixture. Enter the $C_m$, $L_m$, $R_m$, and $C_c$ values for all four crystals (Y1 - Y4) in the top-left panel.  

### Step B: Run an Open Termination Plot

If you know the capacitor values for the coupling capacitors, enter them otherwise you can  leave the caps at `0`, select **Unterminated Z**, and click **Calculate**. This provides a baseline plot of where your raw crystals naturally resonate.

**Note**: Coupling capacitors values are entered pf.  

There are 3 plot modes:
1. Full Plot will generate the plot based on the Start and End sweep frequencies
2. Zoom USB, will display the USB side of the skit so that you can see the impact the skirt (i.e. left hand side of the skirt) will have on the audio passband and the carrier attenuation.  
3. Zoom LSB, will display the LSB side of the skit (i.e right hand side of the skirt) so that you can see the impact the skirt will have on the audio passband and the carrier attenuation

Initially use Full plot.  

Once you are satisfied with you filter you can move on to change the BFO offset (from the center frequency) to minimize audio passband attenuation and maximize carrier attenuation.

Finally, you will need to enter the start and end sweep frequencies.  This may take some trial and error to figure out.  Select frequencies that maximize the view of filter, passband and skirts

### Step C: Dishal/Hayward Synthesis (Generating Capacitors)

If you do not already have specific capacitors in mind:

1. Look at your raw crystal resonance to estimate your **Target Freq (MHz)**.
2. Enter your desired **Target BW (Hz)** (e.g., `2500` for SSB voice).
* **IMPORTANT: `A crystal's bandwidth cannot be pulled infinitely. Most crystals can only comfortably achieve a bandwidth of roughly 0.05% of their center frequency. If you demand a 10,000 Hz bandwidth from a 4 MHz crystal, the synthesis will likely fail or result in impossible component values`**.
1. Click **Synthesize Caps**. The program will average your real-world crystal parameters, apply W7ZOI's Chebyshev mathematics, and auto-populate $C_1 - C_5$ and a theoretical `Z Term Real`.

**IMPORTANT: `Dishal/Hayward algorithm is based on all crystals being identical.  To get around this, the software take the average values of the crystals and completed the calculation`**.

### Step D: Optimize Termination Impedance (Z Opt)

The synthesized impedance is theoretical. Real-world crystal deviations will warp the filter.

1. Select the **Optimize Term Z** radio button.
2. Set your constraints (e.g., Max IL: 10dB, Ripple: 3dB, Skirt Target: 40 dB).
3. Click **Calculate**. The software will sweep from 1 to 2000 ohms to find the termination that yields the steepest skirts without violating your Insertion Loss or Ripple limits.

NOTES:
- dB numbers **MUST BE** positive.  The software knows this is a negative number (i.e. a loss or attenuation)
- Max IL is the **`insertion loss`** of the filter at the center frequency.  
- If you have very high peaks, he software will fixate (i.e. set center frequency) on the highest point in the filter.
- Skirt Target is the amount of attenuation that the carrier need to have.  This is the point on the skirt where the carrier needs to be.

**Optimization Strategy:**
If the optimizer outputs `FAILED: No impedance met the selected constraints`, your expectations are mathematically impossible for your physical components.

* Uncheck **Max Ripple** and calculate again to see how bad the ripple naturally is.
* Uncheck **Skirt Target** (carrier attenuation) to simply optimize for the flattest possible passband, regardless of skirt steepness.

That is start with optimizing insertion loss.  Enter a small number like 4 db, and increase until a solution is found.  Once an optimum insertion loss is found, the you see if termination can optimize ripple or carrier suppression.  

Alternative, if you fell that carrier suppression is most important, uncheck the other parameters (i.e. insertion loss and skirt target)

Note that if the analysis has a low carrier attenuation figure, later on you can adjust the BFO frequency to see the effect of sliding the carrier and audio passband down the skirt.  If real life, you would adjust the BFO until the carrier cannot be heard or is almost in the noise floor.  The BFO adjustment allows you to do this to see the impact of changing the BFO frequency.



### Step E: Visualizing Termination

Once you have optimized the filter and selecting a termination, enable Term Z and enter the termination impedance.  Not this will automatically be populated for you from the prior step.  If you wish you can manually change the termination to see the impact of the filter.  Once selected, you can execute a full plot.

### Step E: Analyzing Carrier Suppression and Audio Fidelity

Single Sideband (SSB) relies on a Beat Frequency Oscillator (BFO) to translate RF signals into audible audio.

* **USB (Upper Sideband):** The BFO is placed *below* the filter.
* **LSB (Lower Sideband):** The BFO is placed *above* the filter.

*Note on Sideband Inversion:* If your radio uses High-Side Injection at the mixer stage, the spectrum flips (USB physically becomes LSB). You must select your BFO offset accordingly based on your specific radio architecture.

**Using the BFO Offset Tool:**
Adjust the **BFO Offset (Hz)** input to slide your carrier up and down the filter skirt.

1. A larger offset (e.g., `800` Hz) pushes the carrier further down the skirt, granting excellent **Carrier Suppression** (-50 dB).
2. However, look at the **Audio Lows (600Hz)** printout. A high offset will result in high insertion loss at 600Hz, meaning your voice will lose all its bass and sound "tinny."
3. Adjust the offset until you find the perfect compromise between suppressing the carrier whistle and preserving your vocal fidelity.

### Step F: Utilizing the Plot Views

When in **Bode Plot |dB|** mode, use the **Plot View** radio buttons to visually verify your BFO placement.

* **Full Plot:** Shows the entire filter response, demonstrating overall passband flatness and both skirts.
* **Zoom USB / Zoom LSB:** Zooms tightly into the selected skirt. The plot draws a green/purple line where your carrier sits, and draws boundary lines at the 600 Hz (Lows) and 2400 Hz (Highs) marks. This provides instant visual confirmation that your desired audio is "fitting" safely inside the flat portion of the passband.


## 3. Data Analysis
The software has a text windows where various calculations will be placed.  
- Center frequency 
- 3dB Bandwidth
- Passband ripple
- Peak Gain (insertion loss) at Center Frequency
- Optimum termination
- SSB Analysis.  For the LSB or USB side of the filter's skirt
	- Carrier Supression 
	- Audio passband Low frequency (600 Hz) attenuation
	- Audio passband High frequency (2400 Hz) attenuation

## 4. Manual Data Analysis
The software allows you to change parameters to see the impact on the filter.  You are free to alter:
- capacitor values (C1, C3, C4, C5, C2) 
- crystal motional parameters
- Termination (applies to both sides)

## 5. Save/Recall
The software allows you to save all the values entered in the data fields in a json file.  Select **`File->Open Profile`** or **`File->Save Profile`**.