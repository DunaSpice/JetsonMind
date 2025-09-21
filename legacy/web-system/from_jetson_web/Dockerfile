FROM nvcr.io/nvidia/l4t-pytorch:r35.2.1-pth2.0-py3

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy application code
COPY . .

# Create swap directory
RUN mkdir -p /tmp/model_swap

# Expose port
EXPOSE 8000

# Run the server
CMD ["python3", "api_server.py", "--host", "0.0.0.0", "--port", "8000"]
