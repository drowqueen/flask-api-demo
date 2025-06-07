FROM python:3.9-slim
# Create non-root user
RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY app.py .
# Install dependencies as root, then clean up
RUN pip install --no-cache-dir flask flask-restful && \
    rm -rf /root/.cache/pip
# Switch to non-root user
USER appuser
EXPOSE 5001
CMD ["python", "app.py"]