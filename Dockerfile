# Use Python 3.8 as the base image
FROM python:3.8

# Set environment variable for the database path (this will be mounted as an external volume)
ENV DATABASE_PATH data/protein_data.db

# Set timezone
ENV TZ=America/Denver
ARG OPENAI_API_KEY_FILE=vars.py
ARG PPLX_API_KEY_FILE=vars.py
ARG DISCORD_TOKEN_FILE=vars.py
RUN export OPENAI_API_KEY=$(grep 'OPENAI_API_KEY' $OPENAI_API_KEY_FILE | cut -d '"' -f 2) && \
    export PPLX_API_KEY=$(grep 'PPLX_API_KEY' $PPLX_API_KEY_FILE | cut -d '"' -f 2) && \
    export DISCORD_TOKEN=$(grep 'DISCORD_TOKEN' $DISCORD_TOKEN_FILE | cut -d '"' -f 2)
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV PPLX_API_KEY=${PPLX_API_KEY}
ENV DISCORD_TOKEN=${DISCORD_TOKEN}
# Set working directory
WORKDIR /app

# Copy project files into the container (excluding the database)
COPY . /app

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the main script
CMD ["python", "main.py"]
