import shutil

import chess
from stockfish import Stockfish


def chess_best_move(fen: str) -> str:
    """Find the best chess move for a given board position using the Stockfish engine.

    Use this tool when you need to determine the best move in a chess position.
    First use read_image to extract the FEN notation from a chess board image,
    then pass that FEN string to this tool.

    FEN format example: "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"

    Args:
        fen: The chess position in FEN (Forsyth-Edwards Notation) format.

    Returns:
        The best move in standard algebraic notation (e.g. "Rd5", "Nf3+", "e4").
    """
    # Find stockfish binary
    stockfish_path = shutil.which("stockfish")
    if not stockfish_path:
        return "Error: Stockfish engine not found. Install it with: brew install stockfish"

    # Validate FEN
    try:
        board = chess.Board(fen)
    except ValueError as e:
        return f"Error: Invalid FEN string: {e}"

    # Get best move from Stockfish
    sf = Stockfish(path=stockfish_path, depth=20)
    if not sf.is_fen_valid(fen):
        return f"Error: Stockfish reports invalid FEN: {fen}"

    sf.set_fen_position(fen)
    best_move_uci = sf.get_best_move()

    if not best_move_uci:
        return "Error: Stockfish could not determine a best move (game may be over)."

    # Convert UCI notation to standard algebraic notation
    uci_move = chess.Move.from_uci(best_move_uci)
    san_move = board.san(uci_move)

    return san_move
