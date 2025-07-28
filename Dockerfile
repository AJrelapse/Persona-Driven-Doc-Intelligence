FROM python:3.10

WORKDIR /app

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir \
    torch==2.1.2+cpu \
    torchvision==0.16.2+cpu \
    torchaudio==2.1.2+cpu \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir \
    PyMuPDF==1.23.7 \
    numpy==1.26.0 \
    scikit-learn==1.4.0 \
    nltk==3.8.1 \
    huggingface_hub==0.12.1 \
    sentence-transformers==2.2.2

COPY . .

CMD ["python", "main.py"]
