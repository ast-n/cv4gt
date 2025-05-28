#!/bin/bash
# This script launches the cv4gt Docker container with ZED SDK on Jetson,
# mounting the repository and data directories, and enabling GUI display.

echo "--- Starting cv4gt Development Environment with ZED SDK on Jetson ---"

# --- PART 1: Host-level Prerequisites ---
# Allow Docker containers to connect to your X server for GUI display
# You MUST run this on your Jetson host every time you reboot!
echo "Setting up X11 forwarding for GUI."
xhost +local:docker

# --- PART 2: Docker Image & Path Configuration ---
# Define host paths (where your directories are on the Jetson)
HOST_REPO_PATH="$(pwd)"

# Define container paths (how these directories will appear inside Docker)
CONTAINER_REPO_PATH=/app/cv4gt_repo

# Docker Image Name (update this to match your new ZED image)
DOCKER_IMAGE="jetson_zed:stable"

# --- PART 3: Container Management ---
echo "--- Stopping and removing any existing Docker containers for a clean start ---"
sudo docker stop $(sudo docker ps -aq) > /dev/null 2>&1
sudo docker rm $(sudo docker ps -aq) > /dev/null 2>&1
echo "Cleaned up old containers."

echo "--- Launching Docker container: ${DOCKER_IMAGE} ---"

# The actual docker run command with ZED SDK specific configurations
sudo docker run -it \
    --privileged \
    --ipc=host \
    --runtime=nvidia \
    --gpus all \
    --group-add video \
    -v "${HOST_REPO_PATH}:${CONTAINER_REPO_PATH}" \
    -e DISPLAY="$DISPLAY" \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /dev:/dev \
    -v /usr/lib/aarch64-linux-gnu/tegra:/usr/lib/aarch64-linux-gnu/tegra \
    -v /usr/local/cuda:/usr/local/cuda \
    -v /tmp/argus_socket:/tmp/argus_socket \
    -e LD_LIBRARY_PATH="/usr/local/zed/lib:/usr/local/cuda/lib64:/usr/lib/aarch64-linux-gnu/tegra:/usr/lib/aarch64-linux-gnu:${LD_LIBRARY_PATH}" \
    -e CUDA_HOME="/usr/local/cuda" \
    -e PATH="/usr/local/zed/bin:/usr/local/cuda/bin:${PATH}" \
    --device-cgroup-rule='c 189:* rmw' \
    --device-cgroup-rule='c 81:* rmw' \
    --device-cgroup-rule='c 13:* rmw' \
    "${DOCKER_IMAGE}" \
    /bin/bash

echo "--- Docker container exited ---"
echo "Remember to stop your X server if you no longer need it."