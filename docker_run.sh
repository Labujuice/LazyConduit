#!/bin/bash

# Allow Docker to access X11
xhost +local:docker

# Build the image if not exists
docker build -t lazy_conduit:jazzy .

# Run the container
docker run -it --rm \
    --name lazy_conduit_container \
    --net=host \
    --privileged \
    -e DISPLAY=$DISPLAY \
    -e OLLAMA_HOST=http://localhost:11434 \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $(pwd):/app \
    -v /home/kenny/Pictures:/app/assets \
    lazy_conduit:jazzy
