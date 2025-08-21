# CV4GT
Computer Vision for garbage truck driver safety

## Overview
This repository contains:
- A **Python YOLO backend**,
- A **Vue 3 + Vite frontend**.

## Getting started


### 1. Clone the repository
```bash
git clone https://github.com/ast-n/cv4gt.git
cd <cv4gt>
```
---
### 2. Install requirements
#### Backend
Requires **Python 3.11**...

```bash
pip install -r requirements.txt
```
#### Frontend
Requires **Node.js >= 20.19.0** and **npm**
 <br>
```bash
cd src/frontend
npm install
```

#### Realsense SDK
Our project relies on the Realsense SDK. This is available on Windows, Linux, and some versions of Mac. We are using Realsense SDK versions >= 2.0.0, and the respective Python library - pyrealsense 2.<br>

**Install instructions**
##### Windows 
1. Go to the [latest stable release](https://github.com/IntelRealSense/librealsense/releases/latest), navigate to the Assets section, download and run Intel.RealSense.SDK.exe

2. Click through several simple steps of the installer

##### Linux
1. Attempt to use the pre-built instructions to install. Find [here](https://github.com/IntelRealSense/librealsense/blob/master/doc/distribution_linux.md)
2. Have it fail and build from source using these instructions [here](https://github.com/IntelRealSense/librealsense/blob/master/doc/installation.md)

##### Mac
1. Good luck
2. Ensure you have the required **XCode 6.0+** , then follow the instructions [here](https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_osx.md)


---
### 3. Run the solution
Still need to couple together the starting of frontend and backend, but without having linked these together, I'll assume these instructions work. Commands issued in the main directory of the project for now. 

THIS DOESN'T WORK YET BECAUSE THEY DON'T TALK!!!!!

#### Backend
```bash
python src/api.py 
```

#### Frontend
```bash
npm --prefix src/frontend run dev
```