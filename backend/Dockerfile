# Use official Python image from Docker Hub
FROM python:3.12-slim

# Set environment variables to not generate .pyc files and disable buffering
ENV PYTHONUNBUFFERED=1

# Install PostgreSQL development libraries
RUN apt-get update \
    && apt-get install -y libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for the Django development server
EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
