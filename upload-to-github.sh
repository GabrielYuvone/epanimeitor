#!/usr/bin/env bash
# Subir Epanimeitor a GitHub — script de un solo paso
# Repo destino: https://github.com/GabrielYuvone/epanimeitor
set -e

REMOTE_URL="https://github.com/GabrielYuvone/epanimeitor.git"

echo "=== Epanimeitor — push a GitHub ==="
echo ""

# 1. Verificar que estamos en un repo git
if [ ! -d .git ]; then
  echo "✗ No estás en un repo git. Extraí epanimeitor-repo.tar.gz primero:"
  echo "    tar -xzf epanimeitor-repo.tar.gz"
  echo "    cd epanimeitor"
  echo "    ./upload-to-github.sh"
  exit 1
fi

# 2. Configurar el remote
if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "$REMOTE_URL"
else
  git remote set-url origin "$REMOTE_URL"
fi
echo "✓ Remote configurado: $REMOTE_URL"

# 3. Instalar dependencias (opcional, solo si vas a correr el proyecto)
if command -v bun >/dev/null 2>&1; then
  echo "→ Instalando dependencias con bun…"
  bun install 2>/dev/null || echo "  (omitido: podés correr bun install después)"
elif command -v npm >/dev/null 2>&1; then
  echo "→ Instalando dependencias con npm…"
  npm install 2>/dev/null || echo "  (omitido: podés correr npm install después)"
fi

# 4. Push
echo ""
echo "→ Haciendo push a main…"
echo "  Git te va a pedir USUARIO y CONTRASEÑA."
echo "  - Usuario: tu usuario de GitHub (GabrielYuvone)"
echo "  - Contraseña: un Personal Access Token NUEVO (no el que filtraste antes)"
echo "    Generá uno acá: https://github.com/settings/tokens/new?scopes=repo"
echo ""
echo "  (mejor opción: SSH — ver https://docs.github.com/es/authentication/connecting-to-github-with-ssh)"
echo ""

git push -u origin main

echo ""
echo "✓ Listo. Tu repo está en: https://github.com/GabrielYuvone/epanimeitor"
echo ""
echo "Para correr la app localmente:"
echo "  bun run dev   (o: npm run dev)"
echo "  Abrí http://localhost:3000"
