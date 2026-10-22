# Use a slim, official Python image as the base
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy ONLY the dependency file first (Docker caching trick — explained below)
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy the rest of the project
COPY . .

# The container's default job: run the test suite
CMD ["python", "-m", "pytest"]