# Use this version because it supports GPU with nvidia-driver-535 and above
FROM tensorflow/tensorflow:2.14.0-gpu

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port
EXPOSE 8080

# Run the application
CMD ["python", "src/main.py"]
