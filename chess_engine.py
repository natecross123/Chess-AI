"""
chess_engine.py
Main chess engine implementing Minimax with Alpha-Beta pruning
"""

import chess
import chess.svg
from typing import Tuple, Optional
import math
from evaluation import evaluate_board, CHECKMATE_SCORE
from utils import get_ordered_moves
 

class ChessEngine:
    """
    Chess engine using Minimax algorithm with Alpha-Beta pruning
    """
    
    def __init__(self, depth: int = 3):
        """
        Initialize the chess engine 
        
        Args:
            depth: Search depth for the Minimax algorithm
        """
        self.depth = depth
        self.nodes_evaluated = 0
        self.pruning_count = 0
        
    def minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, 
                maximizing_player: bool) -> Tuple[float, Optional[chess.Move]]:
        """
        Minimax algorithm with Alpha-Beta pruning
        
        Args:
            board: Current board state
            depth: Remaining search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing_player: True if maximizing, False if minimizing
            
        Returns:
            Tuple of (evaluation score, best move)
        """
        self.nodes_evaluated += 1
        
        # Terminal node checks
        if depth == 0 or board.is_game_over():
            return evaluate_board(board), None
            
        best_move = None
        
        if maximizing_player:
            max_eval = -math.inf
            
            # Get moves ordered by capture priority for better pruning
            for move in get_ordered_moves(board):
                board.push(move)
                eval_score, _ = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                    
                alpha = max(alpha, eval_score)
                
                # Alpha-Beta pruning
                if beta <= alpha:
                    self.pruning_count += 1
                    break
                    
            return max_eval, best_move
            
        else:
            min_eval = math.inf
            
            for move in get_ordered_moves(board):
                board.push(move)
                eval_score, _ = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                    
                beta = min(beta, eval_score)
                
                # Alpha-Beta pruning
                if alpha >= beta:
                    self.pruning_count += 1
                    break
                    
            return min_eval, best_move
    
    def get_best_move(self, board: chess.Board) -> Optional[chess.Move]:
        """
        Get the best move for the current position
        
        Args:
            board: Current board state
            
        Returns:
            Best move found by the engine
        """
        # Reset statistics
        self.nodes_evaluated = 0
        self.pruning_count = 0
        
        # Determine if engine is playing as white or black
        maximizing = board.turn == chess.WHITE
        
        # Run minimax with alpha-beta pruning
        _, best_move = self.minimax(
            board, 
            self.depth, 
            -math.inf, 
            math.inf, 
            maximizing
        )
        
        print(f"Nodes evaluated: {self.nodes_evaluated}")
        print(f"Branches pruned: {self.pruning_count}")
        
        return best_move
    
    def set_depth(self, depth: int):
        """
        Set the search depth
        
        Args:
            depth: New search depth
        """
        self.depth = max(1, min(depth, 10))  # Limit depth between 1 and 10
