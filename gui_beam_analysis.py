import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QMessageBox, QGridLayout, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# --- Helper Function for Reaction Calculation ---
def calculate_reactions(L, W1, W2, x1, x2):
    RA = W1 * (1 - x1 / L) + W2 * (1 - x2 / L)
    RB = W1 * (x1 / L) + W2 * (x2 / L)
    return RA, RB

# --- Analysis Function ---
def analyze_beam(L, W1, W2, d):
    if d > L:
        return {'Max Reaction at A (kN)': np.nan, 'Max Reaction at B (kN)': np.nan,
                'BM at A (kNm)': np.nan, 'SF at Midspan (kN)': np.nan,
                'Max SF (kN)': np.nan, 'Location of Max SF (m)': np.nan,
                'Max BM (kNm)': np.nan, 'Location of Max BM (m)': np.nan}

    step = 0.1
    positions = [round(i * step, 2) for i in range(int(L / step) + 1)]

    max_RA = max_RB = BM_01 = 0
    SF_01_values = []
    max_SF = float('-inf')
    max_BM = float('-inf')
    loc_SF = loc_BM = 0

    for x1 in positions:
        x2 = x1 + d
        if x2 > L:
            continue

        RA, RB = calculate_reactions(L, W1, W2, x1, x2)

        max_RA = max(max_RA, RA)
        max_RB = max(max_RB, RB)

        if x1 == 0:
            BM_01 = W2 * x2 * (L - x2) / L

            for z in positions:
             SF = 0
            for W, x in [(W1, x1), (W2, x2)]:
                if x < z:
                    SF += W * (1 - x / L)
                elif x == z:
                    SF += W * (1 - x / L) * 0.5
                else:
                    SF -= W * (x / L)

            if max_SF is None or abs(SF) > abs(max_SF):
                max_SF = SF
                loc_SF = z

            if abs(z - L/2) < 0.05:
                SF_01_values.append(SF)


        for z in positions:
            M = 0
            for W, x in [(W1, x1), (W2, x2)]:
                if x <= z:
                    M += W * x * (L - z) / L
                else:
                    M += W * z * (L - x) / L
            if M > max_BM:
                max_BM = M
                loc_BM = z

    SF_01 = np.mean(SF_01_values) if SF_01_values else 0

    return {
        'Max Reaction at A (kN)': round(max_RA, 3),
        'Max Reaction at B (kN)': round(max_RB, 3),
        'BM at A (kNm)': round(BM_01, 3),
        'SF at Midspan (kN)': round(SF_01, 3),
        'Max SF (kN)': round(max_SF, 3),
        'Location of Max SF (m)': round(loc_SF, 3),
        'Max BM (kNm)': round(max_BM, 3),
        'Location of Max BM (m)': round(loc_BM, 3)
    }

# --- Save Plot as Image ---
def save_plot_as_image(fig, filename='ild_plot.png'):
    fig.savefig(filename)
    return filename

# --- Plot ILDs with Moving Loads + Save Option ---
def plot_ild_with_loads(L, W1_pos, W2_pos, d, animate=False):
    x = np.linspace(0, L, 500)
    RA = 1 - x / L
    RB = x / L
    mid = L / 2
    BM = np.where(x <= mid, x * (L - mid) / L, mid * (L - x) / L)
    SF = np.where(x < mid, 0.5, -0.5)

    fig, axs = plt.subplots(4, 1, figsize=(9, 12), sharex=True)

    axs[0].plot(x, RA, label='RA ILD', color='blue')
    axs[1].plot(x, RB, label='RB ILD', color='green')
    axs[2].plot(x, BM, label='BM ILD (mid)', color='magenta')
    axs[3].step(x, SF, where='mid', label='SF ILD (mid)', color='red')

    for ax, title in zip(axs, ["Reaction at A", "Reaction at B", "Bending Moment at Midspan", "Shear Force at Midspan"]):
        ax.axvline(W1_pos, color='black', linestyle='--', label='W1')
        ax.axvline(W2_pos, color='orange', linestyle='--', label='W2')
        ax.set_title(f"Influence Line Diagram for {title}", fontsize=12, fontweight='bold')
        ax.set_ylabel('ILD')
        ax.grid(True)
        ax.legend()

    axs[3].set_xlabel('Beam Length (m)')
    plt.tight_layout()
    plt.draw()
    plt.show()

    save_plot_as_image(fig)

# --- GUI Class ---
class BeamAnalysisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beam Analysis GUI")

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f4c2c2"))  # olive pink
        self.setPalette(palette)

        layout = QVBoxLayout()
        grid = QGridLayout()
        self.inputs = {}
        labels = ['L (m)', 'W1 (kN)', 'W2 (kN)', 'd (m)', 'W1 Position', 'W2 Position']
        for i, label in enumerate(labels):
            grid.addWidget(QLabel(label), i, 0)
            self.inputs[label] = QLineEdit()
            self.inputs[label].setStyleSheet("background-color: lightyellow; min-width: 180px")
            grid.addWidget(self.inputs[label], i, 1)
        layout.addLayout(grid)

        btn_layout = QHBoxLayout()
        self.analyze_btn = QPushButton("Analyze Beam")
        self.analyze_btn.setStyleSheet("background-color: purple; color: white")
        self.plot_btn = QPushButton("Plot ILDs")
        self.plot_btn.setStyleSheet("background-color: green; color: white")
        btn_layout.addWidget(self.analyze_btn)
        btn_layout.addWidget(self.plot_btn)
        layout.addLayout(btn_layout)

        self.export_btn = QPushButton("Export to PDF")
        layout.addWidget(self.export_btn)
        self.export_btn.clicked.connect(self.export_pdf)

        self.output = QTextEdit()
        self.output.setStyleSheet("background-color: lightyellow")
        layout.addWidget(self.output)

        self.setLayout(layout)
        self.analyze_btn.clicked.connect(self.analyze_beam_gui)
        self.plot_btn.clicked.connect(self.plot_ild_gui)

    def analyze_beam_gui(self):
        try:
            L = float(self.inputs['L (m)'].text())
            W1 = float(self.inputs['W1 (kN)'].text())
            W2 = float(self.inputs['W2 (kN)'].text())
            d = float(self.inputs['d (m)'].text())
            W1_pos = float(self.inputs['W1 Position'].text())
            W2_pos = float(self.inputs['W2 Position'].text())

            if abs(W2_pos - W1_pos) != d:
                QMessageBox.warning(self, "Input Error", f"The value of d (distance between loads) should be equal to |W2 Position - W1 Position| = {abs(W2_pos - W1_pos)}.")
                return

            results = analyze_beam(L, W1, W2, d)
            self.output.append("--- Beam Analysis Results ---")
            for k, v in results.items():
                self.output.append(f"{k}: {v}")
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numerical values.")

    def plot_ild_gui(self):
        try:
            L = float(self.inputs['L (m)'].text())
            W1_pos = float(self.inputs['W1 Position'].text())
            W2_pos = float(self.inputs['W2 Position'].text())
            d = float(self.inputs['d (m)'].text())
            plot_ild_with_loads(L, W1_pos, W2_pos, d)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numerical values for plotting.")

    def export_pdf(self):
        text = self.output.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Export Error", "No results to export. Please analyze the beam first.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if not path:
            return

        try:
            c = canvas.Canvas(path, pagesize=letter)
            width, height = letter
            c.setFont("Helvetica", 10)
            y = height - 50

            for line in text.split('\n'):
                c.drawString(50, y, line)
                y -= 15
                if y < 50:
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y = height - 50

            image_path = 'ild_plot.png'
            if os.path.exists(image_path):
                c.showPage()
                c.drawImage(image_path, 50, 300, width=500, preserveAspectRatio=True)

            c.save()
            QMessageBox.information(self, "Export Successful", f"Results and ILD exported to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

# --- Main Entry Point ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BeamAnalysisApp()
    window.show()
    sys.exit(app.exec_())