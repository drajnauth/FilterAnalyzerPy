

# Cohn Filter Analyzer - User Guide

## 1. Installation and Prerequisites

This application is written in Python. To run it cleanly without interfering with your other embedded development tools (like PlatformIO), it is strictly recommended to run it inside an isolated Virtual Environment (`venv`).

### Why use a Virtual Environment (`venv`)?

Python relies on a global library system. If you install data-science libraries globally, they might conflict with or bloat the specific versions of Python required by other software on your PC. A `venv` acts as a sealed bubble. Any libraries you install inside the bubble stay in the bubble, keeping your global system safe and clean.

### Setup Instructions (VS Code / Windows)

1. **Install Python:** Ensure Python 3 is installed (downloadable via the Microsoft Store).
2. **Create the Environment:** Open your project folder in VS Code, open a New Terminal (`Ctrl+Shift+` ` `), and type:
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



### Running the Program

Ensure your terminal shows the `(.venv)` prompt. Run the program by typing:
`python FilterAnalyzer.py` (or by clicking the Run Python File button in VS Code).

---

## 2. General Usage Workflow

### Step A: Enter Crystal Parameters

Begin by characterizing your physical crystals using a VNA or an oscillator test fixture. Enter the $C_m$, $L_m$, $R_m$, and $C_c$ values for all four crystals (Y1 - Y4) in the top-left panel.

### Step B: Run an Open Termination Plot

Before adding capacitors or optimizing, leave the caps at `0`, select **Unterminated Z**, and click **Calculate**. This provides a baseline plot of where your raw crystals naturally resonate.

### Step C: Dishal/Hayward Synthesis (Generating Capacitors)

If you do not already have specific capacitors in mind:

1. Look at your raw crystal resonance to estimate your **Target Freq (MHz)**.
2. Enter your desired **Target BW (Hz)** (e.g., `2500` for SSB voice).
* *Note on Limits:* A crystal's bandwidth cannot be pulled infinitely. Most crystals can only comfortably achieve a bandwidth of roughly 0.05% of their center frequency. If you demand a 10,000 Hz bandwidth from a 4 MHz crystal, the synthesis will likely fail or result in impossible component values.


3. Click **Synthesize Caps**. The program will average your real-world crystal parameters, apply W7ZOI's Chebyshev mathematics, and auto-populate $C_1 - C_5$ and a theoretical `Z Term Real`.

### Step D: Optimize Termination Impedance (Z Opt)

The synthesized impedance is theoretical. Real-world crystal deviations will warp the filter.

1. Select the **Optimize Term Z** radio button.
2. Set your constraints (e.g., Max IL: 10dB, Ripple: 3dB).
3. Click **Calculate**. The software will sweep from 1 to 2000 ohms to find the termination that yields the steepest skirts without violating your Insertion Loss or Ripple limits.

**Optimization Strategy:**
If the optimizer outputs `FAILED: No impedance met the selected constraints`, your expectations are mathematically impossible for your physical components.

* Uncheck **Max Ripple** and calculate again to see how bad the ripple naturally is.
* Uncheck **Skirt Target** to simply optimize for the flattest possible passband, regardless of skirt steepness.

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