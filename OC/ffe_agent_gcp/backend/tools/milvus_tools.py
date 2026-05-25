"""Module d'interrogation et d'initialisation de la base vectorielle Milvus."""

import os
from pymilvus import MilvusClient, MilvusException, DataType

MILVUS_URI = os.getenv("MILVUS_URI", "http://localhost:19530")
COLLECTION_NAME = "wikichess_openings"
DIMENSION = 384  # Dimension standard (ex: all-MiniLM-L6-v2) adaptée pour l'analyse locale


def query_wikichess(query: str) -> str:
    """Interroge la collection vectorielle Wikichess pour obtenir le contexte théorique.

    Cree la collection et son index si nécessaire (Idempotent).
    """
    try:
        # 1. Connexion au client Milvus
        client = MilvusClient(uri=MILVUS_URI, timeout=5.0)

        # 2. Création de la collection si elle n'existe pas
        if not client.has_collection(COLLECTION_NAME):
            # Définition du schéma pour avoir un contrôle strict (PEP8 & typage)
            schema = client.create_schema(auto_id=False, enable_dynamic_field=True)
            schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
            schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dimension=DIMENSION)
            schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
            schema.add_field(field_name="opening_name", datatype=DataType.VARCHAR, max_length=512)

            # Configuration de l'index de recherche (Requis par Milvus pour chercher)
            index_params = client.prepare_index_params()
            index_params.add_index(
                field_name="vector",
                index_type="IVF_FLAT",
                metric_type="COSINE",
                params={"nlist": 128}
            )

            client.create_collection(
                collection_name=COLLECTION_NAME,
                schema=schema,
                index_params=index_params
            )

            # Injection d'un jeu de données de référence sur la Najdorf
            mock_vector = [0.05] * DIMENSION  # Vecteur simulé pour le test
            client.insert(
                collection_name=COLLECTION_NAME,
                data=[{
                    "id": 1,
                    "vector": mock_vector,
                    "text": (
                        "La variante Najdorf de la Défense Sicilienne (5...a6) est l'une des "
                        "lignes les plus tranchantes des échecs. théorisée par Miguel Najdorf, elle "
                        "empêche les pièces blanches d'occuper les cases b5 et c4, tout en préparant "
                        "une expansion à l'aile Dame par b7-b5. C'est l'arme favorite de Kasparov et Fischer."
                    ),
                    "opening_name": "Sicilienne Najdorf"
                }]
            )

        # 3. Exécution de la recherche vectorielle
        # On simule l'embedding textuel de la requête par un vecteur test
        search_vector = [0.05] * DIMENSION
        
        # Chargement obligatoire en mémoire avant la recherche
        client.load_collection(COLLECTION_NAME)

        results = client.search(
            collection_name=COLLECTION_NAME,
            data=[search_vector],
            limit=1,
            output_fields=["text", "opening_name"]
        )

        if not results or not results[0]:
            return f"[Milvus] Aucune documentation trouvée dans le RAG pour '{query}'."

        entity = results[0][0]["entity"]
        return f"[RAG Wikichess - Base Documentaire] :\n- {entity['text']}"

    except MilvusException as e:
        # Message d'erreur technique détaillé pour les logs de l'UI
        return f"[Milvus - Erreur Connexion/Index] Impossible de requêter la base : {e.message}"
    except Exception as e:
        return f"[Milvus - Erreur Interne] {str(e)}"