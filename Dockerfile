# Use Python as base image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (modify if necessary)
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
