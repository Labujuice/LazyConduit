# Use the mavros-jazzy image as base
FROM mavros-jazzy:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-tk \
    python3-opencv \
    python3-numpy \
    libgl1 \
    libglib2.0-0 \
    libcanberra-gtk-module \
    libcanberra-gtk3-module \
    build-essential \
    ros-jazzy-cv-bridge \
    ros-jazzy-sensor-msgs \
    ros-jazzy-std-msgs \
    && rm -rf /var/lib/apt/lists/*

# Install Python project dependencies (PEP 668 override)
RUN pip3 install --no-cache-dir --break-system-packages \
    requests \
    pymupdf \
    python-docx \
    odfpy \
    markdown \
    tkhtmlview

# Set working directory
WORKDIR /app

# Copy the project into the container
COPY . .

# Setup ROS2 workspace sourcing
RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc

# Entrypoint
CMD ["bash"]
