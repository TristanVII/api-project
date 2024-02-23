# Base Image
FROM python:3.11

# Work directory
WORKDIR /storage/

# Install dependencies
COPY . .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt


# Expose port 
EXPOSE 8090


# Start instructions (adjust if needed)
CMD ["python3", "app.py"] 