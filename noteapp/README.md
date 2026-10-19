# NoteApp

Aplicación web para guardar notas de texto. Escribes una nota, se almacena en PostgreSQL y aparece en la lista, de la más reciente a la más antigua.

La interfaz es una sola página: un formulario para crear notas y el listado de las que ya existen. `GET /health` responde `ok` cuando el proceso puede consultar la base de datos.

Está pensada para usarse en codelabs, pruebas de despliegue y ejercicios parecidos: una app pequeña, con persistencia y comprobación de salud, que se puede publicar con Docker Compose, un PaaS o un build pack. `READY_AFTER_SECONDS` permite simular un arranque lento sin cambiar la lógica de las notas.

## Ejecutar

Hace falta Docker con Compose.

```bash
docker compose up --build
```

Por defecto la app no publica puertos en el host. Para abrirla en local, agrega esto al servicio `web` en `docker-compose.yml`:

```yaml
ports:
  - "3000:3000"
```

Luego entra a [http://localhost:3000](http://localhost:3000).

## Variables

| Variable | Uso |
| --- | --- |
| `DATABASE_URL` | URL de PostgreSQL. Con Compose: `postgres://noteapp:noteapp@database:5432/noteapp` |
| `PORT` | Puerto del proceso. Por defecto `3000`. |
| `READY_AFTER_SECONDS` | Segundos tras el arranque en los que `/health` responde 500. `0` la deja lista en cuanto la base responde. |

La tabla `notes` se crea sola la primera vez que la app lee o guarda una nota.
