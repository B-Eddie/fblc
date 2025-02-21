# Use Python 3.12 as the base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install Node.js and npm for Tailwind CSS
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy package files first
COPY package.json .
COPY package-lock.json .

# Install only Tailwind CSS and its dependencies
RUN npm install -D tailwindcss@latest postcss@latest autoprefixer@latest

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Initialize Tailwind CSS if config doesn't exist
RUN npx tailwindcss init -p

# Create the CSS build script in package.json
ENV PORT=32771 

# Expose the port
EXPOSE 32771

# Run the application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=32771"]