import os
import sqlite3
import time

from flask import Flask, g, jsonify, redirect, render_template_string, request, url_for
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)

app = Flask(__name__)
app.config["DATABASE"] = os.environ.get(
        "DATABASE_PATH",
        os.path.join(app.instance_path, "counter.sqlite3"),
)
os.makedirs(app.instance_path, exist_ok=True)

PAGE = """
<!doctype html>
<html lang="fr">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Compteur</title>
    </head>
    <body>
        <main>
            <h1>Compteur</h1>
            <p id="counter-value">{{ value }}</p>
            <form action="{{ url_for('increment') }}" method="post">
                <button type="submit">Incrémenter</button>
            </form>
            <form action="{{ url_for('decrement') }}" method="post">
                <button type="submit">Décrémenter</button>
            </form>
        </main>
    </body>
</html>
"""


# Compteur des requêtes HTTP (pour monitoring)
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests received",
    labelnames=("method", "endpoint", "status"),
)


# Histogramme de la durée des requêtes HTTP (pour monitoring)
request_duration_seconds = Histogram(
    "request_duration_seconds",
    "HTTP request processing time in seconds",
    labelnames=("method", "endpoint", "status"),
)


def initialize_database():
    database_path = app.config["DATABASE"]
    os.makedirs(os.path.dirname(os.path.abspath(database_path)), exist_ok=True)
    connection = sqlite3.connect(database_path)
    try:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS counter ("
            "id INTEGER PRIMARY KEY CHECK (id = 1), "
            "value INTEGER NOT NULL)"
        )
        connection.execute(
            "INSERT OR IGNORE INTO counter (id, value) VALUES (1, 0)"
        )
        connection.commit()
    finally:
        connection.close()


def get_counter_value():
    connection = sqlite3.connect(app.config["DATABASE"])
    try:
        result = connection.execute(
            "SELECT value FROM counter WHERE id = 1"
        ).fetchone()
        return result[0]
    finally:
        connection.close()


def change_counter(amount):
    connection = sqlite3.connect(app.config["DATABASE"])
    try:
        connection.execute(
            "UPDATE counter SET value = MAX(0, value + ?) WHERE id = 1",
            (amount,),
        )
        connection.commit()
    finally:
        connection.close()


@app.before_request
def start_timer():
    g.request_started_at = time.perf_counter()


@app.after_request
def record_request(response):
    if request.path != "/metrics":
        labels = {
            "method": request.method,
            "endpoint": request.path,
            "status": str(response.status_code),
        }
        http_requests_total.labels(**labels).inc()
        request_duration_seconds.labels(**labels).observe(
            time.perf_counter() - g.request_started_at
        )
    return response


@app.get("/")
def count():
    return render_template_string(PAGE, value=get_counter_value())


# Fonction d'incrémentation du compteur
@app.post("/increment")
def increment():
    change_counter(1)
    return redirect(url_for("count"))


# Fonction de décrémentation du compteur
@app.post("/decrement")
def decrement():
    change_counter(-1)
    return redirect(url_for("count"))


# Endpoint health de l'application
@app.get("/health")
def health():
    try:
        get_counter_value()
    except sqlite3.Error:
        return jsonify(status="unavailable", dependency="sqlite"), 503
    return jsonify(status="ok"), 200


# Endpoint metrics (pour monitoring)
@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


# Endpoint pour générer erreurs
@app.get("/test-error")
def simulate_error():
    return jsonify(error="test error"), 500


if __name__ == "__main__":
    initialize_database()
    app.run(debug=False)


initialize_database()


def test_counter_buttons_update_database(tmp_path, monkeypatch):
    monkeypatch.setitem(
        app.config,
        "DATABASE",
        str(tmp_path / "counter.sqlite3"),
    )
    initialize_database()

    with app.test_client() as client:
        page = client.get("/")
        assert page.status_code == 200
        assert b"Incr\xc3\xa9menter" in page.data
        assert b"D\xc3\xa9cr\xc3\xa9menter" in page.data
        assert b"<p id=\"counter-value\">0</p>" in page.data

        response = client.post("/increment", follow_redirects=True)
        assert response.status_code == 200
        assert b"<p id=\"counter-value\">1</p>" in response.data

        response = client.post("/decrement", follow_redirects=True)
        assert response.status_code == 200
        assert b"<p id=\"counter-value\">0</p>" in response.data


def test_health_metrics_and_test_error_endpoints():
    with app.test_client() as client:
        health_response = client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json == {"status": "ok"}

        error_response = client.get("/test-error")
        assert error_response.status_code == 500
        assert error_response.json == {"error": "test error"}

        metrics = client.get("/metrics").get_data(as_text=True)
        assert "http_requests_total" in metrics
        assert 'endpoint="/test-error"' in metrics
        assert 'status="500"' in metrics
