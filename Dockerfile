# Use this version because it supports GPU with nvidia-driver-535 and above
FROM nvidia/cuda:12.3.0-devel-ubuntu22.04

RUN apt update && apt install -y python3 python3-pip
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Copy the spacy config file
COPY config.cfg /app/config.cfg

# Install dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_trf

# Copy the rest of the application code
COPY . .

# Expose the port
EXPOSE 8080

# Run the application
CMD ["python", "src/main.py"]
