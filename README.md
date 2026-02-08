# PSBT QR Scanner & TXID Extractor

A lightweight Python tool designed to bridge the gap between air-gapped hardware wallets and your PC. 

This tool scans animated QR codes (Uniform Resources - UR) containing a **Partially Signed Bitcoin Transaction (PSBT)** directly via your webcam. It extracts the **Transaction Hash (TXID)** and automatically copies it to your clipboard.

This is ideal for users following privacy-focused workflows (like the "Flying V" method) who wish to extract a transaction hash offline and broadcast it later via a secure connection (VPN/Tor) without exposing their signing device or original IP.

## 🚀 Features

* **Animated QR Support:** capable of scanning multi-part animated QR codes (UR standard) used by wallets like Seedsigner, Krux, Keystone, and Passport.
* **Privacy Centric:** All processing happens locally on your machine.
* **Auto-Clipboard:** Automatically copies the resulting TXID to your clipboard upon successful scan.
* **Visual Feedback:** On-screen progress percentage and success indicators.
* **Dependencies:** Uses `embit` for Bitcoin logic and `opencv` for computer vision.

## 🛠️ Prerequisites

You will need Python 3 installed. This tool relies on a few external libraries.

### System Dependencies (Linux/macOS)
The `pyzbar` library requires the `zbar` shared library to be installed on your system.

* **Ubuntu/Debian:** `sudo apt-get install libzbar0`
* **macOS:** `brew install zbar`
* **Windows:** Usually handled automatically by the pip package, but you may need the [Visual C++ Redistributable](https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads).

### Python Libraries
Install the required packages using pip:

```bash
pip install opencv-python pyzbar pyperclip embit
