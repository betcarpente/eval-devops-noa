FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR /app

COPY config/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
	&& useradd --create-home --shell /usr/sbin/nologin appuser \
	&& mkdir -p /app/instance \
	&& chown -R appuser:appuser /app

COPY --chown=appuser:appuser app.py ./app.py

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
	CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health')"

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
