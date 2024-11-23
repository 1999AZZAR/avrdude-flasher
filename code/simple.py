import sys
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QComboBox, QPushButton, QTextEdit,
                            QLabel, QFileDialog, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class AvrdudeWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            result = subprocess.run(self.command,
                                  capture_output=True,
                                  text=True,
                                  shell=True)
            if result.returncode == 0:
                self.finished.emit(result.stdout)
            else:
                self.error.emit(result.stderr)
        except Exception as e:
            self.error.emit(str(e))

class AVRFlasherGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AVR Flasher")
        self.setMinimumSize(800, 600)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Chip selection
        chip_group = QGroupBox("Chip Configuration")
        chip_layout = QHBoxLayout()

        self.chip_combo = QComboBox()
        self.chip_combo.addItems([
            "atmega328p",
            "atmega2560",
            "atmega16",
            "atmega32",
            "atmega8",
            "attiny85",
            "attiny13",
            "m8"
        ])

        chip_layout.addWidget(QLabel("Chip:"))
        chip_layout.addWidget(self.chip_combo)
        chip_group.setLayout(chip_layout)
        layout.addWidget(chip_group)

        # Operations group
        operations_group = QGroupBox("Operations")
        operations_layout = QVBoxLayout()

        # Flash operations
        flash_layout = QHBoxLayout()
        self.flash_file_path = QLabel("No file selected")
        select_flash_btn = QPushButton("Select Hex File")
        select_flash_btn.clicked.connect(lambda: self.select_file("hex"))
        write_flash_btn = QPushButton("Write Flash")
        write_flash_btn.clicked.connect(self.write_flash)
        read_flash_btn = QPushButton("Read Flash")
        read_flash_btn.clicked.connect(self.read_flash)
        verify_flash_btn = QPushButton("Verify Flash")
        verify_flash_btn.clicked.connect(self.verify_flash)

        flash_layout.addWidget(select_flash_btn)
        flash_layout.addWidget(self.flash_file_path)
        flash_layout.addWidget(write_flash_btn)
        flash_layout.addWidget(read_flash_btn)
        flash_layout.addWidget(verify_flash_btn)
        operations_layout.addLayout(flash_layout)

        # Fuse operations
        fuse_layout = QHBoxLayout()
        read_fuses_btn = QPushButton("Read All Fuses")
        read_fuses_btn.clicked.connect(self.read_fuses)

        # Fuse write layout
        fuse_write_layout = QHBoxLayout()
        self.lfuse_input = QComboBox()
        self.hfuse_input = QComboBox()
        self.efuse_input = QComboBox()

        # Common fuse values for ATmega328p
        fuse_values = ["0xFF", "0xDE", "0x05", "0xE2", "0xD9"]
        for combo in [self.lfuse_input, self.hfuse_input, self.efuse_input]:
            combo.addItems(fuse_values)
            combo.setEditable(True)

        fuse_write_layout.addWidget(QLabel("L:"))
        fuse_write_layout.addWidget(self.lfuse_input)
        fuse_write_layout.addWidget(QLabel("H:"))
        fuse_write_layout.addWidget(self.hfuse_input)
        fuse_write_layout.addWidget(QLabel("E:"))
        fuse_write_layout.addWidget(self.efuse_input)

        write_fuses_btn = QPushButton("Write Fuses")
        write_fuses_btn.clicked.connect(self.write_fuses)

        fuse_layout.addWidget(read_fuses_btn)
        fuse_layout.addLayout(fuse_write_layout)
        fuse_layout.addWidget(write_fuses_btn)
        operations_layout.addLayout(fuse_layout)

        # EEPROM operations
        eeprom_layout = QHBoxLayout()
        self.eeprom_file_path = QLabel("No file selected")
        select_eeprom_btn = QPushButton("Select EEPROM File")
        select_eeprom_btn.clicked.connect(lambda: self.select_file("eeprom"))
        write_eeprom_btn = QPushButton("Write EEPROM")
        write_eeprom_btn.clicked.connect(self.write_eeprom)
        read_eeprom_btn = QPushButton("Read EEPROM")
        read_eeprom_btn.clicked.connect(self.read_eeprom)

        eeprom_layout.addWidget(select_eeprom_btn)
        eeprom_layout.addWidget(self.eeprom_file_path)
        eeprom_layout.addWidget(write_eeprom_btn)
        eeprom_layout.addWidget(read_eeprom_btn)
        operations_layout.addLayout(eeprom_layout)

        operations_group.setLayout(operations_layout)
        layout.addWidget(operations_group)

        # Output console
        console_group = QGroupBox("Console Output")
        console_layout = QVBoxLayout()
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        console_layout.addWidget(self.console)
        console_group.setLayout(console_layout)
        layout.addWidget(console_group)

        # Extra options
        options_group = QGroupBox("Extra Options")
        options_layout = QHBoxLayout()

        self.slow_clock = QComboBox()
        self.slow_clock.addItems(["Normal Speed", "Slow Clock (Safe Mode)"])
        self.verbose = QComboBox()
        self.verbose.addItems(["Normal Output", "Verbose", "Very Verbose"])

        options_layout.addWidget(QLabel("Clock:"))
        options_layout.addWidget(self.slow_clock)
        options_layout.addWidget(QLabel("Verbosity:"))
        options_layout.addWidget(self.verbose)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

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

    def get_base_command(self):
        cmd = ["avrdude", "-c", "usbasp", "-p", self.chip_combo.currentText()]

        # Add clock option
        if self.slow_clock.currentText() == "Slow Clock (Safe Mode)":
            cmd.extend(["-B", "32"])

        # Add verbosity
        verbose_level = self.verbose.currentIndex()
        if verbose_level == 1:
            cmd.append("-v")
        elif verbose_level == 2:
            cmd.extend(["-v", "-v"])

        return cmd

    def execute_command(self, command):
        self.console.append(f"Executing: {' '.join(command)}\n")
        self.worker = AvrdudeWorker(' '.join(command))
        self.worker.finished.connect(lambda output: self.console.append(f"Success:\n{output}"))
        self.worker.error.connect(lambda error: self.console.append(f"Error:\n{error}"))
        self.worker.start()

    def write_flash(self):
        if self.flash_file_path.text() == "No file selected":
            QMessageBox.warning(self, "Error", "Please select a hex file first!")
            return
        cmd = self.get_base_command()
        cmd.extend(["-U", f"flash:w:{self.flash_file_path.text()}:i"])
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
        cmd = self.get_base_command()
        cmd.extend([
            "-U", f"lfuse:w:{self.lfuse_input.currentText()}:m",
            "-U", f"hfuse:w:{self.hfuse_input.currentText()}:m",
            "-U", f"efuse:w:{self.efuse_input.currentText()}:m"
        ])

        reply = QMessageBox.warning(
            self,
            "Warning",
            "Writing incorrect fuse values can brick your device. Are you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.execute_command(cmd)

    def write_eeprom(self):
        if self.eeprom_file_path.text() == "No file selected":
            QMessageBox.warning(self, "Error", "Please select an EEPROM file first!")
            return
        cmd = self.get_base_command()
        cmd.extend(["-U", f"eeprom:w:{self.eeprom_file_path.text()}:i"])
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

def main():
    app = QApplication(sys.argv)
    window = AVRFlasherGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
