# Base Image
FROM python:3.11

# Work directory
WORKDIR /mock/

# Install dependencies
COPY . .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt


# Expose port 
EXPOSE 8999


# Start instructions (adjust if needed)
CMD ["python3", "app.py"] 