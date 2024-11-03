# Use this version because it supports GPU with nvidia-driver-535 and above
FROM nvidia/cuda:11.8.0-runtime-ubuntu20.04

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Copy the spacy config file
COPY config.cfg /app/config.cfg

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt 

RUN pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu118

# Add NVIDIA libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnvidia-ml-dev \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get install -y nvidia-docker2


RUN python -m spacy download en_core_web_trf

# Copy the rest of the application code
COPY . .

# Expose the port
EXPOSE 8080

# Run the application
RUN chmod +x src/main.py
CMD ["python", "src/main.py"]