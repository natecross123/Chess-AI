"""
evaluation.py
Board evaluation functions for the chess engine
"""

import chess
from typing import Dict

# Piece values
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Piece-square tables for positional evaluation
PAWN_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5,-10,  0,  0,-10, -5,  5,
    5, 10, 10,-20,-20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

ROOK_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    0,  0,  0,  5,  5,  0,  0,  0
]

QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
    0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

KING_MIDDLE_GAME_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20
]

KING_END_GAME_TABLE = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
]

# Constants
CHECKMATE_SCORE = 100000
DRAW_SCORE = 0


def get_piece_square_value(piece: chess.Piece, square: int, endgame: bool = False) -> int:
    """
    Get the piece-square table value for a piece at a given square
    
    Args:
        piece: Chess piece
        square: Square index (0-63)
        endgame: Whether we're in the endgame
        
    Returns:
        Piece-square table value
    """
    piece_type = piece.piece_type
    
    # Mirror the square for black pieces
    if piece.color == chess.BLACK:
        square = chess.square_mirror(square)
    
    if piece_type == chess.PAWN:
        return PAWN_TABLE[square]
    elif piece_type == chess.KNIGHT:
        return KNIGHT_TABLE[square]
    elif piece_type == chess.BISHOP:
        return BISHOP_TABLE[square]
    elif piece_type == chess.ROOK:
        return ROOK_TABLE[square]
    elif piece_type == chess.QUEEN:
        return QUEEN_TABLE[square]
    elif piece_type == chess.KING:
        if endgame:
            return KING_END_GAME_TABLE[square]
        else:
            return KING_MIDDLE_GAME_TABLE[square]
    
    return 0


def count_material(board: chess.Board) -> Dict[chess.Color, int]:
    """
    Count material for both sides
    
    Args:
        board: Chess board
        
    Returns:
        Dictionary with material count for white and black
    """
    material = {chess.WHITE: 0, chess.BLACK: 0}
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            material[piece.color] += PIECE_VALUES[piece.piece_type]
    
    return material


def is_endgame(board: chess.Board) -> bool:
    """
    Determine if the position is in the endgame
    
    Args:
        board: Chess board
        
    Returns:
        True if endgame, False otherwise
    """
    # Count queens
    queens = len(board.pieces(chess.QUEEN, chess.WHITE)) + len(board.pieces(chess.QUEEN, chess.BLACK))
    
    # Count minor pieces
    minors = (len(board.pieces(chess.KNIGHT, chess.WHITE)) + len(board.pieces(chess.BISHOP, chess.WHITE)) +
              len(board.pieces(chess.KNIGHT, chess.BLACK)) + len(board.pieces(chess.BISHOP, chess.BLACK)))
    
    # Endgame if no queens or if each side has at most 1 minor piece
    return queens == 0 or (queens == 2 and minors <= 2)


def evaluate_board(board: chess.Board) -> float:
    """
    Evaluate the board position
    
    Args:
        board: Chess board
        
    Returns:
        Evaluation score (positive favors white, negative favors black)
    """
    # Check for game over
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -CHECKMATE_SCORE
        else:
            return CHECKMATE_SCORE
    
    if board.is_stalemate() or board.is_insufficient_material():
        return DRAW_SCORE
    
    # Material evaluation
    material = count_material(board)
    material_score = material[chess.WHITE] - material[chess.BLACK]
    
    # Positional evaluation
    positional_score = 0
    endgame = is_endgame(board)
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = get_piece_square_value(piece, square, endgame)
            if piece.color == chess.WHITE:
                positional_score += value
            else:
                positional_score -= value
    
    # Mobility evaluation (number of legal moves)
    mobility_score = 0
    if board.turn == chess.WHITE:
        mobility_score = len(list(board.legal_moves))
        board.turn = chess.BLACK
        mobility_score -= len(list(board.legal_moves))
        board.turn = chess.WHITE
    else:
        mobility_score = -len(list(board.legal_moves))
        board.turn = chess.WHITE
        mobility_score += len(list(board.legal_moves))
        board.turn = chess.BLACK
    
    # Combine all factors
    total_score = material_score + positional_score * 0.1 + mobility_score * 2
    
    return total_score