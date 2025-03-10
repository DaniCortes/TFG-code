# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the src directory contents into the container at /app/src
COPY src/ ./src/

# Expose the port the service runs on
EXPOSE 8000

# Run app.py when the container launches
CMD ["uvicorn", "src.main:app", "--log-level", "trace", "--host", "0.0.0.0", "--port", "8000"]