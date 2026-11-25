#!/usr/bin/env bash
# Instala o actualiza cocina-peruana-ar en la VM. Uso: cd ~/cocina-peruana && ./deploy/desplegar-vm.sh
set -euo pipefail

ZIP="${ZIP:-$HOME/cocina-dist.zip}"
DOMINIO="${DOMINIO:-cocinaperuanaar.duckdns.org}"
CADDY="${CADDY:-movifi-web-1}"
cd "$(dirname "$0")/.."

echo "== Disco y memoria"
df -h / | tail -1
free -h | sed -n 1,2p
libre=$(df --output=avail -m / | tail -1 | tr -d ' ')
if [ "$libre" -lt 600 ]; then
  echo "Menos de 600 MB libres, se limpia la cache de construccion"
  docker builder prune -f
fi

echo "== Comprobaciones previas"
[ -f "$ZIP" ] || { echo "Falta $ZIP, subelo con el engranaje del SSH"; exit 1; }
[ -f .env ] || { echo "Falta .env, copia .env.example y pon GEMINI_API_KEY"; exit 1; }
grep -q '^GEMINI_API_KEY=.\+' .env || { echo "GEMINI_API_KEY vacia en .env"; exit 1; }
docker network inspect edge >/dev/null 2>&1 || docker network create edge
docker inspect "$CADDY" >/dev/null 2>&1 || { echo "No existe el contenedor $CADDY"; exit 1; }
getent hosts "$DOMINIO" >/dev/null || echo "Aviso: $DOMINIO no resuelve todavia, crea el subdominio en DuckDNS con la IP de la VM"

echo "== Codigo"
if [ -d .git ]; then
  git pull --ff-only
  git log --oneline -1
fi

echo "== Frontend compilado"
rm -rf frontend/dist
python3 -m zipfile -e "$ZIP" frontend/
[ -f frontend/dist/frontend/browser/index.html ] || { echo "El zip no trae dist/frontend/browser"; exit 1; }

echo "== Contenedores"
docker compose -f docker-compose.vm.yml up -d --build

echo "== Caddy"
docker network connect edge "$CADDY" 2>/dev/null || true
docker cp "$CADDY":/etc/caddy/Caddyfile /tmp/Caddyfile.actual
if grep -q "$DOMINIO" /tmp/Caddyfile.actual; then
  echo "El bloque de $DOMINIO ya existe"
else
  cp /tmp/Caddyfile.actual "$HOME/Caddyfile.respaldo-$(date +%F-%H%M)"
  cat >> /tmp/Caddyfile.actual <<EOF

$DOMINIO {
    reverse_proxy cocina-web:80
}
EOF
  docker cp /tmp/Caddyfile.actual "$CADDY":/etc/caddy/Caddyfile
  docker exec "$CADDY" caddy validate --config /etc/caddy/Caddyfile
  docker exec "$CADDY" caddy reload --config /etc/caddy/Caddyfile
fi

echo "== Espera del backend"
for i in $(seq 1 30); do
  curl -fsS http://127.0.0.1:8082/api/salud >/dev/null 2>&1 && break
  sleep 2
done
curl -fsS http://127.0.0.1:8082/api/salud || { docker logs --tail 40 cocina-backend; exit 1; }
echo
curl -s http://127.0.0.1:8082/api/platos | head -c 200
echo

echo "== Publico, el certificado tarda unos segundos"
sleep 10
curl -s -o /dev/null -w "cocina %{http_code}\n" "https://$DOMINIO/api/salud" || true
curl -s -o /dev/null -w "documind %{http_code}\n" https://documindcloud.duckdns.org/api/health || true
curl -s -o /dev/null -w "movifi %{http_code}\n" https://movifi.duckdns.org/api/health || true
curl -sI "https://$DOMINIO/modelos/causa-limena/paso-1.glb" | grep -i -E "HTTP|content-type" || true
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -E 'cocina|documind|movifi|NAMES' || true
