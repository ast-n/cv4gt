#!/bin/bash

echo "--- Preparing X server for Docker GUI ---"

# Step 1: Grant Docker access to the host's display
xhost +local:

# Step 2: Run the Docker container and execute the start command
echo "--- Starting Docker container and application ---"
docker run -it --rm \
    --runtime nvidia \
    --privileged \
    --network host \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ~/cv4gt:/cv4gt \
    -v ~/models:/cv4gt/models \
    -v ~/data:/cv4gt/data/recordings \
    -e DISPLAY=$DISPLAY \
    l4t-pytorch-realsense:latest \
    /bin/bash -c "npm install && npm --prefix src/frontend install && npm start"
