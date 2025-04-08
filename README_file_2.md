# Beam Analysis GUI - FSF25 Civil Engineering Module

## Overview

This application is a **PyQt5-based GUI tool** for analyzing a simply supported beam under two moving point loads using **Influence Line Diagrams (ILD)**. It calculates:

- Reactions at supports
- Shear Force and Bending Moment at midspan
- Maximum Shear Force (SF), Bending Moment (BM), and their locations

Plots of ILDs for reactions, SF, and BM are shown for visualization.

---

## Features

- Transient moving load simulation
- ILD-based visualization for key responses
- Analysis summary with export options
- Report generation compatible with Overleaf
- Silent video demonstration included

---

## How to Run

1. **Install the dependencies** using:
  
   pip install -r requirements.txt

## Run the main program:
python gui_beam_analysis.py

# Files Included:
gui_beam_analysis.py — Main Python script for the GUI application

requirements.txt — List of required Python libraries

demo_video_link.txt — Contains the link to the demo video

README_file.md — This file

reportffIntern — Folder with Overleaf PDF report

result and plot — Folder containing sample result images and plots

# Demo Video:
Watch the working of the software tool here:
[🔗 Demo Video Link](https://app.filmora.io/#/object/cvqahpa7ppt4leuenk40?source=%7B%22product_id%22:%221901%22,%22product_page%22:%22share_url%22,%22product_version%22:%2214.4.3.11809%22%7D)

# GitHub Repository:
You can explore the source code and development history here:
[📂 GitHub Repository](https://github.com/ALOK66373/beam_analysis_gui/tree/main)

# Difficulties Faced:-

⚙️ ILD Plotting Logic
Mapping moving loads onto ILDs and syncing with correct beam response was conceptually and technically challenging.

📊 Shear Force Calculation Accuracy
Special care was needed to handle midspan behavior and ensure realistic SF transitions and peak values.

🧩 GUI + Backend Integration
Merging PyQt5 interface with numerical engine demanded a clear understanding of signal-slot mechanism.

📄 Result Export & Reporting
Structuring outputs for seamless reporting in LaTeX/Overleaf while preserving clarity and consistency was non-trivial.

⏱️ Time & Task Management
Delivering GUI, code, documentation, video, and export features under a deadline involved focused planning and iteration.

# Author

Developed and submitted by ALOK KUMAR
For FOSSEE Summer Fellowship 2025
Civil Engineering Module Task