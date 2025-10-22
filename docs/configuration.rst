Configuration
=============

CV4GT is configured through the ``config.ini`` file in the project root directory.

Configuration File
------------------

The configuration file uses INI format with two main sections:

config.ini Structure
~~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

   [VIDEO]
   input_video = data/trim.mp4
   use_realsense = false
   output_video =
   enable_auxiliary_display = false
   smoothing_factor = 0.2
   max_fps = 30

   [SYSTEM]
   model_path = models/YOLOv11m-02-09-129e.pt
   enable_logging = false

VIDEO Section
-------------

input_video
~~~~~~~~~~~

:Type: ``string``
:Default: ``data/trim.mp4``

Path to the input video file. Used when ``use_realsense = false``.

**Examples:**

.. code-block:: ini

   # Relative path
   input_video = data/my_video.mp4

   # Absolute path (Windows)
   input_video = C:\Users\user\Videos\test.mp4

   # Absolute path (Linux/Mac)
   input_video = /home/user/videos/test.mp4

   # RealSense recording (.bag file)
   input_video = data/recording.bag

use_realsense
~~~~~~~~~~~~~

:Type: ``boolean``
:Default: ``false``

Whether to use an Intel RealSense camera for live capture.

- ``true``: Use RealSense camera (requires connected camera)
- ``false``: Use video file specified in ``input_video``

**Note:** When using RealSense with ``input_video`` set to a ``.bag`` file, the system plays back the recording.

output_video
~~~~~~~~~~~~

:Type: ``string``
:Default: `` `` (empty)

Path where the annotated output video will be saved. Leave empty to disable video saving.

**Examples:**

.. code-block:: ini

   # Save to data directory
   output_video = data/output.mp4

   # Disable output (empty value)
   output_video =

enable_auxiliary_display
~~~~~~~~~~~~~~~~~~~~~~~~~

:Type: ``boolean``
:Default: ``false``

Whether to show a CV2 window with the annotated video feed during processing.

- ``true``: Display OpenCV window (useful for debugging)
- ``false``: Headless operation (recommended for production)

**Note:** On systems without a display (like Jetson in headless mode), this should be ``false``.

smoothing_factor
~~~~~~~~~~~~~~~~

:Type: ``float``
:Range: ``0.0`` - ``1.0``
:Default: ``0.2``

Strength of bounding box position smoothing using polynomial interpolation.

- ``0.0``: No smoothing (boxes jump between frames)
- ``1.0``: Maximum smoothing (smoother movement, slight lag)

**Recommended:** ``0.2`` - ``0.5`` for good balance.

max_fps
~~~~~~~

:Type: ``integer``
:Default: ``30``

Maximum frames per second for WebSocket streaming.

- ``0``: No FPS cap (maximum throughput)
- ``> 0``: Cap at specified FPS

**Note:** Lower values reduce network bandwidth and client-side processing load.

SYSTEM Section
--------------

model_path
~~~~~~~~~~

:Type: ``string``
:Default: ``models/YOLOv11m-02-09-129e.pt``

Path to the YOLO model file (``.pt`` format).

**Examples:**

.. code-block:: ini

   # Specific model
   model_path = models/YOLOv11m-02-09-129e.pt

   # Auto-load latest (leave empty or use get_latest_model)
   model_path =

enable_logging
~~~~~~~~~~~~~~

:Type: ``boolean``
:Default: ``false``

Whether to save frames with high-relevance objects and log detections.

- ``true``: Saves tagged images to ``data/tagged/`` and logs to ``data/logs/``
- ``false``: No data persistence

**Storage locations:**

- Tagged images: ``data/tagged/YYYY-MM-DD_HH-MM-SS.microsecond.jpg``
- Detection logs: ``data/logs/saved_log_YYYY-MM-DD_HH-MM-SS.microsecond.jsonl``

Platform-Specific Configs
-------------------------

Jetson Configuration
~~~~~~~~~~~~~~~~~~~~

For NVIDIA Jetson devices, use ``config_jetson.ini``:

.. code-block:: ini

   [VIDEO]
   input_video =
   use_realsense = true
   output_video =
   enable_auxiliary_display = false  # No display in headless mode
   smoothing_factor = 0.2
   max_fps = 30

   [SYSTEM]
   model_path = models/YOLOv11m-02-09-129e.pt
   enable_logging = true

Then modify ``api.py``:

.. code-block:: python

   # Line 33-34
   # config.read("config.ini")
   config.read("config_jetson.ini")

Environment Variables
---------------------

While not currently implemented, you can override config values using environment variables by modifying ``api.py``:

.. code-block:: python

   import os

   # Override from environment
   INPUT_VIDEO = os.getenv('CV4GT_INPUT_VIDEO', video_config['input_video'])
   MODEL_PATH = os.getenv('CV4GT_MODEL_PATH', system_config['model_path'])

Best Practices
--------------

Development
~~~~~~~~~~~

.. code-block:: ini

   [VIDEO]
   use_realsense = false
   enable_auxiliary_display = true  # See the output
   max_fps = 30
   output_video = data/debug_output.mp4

   [SYSTEM]
   enable_logging = true  # Collect test data

Production (Jetson)
~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

   [VIDEO]
   use_realsense = true
   enable_auxiliary_display = false  # Headless
   max_fps = 30  # Balance between quality and performance
   output_video =  # No video recording

   [SYSTEM]
   enable_logging = true  # Log important events

Testing with Video Files
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

   [VIDEO]
   input_video = data/test_scenarios/scenario1.mp4
   use_realsense = false
   enable_auxiliary_display = true
   max_fps = 0  # Process as fast as possible

   [SYSTEM]
   enable_logging = false
