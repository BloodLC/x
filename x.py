from flask import Flask
import subprocess

app = Flask(__name__)

@app.route("/open_calc")
def open_calc():
    try:
        subprocess.Popen("calc.exe")  # Abre la calculadora
        return "✅ Calculator opened successfully!"
    except Exception as e:
        return f"❌ Error: {e}"

@app.route("/")
def index():
    return "Server is running. Go to /open_calc to open Calculator."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
