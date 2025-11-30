"""
Keep-alive server for Replit.
Prevents the repl from sleeping by responding to HTTP pings.
"""

from flask import Flask, jsonify
from threading import Thread
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>StoicAlgo</title>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: #0a0a0a; 
                    color: #fff; 
                    display: flex; 
                    justify-content: center; 
                    align-items: center; 
                    height: 100vh; 
                    margin: 0;
                }
                .container { text-align: center; }
                h1 { font-size: 3rem; margin-bottom: 0.5rem; }
                p { color: #888; font-size: 1.2rem; }
                .status { 
                    display: inline-block; 
                    background: #1a472a; 
                    color: #4ade80; 
                    padding: 0.5rem 1rem; 
                    border-radius: 20px; 
                    margin-top: 1rem;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚡ StoicAlgo</h1>
                <p>Automated Instagram Wisdom Engine</p>
                <div class="status">🟢 Running</div>
            </div>
        </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "StoicAlgo",
        "timestamp": datetime.now().isoformat(),
        "message": "Scheduler is running"
    })

@app.route('/ping')
def ping():
    return "pong"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Start the keep-alive server in a background thread."""
    t = Thread(target=run)
    t.daemon = True
    t.start()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
