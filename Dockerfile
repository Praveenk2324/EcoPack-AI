FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY src/ src/
COPY models/ models/
COPY data/raw/ data/raw/
COPY app.py .
COPY streamlit_app.py .

EXPOSE 8000
EXPOSE 8501

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port 8000 & streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]
