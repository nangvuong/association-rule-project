FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements_web.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements_web.txt

COPY . .

EXPOSE 5000
CMD ["python", "web/app.py"]
