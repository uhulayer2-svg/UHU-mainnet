from flask import Flask, render_template_string
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>UHU Pulse Explorer</title>
    <style>
        body { background: #0f172a; color: #38bdf8; font-family: sans-serif; padding: 40px; }
        .container { max-width: 800px; margin: auto; background: #1e293b; padding: 30px; border-radius: 15px; border: 1px solid #334155; }
        h1 { color: #f8fafc; border-bottom: 2px solid #38bdf8; padding-bottom: 10px; }
        .status { color: #4ade80; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>UHU Pulse Chain Explorer <span class="status">● ONLINE</span></h1>
        <p>Network: <strong>UHU Mainnet</strong> | Chain ID: <strong>8844</strong></p>
        <p>Status: Monitoring Live Transactions...</p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
