# Keycloak + PostgreSQL + App web (Flask) con Docker Compose

Aplicación web en Python (Flask) que se autentica contra
[Keycloak](https://www.keycloak.org/) mediante OpenID Connect (flujo
Authorization Code), con Keycloak respaldado por una base de datos PostgreSQL.
Los tres servicios corren en contenedores.

## Arquitectura

```
┌──────────────┐   OIDC    ┌──────────────┐        ┌──────────────┐
│  Flask web   │ ────────► │   Keycloak   │ ─────► │  PostgreSQL  │
│  :5000       │           │  :8080       │  JDBC  │  :5432       │
└──────────────┘           └──────────────┘        └──────────────┘
                   red interna: keycloak-net
```

- **webapp**: app Flask (Authlib) en el puerto 5000. Inicia sesión vía Keycloak.
- **keycloak**: servidor de identidad (puerto 8080). Importa el realm `demo`
  al primer arranque.
- **postgres**: base de datos persistente (volumen `postgres_data`), no expuesta
  al host.

## Requisitos

- Docker Engine 20.10+
- Docker Compose v2 (`docker compose ...`)

## Configuración

Las variables están en `.env`. **Cambia las contraseñas y secretos** antes de
usar esto fuera de pruebas locales:

| Variable                   | Descripción                                 |
|----------------------------|---------------------------------------------|
| `POSTGRES_DB`              | Nombre de la base de datos                   |
| `POSTGRES_USER`           | Usuario de PostgreSQL                         |
| `POSTGRES_PASSWORD`       | Contraseña de PostgreSQL                      |
| `KEYCLOAK_ADMIN`          | Usuario admin inicial de Keycloak             |
| `KEYCLOAK_ADMIN_PASSWORD` | Contraseña del admin inicial de Keycloak      |
| `FLASK_SECRET_KEY`        | Clave para firmar la sesión de Flask          |
| `OIDC_CLIENT_ID`          | Client ID en Keycloak (`flask-app`)           |
| `OIDC_CLIENT_SECRET`      | Secret del cliente (debe coincidir con el realm) |

> El client secret vive en dos sitios: en `.env` (lo usa la webapp) y en
> `realm/demo-realm.json` (lo usa Keycloak). Si cambias uno, cambia el otro.

## Qué se crea automáticamente

El realm `demo` se importa al arrancar Keycloak (`--import-realm`) e incluye:

- Cliente **`flask-app`** (confidential), redirect URI `http://localhost:5000/*`.
- Usuario de prueba: **`demo`** / contraseña **`demo`**.

## Uso

```bash
docker compose up -d --build
```

Sigue el arranque de Keycloak (la primera vez tarda, importa el realm):

```bash
docker compose logs -f keycloak
```

Cuando Keycloak esté listo:

1. Abre la app: http://localhost:5000
2. Clic en **Iniciar sesión con Keycloak**.
3. Entra con `demo` / `demo`.
4. Vuelves a la app y verás los claims de tu usuario.

Consola de administración de Keycloak:

- URL: http://localhost:8080
- Usuario / contraseña: `KEYCLOAK_ADMIN` / `KEYCLOAK_ADMIN_PASSWORD`.

Detener (conserva datos):

```bash
docker compose down
```

Detener y **borrar** la BD y el realm importado (empezar de cero):

```bash
docker compose down -v
```

## Cómo se resuelve el "issuer" tras Docker

El navegador llega a Keycloak por `http://localhost:8080`, pero el contenedor
de la webapp no puede usar ese `localhost`. Para que el `issuer` de los tokens
sea consistente:

- Keycloak fija el frontend con `KC_HOSTNAME=http://localhost:8080`, así el
  `iss` de los tokens es siempre `http://localhost:8080/realms/demo`.
- `KC_HOSTNAME_BACKCHANNEL_DYNAMIC=true` permite que los endpoints de
  backchannel (token, userinfo, jwks) se resuelvan según el host de la petición.
- La webapp descubre la metadata vía `host.docker.internal:8080` (el puerto
  8080 publicado en el host), y reescribe solo la URL de *authorize* del
  navegador a `localhost:8080`.

## Comprobar el estado

```bash
docker compose ps
curl http://localhost:8080/health/ready
curl http://localhost:5000
```

## Notas

- Keycloak usa `start-dev` (modo **desarrollo**, sin HTTPS). Para producción:
  `start` con HTTPS, `KC_HOSTNAME` real y build optimizado.
- En Keycloak 26 el admin inicial se crea con
  `KC_BOOTSTRAP_ADMIN_USERNAME` / `KC_BOOTSTRAP_ADMIN_PASSWORD`.
- `host.docker.internal` funciona en Docker Desktop (Windows/Mac) y, en el
  compose, se mapea con `extra_hosts: host-gateway` para Linux.
