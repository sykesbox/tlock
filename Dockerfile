# Use an official Python runtime
FROM python:3.10

# Install system dependencies required for charm-crypto
RUN apt update && apt install -y libgmp-dev libmpfr-dev libmpc-dev

# Set the working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install git+https://github.com/JHUISI/charm.git

# Expose the port Render uses
EXPOSE 10000

# Command to run the app
CMD ["gunicorn", "time_lock_api:app", "--workers", "3", "--bind", "0.0.0.0:10000"]
