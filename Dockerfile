FROM python:3.9-slim

# Install git and git-lfs
RUN apt-get update && apt-get install -y git git-lfs && git lfs install

# Set workdir
WORKDIR /app

# Copy everything
COPY . .

# Pull LFS files
RUN git lfs pull

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8080

# Start the server
CMD ["python", "annotation_server.py"] 