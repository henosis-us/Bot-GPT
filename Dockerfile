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

# Set environment variables from vars.py
RUN python -c "import vars; import os; os.environ['OPENAI_API_KEY'] = vars.OPENAI_API_KEY; os.environ['PPLX_API_KEY'] = vars.PPLX_API_KEY; os.environ['DISCORD_TOKEN'] = vars.DISCORD_TOKEN"

# Command to run the main script
CMD ["python", "main.py"]