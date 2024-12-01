# Use Python slim image as base
FROM python:3.11.0-slim-buster

# Install required dependencies
RUN apt-get update && apt-get install -y \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama in the background and ensure it runs properly
RUN nohup ollama start & \
    sleep 5 && \
    ollama run llama3.2:1b && \
    kill $(pgrep ollama)

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Start Ollama and FastAPI server
CMD ["sh", "-c", "ollama serve & uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]
