from flask import Flask, request, render_template_string, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = "cambiar_por_algo_secreto"  # necesario para flash

# Reemplazá por tu webhook solo si estás probando con consentimiento
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/..."


TEMPLATE = """
<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <title>Mostrar IP (con consentimiento)</title>
  </head>
  <body>
    <h1>Información sobre tu IP</h1>
    {% if data %}
      <ul>
        <li><strong>IP:</strong> {{ data.query }}</li>
        <li><strong>País:</strong> {{ data.country }} ({{ data.countryCode }})</li>
        <li><strong>Región:</strong> {{ data.regionName }}</li>
        <li><strong>Ciudad:</strong> {{ data.city }}</li>
        <li><strong>Latitud:</strong> {{ data.lat }}</li>
        <li><strong>Longitud:</strong> {{ data.lon }}</li>
        <li><strong>ISP:</strong> {{ data.isp }}</li>
        <li><strong>Proxy/VPN:</strong> {{ data.proxy }}</li>
      </ul>

      <form method="post" action="{{ url_for('send') }}">
        <input type="hidden" name="ip" value="{{ data.query }}">
        <input type="hidden" name="regionName" value="{{ data.regionName }}">
        <input type="hidden" name="city" value="{{ data.city }}">
        <input type="hidden" name="lat" value="{{ data.lat }}">
        <input type="hidden" name="lon" value="{{ data.lon }}">
        <input type="hidden" name="isp" value="{{ data.isp }}">
        <input type="hidden" name="proxy" value="{{ data.proxy }}">
        <button type="submit">Enviar estos datos al Discord (con mi consentimiento)</button>
      </form>
    {% else %}
      <p>No se pudo obtener información de la IP.</p>
    {% endif %}

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <ul>
          {% for msg in messages %}
            <li>{{ msg }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
  </body>
</html>
"""


@app.route("/")
def index():
    # Obtenemos la IP del visitante de la petición
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    # Consulta a ip-api con la IP para obtener geo info
    try:
        resp = requests.get(f"http://ip-api.com/json/{client_ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,proxy,query", timeout=5)
        data = resp.json()
        if data.get("status") != "success":
            data = None
    except Exception:
        data = None

    return render_template_string(TEMPLATE, data=data)


@app.route("/send", methods=["POST"])
def send():
    # Solo enviamos si el usuario hizo POST desde el formulario (consentimiento)
    payload = {
        "ip": request.form.get("ip"),
        "regionName": request.form.get("regionName"),
        "city": request.form.get("city"),
        "lat": request.form.get("lat"),
        "lon": request.form.get("lon"),
        "isp": request.form.get("isp"),
        "proxy": request.form.get("proxy"),
    }

    # Construimos el contenido que vamos a postear a Discord
    content = (
        f"**────────୨ৎ────────**\n"
        f"**IP:** {payload['ip']}\n"
        f"**Region:** {payload['regionName']}\n"
        f"**Ciudad:** {payload['city']}\n"
        f"**Latitud:** {payload['lat']}\n"
        f"**Longitud:** {payload['lon']}\n"
        f"**ISP:** {payload['isp']}\n"
        f"**VPN?:** {payload['proxy']}\n"
    )

    try:
        requests.post(DISCORD_WEBHOOK, json={
            "username": "Derpy Bot",
            "content": content
        }, timeout=5)
        flash("Datos enviados al Discord (gracias por tu consentimiento).")
    except Exception as e:
        flash(f"No se pudo enviar al webhook: {e}")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
