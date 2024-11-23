# README for Advanced AVR Flasher GUI

## Overview
The **Advanced AVR Flasher GUI** is a PyQt6-based desktop application designed to simplify programming, managing, and troubleshooting AVR microcontrollers. It provides a user-friendly interface for chip selection, flashing firmware, reading/writing EEPROM, manipulating fuse bits, and performing verification and debugging tasks. The application leverages the `avrdude` command-line tool for low-level interactions with AVR devices.

## Features
1. **Chip Database**: Comprehensive support for a wide range of AVR microcontrollers (ATmega, ATtiny, ATxmega, AVR32, AT90).
2. **Flash Operations**:
   - Select and write firmware in `.hex` format.
   - Read and verify flash memory.
3. **EEPROM Operations**:
   - Read, write, and verify EEPROM data.
4. **Fuse Management**:
   - View and modify fuse settings.
   - Restore default fuse values for the selected chip.
5. **Advanced Options**:
   - Configure bit clock period and retry count for programming.
   - Enable/disable options like erase before writing, fuse verification, etc.
6. **Console Output**:
   - Real-time display of `avrdude` command outputs and progress.
7. **Settings Persistence**:
   - Save and restore user preferences for chip family, advanced settings, and other options.

## Requirements
### Software
- Python 3.8+
- Required Python Libraries:
  - `PyQt6`
  - `json`
  - `subprocess`
- `avrdude` (Installed and configured in the system PATH)

### Hardware
- Supported AVR microcontroller with an appropriate programmer (e.g., USBasp, STK500).

## Installation
1. Clone or download the repository containing this file.
2. Ensure Python 3.8+ is installed on your system.
3. Install required Python packages:
   ```bash
   pip install PyQt6
   ```
4. Ensure `avrdude` is installed:
   - For Linux:
     ```bash
     sudo apt install avrdude
     ```
   - For Windows:
     Download and install the latest version of `avrdude` and add it to your PATH.
5. Run the application:
   ```bash
   python advance.py
   ```

## Usage Instructions
1. **Launching the Application**:
   - Run `python advance.py` from the command line.
   - The main window will appear, displaying multiple tabs for chip selection, flash operations, EEPROM, fuse management, and advanced settings.

2. **Chip Selection**:
   - Select the chip family from the drop-down menu.
   - Choose the specific chip model.

3. **Flash Operations**:
   - Use the **"Select Hex File"** button to load your firmware.
   - Write to flash memory using the **"Write Flash"** button.
   - Read or verify existing flash memory using **"Read Flash"** or **"Verify Flash"**.

4. **EEPROM Operations**:
   - Use the **"Select EEPROM File"** button to choose an EEPROM file.
   - Write data to EEPROM with **"Write EEPROM"**.
   - Read or verify EEPROM data using the corresponding buttons.

5. **Fuse Management**:
   - View default or existing fuse settings.
   - Modify values and write them using the **"Write Fuses"** button.
   - Restore default fuse values with **"Reset to Defaults"**.

6. **Console Output**:
   - Monitor progress and error messages in real-time via the console window at the bottom of the application.
   - Use the **"Clear Console"** button to reset the output.

7. **Advanced Options**:
   - Configure bit clock period and retry count.
   - Enable or disable options like erase-before-write and fuse verification.

## Developer Notes
- The `CHIP_DATABASE` provides detailed specifications for various AVR chips, including memory sizes, default fuse values, and descriptions. This can be expanded as needed.
- `AvrdudeWorker` is implemented using PyQt's `QThread` to execute commands asynchronously, ensuring the GUI remains responsive.
- Settings are managed using `QSettings`, allowing user preferences to persist between sessions.

## Troubleshooting
- **Missing Dependencies**:
  - Ensure all required Python packages are installed.
  - Verify `avrdude` is correctly installed and accessible from the command line.
- **Permission Errors**:
  - On Linux, ensure your user has permissions to access the programmer hardware (e.g., USBasp).
- **Chip Not Detected**:
  - Verify connections, programmer setup, and chip selection.
  - Check the chip's documentation for correct fuse and clock configurations.

## Acknowledgments
This project simplifies AVR microcontroller programming and management, making it accessible for hobbyists and professionals. It relies on the powerful `avrdude` tool for core functionality.

## Future Enhancements
- Integration with additional programmers and interfaces.
- Support for advanced debugging protocols.
- Improved error handling and diagnostics.

Enjoy programming your AVR microcontrollers with ease! 🚀
