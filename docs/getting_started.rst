Getting Started
===============

This guide will help you set up and run CV4GT on your system.

Prerequisites
-------------

Hardware Requirements
~~~~~~~~~~~~~~~~~~~~~

- **CPU**: Multi-core processor (Intel i5 or better recommended)
- **GPU**: NVIDIA GPU with CUDA support (for GPU acceleration)
- **RAM**: 8GB minimum, 16GB recommended
- **Camera**: Intel RealSense D400 series (optional, can use video files)

Software Requirements
~~~~~~~~~~~~~~~~~~~~~

- **Python**: 3.11 (required)
- **Node.js**: >= 20.19.0
- **CUDA Toolkit**: 12.1, 12.4, 12.6, 12.8, or 12.9 (for GPU acceleration)
- **Visual Studio C++ Build Tools**: Required on Windows for some Python packages
- **Intel RealSense SDK**: >= 2.0.0

Installation
------------

Step 1: Clone the Repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/ast-n/cv4gt.git
   cd cv4gt

Step 2: Install System Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Intel RealSense SDK**

Windows
^^^^^^^

1. Download from `Intel RealSense releases <https://github.com/IntelRealSense/librealsense/releases/latest>`_
2. Run ``Intel.RealSense.SDK.exe``
3. Follow the installation wizard

Linux
^^^^^

Try pre-built packages first:

.. code-block:: bash

   # Add repository
   sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE
   sudo add-apt-repository "deb https://librealsense.intel.com/Debian/apt-repo $(lsb_release -cs) main"

   # Install
   sudo apt-get update
   sudo apt-get install librealsense2-dkms librealsense2-utils librealsense2-dev

If that fails, `build from source <https://github.com/IntelRealSense/librealsense/blob/master/doc/installation.md>`_.

**TurboJPEG**

Windows
^^^^^^^

Download ``libjpeg-turbo-3.1.2-vc-x86.exe`` from `releases <https://github.com/libjpeg-turbo/libjpeg-turbo/releases>`_ and add to PATH.

Linux
^^^^^

.. code-block:: bash

   sudo apt-get install libturbojpeg0-dev

Then install Python bindings:

.. code-block:: bash

   pip install PyTurboJPEG

Step 3: Install Python Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Windows (Automated)**

.. code-block:: bash

   ./run_application.bat

This creates a virtual environment, installs dependencies, and launches the app.

**Linux/Mac (Manual)**

.. code-block:: bash

   # Create virtual environment
   python3.11 -m venv .venv
   source .venv/bin/activate

   # Install PyTorch for your CUDA version
   # For CUDA 12.1:
   pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121

   # For other CUDA versions, replace cu121 with:
   # cu124, cu126, cu128, or cu129

   # Install other dependencies
   pip install -r requirements.txt

Step 4: Install Frontend Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   npm --prefix src/frontend install

Step 5: Download Models
~~~~~~~~~~~~~~~~~~~~~~~

Models are stored in the ``models/`` directory. You can download them using the provided Jupyter notebook:

.. code-block:: bash

   jupyter notebook functions.ipynb

Run cell 1 to download the latest models from Roboflow/HuggingFace.

Running the Application
-----------------------

Full Stack
~~~~~~~~~~

.. code-block:: bash

   npm --prefix src/frontend start

This starts both the backend API server (port 8000) and the Electron frontend.

Backend Only
~~~~~~~~~~~~

.. code-block:: bash

   python src/api.py

Access the WebSocket at ``ws://localhost:8000/ws``.

Frontend Only
~~~~~~~~~~~~~

.. code-block:: bash

   # Dev server
   npm --prefix src/frontend run vite

   # Electron
   npm --prefix src/frontend run electron

Troubleshooting
---------------

Python Dependency Issues
~~~~~~~~~~~~~~~~~~~~~~~~

If you encounter dependency errors:

.. code-block:: bash

   # Delete virtual environment
   rm -rf .venv  # Linux/Mac
   rmdir /s .venv  # Windows

   # Recreate and reinstall
   python3.11 -m venv .venv
   # ... follow installation steps again

CUDA/GPU Not Detected
~~~~~~~~~~~~~~~~~~~~~

Verify CUDA installation:

.. code-block:: bash

   python -c "import torch; print(torch.cuda.is_available())"

Should print ``True`` if GPU is available.

RealSense Camera Not Found
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check device detection:

.. code-block:: bash

   # Linux
   realsense-viewer

   # Windows
   # Launch Intel RealSense Viewer from Start Menu

TurboJPEG Import Error
~~~~~~~~~~~~~~~~~~~~~~

Ensure TurboJPEG is on your system PATH and Python bindings are installed:

.. code-block:: bash

   pip install --force-reinstall PyTurboJPEG

Next Steps
----------

- Configure the system: :doc:`configuration`
- Learn how to use CV4GT: :doc:`usage`
- Explore the API: :doc:`api/modules`
