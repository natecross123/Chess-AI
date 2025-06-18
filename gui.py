"""
gui.py
Graphical User Interface for the chess game using tkinter
"""

import tkinter as tk
from tkinter import messagebox, ttk
import chess
import chess.svg
from PIL import Image, ImageTk
import cairosvg
import io
from chess_engine import ChessEngine
from utils import format_move


class ChessGUI:
    """
    GUI for playing chess using tkinter
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
        self.board_frame = tk.Frame(main_frame, bg="black")
        self.board_frame.grid(row=0, column=0, padx=10)
        
        # Create board squares
        self.squares = {}
        for row in range(8):
            for col in range(8):
                square = chess.square(col, 7 - row)
                color = self.light_color if (row + col) % 2 == 0 else self.dark_color
                
                square_frame = tk.Frame(self.board_frame, width=64, height=64, bg=color)
                square_frame.grid(row=row, column=col)
                square_frame.bind("<Button-1>", lambda e, s=square: self.on_square_click(s))
                
                label = tk.Label(square_frame, bg=color)
                label.place(x=0, y=0, width=64, height=64)
                label.bind("<Button-1>", lambda e, s=square: self.on_square_click(s))
                
                self.squares[square] = (square_frame, label)
        
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
                                   yscrollcommand=scrollbar.set)
        self.move_list.pack(side=tk.LEFT)
        scrollbar.config(command=self.move_list.yview)
        
        # Engine info
        self.engine_info = tk.Label(info_frame, text="", font=("Arial", 10))
        self.engine_info.pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(info_frame)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Undo Move", command=self.undo_move).pack(pady=2)
        tk.Button(button_frame, text="Reset Board", command=self.reset_board).pack(pady=2)
        
    def update_board(self):
        """Update the board display"""
        # Reset colors
        for square in range(64):
            row, col = divmod(square, 8)
            color = self.light_color if (row + col) % 2 == 0 else self.dark_color
            self.squares[square][0].config(bg=color)
        
        # Highlight selected square
        if self.selected_square is not None:
            self.squares[self.selected_square][0].config(bg=self.select_color)
        
        # Highlight possible moves
        for square in self.highlighted_squares:
            self.squares[square][0].config(bg=self.highlight_color)
        
        # Update pieces
        for square in range(64):
            piece = self.board.piece_at(square)
            if piece:
                # Get piece image
                image = self.get_piece_image(piece)
                self.squares[square][1].config(image=image)
                self.squares[square][1].image = image  # Keep reference
            else:
                self.squares[square][1].config(image="")
        
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
    
    def get_piece_image(self, piece):
        """
        Get the image for a chess piece
        
        Args:
            piece: Chess piece
            
        Returns:
            PIL Image
        """
        # Create SVG for the piece
        svg_data = chess.svg.piece(piece, size=64)
        
        # Convert SVG to PNG using cairosvg
        png_data = cairosvg.svg2png(bytestring=svg_data.encode('utf-8'))
        
        # Create PIL Image
        image = Image.open(io.BytesIO(png_data))
        
        # Convert to PhotoImage
        return ImageTk.PhotoImage(image)
    
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
            if (self.board.piece_at(self.selected_square).piece_type == chess.PAWN and
                ((self.board.turn == chess.WHITE and chess.square_rank(square) == 7) or
                 (self.board.turn == chess.BLACK and chess.square_rank(square) == 0))):
                move = chess.Move(self.selected_square, square, chess.QUEEN)
            
            if move in self.board.legal_moves:
                self.make_move(move)
                
                # AI move
                if self.game_mode == "human_vs_ai" and not self.board.is_game_over():
                    self.master.after(100, self.make_ai_move)
            
            # Deselect
            self.selected_square = None
            self.highlighted_squares = []
            self.update_board()
    
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
            
            self.update_board()
    
    def reset_board(self):
        """Reset the board to starting position"""
        self.board = chess.Board()
        self.move_list.delete(0, tk.END)
        self.selected_square = None
        self.highlighted_squares = []
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
            self.make_ai_move()
    
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
        self.master.after(1000, self.ai_vs_ai_loop)
    
    def set_difficulty(self):
        """Set the AI difficulty"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Set Difficulty")
        dialog.geometry("300x150")
        
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
                          variable=difficulty_var, value=depth).pack()
        
        def apply_difficulty():
            self.engine.set_depth(difficulty_var.get())
            dialog.destroy()
        
        tk.Button(dialog, text="Apply", command=apply_difficulty).pack(pady=10)
    
    def show_help(self):
        """Show help dialog"""
        help_text = """How to Play:

1. Click on a piece to select it
2. Legal moves will be highlighted
3. Click on a highlighted square to move

The AI uses the Minimax algorithm with 
Alpha-Beta pruning to find the best moves.

Higher difficulty levels search deeper
in the game tree for better moves."""
        
        messagebox.showinfo("How to Play", help_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Chess AI with Minimax and Alpha-Beta Pruning

This chess engine uses:
- Minimax algorithm for move selection
- Alpha-Beta pruning for optimization
- Advanced position evaluation
- Move ordering for better pruning

Created for educational purposes."""
        
        messagebox.showinfo("About", about_text)


def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()