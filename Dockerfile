FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY bridge.py scorer.py report.py run_suite.py server.py compare.py ./
COPY attacks/ attacks/
COPY targets/ targets/
COPY evidence/ evidence/
ENV PORT=8080
EXPOSE 8080
CMD ["python", "server.py"]
