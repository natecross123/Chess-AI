"""
game_manager.py
Game management and user interface
"""

import chess
import time
from chess_engine import ChessEngine
from utils import print_board, parse_move, format_move


class GameManager:
    """
    Manages chess games between human and AI players
    """
    
    def __init__(self, engine_depth: int = 3):
        """
        Initialize the game manager
        
        Args:
            engine_depth: Search depth for the AI engine
        """
        self.board = chess.Board()
        self.engine = ChessEngine(depth=engine_depth)
        
    def play_human_vs_ai(self, human_color: chess.Color = chess.WHITE):
        """
        Play a game between human and AI
        
        Args:
            human_color: Color for the human player
        """
        print("Welcome to Chess!")
        print(f"You are playing as {'White' if human_color == chess.WHITE else 'Black'}")
        print("Enter moves in UCI format (e.g., 'e2e4') or SAN format (e.g., 'e4')")
        print("Type 'quit' to exit, 'board' to redraw the board")
        print()
        
        while not self.board.is_game_over():
            print_board(self.board)
            
            # Display game status
            if self.board.is_check():
                print("CHECK!")
            
            print(f"{'White' if self.board.turn == chess.WHITE else 'Black'} to move")
            
            if self.board.turn == human_color:
                # Human's turn
                move = self._get_human_move()
                if move is None:
                    print("Game terminated by user")
                    break
            else:
                # AI's turn
                print("AI is thinking...")
                start_time = time.time()
                move = self.engine.get_best_move(self.board)
                end_time = time.time()
                
                if move:
                    print(f"AI plays: {format_move(self.board, move)}")
                    print(f"Time taken: {end_time - start_time:.2f} seconds")
                else:
                    print("AI couldn't find a valid move!")
                    break
            
            # Make the move
            self.board.push(move)
            print()
        
        # Game over
        self._print_game_result()
    
    def play_ai_vs_ai(self, depth1: int = 3, depth2: int = 3):
        """
        Play a game between two AI engines
        
        Args:
            depth1: Search depth for the first AI
            depth2: Search depth for the second AI
        """
        engine1 = ChessEngine(depth=depth1)
        engine2 = ChessEngine(depth=depth2)
        
        print(f"AI vs AI game: Depth {depth1} (White) vs Depth {depth2} (Black)")
        print()
        
        move_count = 0
        while not self.board.is_game_over():
            print_board(self.board)
            
            if self.board.turn == chess.WHITE:
                print(f"White (Depth {depth1}) is thinking...")
                move = engine1.get_best_move(self.board)
            else:
                print(f"Black (Depth {depth2}) is thinking...")
                move = engine2.get_best_move(self.board)
            
            if move:
                print(f"Move {move_count + 1}: {format_move(self.board, move)}")
                self.board.push(move)
                move_count += 1
            else:
                print("No valid move found!")
                break
            
            print()
            time.sleep(0.5)  # Small delay for visibility
        
        self._print_game_result()
    
    def _get_human_move(self) -> chess.Move:
        """
        Get a move from the human player
        
        Returns:
            Chess move or None if user wants to quit
        """
        while True:
            user_input = input("Your move: ").strip()
            
            if user_input.lower() == 'quit':
                return None
            
            if user_input.lower() == 'board':
                print_board(self.board)
                continue
            
            try:
                move = parse_move(self.board, user_input)
                return move
            except ValueError as e:
                print(f"Invalid move: {e}")
                print("Legal moves:", end=" ")
                legal_moves = [format_move(self.board, m) for m in self.board.legal_moves]
                print(", ".join(legal_moves[:10]), "..." if len(legal_moves) > 10 else "")
    
    def _print_game_result(self):
        """
        Print the game result
        """
        print("\nGame Over!")
        print_board(self.board)
        
        if self.board.is_checkmate():
            winner = "White" if self.board.turn == chess.BLACK else "Black"
            print(f"Checkmate! {winner} wins!")
        elif self.board.is_stalemate():
            print("Stalemate! The game is a draw.")
        elif self.board.is_insufficient_material():
            print("Draw due to insufficient material.")
        elif self.board.is_fifty_moves():
            print("Draw by fifty-move rule.")
        elif self.board.is_repetition():
            print("Draw by threefold repetition.")
        else:
            print("Game ended.") 
    
    def reset_game(self):
        """
        Reset the game to initial position
        """
        self.board = chess.Board()
    
    def set_position(self, fen: str):
        """
        Set the board to a specific position
        
        Args:
            fen: FEN string representing the position
        """
        try:
            self.board = chess.Board(fen)
        except:
            print("Invalid FEN string")
            self.board = chess.Board()