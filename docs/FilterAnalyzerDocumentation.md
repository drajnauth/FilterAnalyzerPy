# Cohn Filter Analyzer - User Guide

```toc

```

## 1. Installation and Prerequisites

This application is written in Python. To run it cleanly without interfering with your other embedded development tools (like PlatformIO), it is strictly recommended to run it inside an isolated Virtual Environment (`venv`).  In fact, if you run Python on Linux (python3), **pip install** may fail and you may be forced to use a virtual environment.

### Why use a Virtual Environment (`venv`)?

Python relies on a global library system. If you install data-science libraries globally, they might conflict with or bloat the specific versions of Python required by other software on your PC. A `venv` acts as a sealed bubble. Any libraries you install inside the bubble stay in the bubble, keeping your global system safe and clean.

### Setup Instructions (VS Code / Windows)

1. **Install Python:** Ensure Python 3 is installed (downloadable via the Microsoft Store).
2. Visit the github repo (https://github.com/drajnauth/FilterAnalyzerPy) and get the FilterAnalyzerpy repo on your system. Place the code in a suitable directory. You **MUST** run the program from this directory.
   **Note**: There are two Windows batch files (InstallLibs.bat and FilteraAnalyzer.bat) that you can use to create and load the software as well as run the application.  However, read the instructions below carefully before rushing ahead and running the batch files.  I would **strongly** advise you to look at the commands in the batch files and compare to the instructions below. Use the batch files as a reference.

3. **Create the Environment:** Open a command prompt (NOT Powershell) and navagate to the folder with the FilterAnalyzer.py software, and type:

```cmd
python -m venv .venv

```
3. **Activate the Environment:**  From the command line (where you have navigated to the folder with FilterAnalyzer.py software) execute the following to activate the environment:

```
.venv\Scripts\activate.bat

```
   **Note**: This **MUST** be executed from a command prompt and not Powershell terminal window.  It you try and run this from Powershell it will fail.  Using Powershell is beyond the scope of this tutorial.  Google `"activate .venv from Powershell"` for more information.

- The command prompt should change and should see `(.venv)` at the start of your command prompt.

4. **Install Libraries:** In that active terminal with the `(.venv)`  in the prompt, execute the following to install the required libraries:

```cmd
pip install numpy matplotlib pillow

```
5. Tkinter

- The python program uses tkinter. On Microsoft Windows, tkinter is probably installed and the software should work. If you get a tkinter error you will need to manually install tkinter on Windows. This is done by selecting a python install that includes tkinter.  Consider using python from the Microsoft Store.

- In linux, tkinter needs to be installed from the command line.  If you are using Windows ignore this step.
```
sudo apt update
sudo apt install python3-tk
```
### Running the Program

- If you have not already activated the virtual environment, You will first need to activate the virtual environment. This is done by opening a command prompt and navigate to the folder with the FilterAnalyzer.py software then enter the following command:
```
.venv\Scripts\activate.bat
```
   **Note**: This **MUST** be executed from a command prompt and not Powershell terminal window.  It you try and run this from Powershell it will fail.  Using Powershell is beyond the scope of this tutorial.  Google `"activate .venv from Powershell"` for more information.

- Ensure your terminal shows the `(.venv)` prompt. Run the program by typing:
```
python FilterAnalyzer.py
```
  **Note**: On modern versions of linux (possibly Windows), you may have enter **`python3 FilterAnalyzer.py`** instead of **`python FilterAnalyzer.py`**.

  **Note**: There is a Windows batch files (FilteraAnalyzer.bat) that you can use to run the application provided the virtual environment is created and libraries installed.  

---

## 2. Mathematical Model
The method we are using in the Python code is most commonly known in electrical engineering as **Two-Port Network Analysis** using **Transmission Parameters** (or **ABCD Parameters**).

When applied specifically to building something like a ladder filter, engineers usually refer to the technique as the **Chain Matrix Method** or **Cascade Matrix Analysis**.

### 1. The "Two-Port" Concept
In this method, you stop looking at the circuit as a giant, complicated web of interconnected wires. Instead, you treat every single component as an isolated "black box" with an input (Port 1) and an output (Port 2).
- A series capacitor gets its own box.
- A crystal gets its own box.
- A shunt capacitor gets its own box.
### 2. The "Chain" or "Cascade" Multiplication
There are many types of network matrices in RF design (like S-parameters, Z-parameters, and Y-parameters), but ABCD matrices have one unique mathematical superpower: **they cascade perfectly.**

If you connect the output of Box 1 to the input of Box 2, the mathematical model for the combined system is literally just the ABCD matrix of Box 1 multiplied by the ABCD matrix of Box 2.

Because a crystal ladder filter is just a long "chain" of alternating series and shunt components, the Chain Matrix Method allows a computer to calculate the total transfer function of the entire filter simply by multiplying the individual matrices from left to right. This is exactly what the `matrix_series(...) @ matrix_shunt(...)` lines in the Python code are doing!


## 3. General Usage Workflow

The program has 5 windows that are contained in boxes as well as a schematic of the filter showing capacitors and crystals.  
1. The first window is the **Circuit Parameter** windows.  This is where you enter the values for the capacitor and crystals labelled in the circuit schematic.
2. The next window down is the **Z Optimization Constraints**  This is where you can enter requirement for the filter optimization.  Specifically, insertion loss, passband ripple and carrier suppression.  The program tries to identify a termination impedance that satisfies the constraints entered.
3. Beside this window is the **Dishal/Hayward Systhesis**.  You enter parameters that are used to optimize capacitor values.  Note that since Dishal/Hayward assumed perfectly match crystals and the program computes the average of all the crystal motional parameters and use that for the calculation.  This window also has a **Synthesize Caps** button
4. The 3rd box down is the **Analysis Setup** windows.  This is where you select what you want to analyze.  You can select frequency sweep, plot type, impedance optimization, enter termination and BFO offset. 
5. The final windows is a text output window. This is where the program will display calculated values such as filter center frequency, bandwidth, insertion loss, ripple, carrier attenuation as well as audio passband attenuation.

### Step A: Enter Crystal Parameters

Begin by characterizing your physical crystals using a SNA, VNA or an oscillator test fixture. Enter the $C_m$, $L_m$, $R_m$, and $C_c$ values for all four crystals (Y1 - Y4) in the top-left panel.

 In this document all capacitors will be referred to as coupling capacitors.
#### 1. Shunt Capacitors (The Inner Caps)

The "coupling" capacitors that connect the signal path to ground between the crystals (like $C_3$, $C_4$, and $C_5$ in the program we built) are technically **shunt capacitors**, but they are almost universally referred to as **shunt coupling capacitors**.

Their primary job is to couple the RF energy from one crystal resonator to the next, while determining the overall bandwidth of the filter. 

#### 2. Series Capacitors (The Outer Caps)

The "coupling" capacitors at the very front and back of the filter (like $C_1$ and $C_2$) sit in series with the signal path. While they are still technically coupling energy into and out of the filter, they are often given more specific names based on what they are doing:
- **In a Cohn Filter:** Since all capacitors are identical, people usually just call the whole set "the coupling caps."
- **In a Dishal Filter:** Because the end crystals only see a capacitor on one side, their resonant frequency shifts slightly compared to the inner crystals. The outer series capacitors are mathematically calculated to pull those end crystals back onto the correct center frequency. Therefore, these are often called **pulling capacitors**, **tuning caps**, or **matching caps**.

### Step B: Run an Open Termination Plot

If you know the capacitor values for the coupling capacitors, enter them otherwise you can leave the caps at `0`, disable **Enable Term Z**, then select **Term Impedance**, and click **Calculate**. This provides a baseline plot of where your raw crystals naturally resonate.

**Note**: Coupling capacitors values are entered pf.

There are 3 plot modes:

1. **Full Plo**t will generate the plot based on the Start and End sweep frequencies
2. **Zoom USB**, will display the USB side of the skit so that you can see the impact the skirt (i.e. left hand side of the skirt) will have on the audio passband and the carrier attenuation.
3. **Zoom LSB**, will display the LSB side of the skit (i.e right hand side of the skirt) so that you can see the impact the skirt will have on the audio passband and the carrier attenuation

Initially use **Full Plot**.

Finally, you will need to enter the start and end sweep frequencies. This may take some trial and error to figure out. Select frequencies that maximize the view of filter, passband and skirts

From here you can do trial and error to change the termination impedance or the coupling capacitor values to optimize your filter.  Once you are satisfied with you filter you can move on to change the **BFO Offset** to identify a suitable BFO Frequency that will minimize audio passband attenuation and maximize carrier attenuation.

### Step C: Dishal/Hayward Synthesis (Generating Capacitors)

If you do not already have specific capacitors in mind or you want to optimize your coupling capacitors:

1. Look at your raw crystal resonance or look at the mid point of your filter to estimate your **Target Freq (MHz)**.
2. Enter your desired **Target BW (Hz)** (e.g., `2500` for SSB voice).
   **HINT**: Before selecting caps, try to estimate the termination impedance for the filter (probably 100 to 200 Ohms) and plot this.  The text output windows will show the center frequency
   **IMPORTANT:** **A crystal's bandwidth cannot be pulled infinitely.** `Most crystals can only comfortably achieve a bandwidth of roughly 0.05% of their center frequency. For example, if you demand a 10,000 Hz bandwidth from a 4 MHz crystal, the synthesis will likely fail or result in impossible component values`.

1. Click **Synthesize Caps**. The program will average your real-world crystal parameters, apply W7ZOI's Chebyshev mathematics, and auto-populate $C_1 - C_5$ and a theoretical `Z Term Real`.

**IMPORTANT: `Dishal/Hayward algorithm is based on all crystals being identical.  To get around this, the software computes the average values of the crystals and completes the calculation`**.

### Step D: Optimize Termination Impedance (Z Opt)

The synthesized impedance is theoretical. Real-world crystal deviations will warp the filter.

1. Select the **Optimize Term Z** radio button.
2. Set your constraints (e.g., Max IL: 5dB, Ripple: 3dB, Carrier Suppression: 10 dB).
3. Click **Calculate**. The software will sweep from 1 to 2000 ohms to find the termination that yields the steepest skirts without violating your Insertion, Loss Ripple and Carrier Suppression limits.

NOTES:

- dB numbers **MUST BE** positive. The software knows this is a negative number (i.e. a loss or attenuation)
- Max IL is the **`insertion loss`** of the filter at the center frequency.
- If you have very high peaks, he software will fixate (i.e. set center frequency) on the highest point in the filter.
- Carrier Suppression is the amount of attenuation that the carrier needs to have. This is the point on the skirt where the carrier needs to be.

**Optimization Strategy:**
If the optimizer outputs `FAILED: No impedance met the selected constraints`, your expectations are mathematically impossible for your physical components.

- Uncheck **Max Ripple** and calculate again to see how bad the ripple naturally is.
- Uncheck **Skirt Target** (carrier attenuation) to simply optimize for the flattest possible passband, regardless of skirt steepness.

That is start with optimizing insertion loss. Enter a small number like 4 db, and increase until a solution is found. Once an optimum insertion loss is found, the you see if termination can optimize ripple or carrier suppression.

Alternative, if you feel that carrier suppression is most important, uncheck the other parameters (i.e. insertion loss and skirt target).

**Note**: If the analysis has a low carrier attenuation figure, later on you can adjust the BFO frequency to see the effect of sliding the carrier and audio passband down the skirt. If real life, you would adjust the BFO Frequency until the carrier cannot be heard or is almost in the noise floor. The BFO Offset adjustment allows you to do this to see the impact of changing the BFO frequency.

### Step E: Visualizing Termination

Once you have optimized the filter and selecting a termination, enable Term Z and enter the termination impedance. Not this will automatically be populated for you from the prior step. If you wish you can manually change the termination to see the impact of the filter. Once selected, you can execute a full plot.

Also, once you enter the termination impedance, you can enable the **Term Impedance** option to display the real and imaginary impedance as a function of frequency.  The text output window will display the real and imaginary impedance at the center frequency.  This can help with designing a matching network.

### Step E: Analyzing Carrier Suppression and Audio Fidelity

Single Sideband (SSB) relies on a Beat Frequency Oscillator (BFO) to translate RF signals into audible audio.

- **USB (Upper Sideband):** The BFO is placed _below_ the filter center frequency.
- **LSB (Lower Sideband):** The BFO is placed _above_ the filter center frequency

_Note on Sideband Inversion:_ If your radio uses High-Side Injection at the mixer stage, the spectrum flips (USB physically becomes LSB). You must select your BFO offset accordingly based on your specific radio architecture.

#### BFO Background

The BFO Frequency indicates the starting frequency of the audio passband. For USB the BFO Frequency + 600 Hz will be for 600 Hz audio and BFO Frequency + 2400 Hz will be for 2400 Hz audio.  For LSB, the same applies except the audio frequency is subtracted from the BFO Frequency.  If you don't understand this, use AI and take pen and paper and draw a AM modulated signal with side bands and figure it out. The carrier is usually about 300 Hz or so below/above the BFO frequency.  Carrier suppression is the attenuation (of the filter) that is 300 Hz below the BFO.

This program's BFO analysis is primary for the **transmission** of SSB.  For reception of SSB, the BFO Frequency can be closer to the center frequency where you get better audio quality.  Ideally, the BFO Frequency for reception, would be placed at the filters -3dB points.

The text output window of the program displays (for USB and LSB), the BFO Frequency, the carrier suppression, and attenuation for audio lows (600 Hz away from the BFO frequency) and audio highs (2400 Hz away from the BFO frequency).  With sideband inversion this will be reversed and audio highs will be closer to the BFO frequency and audio lows will be further away from the BFO frequency.  Again if you don't understand this, use pen and paper and AI to figure it out.

#### Using the BFO Offset Tool
Adjust the **BFO Offset (Hz)** input to slide your carrier up and down the filter skirt.

1. A larger offset (e.g., `800` Hz) pushes the carrier further down the skirt, granting large **Carrier Suppression**.
2. However, look at the **Audio Lows (600Hz)** printout. A high offset will result in high insertion loss at 600Hz, meaning your voice will lose all its bass and sound "tinny."
3. Adjust the offset until you find the perfect compromise between suppressing the carrier whistle and preserving your vocal fidelity.

	**Note**: When  **BFO Offset**  is 0, you are telling the program to place the Beat Frequency Oscillator _exactly_ on the -3dB edge of the filter.  When you increase the **BFO Offset** the BFO slides further away from the center frequency by the amount specified.  This is useful to identify the BFO Frequency for reception/receive.
	
### Step F: Utilizing the Plot Views

When in **Bode Plot |dB|** mode, use the **Plot View** radio buttons to visually verify your BFO placement.

- **Full Plot:** Shows the entire filter response, demonstrating overall passband flatness and both skirts.
- **Zoom USB / Zoom LSB:** Zooms tightly into the selected skirt. The plot draws a green/purple line where your carrier sits, and draws boundary lines at the 600 Hz (Lows) and 2400 Hz (Highs) marks. This provides instant visual confirmation that your desired audio is "fitting" safely inside the flat portion of the passband.

## 4. Data Analysis

The software has a text windows where various calculations will be placed.

- Center frequency
- 3dB Bandwidth
- Passband ripple
- Peak Gain (insertion loss) at Center Frequency
- Optimum termination
- Termination impedance (real and imaginary)
- SSB Analysis. For the LSB or USB side of the filter's skirt
  - Carrier Supression
  - Audio passband Low frequency (600 Hz) attenuation
  - Audio passband High frequency (2400 Hz) attenuation

## 5. Manual Data Analysis

The software allows you to change parameters to see the impact on the filter. You are free to alter:

- capacitor values (C1, C3, C4, C5, C2)
- crystal motional parameters
- Termination (applies to both sides)

## 6. Save/Recall

The software allows you to save all the values entered in the data fields in a json file. Select **`File->Open Profile`** or **`File->Save Profile`**.
