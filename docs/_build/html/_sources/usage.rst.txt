Usage Guide
===========

This guide covers common usage scenarios for CV4GT.

Basic Usage
-----------

Running with Video File
~~~~~~~~~~~~~~~~~~~~~~~

1. **Configure** ``config.ini``:

   .. code-block:: ini

      [VIDEO]
      input_video = data/my_video.mp4
      use_realsense = false

2. **Run** the application:

   .. code-block:: bash

      npm --prefix src/frontend start

3. **View** the output in the Electron window.

Running with RealSense Camera
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Connect** your Intel RealSense camera

2. **Configure** ``config.ini``:

   .. code-block:: ini

      [VIDEO]
      input_video =
      use_realsense = true

3. **Run** the application:

   .. code-block:: bash

      npm --prefix src/frontend start

Understanding the Interface
---------------------------

Video Panel
~~~~~~~~~~~

The main video panel shows:

- **Bounding boxes**: Color-coded by relevance (red = highest priority)
- **Labels**: Show class, confidence, relevance score, and depth
- **Bin gripper guides**: Green/red alignment indicators for bin pickup

Color Coding
^^^^^^^^^^^^

- **Red**: Relevance 5 (immediate danger - person, cyclist)
- **Orange**: Relevance 4 (high priority)
- **Yellow**: Relevance 3 (medium priority)
- **Green**: Relevance 2 (low priority)
- **Cyan**: Relevance 1 (very low priority)

Object List
~~~~~~~~~~~

Shows detected objects sorted by relevance with:

- Object class
- Confidence score
- Relevance rating
- Distance (depth) in meters
- Track ID

Map Panel
~~~~~~~~~

Displays current GPS location (currently placeholder at Swinburne University).

System Info
~~~~~~~~~~~

Shows:

- CPU usage percentage
- Memory usage (used / total MB)

Working with Detection Data
----------------------------

Enabling Logging
~~~~~~~~~~~~~~~~

To save frames and detection logs:

.. code-block:: ini

   [SYSTEM]
   enable_logging = true

Logged Data
~~~~~~~~~~~

**Tagged Images** (``data/tagged/``):

- Frames with high-relevance objects (relevance ≥ 4)
- GPS coordinates embedded in EXIF
- Filename: ``YYYY-MM-DD_HH-MM-SS.microsecond.jpg``

**Detection Logs** (``data/logs/``):

- JSONL format (one JSON object per line)
- Contains frame number, timestamp, and all detections
- Filename: ``saved_log_YYYY-MM-DD_HH-MM-SS.microsecond.jsonl``

Reading Log Files
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import json

   with open('data/logs/saved_log_2025-01-20_14-30-45.123456.jsonl', 'r') as f:
       for line in f:
           detection_event = json.loads(line)
           print(f"Frame {detection_event['frame_num']}:")
           for det in detection_event['detections']:
               print(f"  - {det['class']} (R:{det['relevance']}, D:{det['depth']:.1f}m)")

Audio Feedback
--------------

Bin Alignment Audio
~~~~~~~~~~~~~~~~~~~

When a bin is detected:

- **No sound**: Bin is aligned (green indicators)
- **Beeping**: Bin is misaligned (red indicators)
- **Suppressed**: After successful pickup or timeout

The system tracks individual bins to avoid repetitive alerts.

Advanced Usage
--------------

Custom Models
~~~~~~~~~~~~~

To use a custom YOLO model:

1. Train your model using Ultralytics YOLO
2. Save as ``.pt`` format
3. Place in ``models/`` directory
4. Update ``config.ini``:

   .. code-block:: ini

      [SYSTEM]
      model_path = models/my_custom_model.pt

Backend-Only Mode
~~~~~~~~~~~~~~~~~

For testing or headless deployment:

.. code-block:: bash

   # Start backend
   python src/api.py

   # Connect custom client to ws://localhost:8000/ws

Recording RealSense Data
~~~~~~~~~~~~~~~~~~~~~~~~

To record a RealSense session for playback:

1. Use Intel RealSense Viewer
2. Click "Record" button
3. Save as ``.bag`` file
4. Use in ``config.ini``:

   .. code-block:: ini

      [VIDEO]
      input_video = data/recordings/session1.bag
      use_realsense = true

Performance Tuning
------------------

FPS Optimization
~~~~~~~~~~~~~~~~

Adjust FPS based on your needs:

.. code-block:: ini

   [VIDEO]
   # Maximum throughput (may overwhelm frontend)
   max_fps = 0

   # Balanced (recommended)
   max_fps = 30

   # Reduced load
   max_fps = 15

Smoothing
~~~~~~~~~

Adjust bounding box smoothing:

.. code-block:: ini

   [VIDEO]
   # No smoothing (responsive but jumpy)
   smoothing_factor = 0.0

   # Light smoothing (recommended)
   smoothing_factor = 0.2

   # Heavy smoothing (smooth but laggy)
   smoothing_factor = 0.8

Troubleshooting
---------------

No Detections
~~~~~~~~~~~~~

1. Check model is loaded: Look for "Model successfully loaded" in console
2. Verify video feed: Check frames are being processed
3. Lower confidence threshold if using custom model

High CPU/Memory Usage
~~~~~~~~~~~~~~~~~~~~~

1. Reduce ``max_fps``
2. Disable ``enable_auxiliary_display`` if not needed
3. Use smaller YOLO model (YOLOv11s instead of YOLOv11m)

Audio Not Working
~~~~~~~~~~~~~~~~~

Audio automatically disables on headless systems (Jetson). This is expected behavior.

WebSocket Connection Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Ensure backend is running: ``python src/api.py``
2. Check port 8000 is not in use
3. Verify CORS settings in ``api.py`` if using custom frontend
