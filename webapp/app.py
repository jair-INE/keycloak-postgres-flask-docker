import os

from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, render_template, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

# Keycloak queda detrás de la red de Docker. El navegador del usuario y el
# backend Flask lo alcanzan por hostnames distintos, PERO para que la
# validación del id_token funcione el 'issuer' debe coincidir en ambos lados.
#
# Solución: fijamos KC_HOSTNAME=http://localhost:8080 en Keycloak, de modo que
# el issuer de los tokens sea siempre 'http://localhost:8080/realms/demo'.
# Desde el contenedor de la webapp alcanzamos ese mismo 'localhost:8080' vía
# host.docker.internal (el puerto 8080 está publicado en el host).
#
# ISSUER        -> valor del claim 'iss' en los tokens (lo que ve el navegador)
# METADATA_HOST -> host que el backend usa para descargar la metadata/JWKS/token
ISSUER = os.environ.get("OIDC_ISSUER", "http://localhost:8080/realms/demo")
METADATA_URL = os.environ.get(
    "OIDC_METADATA_URL",
    "http://host.docker.internal:8080/realms/demo/.well-known/openid-configuration",
)
CLIENT_ID = os.environ.get("OIDC_CLIENT_ID", "flask-app")
CLIENT_SECRET = os.environ.get("OIDC_CLIENT_SECRET", "flask-app-secret")

oauth = OAuth(app)
oauth.register(
    name="keycloak",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url=METADATA_URL,
    client_kwargs={"scope": "openid profile email"},
)


def _rewrite_to_public(url: str) -> str:
    """La metadata descubierta apunta a host.docker.internal; el navegador
    debe ir a localhost. Reescribimos solo el host en URLs de navegador."""
    return url.replace("http://host.docker.internal:8080", "http://localhost:8080")


@app.route("/")
def index():
    return render_template("index.html", user=session.get("user"))


@app.route("/login")
def login():
    redirect_uri = url_for("auth", _external=True)
    resp = oauth.keycloak.authorize_redirect(redirect_uri)
    # El Location apunta al authorize endpoint interno; lo mandamos al público.
    resp.headers["Location"] = _rewrite_to_public(resp.headers["Location"])
    return resp


@app.route("/auth")
def auth():
    token = oauth.keycloak.authorize_access_token()
    userinfo = token.get("userinfo") or oauth.keycloak.userinfo(token=token)
    session["user"] = dict(userinfo)
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    end_session = (
        f"{ISSUER}/protocol/openid-connect/logout"
        f"?post_logout_redirect_uri={url_for('index', _external=True)}"
        f"&client_id={CLIENT_ID}"
    )
    return redirect(end_session)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
