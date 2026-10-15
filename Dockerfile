# Start from a small official Python image
FROM python:3.12-slim
# Work inside /app in the image
WORKDIR /app
# Copy the dependency list first, then install it
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy the app code
COPY app.py .
# Document the port the app listens on
EXPOSE 5000
# The command that starts the app
CMD ["python", "app.py"]
