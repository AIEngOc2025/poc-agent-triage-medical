"""Module d'analyse tactique via le moteur de secours Stockfish."""

import chess
import chess.engine


def evaluate_position(fen: str) -> str:
    """Analyse la position FEN et extrait l'évaluation en centipawns.

    Args:
        fen: La chaîne FEN réglementaire de la position.
    """
    try:
        # Validation de la position avec python-chess (Exigence Étape 2)
        board = chess.Board(fen)
    except ValueError:
        return "[Stockfish] Erreur : Le format de la chaîne FEN est invalide."

    # Chemin du binaire configuré localement ou via Docker
    stockfish_path = "/usr/games/stockfish"

    try:
        with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
            info = engine.analyse(board, chess.engine.Limit(time=0.5))
            score = info["score"].white()

            # Extraction de la valeur en centipawns
            if score.is_mate():
                eval_str = f"Mat en {abs(score.mate())}"
            else:
                eval_str = f"{score.score() / 100:+.2f} cp"

            result = engine.play(board, chess.engine.Limit(time=0.5))
            return f"[Stockfish] Évaluation : {eval_str} | Meilleur coup suggéré : {result.move}"
    except Exception as e:
        return f"[Stockfish] Erreur lors de l'exécution du moteur : {str(e)}"
    
    # recherche et importe les videaos youtube sur les échecs
def search_chess_videos(query: str) -> str:
    """Recherche des vidéos YouTube sur les échecs en fonction d'une requête.

    Args:
        query: Le sujet de recherche, par exemple "meilleures ouvertures d'échecs".
    """
    # Implémentation fictive pour l'exemple
    return f"[YouTube] Résultats de recherche pour '{query}' :\n- Vidéo 1 : 'Top 5 des ouvertures d'échecs'\n- Vidéo 2 : 'Comment jouer la Sicilienne Najdorf'"