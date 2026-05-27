# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (curl for healthcheck, build-essential for some python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure outputs directory exists for generated reports
RUN mkdir -p outputs

# Ensure outputs directory exists for generated reports
RUN mkdir -p outputs

# Entrypoint will be handled by docker-compose commands

