# Use Python 3.12 as the base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install Node.js and npm for Tailwind CSS
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy package.json and install Node dependencies
COPY package.json .
COPY package-lock.json .
RUN npm install

# Copy the rest of the application
COPY . .

# Build Tailwind CSS
RUN npm run build

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=32771 

# Expose the port
EXPOSE 32771

# Run the application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=32771"]