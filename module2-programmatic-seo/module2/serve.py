# ============================================================
# FLASK WEB SERVER - View your generated pages in browser
# ============================================================
# Flask is a mini web server
# It "serves" your HTML files at http://localhost:5000

from flask import Flask, send_from_directory, render_template_string
import os

# Create Flask app
# __name__ tells Flask this is the main file
app = Flask(__name__)

# Where are our generated files?
OUTPUT_DIR = "output"

@app.route('/')
def index():
    """
    When user visits http://localhost:5000
    Show the index page
    """
    return send_from_directory(OUTPUT_DIR, 'index.html')


@app.route('/<filename>')
def serve_file(filename):
    """
    When user visits http://localhost:5000/web-design-chennai.html
    Serve that specific file
    
    '<filename>' is a VARIABLE - it captures whatever comes after /
    """
    return send_from_directory(OUTPUT_DIR, filename)


# Start the server
if __name__ == '__main__':
    print("🌐 Starting Flask server...")
    print("📂 Serving files from:", OUTPUT_DIR)
    print("🔗 Open browser: http://localhost:5000")
    print("Press Ctrl+C to stop")
    
    # debug=True means: auto-reload when you change code
    app.run(debug=True, port=5000)