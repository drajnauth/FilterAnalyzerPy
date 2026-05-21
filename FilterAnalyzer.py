"""
Crystal Ladder Filter Analyzer (Cohn/Dishal Topology)
Version: 0.1 Beta
Date: May 16, 2026

This application simulates the RF transfer function of a 4-pole crystal ladder filter.
It uses ABCD parameter matrix cascading to compute insertion loss, passband ripple,
and input impedance. It includes a Dishal/Hayward (W7ZOI) synthesis tool to estimate
optimal coupling capacitors based on target bandwidths.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
import json
import os

# ==========================================
# 1. Mathematical Core (ABCD Matrices)
# ==========================================
def z_capacitor(f, C):
    """Calculates complex impedance of a capacitor. Adds epsilon to avoid div-by-zero."""
    C = max(C, 1e-20) 
    omega = 2 * np.pi * f
    return 1.0 / (1j * omega * C)

def z_crystal(f, Cm, Lm, Rs, Cc):
    """Calculates the Butterworth-Van Dyke (BVD) equivalent impedance of a quartz crystal."""
    Cm, Lm, Cc = max(Cm, 1e-20), max(Lm, 1e-20), max(Cc, 1e-20)
    omega = 2 * np.pi * f
    Zm = Rs + 1j * (omega * Lm - 1.0 / (omega * Cm))
    Zc = 1.0 / (1j * omega * Cc)
    return (Zm * Zc) / (Zm + Zc)

def matrix_series(Z):
    """Creates an ABCD matrix for a series-connected component."""
    N = len(Z)
    A = np.zeros((N, 2, 2), dtype=complex)
    A[:, 0, 0] = 1.0; A[:, 0, 1] = Z
    A[:, 1, 0] = 0.0; A[:, 1, 1] = 1.0
    return A

def matrix_shunt(Z):
    """Creates an ABCD matrix for a shunt-connected component to ground."""
    N = len(Z)
    A = np.zeros((N, 2, 2), dtype=complex)
    A[:, 0, 0] = 1.0;       A[:, 0, 1] = 0.0
    Z_safe = np.where(Z == 0j, 1e-20 + 0j, Z) 
    A[:, 1, 0] = 1.0 / Z_safe; A[:, 1, 1] = 1.0
    return A

# ==========================================
# 2. GUI Application Class
# ==========================================
class CrystalAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cohn Filter Analyzer")
        self.root.geometry("980x950")
        
        self.create_menu()
        self.create_widgets()
        self.reset_all_fields()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New Profile", command=self.reset_all_fields)
        filemenu.add_separator()
        filemenu.add_command(label="Open Profile (JSON)", command=self.load_data)
        filemenu.add_command(label="Save Profile (JSON)", command=self.save_data)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=filemenu)
        
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Help contents", command=self.open_help)
        helpmenu.add_separator()
        helpmenu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        
        self.root.config(menu=menubar)

    def create_widgets(self):
        # --- Row 0: Crystals, Caps, and Image ---
        row0_container = ttk.Frame(self.root)
        row0_container.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        param_frame = ttk.LabelFrame(row0_container, text="Circuit Parameters", padding=10)
        param_frame.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(param_frame, text="Capacitors (pF):").grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.caps = {}
        for idx, name in enumerate(["C1", "C3", "C4", "C5", "C2"]):
            ttk.Label(param_frame, text=name).grid(row=0, column=idx+1)
            entry = ttk.Entry(param_frame, width=8)
            entry.grid(row=1, column=idx+1, padx=2, pady=(0, 15))
            self.caps[name] = entry

        crystal_labels = ["Y1", "Y2", "Y3", "Y4"]
        for idx, clabel in enumerate(crystal_labels):
            ttk.Label(param_frame, text=clabel, font=("TkDefaultFont", 9, "bold")).grid(row=2, column=idx+1)

        row_labels = [
            ("Motional Cap (fF):", "cm"), ("Motional Ind (mH):", "lm"),
            ("Motional Res (Ohm):", "rm"), ("Case Cap (pF):", "cc")
        ]

        self.crystals = {"Y1": {}, "Y2": {}, "Y3": {}, "Y4": {}}
        for r_idx, (label_text, param_key) in enumerate(row_labels):
            ttk.Label(param_frame, text=label_text).grid(row=r_idx+3, column=0, sticky="e")
            for c_idx, y_key in enumerate(crystal_labels):
                entry = ttk.Entry(param_frame, width=8)
                entry.grid(row=r_idx+3, column=c_idx+1, padx=2, pady=2)
                self.crystals[y_key][param_key] = entry

        img_frame = ttk.Frame(row0_container)
        img_frame.pack(side="right", fill="both", expand=True)
        try:
            img = Image.open("CrystalFilterSchematic.jpg")
            img = img.resize((450, 180), Image.Resampling.LANCZOS)
            self.schematic = ImageTk.PhotoImage(img)
            ttk.Label(img_frame, image=self.schematic).pack()
        except Exception:
            ttk.Label(img_frame, text="[Schematic Image Not Found]").pack()

        # --- Row 1: Optimization and Synthesis ---
        row1_container = ttk.Frame(self.root)
        row1_container.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        opt_frame = ttk.LabelFrame(row1_container, text="Z Optimization Constraints", padding=10)
        opt_frame.pack(side="left", fill="y", padx=(0, 10))
        
        self.en_il = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt_frame, variable=self.en_il).grid(row=0, column=0)
        ttk.Label(opt_frame, text="Max IL (dB):").grid(row=0, column=1, sticky="e")
        self.opt_il = ttk.Entry(opt_frame, width=8)
        self.opt_il.grid(row=0, column=2, padx=5, pady=2)

        self.en_rip = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt_frame, variable=self.en_rip).grid(row=1, column=0)
        ttk.Label(opt_frame, text="Max Ripple (dB):").grid(row=1, column=1, sticky="e")
        self.opt_rip = ttk.Entry(opt_frame, width=8)
        self.opt_rip.grid(row=1, column=2, padx=5, pady=2)

        self.en_skirt = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt_frame, variable=self.en_skirt).grid(row=2, column=0)
        ttk.Label(opt_frame, text="Carrier Supp (dB):").grid(row=2, column=1, sticky="e")
        self.opt_skirt = ttk.Entry(opt_frame, width=8)
        self.opt_skirt.grid(row=2, column=2, padx=5, pady=2)

        syn_frame = ttk.LabelFrame(row1_container, text="Dishal/Hayward Synthesis", padding=10)
        syn_frame.pack(side="left", fill="y")

        ttk.Label(syn_frame, text="Target Freq (MHz):").grid(row=0, column=0, sticky="e")
        self.syn_f0 = ttk.Entry(syn_frame, width=12)
        self.syn_f0.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(syn_frame, text="Target BW (Hz):").grid(row=1, column=0, sticky="e")
        self.syn_bw = ttk.Entry(syn_frame, width=12)
        self.syn_bw.grid(row=1, column=1, padx=5, pady=2)

        ttk.Button(syn_frame, text="Synthesize Caps", command=self.synthesize_caps).grid(row=2, column=0, columnspan=2, pady=5)

        # --- Row 2: Analysis Setup ---
        row2_container = ttk.Frame(self.root)
        row2_container.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        ctrl_frame = ttk.LabelFrame(row2_container, text="Analysis Setup", padding=10)
        ctrl_frame.pack(fill="both", expand=True)

        ttk.Label(ctrl_frame, text="Sweep Start (MHz):").grid(row=0, column=0, sticky="e")
        self.f_start = ttk.Entry(ctrl_frame, width=10)
        self.f_start.grid(row=0, column=1, padx=5)

        ttk.Label(ctrl_frame, text="Sweep End (MHz):").grid(row=1, column=0, sticky="e")
        self.f_end = ttk.Entry(ctrl_frame, width=10)
        self.f_end.grid(row=1, column=1, padx=5)

        self.calc_mode = tk.StringVar(value="bode")
        ttk.Radiobutton(ctrl_frame, text="Bode Plot |dB|", variable=self.calc_mode, value="bode").grid(row=0, column=2, padx=15, sticky="w")
        ttk.Radiobutton(ctrl_frame, text="Term Impedance (r+j)", variable=self.calc_mode, value="z_unterm").grid(row=1, column=2, padx=15, sticky="w")
        ttk.Radiobutton(ctrl_frame, text="Optimize Term Impedance", variable=self.calc_mode, value="z_opt").grid(row=2, column=2, padx=15, sticky="w")

        self.term_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(ctrl_frame, text="Enable Term Z", variable=self.term_enabled).grid(row=0, column=3, padx=15, sticky="w")
        
        ttk.Label(ctrl_frame, text="Z Term Real (\u03A9):").grid(row=1, column=3, sticky="e")
        self.z_term_r = ttk.Entry(ctrl_frame, width=8)
        self.z_term_r.grid(row=1, column=4, sticky="w")
        
        ttk.Label(ctrl_frame, text="BFO Offset (Hz):").grid(row=2, column=3, sticky="e")
        self.bfo_offset = ttk.Entry(ctrl_frame, width=8)
        self.bfo_offset.grid(row=2, column=4, sticky="w")

        ttk.Label(ctrl_frame, text="Plot View:").grid(row=0, column=5, sticky="e", padx=5)
        self.plot_zoom = tk.StringVar(value="full")
        ttk.Radiobutton(ctrl_frame, text="Full Plot", variable=self.plot_zoom, value="full").grid(row=0, column=6, sticky="w")
        ttk.Radiobutton(ctrl_frame, text="Zoom USB", variable=self.plot_zoom, value="usb").grid(row=1, column=6, sticky="w")
        ttk.Radiobutton(ctrl_frame, text="Zoom LSB", variable=self.plot_zoom, value="lsb").grid(row=2, column=6, sticky="w")

        ttk.Button(ctrl_frame, text="Calculate", command=self.calculate).grid(row=0, column=7, padx=20, rowspan=2, ipady=10)
        ttk.Button(ctrl_frame, text="Exit", command=self.exit_app).grid(row=2, column=7, padx=20)

        # --- Row 3: Text Output ---
        self.text_out = tk.Text(self.root, height=14, wrap="word", bg="#f4f4f4")
        self.text_out.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    def get_float(self, entry_widget, field_name):
        val = entry_widget.get().strip()
        if not val:
            raise ValueError(f"'{field_name}' cannot be empty. Please enter a valid number.")
        try:
            return float(val)
        except ValueError:
            raise ValueError(f"Invalid number in '{field_name}': '{val}'")

    def reset_all_fields(self):
        def reset_entry(entry_widget, default_val="0"):
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, default_val)

        for k in self.caps: reset_entry(self.caps[k])
        for y in self.crystals:
            for p in self.crystals[y]:
                reset_entry(self.crystals[y][p])
        
        reset_entry(self.f_start)
        reset_entry(self.f_end)
        reset_entry(self.z_term_r)
        
        reset_entry(self.opt_il, "10.0")
        reset_entry(self.opt_rip, "3.0")
        reset_entry(self.opt_skirt, "20.0")
        
        reset_entry(self.syn_f0, "0")
        reset_entry(self.syn_bw, "0")
        
        reset_entry(self.bfo_offset, "0")

        self.text_out.delete(1.0, tk.END)
        self.log("Ready. Workspace reset to default values.")

    def log(self, message):
        self.text_out.insert(tk.END, message + "\n")
        self.text_out.see(tk.END)

    def show_about(self):
        about_text = "Program Name: Cohn Filter Analyzer\nVersion: 0.1 Beta\nRelease Date: 16/05/2026\nAuthor: Some Body"
        messagebox.showinfo("About", about_text)

    def exit_app(self):
        plt.close('all')
        self.root.quit()
        self.root.destroy()

    # Updated 20May26 to flag multiple peaks in the filter 
    def print_performance_metrics(self, freqs, gain_db, best_R=None, best_metric=None, check_skirt=False):
        max_gain = np.max(gain_db)
        
        # ========================================================
        # NEW: MULTI-PEAK EXCURSION DETECTOR
        # ========================================================
        # 1. Isolate the "top" of the filter (everything within 10dB of the peak)
        top_indices = np.where(gain_db > max_gain - 10.0)[0]
        
        warning_flagged = False
        if len(top_indices) > 2:
            top_slice = gain_db[top_indices]
            
            # 2. Find Local Maxima (Pixels that are higher than both their left and right neighbors)
            # We add +1 because the slice shifts the index by 1
            peaks = np.where((top_slice[1:-1] > top_slice[:-2]) & (top_slice[1:-1] > top_slice[2:]))[0] + 1
            
            # 3. If multiple peaks exist, find how deep the valley is between them
            if len(peaks) > 1:
                # Find the absolute minimum value between the first peak and the last peak
                valley_min = np.min(top_slice[peaks[0]:peaks[-1]])
                excursion = max_gain - valley_min
                
                # 4. If the excursion is worse than 3.0 dB, throw a warning
                if excursion > 3.0:
                    self.log("\n" + "="*50)
                    self.log(" ⚠️ WARNING: SEVERE MULTI-PEAKING DETECTED!")
                    self.log(f"    • {len(peaks)} distinct peaks found in the passband.")
                    self.log(f"    • Maximum peak-to-valley excursion: {excursion:.1f} dB.")
                    self.log("    • Filter is unterminated OR crystals are severely unmatched.")
                    self.log("    • Measurements below may be physically invalid.")
                    self.log("="*50)
                    warning_flagged = True
        # ========================================================
        
        crossings_3db = np.where(np.diff(np.sign(gain_db - (max_gain - 3.0))))[0]
        
        if len(crossings_3db) < 2:
            if not warning_flagged:
                self.log("Could not detect full -3dB bandwidth within sweep limits.")
            return None

        f_low = freqs[crossings_3db[0]]
        f_high = freqs[crossings_3db[-1]]
        bw = f_high - f_low
        center_freq = (f_high + f_low) / 2
        
        self.syn_f0.delete(0, tk.END)
        self.syn_f0.insert(0, f"{center_freq / 1e6:.6f}")
        
        # Evaluate ripple only on the inner 80% of the passband
        bw_indices = crossings_3db[-1] - crossings_3db[0]
        margin = int(bw_indices * 0.10)
        
        if margin > 0:
            flat_top_gains = gain_db[crossings_3db[0] + margin : crossings_3db[-1] - margin]
            ripple = np.max(flat_top_gains) - np.min(flat_top_gains)
        else:
            ripple = 0.0

        offset = self.get_float(self.bfo_offset, "BFO Offset")
        
        bfo_usb = f_low - offset
        bfo_lsb = f_high + offset
        
        gain_usb = np.interp(bfo_usb, freqs, gain_db)
        gain_lsb = np.interp(bfo_lsb, freqs, gain_db)
        atten_usb = max_gain - gain_usb
        atten_lsb = max_gain - gain_lsb

        gain_usb_low = np.interp(bfo_usb + 600, freqs, gain_db)
        gain_usb_high = np.interp(bfo_usb + 2400, freqs, gain_db)
        gain_lsb_low = np.interp(bfo_lsb - 600, freqs, gain_db)
        gain_lsb_high = np.interp(bfo_lsb - 2400, freqs, gain_db)
        
        il_usb_low = abs(gain_usb_low)
        il_usb_high = abs(gain_usb_high)
        il_lsb_low = abs(gain_lsb_low)
        il_lsb_high = abs(gain_lsb_high)

        if best_R is not None:
            self.log(f"--> Optimal Termination Resistance Found: {best_R} Ohms")
            if check_skirt and best_metric is not None:
                self.log(f"--> Resulting Shape Factor: {best_metric:.2f}")

        self.log("\n--- Absolute Filter Performance ---")
        self.log(f"Peak Gain (Insertion Loss): {max_gain:.2f} dB")
        self.log(f"Passband Ripple: {ripple:.2f} dB")
        self.log(f"Center Frequency (fc): {center_freq / 1e6:.6f} MHz")
        self.log(f"-3dB Bandwidth: {bw:.1f} Hz")

        self.log("\n--- SSB System Performance (Baseband Mapping) ---")
        self.log(f"Effective Audio Frequencies Passed: {offset:.0f} Hz to {(offset + bw):.0f} Hz")
        
        self.log(f"\n[ USB Mode ]  (Carrier BFO = {bfo_usb / 1e6:.6f} MHz)")
        self.log(f"  -> Carrier Suppression: {atten_usb:.1f} dB down")
        self.log(f"  -> Audio Lows  (IL at BFO + 600Hz):  {il_usb_low:.2f} dB")
        self.log(f"  -> Audio Highs (IL at BFO + 2400Hz): {il_usb_high:.2f} dB")
        
        self.log(f"\n[ LSB Mode ]  (Carrier BFO = {bfo_lsb / 1e6:.6f} MHz)")
        self.log(f"  -> Carrier Suppression: {atten_lsb:.1f} dB down")
        self.log(f"  -> Audio Lows  (IL at BFO - 600Hz):  {il_lsb_low:.2f} dB")
        self.log(f"  -> Audio Highs (IL at BFO - 2400Hz): {il_lsb_high:.2f} dB")
        
        return center_freq, f_low, f_high, bfo_usb, bfo_lsb

    def synthesize_caps(self):
        self.text_out.delete(1.0, tk.END)
        self.log("--- Dishal/Hayward Synthesis Started ---")
        try:
            target_f0 = self.get_float(self.syn_f0, "Synthesis Target Freq") * 1e6
            target_bw = self.get_float(self.syn_bw, "Synthesis Target BW")
            
            if target_bw <= 0 or target_f0 <= 0:
                raise ValueError("Target Freq and BW must be greater than 0.")

            cm_vals, lm_vals = [], []
            for y in self.crystals:
                cm = self.get_float(self.crystals[y]["cm"], f"Crystal {y} Cm")
                lm = self.get_float(self.crystals[y]["lm"], f"Crystal {y} Lm")
                if cm <= 0 or lm <= 0:
                    raise ValueError(f"Crystal {y} Cm and Lm values must be greater than 0.")
                cm_vals.append(cm)
                lm_vals.append(lm)
                
            cm_avg = np.mean(cm_vals) * 1e-15
            lm_avg = np.mean(lm_vals) * 1e-3

            q1 = 1.046; k12 = 0.913; k23 = 0.871

            C12 = (cm_avg * target_f0) / (target_bw * k12)
            C23 = (cm_avg * target_f0) / (target_bw * k23)

            c_3 = C12 * 1e12; c_4 = C23 * 1e12; c_5 = c_3
            c_1 = c_3; c_2 = c_5
            r_term = (2 * np.pi * lm_avg * target_bw) / q1

            self.caps["C1"].delete(0, tk.END); self.caps["C1"].insert(0, f"{c_1:.1f}")
            self.caps["C2"].delete(0, tk.END); self.caps["C2"].insert(0, f"{c_2:.1f}")
            self.caps["C3"].delete(0, tk.END); self.caps["C3"].insert(0, f"{c_3:.1f}")
            self.caps["C4"].delete(0, tk.END); self.caps["C4"].insert(0, f"{c_4:.1f}")
            self.caps["C5"].delete(0, tk.END); self.caps["C5"].insert(0, f"{c_5:.1f}")
            
            self.z_term_r.delete(0, tk.END); self.z_term_r.insert(0, f"{r_term:.0f}")
            self.term_enabled.set(True)

            self.log("Success! Capacitors synthesized and loaded into the UI.")
        except Exception as e:
            messagebox.showerror("Synthesis Error", str(e))
            self.log(f"Synthesis Error: {str(e)}")

    def build_transfer_matrix(self, freqs):
        c1 = self.get_float(self.caps["C1"], "C1") * 1e-12
        c2 = self.get_float(self.caps["C2"], "C2") * 1e-12
        c3 = self.get_float(self.caps["C3"], "C3") * 1e-12
        c4 = self.get_float(self.caps["C4"], "C4") * 1e-12
        c5 = self.get_float(self.caps["C5"], "C5") * 1e-12

        def extract_xtal(y_name):
            cm = self.get_float(self.crystals[y_name]["cm"], f"{y_name} Cm") * 1e-15
            lm = self.get_float(self.crystals[y_name]["lm"], f"{y_name} Lm") * 1e-3
            rm = self.get_float(self.crystals[y_name]["rm"], f"{y_name} Rm")
            cc = self.get_float(self.crystals[y_name]["cc"], f"{y_name} Cc") * 1e-12
            if cm <= 0 or lm <= 0: raise ValueError(f"{y_name} Cm and Lm cannot be zero.")
            return z_crystal(freqs, cm, lm, rm, cc)

        Z_Y1, Z_Y2 = extract_xtal("Y1"), extract_xtal("Y2")
        Z_Y3, Z_Y4 = extract_xtal("Y3"), extract_xtal("Y4")

        Total = matrix_series(z_capacitor(freqs, c1)) @ matrix_series(Z_Y1) @ matrix_shunt(z_capacitor(freqs, c3)) @ \
                matrix_series(Z_Y2) @ matrix_shunt(z_capacitor(freqs, c4)) @ matrix_series(Z_Y3) @ \
                matrix_shunt(z_capacitor(freqs, c5)) @ matrix_series(Z_Y4) @ matrix_series(z_capacitor(freqs, c2))
        return Total

    def calculate(self):
        self.text_out.delete(1.0, tk.END) 
        self.log("--- Starting Calculation ---")
        
        try:
            f_s = self.get_float(self.f_start, "Sweep Start Freq") * 1e6
            f_e = self.get_float(self.f_end, "Sweep End Freq") * 1e6
            if f_s <= 0 or f_e <= 0 or f_s >= f_e:
                raise ValueError("Sweep bounds invalid. Ensure Start < End.")
                
            freqs = np.linspace(f_s, f_e, 3000)
            mode = self.calc_mode.get()
            _ = self.get_float(self.bfo_offset, "BFO Offset")

            if mode == "z_opt":
                limit_il = self.get_float(self.opt_il, "Max IL Limit")
                limit_rip = self.get_float(self.opt_rip, "Max Ripple Limit")
                target_skirt = self.get_float(self.opt_skirt, "Skirt Target Limit")
                
                check_il, check_rip, check_skirt = self.en_il.get(), self.en_rip.get(), self.en_skirt.get()
                
                self.log("Running Selective Optimization (Sweeping Z from 1 to 2000 ohms)...")
                self.root.update()
                
                Total = self.build_transfer_matrix(freqs)
                A, B, C, D = Total[:, 0, 0], Total[:, 0, 1], Total[:, 1, 0], Total[:, 1, 1]
                
                best_R = None
                best_metric = float('inf')
                
                for R_test in range(1, 2000, 5):
                    V_out_V_in = R_test / (A * R_test + B + C * R_test**2 + D * R_test)
                    gain_db = 20 * np.log10(np.abs(2 * V_out_V_in))
                    max_gain = np.max(gain_db)
                    insertion_loss = abs(max_gain)
                    
                    if check_il and insertion_loss > limit_il: continue 
                        
                    crossings_3db = np.where(np.diff(np.sign(gain_db - (max_gain - 3.0))))[0]
                    if len(crossings_3db) < 2: continue 
                        
                    idx_low, idx_high = crossings_3db[0], crossings_3db[-1]
                    
                    # Evaluate ripple only on the inner 80% of the passband
                    bw_indices = idx_high - idx_low
                    margin = int(bw_indices * 0.10)
                    
                    if margin > 0:
                        flat_top_gains = gain_db[idx_low + margin : idx_high - margin]
                        ripple = np.max(flat_top_gains) - np.min(flat_top_gains)
                    else:
                        ripple = 0.0
                    
                    if check_rip and ripple > limit_rip: continue
                        
                    if check_skirt:
                        crossings_skirt = np.where(np.diff(np.sign(gain_db - (max_gain - target_skirt))))[0]
                        if len(crossings_skirt) < 2: continue 
                        bw_3 = freqs[idx_high] - freqs[idx_low]
                        bw_skirt = freqs[crossings_skirt[-1]] - freqs[crossings_skirt[0]]
                        current_metric = bw_skirt / bw_3 
                    else:
                        current_metric = ripple 
                    
                    if current_metric < best_metric:
                        best_metric = current_metric
                        best_R = R_test
                            
                if best_R is not None:
                    V_out_V_in = best_R / (A * best_R + B + C * best_R**2 + D * best_R)
                    gain_db = 20 * np.log10(np.abs(2 * V_out_V_in))
                    self.print_performance_metrics(freqs, gain_db, best_R=best_R, best_metric=best_metric, check_skirt=check_skirt)
                    self.z_term_r.delete(0, tk.END); self.z_term_r.insert(0, str(best_R))
                    self.term_enabled.set(True)
                else:
                    self.log("--> FAILED: No impedance met the selected constraints.")
                return

            Total = self.build_transfer_matrix(freqs)
            A, B, C, D = Total[:, 0, 0], Total[:, 0, 1], Total[:, 1, 0], Total[:, 1, 1]

            if mode == "bode":
                self.log("Plotting Bode |dB|...")
                if self.term_enabled.get():
                    Z0 = self.get_float(self.z_term_r, "Z Term Real")
                    if Z0 <= 0: raise ValueError("Termination impedance must be > 0.")
                    self.log(f"Applying Source and Load Termination: {Z0} Ohms")
                    V_out_V_in = Z0 / (A * Z0 + B + C * Z0**2 + D * Z0)
                    gain_db = 20 * np.log10(np.abs(2 * V_out_V_in))
                else:
                    self.log("Unterminated Transfer Function (Open Circuit Load)")
                    gain_db = 20 * np.log10(np.abs(1.0 / A))
                
                metrics = self.print_performance_metrics(freqs, gain_db)
                
                max_gain = np.max(gain_db)
                threshold = max_gain - 3.0

                plt.figure("Bode Plot")
                plt.clf()
                plt.plot(freqs / 1e6, gain_db, color='blue')
                
                crossings = np.where(np.diff(np.sign(gain_db - threshold)))[0]
                if len(crossings) >= 2 and metrics is not None:
                    plt.axhline(threshold, color='red', linestyle='--', label='-3dB Threshold')
                    
                    center_freq, f_low, f_high, bfo_usb, bfo_lsb = metrics
                    zoom_mode = self.plot_zoom.get()

                    if zoom_mode in ["full", "usb"]:
                        plt.axvline(bfo_usb / 1e6, color='green', linestyle=':', linewidth=2, label='USB BFO')
                        plt.axvline((bfo_usb + 600) / 1e6, color='orange', linestyle='-', linewidth=1, label='+600Hz')
                        plt.axvline((bfo_usb + 2400) / 1e6, color='red', linestyle='-', linewidth=1, label='+2400Hz')
                    
                    if zoom_mode in ["full", "lsb"]:
                        plt.axvline(bfo_lsb / 1e6, color='purple', linestyle=':', linewidth=2, label='LSB BFO')
                        plt.axvline((bfo_lsb - 600) / 1e6, color='cyan', linestyle='-', linewidth=1, label='-600Hz')
                        plt.axvline((bfo_lsb - 2400) / 1e6, color='blue', linestyle='-', linewidth=1, label='-2400Hz')
                    
                    # Lock the X-axis tightly around the BFO +/- 3000 Hz to ensure the 2400 Hz line is always perfectly in frame
                    if zoom_mode == "usb":
                        plt.xlim((bfo_usb - 500) / 1e6, (bfo_usb + 3000) / 1e6)
                    elif zoom_mode == "lsb":
                        plt.xlim((bfo_lsb - 3000) / 1e6, (bfo_lsb + 500) / 1e6)
                    
                    plt.legend(loc='lower center', fontsize='small')
                    
                plt.title("Crystal Filter Transfer Function")
                plt.xlabel("Frequency (MHz)")
                plt.ylabel("Magnitude (dB)")
                plt.grid(True)
                plt.show()

            #updated 20May26 to allow real/imaginary plot of impedance
            elif mode == "z_unterm":
                if self.term_enabled.get():
                    Z0 = self.get_float(self.z_term_r, "Z Term Real")
                    if Z0 <= 0: raise ValueError("Termination impedance must be > 0.")
                    self.log(f"Calculating Terminated Input Impedance (Load = {Z0} Ohms)")
                    
                    # Full ABCD formula for a terminated network
                    Z_in = (A * Z0 + B) / (C * Z0 + D)
                    title_str = f"Terminated Input Impedance | Z_load = {Z0} \u03A9"
                else:
                    self.log("Calculating Unterminated Input Impedance (Open Load)")
                    
                    # Simplified ABCD formula for an open circuit
                    Z_in = A / C
                    title_str = "Unterminated Input Impedance (Open Load)"

                R_in = np.real(Z_in)
                X_in = np.imag(Z_in)
                
                center_idx = len(freqs) // 2
                self.log(f"Z_in at {freqs[center_idx]/1e6:.6f} MHz = {R_in[center_idx]:.1f} {'+' if X_in[center_idx] >= 0 else '-'} j{abs(X_in[center_idx]):.1f} Ohms")
                
                plt.figure("Impedance Plot")
                plt.clf()
                
                # Plot Real and Imaginary components separately
                plt.plot(freqs / 1e6, R_in, color='red', label='Real (Resistance)')
                plt.plot(freqs / 1e6, X_in, color='blue', label='Imaginary (Reactance)')
                
                plt.axhline(0, color='black', linewidth=1, linestyle='--')
                
                # Only clamp the Y-axis if it is unterminated (to hide the massive spikes)
                # If terminated, let matplotlib auto-scale to show the fine passband details
                if not self.term_enabled.get():
                    plt.ylim(-2000, 2000) 
                
                plt.title(title_str)
                plt.xlabel("Frequency (MHz)")
                plt.ylabel("Impedance (Ohms)")
                plt.legend()
                plt.grid(True)
                plt.show()

        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
            self.log(f"Error: {str(ve)}")
        except Exception as e:
            messagebox.showerror("Calculation Error", str(e))
            self.log(f"Unexpected Error: {str(e)}")

    def save_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not file_path: return
        data = {
            "capacitors": {k: v.get() for k, v in self.caps.items()},
            "crystals": {y: {p: v.get() for p, v in self.crystals[y].items()} for y in self.crystals},
            "settings": {
                "f_start": self.f_start.get(), "f_end": self.f_end.get(),
                "z_term": self.z_term_r.get(), "term_enabled": self.term_enabled.get(),
                "mode": self.calc_mode.get(), "opt_il": self.opt_il.get(),
                "opt_rip": self.opt_rip.get(), "opt_skirt": self.opt_skirt.get(),
                "en_il": self.en_il.get(), "en_rip": self.en_rip.get(),
                "en_skirt": self.en_skirt.get(), "syn_f0": self.syn_f0.get(),
                "syn_bw": self.syn_bw.get(), "bfo_offset": self.bfo_offset.get(),
                "plot_zoom": self.plot_zoom.get()
            }
        }
        try:
            with open(file_path, 'w') as f: json.dump(data, f, indent=4)
            self.log(f"Profile saved to {file_path}")
        except Exception as e: messagebox.showerror("Save Error", str(e))

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path: return
        try:
            with open(file_path, 'r') as f: data = json.load(f)
            for k, v in data.get("capacitors", {}).items():
                if k in self.caps: self.caps[k].delete(0, tk.END); self.caps[k].insert(0, v)
            for y_key, params in data.get("crystals", {}).items():
                if y_key in self.crystals:
                    for p_key, val in params.items():
                        if p_key in self.crystals[y_key]:
                            self.crystals[y_key][p_key].delete(0, tk.END); self.crystals[y_key][p_key].insert(0, val)
            
            settings = data.get("settings", {})
            def load_entry(entry_widget, key, default="0"):
                entry_widget.delete(0, tk.END); entry_widget.insert(0, settings.get(key, default))

            load_entry(self.f_start, "f_start", "0")
            load_entry(self.f_end, "f_end", "0")
            load_entry(self.z_term_r, "z_term", "0")
            load_entry(self.bfo_offset, "bfo_offset", "600")
            load_entry(self.opt_il, "opt_il", "10.0")
            load_entry(self.opt_rip, "opt_rip", "3.0")
            load_entry(self.opt_skirt, "opt_skirt", "40.0")
            load_entry(self.syn_f0, "syn_f0", "4.915")
            load_entry(self.syn_bw, "syn_bw", "2500")
            
            self.term_enabled.set(settings.get("term_enabled", False))
            self.calc_mode.set(settings.get("mode", "bode"))
            self.plot_zoom.set(settings.get("plot_zoom", "full"))
            self.en_il.set(settings.get("en_il", True))
            self.en_rip.set(settings.get("en_rip", True))
            self.en_skirt.set(settings.get("en_skirt", True))
            
            self.log(f"Profile loaded from {file_path}")
        except Exception as e: messagebox.showerror("Load Error", str(e))

    def open_help(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            help_file_path = os.path.join(current_dir, "FilterAnalyzer.txt")
            if os.path.exists(help_file_path):
                os.startfile(help_file_path)
                self.log("Opening Help File in default text editor...")
            else:
                messagebox.showerror("Help Error", f"Could not find help file at:\n{help_file_path}")
                self.log("Error: Help file not found.")
        except Exception as e:
            messagebox.showerror("Help Error", f"Could not open help file: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CrystalAnalyzerApp(root)
    root.mainloop()