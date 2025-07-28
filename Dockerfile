FROM python:3.10

WORKDIR /app

RUN python -m pip install --upgrade pip && \
    pip config set global.timeout 100 && \
    pip config set global.retries 10 && \
    pip config set global.trusted-host pypi.org && \
    pip config set global.trusted-host files.pythonhosted.org

RUN pip install --no-cache-dir torch==2.1.2+cpu torchvision==0.16.2+cpu torchaudio==2.1.2+cpu \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir PyMuPDF==1.23.7
RUN pip install --no-cache-dir numpy==1.26.0
RUN pip install --no-cache-dir scikit-learn==1.4.0
RUN pip install --no-cache-dir nltk==3.8.1
RUN pip install --no-cache-dir huggingface_hub==0.13.4
RUN pip install --no-cache-dir sentence-transformers==2.2.2

COPY . .

CMD ["python", "main.py"]
