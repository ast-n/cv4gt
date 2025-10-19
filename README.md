# CV4GT
Computer Vision for garbage truck driver safety

## Overview
This repository contains:
- A **Python YOLO backend**,
- A **Vue 3 + Vite + Electron frontend**.

## Getting started


### 1. Clone the repository
```bash
git clone https://github.com/ast-n/cv4gt.git
cd cv4gt
```
---
### 2. Install requirements
#### Backend
Requires `Python 3.11`

Get the latest from [here](https://www.python.org/downloads/release/python-3119/).

If you want GPU-accelerated performance (you probably do), you will also need CUDA Toolkit. Supported versions include `12.1`, `12.4`, `12.6`, `12.8`, and `12.9`. Download one from [here](https://developer.nvidia.com/cuda-toolkit-archive).

You may also need to install the Visual Studio C++ Build Tools, including the Win10/11 SDK. Some of the python libraries used might need to be manually built, which requires this.


#### Frontend
Requires `Node.js >= 20.19.0` and `npm`

Get them from [here](https://nodejs.org/en/download).

#### Realsense SDK
Our project relies on the Realsense SDK. This is available on Windows, Linux, and some versions of Mac. We are using Realsense SDK versions >= 2.0.0, and the respective Python library - pyrealsense 2.<br>

**Realsense SDK Install instructions**
##### Windows 
1. Go to the [latest stable release](https://github.com/IntelRealSense/librealsense/releases/latest), navigate to the Assets section, download and run Intel.RealSense.SDK.exe
2. Click through several simple steps of the installer

##### Linux
1. Attempt to use the pre-built instructions to install. Find [here](https://github.com/IntelRealSense/librealsense/blob/master/doc/distribution_linux.md)
2. It will probably fail, in which case you should build from source using these instructions [here](https://github.com/IntelRealSense/librealsense/blob/master/doc/installation.md)

##### Mac
1. Good luck
2. Ensure you have the required **XCode 6.0+** , then follow the instructions [here](https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_osx.md)


#### TurboJPEG
Needs to be installed for faster encoding before shipment to websockets. Installation method varies on OS. Easiest to just find from [releases](https://github.com/libjpeg-turbo/libjpeg-turbo/releases) or from package manager if using UNIX-based system. It is likely that `libjpeg-turbo-3.1.2-vc-x86.exe` is sufficient for most Windows environments.

Ensure that the installation is on system PATH.

Follow up by installing python bindings if not automatically installed.

`pip install PyTurboJPEG`

---
### 3. Run the solution

#### Windows
If you are on Windows, just run `run_application.bat` in the project's top level directory. It will automatically download and install any remaining requirements, then launch the application.

Once requirements have been installed from the first time you run it, it should take ~10s to start up.

If you encounter any issues with python dependencies, you can delete the .venv file then run the launcher again to reinstall them all.

#### Linux/Mac
No installer or one-click launcher has been set up for these platforms, so requirements will have to be manually installed.

1. Create a new python venv with Python 3.11 and save it in a `.venv` folder in the base folder of this repository.
```bash
python3.11 -m venv .venv
```
Activate the venv.
```bash
source .venv/bin/activate
```
2. Find out your CUDA Toolkit version and install the appropriate version of torch.
```bash
pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu<your-cuda-version>

# Example for CUDA Toolkit version 12.1:
pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121
```
3. Install the remaining python requirements.
```bash
pip install -r "requirements.txt"
```
4. Install frontend requirements.
```bash
npm --prefix src/frontend install
```

5. Launch the application

```bash
npm --prefix src/frontend start
```
