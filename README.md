# Netleaf

![template](https://github.com/Niamorro/Netleaf/assets/123011549/1b4c43d9-2db6-413d-951d-df0648d19992)

Netleaf is a simple network scanner written in Python using PyQt5. It allows you to scan devices in a given IP range and provides information about their status.

## Features

- Scan devices in a specified IP range(using ICMP(ping) protocol) 
- Display connected devices and their status (the program may not work properly if you are using a gray IP address or if you have devices with DHCP enabled)
- Save scan results to a CSV file
- Dark and light theme options

## Installation

Netleaf comes with a Windows installer for easy installation.

1. Download the latest release from the [Releases](https://github.com/Niamorro/Netleaf/releases) page.
2. Run the installer and follow the on-screen instructions.

## Usage

1. Launch the application.
2. Enter the desired IP range in the provided fields.
3. Click the "Scan Devices" button to start the scanning process.
4. View the results in the "Connected Devices" and "Console" sections.
5. Save the scan results to a CSV file using the "Save to File" option in the menu.

## Dependencies

- Python 3.9
- PyQt5 5.15.10

## Settings

The application allows you to customize its appearance.

1. Open the "Settings" menu.
2. Choose between light and dark themes.
3. Click "Ok" to apply the changes.

## Main Window

<img width="397" alt="mainwindowscreen" src="https://github.com/Niamorro/Netleaf/assets/123011549/18e56c64-a2c3-412f-a6b1-cb147a4755b0">

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- PyQt5 for the GUI framework

## Author
Niamorro
