import os
import pathlib
import shutil
from functools import lru_cache

import chess
import chess.engine


@lru_cache(maxsize=1)
def _patch_keras_loader() -> None:
    os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")

    import keras.models
    import keras.src.saving.saving_api as saving_api
    import tf_keras

    original_load_model = saving_api.load_model

    def patched_load_model(filepath, **kwargs):
        try:
            return original_load_model(filepath, **kwargs)
        except ValueError:
            return tf_keras.models.load_model(filepath)

    saving_api.load_model = patched_load_model
    keras.models.load_model = patched_load_model


def _extract_fen_from_image(image_path: str) -> str:
    _patch_keras_loader()

    from board_to_fen.predict import get_fen_from_image_path

    for black_view in (True, False):
        fen_pieces = get_fen_from_image_path(image_path, black_view=black_view)
        fen = f"{fen_pieces} b - - 0 1"
        try:
            chess.Board(fen)
            return fen
        except ValueError:
            continue

    return ""


def chess_best_move(position: str) -> str:
    """Find the best chess move for a given board position using Stockfish.

    Provide either:
    - a FEN string, or
    - the path to a chess board image (PNG/JPG/WEBP), which will be converted
      to FEN with the specialized board recognizer before analysis.

    FEN example: "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"

    Returns:
        The best move in standard algebraic notation (e.g. "Rd5", "Nf3+", "e4").
    """
    path = pathlib.Path(position)
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"} or path.exists():
        fen = _extract_fen_from_image(position)
        if not fen:
            return f"Error: Could not extract a valid FEN from image: {position}"
    else:
        fen = position

    # Find stockfish binary
    stockfish_path = shutil.which("stockfish")
    if not stockfish_path:
        for candidate in ("/opt/homebrew/bin/stockfish", "/usr/local/bin/stockfish", "/usr/bin/stockfish"):
            if os.path.isfile(candidate):
                stockfish_path = candidate
                break
    if not stockfish_path:
        return "Error: Stockfish engine not found on this system."

    # Validate FEN
    try:
        board = chess.Board(fen)
    except ValueError as exc:
        return f"Invalid FEN: {exc}"

    try:
        with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
            result = engine.analyse(board, chess.engine.Limit(time=0.5))
            best_move = result.get("pv", [None])[0]

            if best_move is None:
                return "No move found (position may be terminal)."

            return board.san(best_move)
    except Exception as exc:
        return f"Engine error: {exc}"
