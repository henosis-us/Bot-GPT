# Use Python 3.8 as the base image
FROM python:3.8

# Set environment variable for the database path (this will be mounted as an external volume)
ENV DATABASE_PATH data/protein_data.db

# Set timezone
ENV TZ=America/Denver

# Set working directory
WORKDIR /app

# Copy project files into the container (excluding the database)
COPY . /app

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the main script
CMD ["python", "main.py"]
