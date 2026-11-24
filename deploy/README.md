# Despliegue en la VM compartida

Misma arquitectura que DocuMind: el Caddy de MoviFi publica 80 y 443 y pasa el tráfico a `cocina-web` por la red externa `edge`. El backend queda en la red interna, sin puertos.

## Antes
- Subdominio en DuckDNS, por ejemplo `cocinaperuana`, con la IP de la VM.
- `npm run build` en `frontend/` y `zip -r cocina-dist.zip dist/frontend/browser`.
- Subir el zip a `~/cocina-dist.zip` con el engranaje del SSH.
- Commit y push de `docker-compose.vm.yml`, `frontend/Dockerfile.prebuilt` y `deploy/`.

## En la VM
```bash
cd ~ && git clone https://github.com/CristopherVQ1024/cocina-peruana-ar.git cocina-peruana
cd cocina-peruana
cp .env.example .env && nano .env     # GEMINI_API_KEY
./deploy/desplegar-vm.sh
```

Actualizar: subir el zip nuevo y `cd ~/cocina-peruana && ./deploy/desplegar-vm.sh`.

No renombrar `~/cocina-peruana`. No construir dos proyectos a la vez.
