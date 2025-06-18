"""
utils.py
Utility functions for the chess engine
"""

import chess
from typing import List


def get_ordered_moves(board: chess.Board) -> List[chess.Move]:
    """
    Get moves ordered by likely importance for better alpha-beta pruning
    
    Args:
        board: Chess board
        
    Returns:
        List of moves ordered by priority
    """
    moves = list(board.legal_moves)
    
    def move_priority(move: chess.Move) -> int:
        """
        Calculate move priority for ordering
        Higher values = higher priority
        """
        priority = 0
        
        # Captures are high priority
        if board.is_capture(move):
            # MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
            victim_piece = board.piece_at(move.to_square)
            attacker_piece = board.piece_at(move.from_square)
            
            if victim_piece and attacker_piece:
                victim_value = get_piece_value(victim_piece.piece_type)
                attacker_value = get_piece_value(attacker_piece.piece_type)
                priority += 10 * victim_value - attacker_value
        
        # Checks are good
        board.push(move)
        if board.is_check():
            priority += 900
        board.pop()
        
        # Promotions are valuable
        if move.promotion:
            priority += 800
        
        # Center moves in opening
        to_file = chess.square_file(move.to_square)
        to_rank = chess.square_rank(move.to_square)
        if 2 <= to_file <= 5 and 2 <= to_rank <= 5:
            priority += 50
        
        return priority
    
    # Sort moves by priority (highest first)
    moves.sort(key=move_priority, reverse=True)
    
    return moves


def get_piece_value(piece_type: chess.PieceType) -> int:
    """
    Get the value of a piece type
    
    Args:
        piece_type: Type of chess piece
        
    Returns:
        Piece value
    """
    values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 100
    }
    return values.get(piece_type, 0)


def format_move(board: chess.Board, move: chess.Move) -> str:
    """
    Format a move in standard algebraic notation
    
    Args:
        board: Chess board
        move: Chess move
        
    Returns:
        Move in SAN format
    """
    return board.san(move)


def parse_move(board: chess.Board, move_str: str) -> chess.Move:
    """
    Parse a move from string format
    
    Args:
        board: Chess board
        move_str: Move string (UCI or SAN format)
        
    Returns:
        Chess move object
        
    Raises:
        ValueError: If move is invalid
    """
    try:
        # Try UCI format first (e.g., "e2e4")
        move = chess.Move.from_uci(move_str)
        if move in board.legal_moves:
            return move
    except:
        pass
    
    try:
        # Try SAN format (e.g., "e4", "Nf3")
        move = board.parse_san(move_str)
        if move in board.legal_moves:
            return move
    except:
        pass
    
    raise ValueError(f"Invalid move: {move_str}")


def print_board(board: chess.Board):
    """
    Print the board in a nice format
    
    Args:
        board: Chess board
    """
    print("\n  a b c d e f g h")
    print("  ---------------")
    for rank in range(7, -1, -1):
        print(f"{rank + 1}|", end="")
        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            if piece:
                symbol = piece.symbol()
            else:
                symbol = "."
            print(f"{symbol} ", end="")
        print(f"|{rank + 1}")
    print("  ---------------")
    print("  a b c d e f g h\n")