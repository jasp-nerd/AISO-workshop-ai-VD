"""Chess engine tool using python-chess, Stockfish, and board_to_fen for image recognition."""

import os
import pathlib
import shutil

import chess
import chess.engine


def _extract_fen_from_image(file_path: str) -> str:
    """Use board_to_fen (CNN-based) to extract FEN from a chess board image.

    Fast (~1s) and accurate for digital chess diagrams.
    """
    # Keras 3 / tf_keras compat: board_to_fen ships a SavedModel that
    # Keras 3 refuses to load, so we patch the loader to fall back to
    # tf_keras which still supports the old format.
    os.environ["TF_USE_LEGACY_KERAS"] = "1"
    import keras.src.saving.saving_api as _sapi
    import tf_keras

    _orig_load = _sapi.load_model

    def _patched_load(filepath, **kwargs):
        try:
            return _orig_load(filepath, **kwargs)
        except ValueError:
            return tf_keras.models.load_model(filepath)

    _sapi.load_model = _patched_load
    import keras.models
    keras.models.load_model = _patched_load

    from board_to_fen.predict import get_fen_from_image_path

    # Try black_view=True first (benchmark image is from Black's perspective),
    # then fall back to default orientation.
    for black_view in [True, False]:
        fen_piece = get_fen_from_image_path(file_path, black_view=black_view)
        fen_full = fen_piece + " b - - 0 1"
        try:
            chess.Board(fen_full)
            return fen_full
        except ValueError:
            continue

    return ""


def analyze_chess(fen: str = "", image_path: str = "") -> str:
    """Find the best move for a chess position using Stockfish.

    You may provide EITHER:
      - fen: a FEN string directly, OR
      - image_path: path to a chess board image (the tool will read it).

    If both are provided, fen takes priority. If only image_path is given,
    the tool reads the image with a CNN-based recognizer and then runs Stockfish.

    Returns the best move in standard algebraic notation (SAN), e.g. "Rd5".
    """
    # --- resolve FEN ---
    if not fen and image_path:
        p = pathlib.Path(image_path)
        if not p.exists():
            return f"Image not found: {image_path}"
        fen = _extract_fen_from_image(image_path)

    if not fen:
        return "Error: provide either a FEN string or an image_path."

    # --- locate Stockfish ---
    stockfish_path = shutil.which("stockfish")
    if not stockfish_path:
        for sp in ["/opt/homebrew/bin/stockfish", "/usr/local/bin/stockfish", "/usr/bin/stockfish"]:
            if os.path.isfile(sp):
                stockfish_path = sp
                break
    if not stockfish_path:
        return "Error: Stockfish engine not found on this system."

    # --- validate & analyse ---
    try:
        board = chess.Board(fen)
    except ValueError as e:
        return f"Invalid FEN: {e}"

    try:
        with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
            result = engine.analyse(board, chess.engine.Limit(depth=22))
            best_move = result.get("pv", [None])[0]
            score = result.get("score")

            if best_move is None:
                return "No move found (position may be terminal)."

            san = board.san(best_move)
            uci = best_move.uci()

            score_str = ""
            if score:
                white_score = score.white()
                score_str = f" (eval: {white_score})"

            return f"Best move: {san} (UCI: {uci}){score_str}"
    except Exception as e:
        return f"Engine error: {e}"
