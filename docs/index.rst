CV4GT Documentation
===================

**CV4GT** (Computer Vision for Garbage Truck driver safety) is a real-time object detection and tracking system designed to enhance safety around garbage trucks. The system uses YOLO-based detection with ByteTrack tracking, Intel RealSense depth sensing, and dynamic relevance scoring to identify and prioritize hazards.

.. image:: https://img.shields.io/badge/python-3.11-blue.svg
   :target: https://www.python.org/downloads/release/python-3119/
   :alt: Python Version

.. image:: https://img.shields.io/badge/framework-FastAPI-009688.svg
   :target: https://fastapi.tiangolo.com/
   :alt: FastAPI

.. image:: https://img.shields.io/badge/frontend-Vue%203-4FC08D.svg
   :target: https://vuejs.org/
   :alt: Vue 3

Features
--------

- **Real-time Object Detection**: YOLO-based detection with custom-trained models
- **Persistent Object Tracking**: ByteTrack integration for stable IDs across frames
- **Depth Sensing**: Intel RealSense integration for accurate distance measurement
- **Dynamic Relevance Scoring**: Priority-based system (1-5 scale) considering distance and velocity
- **Audio Feedback**: Bin gripper alignment guidance for drivers
- **WebSocket Streaming**: Real-time frame and detection data to Electron frontend
- **Data Logging**: GPS-tagged image storage and JSONL detection logs

Quick Start
-----------

Installation
~~~~~~~~~~~~

**Windows:**

.. code-block:: bash

   # Run the automated installer
   ./run_application.bat

**Linux/Mac:**

.. code-block:: bash

   # Create Python 3.11 virtual environment
   python3.11 -m venv .venv
   source .venv/bin/activate

   # Install PyTorch (example for CUDA 12.1)
   pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121

   # Install dependencies
   pip install -r requirements.txt

   # Install frontend dependencies
   npm --prefix src/frontend install

Running the Application
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Full stack (backend + frontend)
   npm --prefix src/frontend start

   # Backend only
   python src/api.py

Configuration
~~~~~~~~~~~~~

Edit ``config.ini`` before running:

.. code-block:: ini

   [VIDEO]
   input_video = data/trim.mp4
   use_realsense = false
   max_fps = 30

   [SYSTEM]
   model_path = models/YOLOv11m-02-09-129e.pt

Architecture Overview
---------------------

Backend (Python)
~~~~~~~~~~~~~~~~

The backend consists of several core modules:

- **api.py**: FastAPI server with WebSocket streaming
- **video_processing.py**: Main processing pipeline coordinator
- **ai_handler.py**: YOLO model management and ByteTrack integration
- **obstacle_relevance.py**: Dynamic relevance scoring system
- **camera_feed.py**: RealSense camera interface
- **audio_alerts.py**: Audio feedback for bin alignment
- **store.py**: Data persistence and logging

Frontend (Vue 3 + Electron)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **App.vue**: Main application with WebSocket client
- **VideoPanel.vue**: Real-time video display
- **ObjectList.vue**: Detection list with relevance scores
- **MapPanel.vue**: GPS location visualization
- **SystemInformation.vue**: CPU/memory metrics

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   getting_started
   configuration
   usage

.. toctree::
   :maxdepth: 3
   :caption: API Reference

   api/modules

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
