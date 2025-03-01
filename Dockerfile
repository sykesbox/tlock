FROM python:3.10

# Install system dependencies
RUN apt update && apt install -y libgmp-dev libmpfr-dev libmpc-dev

# Set the working directory
WORKDIR /app

# Copy the project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 10000

# Start the application
CMD ["gunicorn", "time_lock_api:app", "--workers", "3", "--bind", "0.0.0.0:10000"]
