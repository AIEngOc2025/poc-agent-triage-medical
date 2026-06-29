# 1. Image de base légère (Debian Bookworm slim)
FROM python:3.12-slim-bookworm

# 2. Installation de l'orchestrateur 'uv' (Standard 2026)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 3. Définition des variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

# 4. Copie des fichiers de configuration
COPY pyproject.toml uv.lock ./

# 5. Installation des dépendances de production 
# Note : En Docker/Linux, uv installera la version standard de vLLM (CUDA ou CPU)
RUN uv sync --frozen --no-cache --no-dev

# 6. Copie du code source et du modèle fusionné
COPY src/ ./src/
COPY models/merged_final_dpo_chsa/ ./models/merged_final_dpo_chsa/
COPY logs/ ./logs/

# 7. Exposition du port de l'agent
EXPOSE 8000

# 8. Lancement de l'API via le venv de uv
# On force le mode CPU dans Docker pour la portabilité, 
# sauf si un GPU NVIDIA est présent.
CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]# Utilisation d'une image légère
FROM python:3.12-slim

# Installation de uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Définition du répertoire de travail
WORKDIR /app

# Copie des fichiers de configuration
COPY pyproject.toml uv.lock ./

# Installation des dépendances (sans installer le projet lui-même)
RUN uv sync --frozen --no-cache

# Copie du code source et du modèle
COPY src/ ./src/
COPY models/chsa_model_dpo_final/ ./models/chsa_model_dpo_final/
COPY logs/ ./logs/

# Exposition du port API
EXPOSE 8000

# Commande de lancement via uv (plus sécurisé et gère le venv)
CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
