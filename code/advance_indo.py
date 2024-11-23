import sys
import json
import subprocess
from dataclasses import dataclass
from typing import Dict, List
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QComboBox, QPushButton, QTextEdit,
                            QLabel, QFileDialog, QGroupBox, QMessageBox,
                            QTabWidget, QCheckBox, QSpinBox, QGridLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QFont

@dataclass
class ChipInfo:
    name: str
    signature: str
    flash_size: int
    eeprom_size: int
    default_lfuse: str
    default_hfuse: str
    default_efuse: str
    description: str

# database chips
CHIP_DATABASE = {
    "ATmega Series": {
        # ATmega8 variants
        "atmega8": ChipInfo("ATmega8", "0x1E9307", 8192, 512, "0xE4", "0xD9", "0xFF", "8KB Flash, 512B EEPROM, 1KB SRAM"),
        "m8": ChipInfo("ATmega8", "0x1E9307", 8192, 512, "0xE4", "0xD9", "0xFF", "8KB Flash, 512B EEPROM, 1KB SRAM"),
        "m8a": ChipInfo("ATmega8A", "0x1E9307", 8192, 512, "0xE4", "0xD9", "0xFF", "8KB Flash, 512B EEPROM, 1KB SRAM"),
        "m808": ChipInfo("ATmega808", "0x1E9359", 8192, 256, "0xFF", "0xDE", "0x05", "8KB Flash, 256B EEPROM, 1KB SRAM"),
        "m809": ChipInfo("ATmega809", "0x1E935A", 8192, 256, "0xFF", "0xDE", "0x05", "8KB Flash, 256B EEPROM, 1KB SRAM"),
        "m8515": ChipInfo("ATmega8515", "0x1E9306", 8192, 512, "0xE4", "0xD9", "0xFF", "8KB Flash, 512B EEPROM, 512B SRAM"),
        "m8535": ChipInfo("ATmega8535", "0x1E9308", 8192, 512, "0xE4", "0xD9", "0xFF", "8KB Flash, 512B EEPROM, 512B SRAM"),

        # ATmega16 variants
        "m16": ChipInfo("ATmega16", "0x1E9403", 16384, 512, "0xE4", "0xD9", "0xFF", "16KB Flash, 512B EEPROM, 1KB SRAM"),
        "m16a": ChipInfo("ATmega16A", "0x1E9403", 16384, 512, "0xE4", "0xD9", "0xFF", "16KB Flash, 512B EEPROM, 1KB SRAM"),
        "m16u2": ChipInfo("ATmega16U2", "0x1E9489", 16384, 512, "0xFF", "0xDE", "0x05", "16KB Flash, 512B EEPROM, 512B SRAM (USB)"),
        "m16u4": ChipInfo("ATmega16U4", "0x1E9488", 16384, 512, "0xFF", "0xDE", "0x05", "16KB Flash, 512B EEPROM, 1.25KB SRAM (USB)"),

        # ATmega32 variants
        "m32": ChipInfo("ATmega32", "0x1E9502", 32768, 1024, "0xE4", "0xD9", "0xFF", "32KB Flash, 1KB EEPROM, 2KB SRAM"),
        "m32a": ChipInfo("ATmega32A", "0x1E9502", 32768, 1024, "0xE4", "0xD9", "0xFF", "32KB Flash, 1KB EEPROM, 2KB SRAM"),
        "m328": ChipInfo("ATmega328", "0x1E9514", 32768, 1024, "0xFF", "0xDE", "0x05", "32KB Flash, 1KB EEPROM, 2KB SRAM"),
        "m328p": ChipInfo("ATmega328P", "0x1E950F", 32768, 1024, "0xFF", "0xDE", "0x05", "32KB Flash, 1KB EEPROM, 2KB SRAM"),
        "m328pb": ChipInfo("ATmega328PB", "0x1E9516", 32768, 1024, "0xFF", "0xDE", "0x05", "32KB Flash, 1KB EEPROM, 2KB SRAM"),

        # ATmega64 variants
        "m64": ChipInfo("ATmega64", "0x1E9602", 65536, 2048, "0xE4", "0xD9", "0xFF", "64KB Flash, 2KB EEPROM, 4KB SRAM"),
        "m64a": ChipInfo("ATmega64A", "0x1E9602", 65536, 2048, "0xE4", "0xD9", "0xFF", "64KB Flash, 2KB EEPROM, 4KB SRAM"),
        "m640": ChipInfo("ATmega640", "0x1E9608", 65536, 4096, "0xFF", "0xDE", "0x05", "64KB Flash, 4KB EEPROM, 8KB SRAM"),

        # ATmega128 variants
        "m128": ChipInfo("ATmega128", "0x1E9702", 131072, 4096, "0xE4", "0xD9", "0xFF", "128KB Flash, 4KB EEPROM, 4KB SRAM"),
        "m1280": ChipInfo("ATmega1280", "0x1E9703", 131072, 4096, "0xFF", "0xDE", "0x05", "128KB Flash, 4KB EEPROM, 8KB SRAM"),
        "m1281": ChipInfo("ATmega1281", "0x1E9704", 131072, 4096, "0xFF", "0xDE", "0x05", "128KB Flash, 4KB EEPROM, 8KB SRAM"),
        "m1284p": ChipInfo("ATmega1284P", "0x1E9705", 131072, 4096, "0xFF", "0xDE", "0x05", "128KB Flash, 4KB EEPROM, 16KB SRAM"),

        # ATmega256 variants
        "m2560": ChipInfo("ATmega2560", "0x1E9801", 262144, 4096, "0xE4", "0xD9", "0xFF", "256KB Flash, 4KB EEPROM, 8KB SRAM"),
        "m2561": ChipInfo("ATmega2561", "0x1E9802", 262144, 4096, "0xFF", "0xDE", "0x05", "256KB Flash, 4KB EEPROM, 8KB SRAM"),

        # additional part
        "m103": ChipInfo("ATmega103", "0x1E9400", 1024 * 8, 1024, "0xE4", "0xD9", "0xFF", "8KB Flash, 1KB EEPROM, 512B SRAM"),
        "m1284": ChipInfo("ATmega1284", "0x1E9705", 131072, 4096, "0xFF", "0xDE", "0x05", "128KB Flash, 4KB EEPROM, 16KB SRAM"),
        "m1284rfr2": ChipInfo("ATmega1284RFR2", "0x1E9707", 131072, 4096, "0xFF", "0xDE", "0x05", "128KB Flash, 4KB EEPROM, 16KB SRAM (RFR2)"),
        "m128a": ChipInfo("ATmega128A", "0x1E9708", 131072, 4096, "0xE4", "0xD9", "0xFF", "128KB Flash, 4KB EEPROM, 4KB SRAM"),
    },

    "ATtiny Series": {
        # ATtiny13 variants
        "t13": ChipInfo("ATtiny13", "0x1E9007", 1024, 64, "0x6A", "0xFF", "0xFF", "1KB Flash, 64B EEPROM, 64B SRAM"),
        "t13a": ChipInfo("ATtiny13A", "0x1E9007", 1024, 64, "0x6A", "0xFF", "0xFF", "1KB Flash, 64B EEPROM, 64B SRAM"),

        # ATtiny24/44/84 variants
        "t24": ChipInfo("ATtiny24", "0x1E910B", 2048, 128, "0x62", "0xDF", "0xFF", "2KB Flash, 128B EEPROM, 128B SRAM"),
        "t44": ChipInfo("ATtiny44", "0x1E9207", 4096, 256, "0x62", "0xDF", "0xFF", "4KB Flash, 256B EEPROM, 256B SRAM"),
        "t84": ChipInfo("ATtiny84", "0x1E930C", 8192, 512, "0x62", "0xDF", "0xFF", "8KB Flash, 512B EEPROM, 512B SRAM"),

        # ATtiny25/45/85 variants
        "t25": ChipInfo("ATtiny25", "0x1E9108", 2048, 128, "0x62", "0xDF", "0xFF", "2KB Flash, 128B EEPROM, 128B SRAM"),
        "t45": ChipInfo("ATtiny45", "0x1E9206", 4096, 256, "0x62", "0xDF", "0xFF", "4KB Flash, 256B EEPROM, 256B SRAM"),
        "t85": ChipInfo("ATtiny85", "0x1E930B", 8192, 512, "0x62", "0xDF", "0xFF", "8KB Flash, 512B EEPROM, 512B SRAM"),

        # ATtiny2313 variants
        "t2313": ChipInfo("ATtiny2313", "0x1E910A", 2048, 128, "0x6A", "0xFF", "0xFF", "2KB Flash, 128B EEPROM, 128B SRAM"),
        "t2313a": ChipInfo("ATtiny2313A", "0x1E910A", 2048, 128, "0x6A", "0xFF", "0xFF", "2KB Flash, 128B EEPROM, 128B SRAM"),

        # Modern ATtiny variants
        "t1604": ChipInfo("ATtiny1604", "0x1E9425", 16384, 256, "0xFF", "0xDE", "0x05", "16KB Flash, 256B EEPROM, 1KB SRAM"),
        "t1614": ChipInfo("ATtiny1614", "0x1E9422", 16384, 256, "0xFF", "0xDE", "0x05", "16KB Flash, 256B EEPROM, 2KB SRAM"),
        "t817": ChipInfo("ATtiny817", "0x1E9322", 8192, 128, "0xFF", "0xDE", "0x05", "8KB Flash, 128B EEPROM, 512B SRAM"),

        # additional part
        "t10": ChipInfo("ATtiny10", "0x1E9005", 1024, 64, "0x6A", "0xFF", "0xFF", "1KB Flash, 64B EEPROM, 64B SRAM"),
        "t1606": ChipInfo("ATtiny1606", "0x1E9426", 16384, 256, "0xFF", "0xDE", "0x05", "16KB Flash, 256B EEPROM, 2KB SRAM"),
        "t1607": ChipInfo("ATtiny1607", "0x1E9427", 16384, 256, "0xFF", "0xDE", "0x05", "16KB Flash, 256B EEPROM, 2KB SRAM"),
        "t204": ChipInfo("ATtiny204", "0x1E9428", 4096, 256, "0xFF", "0xDE", "0x05", "4KB Flash, 256B EEPROM, 256B SRAM"),
        "t414": ChipInfo("ATtiny414", "0x1E9429", 4096, 256, "0xFF", "0xDE", "0x05", "4KB Flash, 256B EEPROM, 256B SRAM"),
    },

    "ATxmega Series": {
        # ATxmega A series
        "x16a4": ChipInfo("ATxmega16A4", "0x1E9441", 16384, 1024, "0xFF", "0xFF", "0x05", "16KB Flash, 1KB EEPROM, 2KB SRAM"),
        "x32a4": ChipInfo("ATxmega32A4", "0x1E9541", 32768, 1024, "0xFF", "0xFF", "0x05", "32KB Flash, 1KB EEPROM, 4KB SRAM"),
        "x64a4": ChipInfo("ATxmega64A4", "0x1E9646", 65536, 2048, "0xFF", "0xFF", "0x05", "64KB Flash, 2KB EEPROM, 4KB SRAM"),
        "x128a4": ChipInfo("ATxmega128A4", "0x1E9746", 131072, 2048, "0xFF", "0xFF", "0x05", "128KB Flash, 2KB EEPROM, 8KB SRAM"),

        # ATxmega USB series
        "x16a4u": ChipInfo("ATxmega16A4U", "0x1E9442", 16384, 1024, "0xFF", "0xFF", "0x05", "16KB Flash, 1KB EEPROM, 2KB SRAM (USB)"),
        "x32a4u": ChipInfo("ATxmega32A4U", "0x1E9542", 32768, 1024, "0xFF", "0xFF", "0x05", "32KB Flash, 1KB EEPROM, 4KB SRAM (USB)"),
        "x64a4u": ChipInfo("ATxmega64A4U", "0x1E9647", 65536, 2048, "0xFF", "0xFF", "0x05", "64KB Flash, 2KB EEPROM, 4KB SRAM (USB)"),
        "x128a4u": ChipInfo("ATxmega128A4U", "0x1E9747", 131072, 2048, "0xFF", "0xFF", "0x05", "128KB Flash, 2KB EEPROM, 8KB SRAM (USB)"),
    },

    "AT90 Series": {
        # Classic AT90S chips
        "90s2313": ChipInfo("AT90S2313", "0x1E9101", 2048, 128, "0xE4", "0xD9", "0xFF", "2KB Flash, 128B EEPROM, 128B SRAM"),
        "90s2333": ChipInfo("AT90S2333", "0x1E9102", 2048, 128, "0xE4", "0xD9", "0xFF", "2KB Flash, 128B EEPROM, 128B SRAM"),
        "90s4414": ChipInfo("AT90S4414", "0x1E9201", 4096, 256, "0xE4", "0xD9", "0xFF", "4KB Flash, 256B EEPROM, 256B SRAM"),
        "90s8515": ChipInfo("AT90S8515", "0x1E9301", 8192, 512, "0xE4", "0xD9", "0xFF", "8KB Flash, 512B EEPROM, 512B SRAM"),

        # AT90USB series
        "usb162": ChipInfo("AT90USB162", "0x1E9482", 16384, 512, "0xFF", "0xDE", "0x05", "16KB Flash, 512B EEPROM, 512B SRAM (USB)"),
        "usb82": ChipInfo("AT90USB82", "0x1E9382", 8192, 512, "0xFF", "0xDE", "0x05", "8KB Flash, 512B EEPROM, 512B SRAM (USB)"),
        "usb1286": ChipInfo("AT90USB1286", "0x1E9782", 131072, 4096, "0xFF", "0xDE", "0x05", "128KB Flash, 4KB EEPROM, 8KB SRAM (USB)"),

        # AT90CAN series
        "c32": ChipInfo("AT90CAN32", "0x1E9581", 32768, 1024, "0xFF", "0xDE", "0x05", "32KB Flash, 1KB EEPROM, 2KB SRAM (CAN Bus)"),
        "c64": ChipInfo("AT90CAN64", "0x1E9681", 65536, 2048, "0xFF", "0xDE", "0x05", "64KB Flash, 2KB EEPROM, 4KB SRAM (CAN Bus)"),

        "c128": ChipInfo("AT90CAN128", "0x1E9709", 131072, 4096, "0xFF", "0xDE", "0x05", "128KB Flash, 4KB EEPROM, 8KB SRAM (CAN Bus)"),
        "pwm2": ChipInfo("AT90PWM2", "0x1E9309", 8192, 512, "0xFF", "0xDE", "0x05", "8KB Flash, 512B EEPROM, 512B SRAM"),
        "pwm216": ChipInfo("AT90PWM216", "0x1E930A", 8192, 512, "0xFF", "0xDE", "0x05", "8KB Flash, 512B EEPROM, 512B SRAM"),
        "pwm2b": ChipInfo("AT90PWM2B", "0x1E930B", 8192, 512, "0xFF", "0xDE", "0x05", "8KB Flash, 512B EEPROM, 512B SRAM"),
        "pwm3": ChipInfo("AT90PWM3", "0x1E930C", 8192, 512, "0xFF", "0xDE", "0x05", "8KB Flash, 512B EEPROM, 512B SRAM"),
        "pwm316": ChipInfo("AT90PWM316", "0x1E930D", 8192, 512, "0xFF", "0xDE", "0x05", "8KB Flash, 512B EEPROM, 512B SRAM"),
        "pwm3b": ChipInfo("AT90PWM3B", "0x1E930E", 8192, 512, "0xFF", "0xDE", "0x05", "8KB Flash, 512B EEPROM, 512B SRAM"),
        "1200": ChipInfo("AT90S1200", "0x1E9001", 1024, 64, "0xE4", "0xD9", "0xFF", "1KB Flash, 64B EEPROM, 64B SRAM"),
        "2313": ChipInfo("AT90S2313", "0x1E9101", 2048, 128, "0xE4", "0xD9", "0xFF", "2KB Flash, 128B EEPROM, 128B SRAM"),
        "2333": ChipInfo("AT90S2333", "0x1E9102", 2048, 128, "0xE4", "0xD9", "0xFF", "2KB Flash, 128B EEPROM, 128B SRAM"),
        "2343": ChipInfo("AT90S2343", "0x1E9103", 2048, 128, "0xE4", "0xD9", "0xFF", "2KB Flash, 128B EEPROM, 128B SRAM"),
        "4414": ChipInfo("AT90S4414", "0x1E9201", 4096, 256, "0xE4", "0xD9", "0xFF", "4KB Flash, 256B EEPROM, 256B SRAM"),
        "4433": ChipInfo("AT90S4433", "0x1E9202", 4096, 256, "0xE4", "0xD9", "0xFF", "4KB Flash, 256B EEPROM, 256B SRAM"),
        "4434": ChipInfo("AT90S4434", "0x1E9203", 4096, 256, "0xE4", "0xD9", "0xFF", "4KB Flash, 256B EEPROM, 256B SRAM"),
        "8515": ChipInfo("AT90S8515", "0x1E9301", 8192, 512, "0xE4", "0xD9", "0xFF", "8KB Flash, 512B EEPROM, 512B SRAM"),
        "8535": ChipInfo("AT90S8535", "0x1E9302", 8192, 512, "0xE4", "0xD9", "0xFF", "8KB Flash, 512B EEPROM, 512B SRAM"),
    },

    "AVR32 Series": {
        # AVR32 UC3 series
        "uc3a0512": ChipInfo("AVR32 UC3A0512", "0x1E9401", 524288, 8192, "0xFF", "0xDE", "0x05", "512KB Flash, 8KB EEPROM, 32KB SRAM"),
        "uc3a0256": ChipInfo("AVR32 UC3A0256", "0x1E9402", 262144, 8192, "0xFF", "0xDE", "0x05", "256KB Flash, 8KB EEPROM, 16KB SRAM"),
        "uc3b0256": ChipInfo("AVR32 UC3B0256", "0x1E9403", 262144, 8192, "0xFF", "0xDE", "0x05", "256KB Flash, 8KB EEPROM, 16KB SRAM"),
        "uc3b0512": ChipInfo("AVR32 UC3B0512", "0x1E9404", 524288, 8192, "0xFF", "0xDE", "0x05", "512KB Flash, 8KB EEPROM, 32KB SRAM"),
    },

    "ATmega0 Series": {
        # ATmega0 variants
        "m0": ChipInfo("ATmega4809", "0x1E951E", 49152, 2560, "0xFF", "0xDE", "0x05", "48KB Flash, 2560B EEPROM, 6KB SRAM"),
        "m0a": ChipInfo("ATmega4808", "0x1E951D", 49152, 2560, "0xFF", "0xDE", "0x05", "48KB Flash, 2560B EEPROM, 6KB SRAM"),
        "m0p": ChipInfo("ATmega4809P", "0x1E951F", 49152, 2560, "0xFF", "0xDE", "0x05", "48KB Flash, 2560B EEPROM, 6KB SRAM"),
    },

    "ATtiny0 Series": {
        # ATtiny0 variants
        "t0": ChipInfo("ATtiny404", "0x1E9405", 4096, 256, "0xFF", "0xDE", "0x05", "4KB Flash, 256B EEPROM, 256B SRAM"),
        "t0a": ChipInfo("ATtiny414", "0x1E9406", 4096, 256, "0xFF", "0xDE", "0x05", "4KB Flash, 256B EEPROM, 256B SRAM"),
        "t0b": ChipInfo("ATtiny814", "0x1E9407", 8192, 512, "0xFF", "0xDE", "0x05", "8KB Flash, 512B EEPROM, 512B SRAM"),
    },
}

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
                self.finished.emit("Operation berhasil!")
            else:
                self.error.emit("Operation gagal dengan kode error: " + str(returncode))

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
Informasi Chip:
----------------
Name: {chip_info.name}
Tanda tangan: {chip_info.signature}
Ukuran Flash: {chip_info.flash_size} bytes
Ukuran EEPROM: {chip_info.eeprom_size} bytes

Nilai Fuse Default:
------------------
Low Fuse: {chip_info.default_lfuse}
High Fuse: {chip_info.default_hfuse}
Extended Fuse: {chip_info.default_efuse}

Deskripsi:
-----------
{chip_info.description}
"""
        self.info_text.setText(info_text)

class AdvancedOptionsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Programming Options
        prog_group = QGroupBox("Opsi pemrograman")
        prog_layout = QGridLayout()

        self.verify_check = QCheckBox("verifikasi setelah menulis")
        self.verify_check.setChecked(True)
        prog_layout.addWidget(self.verify_check, 0, 0)

        self.erase_check = QCheckBox("hapus data sebelum menulis")
        self.erase_check.setChecked(True)
        prog_layout.addWidget(self.erase_check, 0, 1)

        self.disable_fuse_check = QCheckBox("nonaktifkan verifikasi fuse")
        prog_layout.addWidget(self.disable_fuse_check, 1, 0)

        prog_group.setLayout(prog_layout)
        layout.addWidget(prog_group)

        # Timing Options
        timing_group = QGroupBox("Opsi pewaktuan")
        timing_layout = QGridLayout()

        timing_layout.addWidget(QLabel("Periode Bit Clock (µs):"), 0, 0)
        self.bit_clock = QSpinBox()
        self.bit_clock.setRange(0, 250)
        self.bit_clock.setValue(1)
        timing_layout.addWidget(self.bit_clock, 0, 1)

        timing_layout.addWidget(QLabel("Coba sebanyak:"), 1, 0)
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
        self.setWindowTitle("Flasher AVR Tingkat Lanjut")
        self.setMinimumSize(1000, 800)

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
        chip_group = QGroupBox("Pemilihan chip")
        chip_layout = QGridLayout()

        self.chip_family = QComboBox()
        self.chip_family.addItems(CHIP_DATABASE.keys())
        self.chip_family.currentTextChanged.connect(self.update_chip_list)

        self.chip_combo = QComboBox()
        self.update_chip_list(self.chip_family.currentText())
        self.chip_combo.currentTextChanged.connect(self.update_chip_info)

        chip_layout.addWidget(QLabel("Keluarga:"), 0, 0)
        chip_layout.addWidget(self.chip_family, 0, 1)
        chip_layout.addWidget(QLabel("Chip:"), 0, 2)
        chip_layout.addWidget(self.chip_combo, 0, 3)

        chip_group.setLayout(chip_layout)
        operations_layout.addWidget(chip_group)

        # Flash operations
        flash_group = QGroupBox("Operasi Flash")
        flash_layout = QGridLayout()

        self.flash_file_path = QLabel("Tidak ada file dipilih")
        select_flash_btn = QPushButton("Pilih file Hex")
        select_flash_btn.clicked.connect(lambda: self.select_file("hex"))
        write_flash_btn = QPushButton("Tulis Flash")
        write_flash_btn.clicked.connect(self.write_flash)
        read_flash_btn = QPushButton("Baca Flash")
        read_flash_btn.clicked.connect(self.read_flash)
        verify_flash_btn = QPushButton("Verifikasi Flash")
        verify_flash_btn.clicked.connect(self.verify_flash)

        flash_layout.addWidget(select_flash_btn, 0, 0)
        flash_layout.addWidget(self.flash_file_path, 0, 1, 1, 2)
        flash_layout.addWidget(write_flash_btn, 1, 0)
        flash_layout.addWidget(read_flash_btn, 1, 1)
        flash_layout.addWidget(verify_flash_btn, 1, 2)

        flash_group.setLayout(flash_layout)
        operations_layout.addWidget(flash_group)

        # Fuse operations
        fuse_group = QGroupBox("Operasi Fuse")
        fuse_layout = QGridLayout()

        read_fuses_btn = QPushButton("Baca semua Fuses")
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

        write_fuses_btn = QPushButton("Tulis Fuses")
        write_fuses_btn.clicked.connect(self.write_fuses)
        reset_fuses_btn = QPushButton("Kembalikan ke Defaults")
        reset_fuses_btn.clicked.connect(self.reset_fuses)

        fuse_layout.addWidget(read_fuses_btn, 1, 0, 1, 2)
        fuse_layout.addWidget(write_fuses_btn, 1, 2, 1, 2)
        fuse_layout.addWidget(reset_fuses_btn, 1, 4, 1, 2)

        fuse_group.setLayout(fuse_layout)
        operations_layout.addWidget(fuse_group)

        # EEPROM operations
        eeprom_group = QGroupBox("Operasi EEPROM")
        eeprom_layout = QGridLayout()

        self.eeprom_file_path = QLabel("Tidak ada file dipilih")
        select_eeprom_btn = QPushButton("Pilih file EEPROM")
        select_eeprom_btn.clicked.connect(lambda: self.select_file("eeprom"))
        write_eeprom_btn = QPushButton("Tulis EEPROM")
        write_eeprom_btn.clicked.connect(self.write_eeprom)
        read_eeprom_btn = QPushButton("Baca EEPROM")
        read_eeprom_btn.clicked.connect(self.read_eeprom)
        verify_eeprom_btn = QPushButton("verifikasi EEPROM")
        verify_eeprom_btn.clicked.connect(self.verify_eeprom)

        eeprom_layout.addWidget(select_eeprom_btn, 0, 0)
        eeprom_layout.addWidget(self.eeprom_file_path, 0, 1, 1, 2)
        eeprom_layout.addWidget(write_eeprom_btn, 1, 0)
        eeprom_layout.addWidget(read_eeprom_btn, 1, 1)
        eeprom_layout.addWidget(verify_eeprom_btn, 1, 2)

        eeprom_group.setLayout(eeprom_layout)
        operations_layout.addWidget(eeprom_group)

        # Add operations tab to tab widget
        tab_widget.addTab(operations_tab, "Operasi")

        # Chip info tab
        self.chip_info_widget = ChipInfoWidget()
        tab_widget.addTab(self.chip_info_widget, "Info Chip")

        # Advanced options tab
        self.advanced_options = AdvancedOptionsWidget()
        tab_widget.addTab(self.advanced_options, "Opsi lanjutan")

        layout.addWidget(tab_widget)

        # Console output
        console_group = QGroupBox("Keluaran Console")
        console_layout = QVBoxLayout()
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Courier"))
        clear_console_btn = QPushButton("Bersihkan Console")
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
        self.settings.setValue("Keluarga", self.chip_family.currentText())
        self.settings.setValue("chip", self.chip_combo.currentText())
        self.settings.setValue("verifikasi", self.advanced_options.verify_check.isChecked())
        self.settings.setValue("hapus", self.advanced_options.erase_check.isChecked())
        self.settings.setValue("bit_clock", self.advanced_options.bit_clock.value())
        self.settings.setValue("percobaan", self.advanced_options.retry_count.value())

    def restore_settings(self):
        family = self.settings.value("keluarga", self.chip_family.currentText())
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
            self.settings.value("verivikasi", True, type=bool))
        self.advanced_options.erase_check.setChecked(
            self.settings.value("hapus", True, type=bool))
        self.advanced_options.bit_clock.setValue(
            self.settings.value("bit_clock", 1, type=int))
        self.advanced_options.retry_count.setValue(
            self.settings.value("percobaan", 3, type=int))

    def update_chip_list(self, family):
        self.chip_combo.clear()
        if family in CHIP_DATABASE:
            self.chip_combo.addItems(CHIP_DATABASE[family].keys())

    def update_chip_info(self, chip_name):
        for family, chips in CHIP_DATABASE.items():
            if chip_name in chips:
                chip_info = chips[chip_name]
                self.chip_info_widget.update_info(chip_info)

                # Update fuse defaults
                self.lfuse_input.setCurrentText(chip_info.default_lfuse)
                self.hfuse_input.setCurrentText(chip_info.default_hfuse)
                self.efuse_input.setCurrentText(chip_info.default_efuse)
                break

    def reset_fuses(self):
        for family, chips in CHIP_DATABASE.items():
            chip_name = self.chip_combo.currentText()
            if chip_name in chips:
                chip_info = chips[chip_name]
                self.lfuse_input.setCurrentText(chip_info.default_lfuse)
                self.hfuse_input.setCurrentText(chip_info.default_hfuse)
                self.efuse_input.setCurrentText(chip_info.default_efuse)
                break

    def get_base_command(self):
        cmd = ["avrdude", "-c", "usbasp", "-p", self.chip_combo.currentText()]

        # Add advanced options
        if self.advanced_options.bit_clock.value() != 1:
            cmd.extend(["-B", str(self.advanced_options.bit_clock.value())])

        if self.advanced_options.retry_count.value() != 3:
            cmd.extend(["-r", str(self.advanced_options.retry_count.value())])

        if self.advanced_options.disable_fuse_check.isChecked():
            cmd.append("-u")

        return cmd

    def execute_command(self, command):
        self.console.append(f"Menjalankan: {' '.join(command)}\n")
        self.worker = AvrdudeWorker(' '.join(command))
        self.worker.progress.connect(lambda msg: self.console.append(msg))
        self.worker.finished.connect(lambda msg: self.console.append(f"\n{msg}\n"))
        self.worker.error.connect(lambda msg: self.console.append(f"\nError: {msg}\n"))
        self.worker.start()

    def select_file(self, file_type):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Pilih {file_type.upper()} File",
            "",
            "File Hex (*.hex);;Semua files (*.*)"
        )
        if file_path:
            if file_type == "hex":
                self.flash_file_path.setText(file_path)
            else:
                self.eeprom_file_path.setText(file_path)

    def write_flash(self):
        if self.flash_file_path.text() == "Tidak ada file dipilih":
            QMessageBox.warning(self, "Error", "Pilih file hex terlebih dahulu!")
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
            "Simpan Flash Dump",
            "",
            "File Hex (*.hex);;Semua files (*.*)"
        )
        if file_path:
            cmd = self.get_base_command()
            cmd.extend(["-U", f"flash:r:{file_path}:i"])
            self.execute_command(cmd)

    def verify_flash(self):
        if self.flash_file_path.text() == "Tidak ada file dipilih":
            QMessageBox.warning(self, "Error", "Pilih file hex terlebih dahulu!")
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
            "Menulis nilai Fuse yang salah dapat merusak perangkat Anda. Apakah Anda yakin ingin melanjutkan?",
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
        if self.eeprom_file_path.text() == "Tidak ada file dipilih":
            QMessageBox.warning(self, "Error", "Pilih file EEPROM terlebih dahulu!")
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
        if self.eeprom_file_path.text() == "Tidak ada file dipilih":
            QMessageBox.warning(self, "Error", "Pilih file EEPROM terlebih dahulu!")
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
