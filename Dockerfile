# Use Python 3.8 as the base image
FROM python:3.8-slim

# Set timezone
ENV TZ=America/Denver

# Set working directory
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV PPLX_API_KEY=$PPLX_API_KEY
ENV DISCORD_TOKEN=$DISCORD_TOKEN

# Command to run the main script
CMD ["python", "main.py"]