FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY agents/ agents/
COPY config/ config/
COPY prompts/ prompts/
COPY schemas/ schemas/
COPY utils/ utils/
COPY api.py .
COPY main.py .

# Create data directories
RUN mkdir -p data/inputs data/outputs/images data/outputs/videos data/outputs/carousels data/outputs/scripts data/temp data/brand_assets logs

# Expose API port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
