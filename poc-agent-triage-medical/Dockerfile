# --- Étape 1: Image de base avec CUDA ---
# Utilisation d'une image officielle NVIDIA pour garantir la compatibilité GPU.
# Python 3.12 est installé manuellement car il n'est pas disponible par défaut.
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# --- Étape 2: Installation des dépendances système et de Python 3.12 ---
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-venv \
    python3-pip \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Mise à jour des liens symboliques pour que 'python' et 'pip' pointent vers la version 3.12
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# --- Étape 3: Installation de 'uv' (gestionnaire de paquets) ---
RUN python -m pip install uv

# --- Étape 4: Configuration de l'environnement de l'application ---
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Variable pour activer la configuration de production dans config.py
ENV FASTAPI_CLOUD=true

WORKDIR /app

# --- Étape 5: Installation des dépendances Python ---
# Copier uniquement les fichiers de dépendances pour profiter du cache Docker.
# Cette couche ne sera reconstruite que si pyproject.toml change.
COPY pyproject.toml ./

# Installation des dépendances de production (sans les dépendances de dev)
RUN uv pip install --system --no-cache --no-deps -r pyproject.toml

# --- Étape 6: Copie du code source et des modèles ---
# Copier le reste de l'application.
COPY src/ ./src/
COPY models/merged_dpo_final_chsa/ ./models/merged_dpo_final_chsa/

# --- Étape 7: Exposition du port ---
# Le port de l'API est défini dans config.py comme 8001
EXPOSE 8001

# --- Étape 8: Commande de lancement ---
# Lancement de l'application avec Uvicorn. L'hôte 0.0.0.0 est crucial.
# Le port est récupéré depuis la configuration pour plus de cohérence.
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8001"]
