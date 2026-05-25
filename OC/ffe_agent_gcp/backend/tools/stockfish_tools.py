"""Module d'analyse tactique via le moteur de secours Stockfish."""

import os
import shutil
import chess
import chess.engine


def evaluate_position(fen: str) -> str:
    """Analyse la position FEN et extrait l'évaluation en centipawns.

    Args:
        fen: La chaîne FEN réglementaire de la position.
    """
    try:
        # Validation de la position avec python-chess
        board = chess.Board(fen)
    except ValueError:
        return "[Stockfish] Erreur : Le format de la chaîne FEN est invalide."

    # 🛠️ STRATÉGIE DE RECHERCHE DYNAMIQUE DU BINAIRE
    # 1. On regarde si un chemin spécifique est défini dans le .env
    stockfish_path = os.getenv("STOCKFISH_PATH")

    # 2. Si rien n'est défini, on demande au système de chercher "stockfish" dans le PATH (Mac ou Linux)
    if not stockfish_path:
        stockfish_path = shutil.which("stockfish")

    # 3. En dernier recours, on teste les chemins par défaut historiques
    if not stockfish_path:
        chemins_defaut = [
            "/opt/homebrew/bin/stockfish",  # Mac Apple Silicon (M1/M2/M3)
            "/usr/local/bin/stockfish",     # Mac Intel
            "/usr/games/stockfish"          # Linux / Docker
        ]
        for chemin in chemins_defaut:
            if os.path.exists(chemin):
                stockfish_path = chemin
                break

    # Si on n'a toujours rien trouvé, on lève une erreur claire avant de crash le sous-processus
    if not stockfish_path:
        return "[Stockfish] Erreur : Le binaire 'stockfish' est introuvable sur la machine. Installez-le avec 'brew install stockfish' (Mac) ou configurez STOCKFISH_PATH."

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
        return f"[Stockfish] Erreur lors de l'exécution du moteur ({stockfish_path}) : {str(e)}"