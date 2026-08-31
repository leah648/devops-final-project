from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "Hello World", 200

    @app.route('/health')
    def health():
        return jsonify(status="healthy"), 200

    return app


# Expose a module-level WSGI app for WSGI servers (gunicorn)
app = create_app()

if __name__ == '__main__':
    # Run for local development only. In production use a WSGI server (gunicorn).
    app.run(host='0.0.0.0', port=5000)
