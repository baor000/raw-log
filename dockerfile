# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV MONGODB_CONNECTION_STRING=<your-connection-string>
ENV MONGODB_DATABASE_NAME=<your-database-name>
ENV MONGODB_COLLECTION_NAME=<your-collection-name>

# Expose port 5000 for the Flask app
EXPOSE 5000

# Run the command to start the Flask app
CMD ["python", "main.py"]
