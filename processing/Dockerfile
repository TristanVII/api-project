# Base Image
FROM python:3.11

# Work directory
WORKDIR /processing/

# Install dependencies
COPY . .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt


# Expose port 
EXPOSE 8100


# Start instructions (adjust if needed)
CMD ["py", "app.py"] 