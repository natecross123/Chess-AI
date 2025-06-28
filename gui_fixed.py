"""
gui.py
Fixed Graphical User Interface for the chess game using tkinter
"""

import tkinter as tk
from tkinter import messagebox, ttk
import chess
from chess_engine import ChessEngine
from utils import format_move


class ChessGUI:
    """
    GUI for playing chess using tkinter with text-based pieces
    """
    
    def __init__(self, master):
        """
        Initialize the chess GUI
        
        Args:
            master: Tkinter root window
        """
        self.master = master
        self.master.title("Chess AI - Minimax with Alpha-Beta Pruning")
        self.master.resizable(False, False)
        
        # Game state
        self.board = chess.Board()
        self.engine = ChessEngine(depth=3)
        self.selected_square = None
        self.highlighted_squares = []
        self.human_color = chess.WHITE
        self.game_mode = "human_vs_ai"  # or "ai_vs_ai"
        
        # Colors
        self.light_color = "#F0D9B5"
        self.dark_color = "#B58863"
        self.highlight_color = "#829769"
        self.select_color = "#646D40"
        
        # Piece symbols for display
        self.piece_symbols = {
            chess.PAWN: {"white": "♙", "black": "♟"},
            chess.ROOK: {"white": "♖", "black": "♜"},
            chess.KNIGHT: {"white": "♘", "black": "♞"},
            chess.BISHOP: {"white": "♗", "black": "♝"},
            chess.QUEEN: {"white": "♕", "black": "♛"},
            chess.KING: {"white": "♔", "black": "♚"}
        }
        
        # Create UI elements
        self.create_menu()
        self.create_widgets()
        self.update_board()
        
    def create_menu(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        
        # Game menu
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Game as White", command=lambda: self.new_game(chess.WHITE))
        game_menu.add_command(label="New Game as Black", command=lambda: self.new_game(chess.BLACK))
        game_menu.add_command(label="AI vs AI", command=self.start_ai_vs_ai)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.master.quit)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Set Difficulty", command=self.set_difficulty)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="How to Play", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_widgets(self):
        """Create the main widgets"""
        # Main frame
        main_frame = tk.Frame(self.master)
        main_frame.pack(padx=10, pady=10)
        
        # Board frame
        self.board_frame = tk.Frame(main_frame, bg="black", bd=2, relief="solid")
        self.board_frame.grid(row=0, column=0, padx=10)
        
        # Create board squares
        self.squares = {}
        for row in range(8):
            for col in range(8):
                square = chess.square(col, 7 - row)
                color = self.light_color if (row + col) % 2 == 0 else self.dark_color
                
                square_button = tk.Button(
                    self.board_frame, 
                    width=8, 
                    height=4,
                    bg=color,
                    font=("Arial", 20),
                    command=lambda s=square: self.on_square_click(s)
                )
                square_button.grid(row=row, column=col, padx=1, pady=1)
                
                self.squares[square] = square_button
        
        # Info frame
        info_frame = tk.Frame(main_frame)
        info_frame.grid(row=0, column=1, padx=10, sticky="n")
        
        # Status label
        self.status_label = tk.Label(info_frame, text="White to move", 
                                    font=("Arial", 14, "bold"))
        self.status_label.pack(pady=10)
        
        # Move history
        tk.Label(info_frame, text="Move History", font=("Arial", 12, "bold")).pack()
        
        history_frame = tk.Frame(info_frame)
        history_frame.pack(pady=5)
        
        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.move_list = tk.Listbox(history_frame, width=20, height=15,
                                   yscrollcommand=scrollbar.set, font=("Courier", 10))
        self.move_list.pack(side=tk.LEFT)
        scrollbar.config(command=self.move_list.yview)
        
        # Engine info
        self.engine_info = tk.Label(info_frame, text="", font=("Arial", 10))
        self.engine_info.pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(info_frame)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Undo Move", command=self.undo_move, width=12).pack(pady=2)
        tk.Button(button_frame, text="Reset Board", command=self.reset_board, width=12).pack(pady=2)
        tk.Button(button_frame, text="Flip Board", command=self.flip_board, width=12).pack(pady=2)
        
    def update_board(self):
        """Update the board display"""
        # Reset colors and update pieces
        for square in range(64):
            row, col = divmod(square, 8)
            # Default color
            color = self.light_color if (row + col) % 2 == 0 else self.dark_color
            
            # Apply highlights
            if square == self.selected_square:
                color = self.select_color
            elif square in self.highlighted_squares:
                color = self.highlight_color
            
            # Update square
            button = self.squares[square]
            button.config(bg=color)
            
            # Update piece
            piece = self.board.piece_at(square)
            if piece:
                color_key = "white" if piece.color == chess.WHITE else "black"
                symbol = self.piece_symbols[piece.piece_type][color_key]
                button.config(text=symbol, fg="black" if piece.color == chess.WHITE else "darkred")
            else:
                button.config(text="", fg="black")
        
        # Update status
        if self.board.is_game_over():
            if self.board.is_checkmate():
                winner = "Black" if self.board.turn == chess.WHITE else "White"
                self.status_label.config(text=f"Checkmate! {winner} wins!")
            elif self.board.is_stalemate():
                self.status_label.config(text="Stalemate!")
            else:
                self.status_label.config(text="Game Over!")
        else:
            turn = "White" if self.board.turn == chess.WHITE else "Black"
            if self.board.is_check():
                self.status_label.config(text=f"{turn} to move (CHECK!)")
            else:
                self.status_label.config(text=f"{turn} to move")
    
    def on_square_click(self, square):
        """
        Handle square click
        
        Args:
            square: Clicked square
        """
        if self.game_mode == "ai_vs_ai" or self.board.is_game_over():
            return
        
        if self.board.turn != self.human_color and self.game_mode == "human_vs_ai":
            return
        
        if self.selected_square is None:
            # Select piece
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                self.highlighted_squares = []
                
                # Highlight legal moves
                for move in self.board.legal_moves:
                    if move.from_square == square:
                        self.highlighted_squares.append(move.to_square)
                
                self.update_board()
        else:
            # Try to make move
            move = chess.Move(self.selected_square, square)
            
            # Check for promotion
            piece = self.board.piece_at(self.selected_square)
            if (piece and piece.piece_type == chess.PAWN and
                ((self.board.turn == chess.WHITE and chess.square_rank(square) == 7) or
                 (self.board.turn == chess.BLACK and chess.square_rank(square) == 0))):
                # Ask for promotion piece
                promotion_piece = self.ask_promotion()
                move = chess.Move(self.selected_square, square, promotion_piece)
            
            if move in self.board.legal_moves:
                self.make_move(move)
                
                # AI move
                if self.game_mode == "human_vs_ai" and not self.board.is_game_over():
                    self.master.after(100, self.make_ai_move)
            
            # Deselect
            self.selected_square = None
            self.highlighted_squares = []
            self.update_board()
    
    def ask_promotion(self):
        """Ask user which piece to promote to"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Choose Promotion")
        dialog.geometry("300x150")
        dialog.transient(self.master)
        dialog.grab_set()
        
        promotion_piece = [chess.QUEEN]  # Default to queen
        
        tk.Label(dialog, text="Choose piece to promote to:", font=("Arial", 12)).pack(pady=10)
        
        button_frame = tk.Frame(dialog)
        button_frame.pack()
        
        pieces = [
            (chess.QUEEN, "Queen ♕"),
            (chess.ROOK, "Rook ♖"),
            (chess.BISHOP, "Bishop ♗"),
            (chess.KNIGHT, "Knight ♘")
        ]
        
        for piece_type, name in pieces:
            tk.Button(
                button_frame, 
                text=name,
                command=lambda p=piece_type: (promotion_piece.__setitem__(0, p), dialog.destroy())
            ).pack(side=tk.LEFT, padx=5)
        
        dialog.wait_window()
        return promotion_piece[0]
    
    def make_move(self, move):
        """
        Make a move on the board
        
        Args:
            move: Chess move
        """
        # Add to move history
        move_num = len(self.board.move_stack) // 2 + 1
        if self.board.turn == chess.WHITE:
            move_text = f"{move_num}. {format_move(self.board, move)}"
        else:
            move_text = f"    {format_move(self.board, move)}"
        
        self.board.push(move)
        self.move_list.insert(tk.END, move_text)
        self.move_list.see(tk.END)
        self.update_board()
    
    def make_ai_move(self):
        """Make an AI move"""
        self.engine_info.config(text="AI is thinking...")
        self.master.update()
        
        # Get AI move
        move = self.engine.get_best_move(self.board)
        
        if move:
            self.engine_info.config(
                text=f"Evaluated {self.engine.nodes_evaluated} nodes\n"
                     f"Pruned {self.engine.pruning_count} branches"
            )
            self.make_move(move)
        else:
            messagebox.showerror("Error", "AI couldn't find a valid move!")
    
    def undo_move(self):
        """Undo the last move"""
        if len(self.board.move_stack) > 0:
            self.board.pop()
            self.move_list.delete(tk.END)
            
            # In human vs AI mode, undo AI move too
            if (self.game_mode == "human_vs_ai" and 
                len(self.board.move_stack) > 0 and 
                self.board.turn == self.human_color):
                self.board.pop()
                self.move_list.delete(tk.END)
            
            self.selected_square = None
            self.highlighted_squares = []
            self.update_board()
    
    def reset_board(self):
        """Reset the board to starting position"""
        self.board = chess.Board()
        self.move_list.delete(0, tk.END)
        self.selected_square = None
        self.highlighted_squares = []
        self.engine_info.config(text="")
        self.update_board()
    
    def flip_board(self):
        """Flip the board view"""
        # Recreate squares in flipped order
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        
        self.squares = {}
        for row in range(8):
            for col in range(8):
                # Flip the board by reversing the row calculation
                if hasattr(self, '_flipped') and self._flipped:
                    square = chess.square(7-col, row)
                else:
                    square = chess.square(col, 7 - row)
                    
                color = self.light_color if (row + col) % 2 == 0 else self.dark_color
                
                square_button = tk.Button(
                    self.board_frame, 
                    width=8, 
                    height=4,
                    bg=color,
                    font=("Arial", 20),
                    command=lambda s=square: self.on_square_click(s)
                )
                square_button.grid(row=row, column=col, padx=1, pady=1)
                
                self.squares[square] = square_button
        
        # Toggle flip state
        self._flipped = not hasattr(self, '_flipped') or not self._flipped
        self.update_board()
    
    def new_game(self, human_color):
        """
        Start a new game
        
        Args:
            human_color: Color for human player
        """
        self.human_color = human_color
        self.game_mode = "human_vs_ai"
        self.reset_board()
        
        # If AI plays first
        if human_color == chess.BLACK:
            self.master.after(500, self.make_ai_move)
    
    def start_ai_vs_ai(self):
        """Start an AI vs AI game"""
        self.game_mode = "ai_vs_ai"
        self.reset_board()
        
        # Start AI moves
        self.master.after(1000, self.ai_vs_ai_loop)
    
    def ai_vs_ai_loop(self):
        """Main loop for AI vs AI games"""
        if self.game_mode != "ai_vs_ai" or self.board.is_game_over():
            return
        
        self.make_ai_move()
        
        # Schedule next move
        if not self.board.is_game_over():
            self.master.after(2000, self.ai_vs_ai_loop)
    
    def set_difficulty(self):
        """Set the AI difficulty"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Set Difficulty")
        dialog.geometry("300x200")
        dialog.transient(self.master)
        dialog.grab_set()
        
        tk.Label(dialog, text="Select AI Difficulty:", font=("Arial", 12)).pack(pady=10)
        
        difficulty_var = tk.IntVar(value=self.engine.depth)
        
        difficulties = [
            (1, "Beginner"),
            (2, "Easy"),
            (3, "Medium"),
            (4, "Hard"),
            (5, "Expert"),
            (6, "Master")
        ]
        
        for depth, name in difficulties:
            tk.Radiobutton(dialog, text=f"{name} (Depth {depth})", 
                          variable=difficulty_var, value=depth).pack(anchor="w", padx=20)
        
        def apply_difficulty():
            self.engine.set_depth(difficulty_var.get())
            dialog.destroy()
            messagebox.showinfo("Difficulty", f"Difficulty set to depth {difficulty_var.get()}")
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Apply", command=apply_difficulty).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def show_help(self):
        """Show help dialog"""
        help_text = """How to Play:

1. Click on a piece to select it
2. Legal moves will be highlighted in green
3. Click on a highlighted square to move
4. The selected piece is shown in dark green

Game Modes:
• Human vs AI: Play against the computer
• AI vs AI: Watch two AIs play each other

Controls:
• Undo Move: Take back the last move(s)
• Reset Board: Start a new game
• Flip Board: Change board orientation

The AI uses the Minimax algorithm with 
Alpha-Beta pruning to find the best moves.

Higher difficulty levels search deeper
for better moves but take longer to think."""
        
        messagebox.showinfo("How to Play", help_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Chess AI with Minimax and Alpha-Beta Pruning

Features:
• Complete chess rule implementation
• Minimax algorithm for move selection
• Alpha-Beta pruning for optimization
• Advanced position evaluation
• Move ordering for better pruning
• Adjustable difficulty levels
• Human vs AI and AI vs AI modes

Algorithm Details:
• Material evaluation with piece values
• Positional evaluation using piece-square tables
• Mobility evaluation (number of legal moves)
• Endgame detection and king safety

Created for educational purposes to demonstrate
game AI algorithms and chess programming."""
        
        messagebox.showinfo("About Chess AI", about_text)


def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (800 // 2)
    y = (root.winfo_screenheight() // 2) - (600 // 2)
    root.geometry(f"800x600+{x}+{y}")
    
    app = ChessGUI(root)
    
    # Show welcome message
    messagebox.showinfo("Welcome", 
                       "Welcome to Chess AI!\n\n" +
                       "Click 'Game' menu to start a new game.\n" +
                       "Check 'Help' -> 'How to Play' for instructions.")
    
    root.mainloop()


if __name__ == "__main__":
    main()