import sys
import json
import subprocess
from dataclasses import dataclass
from typing import Dict, Any
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QComboBox, QPushButton, QTextEdit,
                             QLabel, QFileDialog, QGroupBox, QMessageBox,
                             QTabWidget, QCheckBox, QSpinBox, QGridLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QFont

@dataclass
class ChipInfo:
    command: str
    name: str
    signature: str
    flash_size: int
    eeprom_size: int
    default_lfuse: str
    default_hfuse: str
    default_efuse: str
    description: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChipInfo':
        """Create a ChipInfo instance from a dictionary."""
        return cls(
            command=data['command'],
            name=data['name'],
            signature=data['signature'],
            flash_size=data['flash_size'],
            eeprom_size=data['eeprom_size'],
            default_lfuse=data['default_lfuse'],
            default_hfuse=data['default_hfuse'],
            default_efuse=data['default_efuse'],
            description=data['description']
        )

def load_chip_database(file_path: str) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Load chip database from a JSON file."""
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading chip database: {e}")
        sys.exit(1)

# Load chip database from 'chips.json'
# CHIP_DATABASE = load_chip_database("chips.json")

class AvrdudeWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True,
                bufsize=1,
                universal_newlines=True
            )

            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.progress.emit(output.strip())

            returncode = process.poll()

            if returncode == 0:
                self.finished.emit("Operation completed successfully!")
            else:
                self.error.emit("Operation failed with error code: " + str(returncode))

        except Exception as e:
            self.error.emit(str(e))

class ChipInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setFont(QFont("Courier"))
        layout.addWidget(self.info_text)

    def update_info(self, chip_info: ChipInfo):
        info_text = f"""
Chip Information:
----------------
Name: {chip_info.name}
Signature: {chip_info.signature}
Flash Size: {chip_info.flash_size} bytes
EEPROM Size: {chip_info.eeprom_size} bytes

Default Fuse Values:
------------------
Low Fuse: {chip_info.default_lfuse}
High Fuse: {chip_info.default_hfuse}
Extended Fuse: {chip_info.default_efuse}

Description:
-----------
{chip_info.description}
"""
        self.info_text.setText(info_text)

class AdvancedOptionsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Programming Options
        prog_group = QGroupBox("Programming Options")
        prog_layout = QGridLayout()

        self.verify_check = QCheckBox("Verify after writing")
        self.verify_check.setChecked(True)
        prog_layout.addWidget(self.verify_check, 0, 0)

        self.erase_check = QCheckBox("Erase before writing")
        self.erase_check.setChecked(True)
        prog_layout.addWidget(self.erase_check, 0, 1)

        self.disable_fuse_check = QCheckBox("Disable fuse verification")
        prog_layout.addWidget(self.disable_fuse_check, 1, 0)

        prog_group.setLayout(prog_layout)
        layout.addWidget(prog_group)

        # Timing Options
        timing_group = QGroupBox("Timing Options")
        timing_layout = QGridLayout()

        timing_layout.addWidget(QLabel("Bit Clock Period (µs):"), 0, 0)
        self.bit_clock = QSpinBox()
        self.bit_clock.setRange(0, 250)
        self.bit_clock.setValue(1)
        timing_layout.addWidget(self.bit_clock, 0, 1)

        timing_layout.addWidget(QLabel("Connect Retry Count:"), 1, 0)
        self.retry_count = QSpinBox()
        self.retry_count.setRange(0, 10)
        self.retry_count.setValue(3)
        timing_layout.addWidget(self.retry_count, 1, 1)

        timing_group.setLayout(timing_layout)
        layout.addWidget(timing_group)

        # Add stretcher
        layout.addStretch()

class AVRFlasherGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced AVR Flasher")
        self.setMinimumSize(1000, 800)

        # Load chip database
        self.chip_database = load_chip_database("chips.json")

        # Store current chip info
        self.current_chip_info = None

        # Load settings
        self.settings = QSettings("AVRFlasher", "Settings")

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create tab widget
        tab_widget = QTabWidget()

        # Main operations tab
        operations_tab = QWidget()
        operations_layout = QVBoxLayout(operations_tab)

        # Chip selection
        chip_group = QGroupBox("Chip Selection")
        chip_layout = QGridLayout()

        self.chip_family = QComboBox()
        self.chip_family.addItems(self.chip_database.keys())
        self.chip_family.currentTextChanged.connect(self.update_chip_list)

        self.chip_combo = QComboBox()
        self.update_chip_list(self.chip_family.currentText())
        self.chip_combo.currentTextChanged.connect(self.update_chip_info)

        chip_layout.addWidget(QLabel("Series:"), 0, 0)
        chip_layout.addWidget(self.chip_family, 0, 1)
        chip_layout.addWidget(QLabel("Model:"), 0, 2)
        chip_layout.addWidget(self.chip_combo, 0, 3)

        chip_group.setLayout(chip_layout)
        operations_layout.addWidget(chip_group)

        # Flash operations
        flash_group = QGroupBox("Flash Operations")
        flash_layout = QGridLayout()

        self.flash_file_path = QLabel("No file selected")
        select_flash_btn = QPushButton("Select Hex File")
        select_flash_btn.clicked.connect(lambda: self.select_file("hex"))
        write_flash_btn = QPushButton("Write Flash")
        write_flash_btn.clicked.connect(self.write_flash)
        read_flash_btn = QPushButton("Read Flash")
        read_flash_btn.clicked.connect(self.read_flash)
        verify_flash_btn = QPushButton("Verify Flash")
        verify_flash_btn.clicked.connect(self.verify_flash)

        flash_layout.addWidget(select_flash_btn, 0, 0)
        flash_layout.addWidget(self.flash_file_path, 0, 1, 1, 2)
        flash_layout.addWidget(write_flash_btn, 1, 0)
        flash_layout.addWidget(read_flash_btn, 1, 1)
        flash_layout.addWidget(verify_flash_btn, 1, 2)

        flash_group.setLayout(flash_layout)
        operations_layout.addWidget(flash_group)

        # Fuse operations
        fuse_group = QGroupBox("Fuse Operations")
        fuse_layout = QGridLayout()

        read_fuses_btn = QPushButton("Read All Fuses")
        read_fuses_btn.clicked.connect(self.read_fuses)

        self.lfuse_input = QComboBox()
        self.hfuse_input = QComboBox()
        self.efuse_input = QComboBox()

        for combo in [self.lfuse_input, self.hfuse_input, self.efuse_input]:
            combo.setEditable(True)

        fuse_layout.addWidget(QLabel("Low Fuse:"), 0, 0)
        fuse_layout.addWidget(self.lfuse_input, 0, 1)
        fuse_layout.addWidget(QLabel("High Fuse:"), 0, 2)
        fuse_layout.addWidget(self.hfuse_input, 0, 3)
        fuse_layout.addWidget(QLabel("Extended Fuse:"), 0, 4)
        fuse_layout.addWidget(self.efuse_input, 0, 5)

        write_fuses_btn = QPushButton("Write Fuses")
        write_fuses_btn.clicked.connect(self.write_fuses)
        reset_fuses_btn = QPushButton("Reset to Defaults")
        reset_fuses_btn.clicked.connect(self.reset_fuses)

        fuse_layout.addWidget(read_fuses_btn, 1, 0, 1, 2)
        fuse_layout.addWidget(write_fuses_btn, 1, 2, 1, 2)
        fuse_layout.addWidget(reset_fuses_btn, 1, 4, 1, 2)

        fuse_group.setLayout(fuse_layout)
        operations_layout.addWidget(fuse_group)

        # EEPROM operations
        eeprom_group = QGroupBox("EEPROM Operations")
        eeprom_layout = QGridLayout()

        self.eeprom_file_path = QLabel("No file selected")
        select_eeprom_btn = QPushButton("Select EEPROM File")
        select_eeprom_btn.clicked.connect(lambda: self.select_file("eeprom"))
        write_eeprom_btn = QPushButton("Write EEPROM")
        write_eeprom_btn.clicked.connect(self.write_eeprom)
        read_eeprom_btn = QPushButton("Read EEPROM")
        read_eeprom_btn.clicked.connect(self.read_eeprom)
        verify_eeprom_btn = QPushButton("Verify EEPROM")
        verify_eeprom_btn.clicked.connect(self.verify_eeprom)

        eeprom_layout.addWidget(select_eeprom_btn, 0, 0)
        eeprom_layout.addWidget(self.eeprom_file_path, 0, 1, 1, 2)
        eeprom_layout.addWidget(write_eeprom_btn, 1, 0)
        eeprom_layout.addWidget(read_eeprom_btn, 1, 1)
        eeprom_layout.addWidget(verify_eeprom_btn, 1, 2)

        eeprom_group.setLayout(eeprom_layout)
        operations_layout.addWidget(eeprom_group)

        # Add operations tab to tab widget
        tab_widget.addTab(operations_tab, "Operations")

        # Chip info tab
        self.chip_info_widget = ChipInfoWidget()
        tab_widget.addTab(self.chip_info_widget, "Chip Info")

        # Advanced options tab
        self.advanced_options = AdvancedOptionsWidget()
        tab_widget.addTab(self.advanced_options, "Advanced Options")

        layout.addWidget(tab_widget)

        # Console output
        console_group = QGroupBox("Console Output")
        console_layout = QVBoxLayout()
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Courier"))
        clear_console_btn = QPushButton("Clear Console")
        clear_console_btn.clicked.connect(self.console.clear)

        console_layout.addWidget(self.console)
        console_layout.addWidget(clear_console_btn)
        console_group.setLayout(console_layout)
        layout.addWidget(console_group)

        # Initialize chip info
        self.update_chip_info(self.chip_combo.currentText())

        # Restore settings
        self.restore_settings()

    def closeEvent(self, event):
        # Save settings before closing
        self.save_settings()
        super().closeEvent(event)

    def save_settings(self):
        self.settings.setValue("chip_family", self.chip_family.currentText())
        self.settings.setValue("chip", self.chip_combo.currentText())
        self.settings.setValue("verify", self.advanced_options.verify_check.isChecked())
        self.settings.setValue("erase", self.advanced_options.erase_check.isChecked())
        self.settings.setValue("bit_clock", self.advanced_options.bit_clock.value())
        self.settings.setValue("retry_count", self.advanced_options.retry_count.value())

    def restore_settings(self):
        family = self.settings.value("chip_family", self.chip_family.currentText())
        chip = self.settings.value("chip", self.chip_combo.currentText())

        # Restore chip selection
        index = self.chip_family.findText(family)
        if index >= 0:
            self.chip_family.setCurrentIndex(index)
            self.update_chip_list(family)
            index = self.chip_combo.findText(chip)
            if index >= 0:
                self.chip_combo.setCurrentIndex(index)

        # Restore advanced options
        self.advanced_options.verify_check.setChecked(
            self.settings.value("verify", True, type=bool))
        self.advanced_options.erase_check.setChecked(
            self.settings.value("erase", True, type=bool))
        self.advanced_options.bit_clock.setValue(
            self.settings.value("bit_clock", 1, type=int))
        self.advanced_options.retry_count.setValue(
            self.settings.value("retry_count", 3, type=int))

    def update_chip_list(self, series):
        """Update the chip list combo box based on selected series."""
        self.chip_combo.clear()
        if series in self.chip_database:
            self.chip_combo.addItems(self.chip_database[series].keys())

    def update_chip_info(self, model):
        """Update chip information based on selected model."""
        series = self.chip_family.currentText()
        if series in self.chip_database and model in self.chip_database[series]:
            chip_data = self.chip_database[series][model]
            self.current_chip_info = ChipInfo.from_dict(chip_data)
            self.chip_info_widget.update_info(self.current_chip_info)

            # Update fuse defaults
            self.lfuse_input.setCurrentText(self.current_chip_info.default_lfuse)
            self.hfuse_input.setCurrentText(self.current_chip_info.default_hfuse)
            self.efuse_input.setCurrentText(self.current_chip_info.default_efuse)

    def reset_fuses(self):
        """Reset fuses to default values for current chip."""
        if self.current_chip_info:
            self.lfuse_input.setCurrentText(self.current_chip_info.default_lfuse)
            self.hfuse_input.setCurrentText(self.current_chip_info.default_hfuse)
            self.efuse_input.setCurrentText(self.current_chip_info.default_efuse)

    def get_base_command(self):
        """Get base avrdude command with current chip model."""
        cmd = ["avrdude", "-c", "usbasp", "-p", self.current_chip_info.command]

        # Add advanced options
        if self.advanced_options.bit_clock.value() != 1:
            cmd.extend(["-B", str(self.advanced_options.bit_clock.value())])

        if self.advanced_options.retry_count.value() != 3:
            cmd.extend(["-r", str(self.advanced_options.retry_count.value())])

        if self.advanced_options.disable_fuse_check.isChecked():
            cmd.append("-u")

        return cmd

    def execute_command(self, command):
        self.console.append(f"Executing: {' '.join(command)}\n")
        self.worker = AvrdudeWorker(' '.join(command))
        self.worker.progress.connect(lambda msg: self.console.append(msg))
        self.worker.finished.connect(lambda msg: self.console.append(f"\n{msg}\n"))
        self.worker.error.connect(lambda msg: self.console.append(f"\nError: {msg}\n"))
        self.worker.start()

    def select_file(self, file_type):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {file_type.upper()} File",
            "",
            "Hex Files (*.hex);;All Files (*.*)"
        )
        if file_path:
            if file_type == "hex":
                self.flash_file_path.setText(file_path)
            else:
                self.eeprom_file_path.setText(file_path)

    def write_flash(self):
        if self.flash_file_path.text() == "No file selected":
            QMessageBox.warning(self, "Error", "Please select a hex file first!")
            return

        cmd = self.get_base_command()
        options = []

        if self.advanced_options.erase_check.isChecked():
            cmd.append("-e")

        if self.advanced_options.verify_check.isChecked():
            options.append("v")

        options.append("w")
        cmd.extend(["-U", f"flash:{''.join(options)}:{self.flash_file_path.text()}:i"])
        self.execute_command(cmd)

    def read_flash(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Flash Dump",
            "",
            "Hex Files (*.hex);;All Files (*.*)"
        )
        if file_path:
            cmd = self.get_base_command()
            cmd.extend(["-U", f"flash:r:{file_path}:i"])
            self.execute_command(cmd)

    def verify_flash(self):
        if self.flash_file_path.text() == "No file selected":
            QMessageBox.warning(self, "Error", "Please select a hex file first!")
            return

        cmd = self.get_base_command()
        cmd.extend(["-U", f"flash:v:{self.flash_file_path.text()}:i"])
        self.execute_command(cmd)

    def read_fuses(self):
        cmd = self.get_base_command()
        cmd.extend([
            "-U", "lfuse:r:-:h",
            "-U", "hfuse:r:-:h",
            "-U", "efuse:r:-:h"
        ])
        self.execute_command(cmd)

    def write_fuses(self):
        reply = QMessageBox.warning(
            self,
            "Warning",
            "Writing incorrect fuse values can brick your device. Are you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            cmd = self.get_base_command()
            cmd.extend([
                "-U", f"lfuse:w:{self.lfuse_input.currentText()}:m",
                "-U", f"hfuse:w:{self.hfuse_input.currentText()}:m",
                "-U", f"efuse:w:{self.efuse_input.currentText()}:m"
            ])
            self.execute_command(cmd)

    def write_eeprom(self):
        if self.eeprom_file_path.text() == "No file selected":
            QMessageBox.warning(self, "Error", "Please select an EEPROM file first!")
            return

        cmd = self.get_base_command()
        options = []

        if self.advanced_options.verify_check.isChecked():
            options.append("v")

        options.append("w")
        cmd.extend(["-U", f"eeprom:{''.join(options)}:{self.eeprom_file_path.text()}:i"])
        self.execute_command(cmd)

    def read_eeprom(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save EEPROM Dump",
            "",
            "Hex Files (*.hex);;All Files (*.*)"
        )
        if file_path:
            cmd = self.get_base_command()
            cmd.extend(["-U", f"eeprom:r:{file_path}:i"])
            self.execute_command(cmd)

    def verify_eeprom(self):
        if self.eeprom_file_path.text() == "No file selected":
            QMessageBox.warning(self, "Error", "Please select an EEPROM file first!")
            return

        cmd = self.get_base_command()
        cmd.extend(["-U", f"eeprom:v:{self.eeprom_file_path.text()}:i"])
        self.execute_command(cmd)

def main():
    app = QApplication(sys.argv)
    window = AVRFlasherGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

