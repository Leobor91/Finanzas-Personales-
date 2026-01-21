Despliegue en Render con imagen Docker (GitHub Actions)

Resumen rápido
- El workflow `.github/workflows/docker-publish.yml` construye y publica la imagen a Docker Hub cuando haces push a `main` o `master`.
- En Render puedes usar esa imagen (pública o privada) para crear un servicio Docker sin necesidad de que Render construya desde el repo.

Pasos para configurar Docker Hub + GitHub Actions
1. Crea un repositorio en Docker Hub, por ejemplo `youruser/finanzas-personales`.
2. Crea un token en Docker Hub: Account > Security > New Access Token. Copia el token.
3. En GitHub del repo ve a `Settings > Secrets > Actions` y añade:
   - `DOCKERHUB_USERNAME` = tu usuario de Docker Hub
   - `DOCKERHUB_TOKEN` = el token generado
4. Haz push a `main` o `master` y verifica la ejecución del workflow en `Actions`.

Usar la imagen en Render (imagen pública o privada)
Opción A — Imagen pública (más simple):
- En Render: New > Web Service > Docker
- Registry: Docker Hub
- Image: `youruser/finanzas-personales:latest`
- Start Command: `gunicorn "src.app:app" --bind 0.0.0.0:$PORT --workers 2`
- Definir variables de entorno (ENV) en Render: `FLASK_ENV=production`, `DATABASE_URL` si migras a Postgres.

Opción B — Imagen privada:
- Conecta Render a Docker Hub con credenciales en el panel de Render (Add Registry), o deja la imagen pública.
- En Render añade el servicio apuntando a la imagen privada.

Ejemplo de manifest (opcional) — `render-image-example.yaml`
(este archivo es solo un ejemplo para referencia; Render lo puede usar si configuras integration con repo)

```yaml
services:
  - type: web
    name: FinanzasPersonales-Image
    env: docker
    plan: starter
    image: youruser/finanzas-personales:latest
    envVars:
      - key: FLASK_ENV
        value: production
      - key: DATABASE_URL
        value: postgres://user:pass@host:5432/dbname
```

Notas sobre la base de datos
- Actualmente la app usa SQLite (`finance_app.db`) en el working dir. En Render esto es efímero.
- Para producción usa Postgres: crea un servicio Postgres en Render y actualiza `DATABASE_URL`.
- Puedo ayudarte a adaptar la app para leer `DATABASE_URL` y usar Postgres si lo deseas.

Comandos alternativos (con Docker local)
```bash
# Build y tag manual
docker build -t youruser/finanzas-personales:latest .
# Login y push
docker login --username youruser
docker push youruser/finanzas-personales:latest
# Run local
docker run -p 8000:8000 youruser/finanzas-personales:latest
```

Si quieres que actualice `render.yaml` para apuntar directamente a la imagen (en lugar de build desde repo), dime la imagen (p. ej. `youruser/finanzas-personales:latest`) y lo actualizo.
