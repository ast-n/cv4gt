#!/bin/bash

# This script sets up and launches the cv4gt development Docker container
# for AMD64 PCs (Windows/WSL2).

echo "--- Starting cv4gt Development Environment Setup ---"

# Ensure X Server is running on Windows (VcXsrv/MobaXterm required).
echo "Setting up X11 forwarding for GUI (VcXsrv/MobaXterm required on Windows host)."
export DISPLAY=host.docker.internal:0.0

# Docker image management
DOCKER_IMAGE_NAME="astonlynch/cv4gt_dev_env:v1"
LOCAL_IMAGE_TAG="dev_env:v1"

echo "Checking for Docker image: ${DOCKER_IMAGE_NAME}"
if [[ "$(sudo docker images -q ${LOCAL_IMAGE_TAG} 2> /dev/null)" == "" ]]; then
    echo "Image '${LOCAL_IMAGE_TAG}' not found locally. Attempting to pull from Docker Hub..."
    sudo docker pull ${DOCKER_IMAGE_NAME}
    if [ $? -ne 0 ]; then
        echo "Error: Failed to pull Docker image. Please check your internet connection or Docker Hub login."
        exit 1
    fi
    sudo docker tag ${DOCKER_IMAGE_NAME} ${LOCAL_IMAGE_TAG}
else
    echo "Image '${LOCAL_IMAGE_TAG}' found locally. Skipping pull."
fi

# Define host path
HOST_REPO_PATH=$(pwd)
# Define container path
CONTAINER_REPO_PATH=/app/cv4gt_repo

echo "--- Stopping and removing any existing Docker containers for a clean start ---"
sudo docker stop $(sudo docker ps -aq) > /dev/null 2>&1
sudo docker rm $(sudo docker ps -aq) > /dev/null 2>&1
echo "Cleaned up old containers."

echo "--- Launching Docker container ---"
DOCKER_RUN_CMD="sudo docker run -it --rm --gpus all "
DOCKER_RUN_CMD+="-v \"${HOST_REPO_PATH}:${CONTAINER_REPO_PATH}\" "
DOCKER_RUN_CMD+="-e DISPLAY=\"${DISPLAY}\" -v /tmp/.X11-unix:/tmp/.X11-unix "

if [ -n "$HOST_DATA_INPUT" ]; then
    DOCKER_RUN_CMD+="-v \"${HOST_DATA_INPUT}:${CONTAINER_DATA_INPUT}\" "
fi
if [ -n "$HOST_DATA_OUTPUT" ]; then
    DOCKER_RUN_CMD+="-v \"${HOST_DATA_OUTPUT}:${CONTAINER_DATA_OUTPUT}\" "
fi

DOCKER_RUN_CMD+="${LOCAL_IMAGE_TAG} /bin/bash"

# Execute the command
eval "$DOCKER_RUN_CMD"

echo "--- Docker container exited ---"
echo "Remember to stop your X server (VcXsrv) if you no longer need it."