"""
gui.py
Simple but complete chess GUI with menus and features
"""

import tkinter as tk
from tkinter import messagebox
import chess
from chess_engine import ChessEngine
from utils import format_move
import os

# Suppress warning
os.environ['TK_SILENCE_DEPRECATION'] = '1'

class ChessGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chess AI - Minimax Algorithm")
        
        # Game state
        self.board = chess.Board()
        self.engine = ChessEngine(depth=3)
        self.selected_square = None
        self.human_color = chess.WHITE
        self.game_mode = "human_vs_ai"
        
        # Simple Unicode pieces (with fallback)
        try:
            self.pieces = {
                'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
                'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚'
            }
            # Test if Unicode works
            test = '♔'
        except:
            # Fallback to letters
            self.pieces = {
                'P': 'P', 'R': 'R', 'N': 'N', 'B': 'B', 'Q': 'Q', 'K': 'K',
                'p': 'p', 'r': 'r', 'n': 'n', 'b': 'b', 'q': 'q', 'k': 'k'
            }
        
        self.create_menu()
        self.create_widgets()
        self.update_display()
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Game menu
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Game as White", command=lambda: self.new_game(chess.WHITE))
        game_menu.add_command(label="New Game as Black", command=lambda: self.new_game(chess.BLACK))
        game_menu.add_separator()
        game_menu.add_command(label="AI vs AI", command=self.ai_vs_ai)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.root.quit)
        
        # Options menu
        options_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", menu=options_menu)
        options_menu.add_command(label="Set Difficulty", command=self.set_difficulty)
        options_menu.add_command(label="Undo Move", command=self.undo_move)
        options_menu.add_command(label="Reset Board", command=self.reset_board)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="How to Play", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_widgets(self):
        """Create main widgets"""
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=15, pady=15)
        
        # Left side - Chess board
        board_frame = tk.Frame(main_frame, relief="ridge", bd=2)
        board_frame.grid(row=0, column=0, padx=10)
        
        # Create board squares
        self.squares = []
        for row in range(8):
            square_row = []
            for col in range(8):
                square_index = col + (7-row) * 8
                
                # Alternating colors
                if (row + col) % 2 == 0:
                    bg_color = "#F0D9B5"  # Light squares
                else:
                    bg_color = "#B58863"  # Dark squares
                
                square = tk.Button(
                    board_frame,
                    width=4,
                    height=2,
                    bg=bg_color,
                    font=("Arial", 16),
                    command=lambda sq=square_index: self.square_clicked(sq)
                )
                square.grid(row=row, column=col, padx=1, pady=1)
                square_row.append(square)
            self.squares.append(square_row)
        
        # Right side - Game info
        info_frame = tk.Frame(main_frame)
        info_frame.grid(row=0, column=1, padx=15, sticky="n")
        
        # Game status
        self.status_label = tk.Label(info_frame, text="White to move", 
                                    font=("Arial", 14, "bold"))
        self.status_label.pack(pady=10)
        
        # Move history
        tk.Label(info_frame, text="Move History", font=("Arial", 12, "bold")).pack()
        
        # Move list with scrollbar
        list_frame = tk.Frame(info_frame)
        list_frame.pack(pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.move_listbox = tk.Listbox(list_frame, width=18, height=12,
                                      yscrollcommand=scrollbar.set,
                                      font=("Courier", 10))
        self.move_listbox.pack(side=tk.LEFT)
        scrollbar.config(command=self.move_listbox.yview)
        
        # AI information
        self.ai_label = tk.Label(info_frame, text="", font=("Arial", 10))
        self.ai_label.pack(pady=10)
        
        # Control buttons
        button_frame = tk.Frame(info_frame)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Undo Move", command=self.undo_move, 
                 width=12).pack(pady=2)
        tk.Button(button_frame, text="Reset Game", command=self.reset_board, 
                 width=12).pack(pady=2)
        tk.Button(button_frame, text="Get Hint", command=self.get_hint, 
                 width=12).pack(pady=2)
    
    def update_display(self):
        """Update the board display"""
        for row in range(8):
            for col in range(8):
                square_index = col + (7-row) * 8
                square_button = self.squares[row][col]
                
                # Default colors
                if (row + col) % 2 == 0:
                    bg_color = "#F0D9B5"
                else:
                    bg_color = "#B58863"
                
                # Highlight selected square
                if square_index == self.selected_square:
                    bg_color = "#FFFF99"  # Yellow for selected
                elif self.selected_square is not None and self.is_legal_destination(square_index):
                    bg_color = "#98FB98"  # Light green for legal moves
                
                square_button.config(bg=bg_color)
                
                # Display piece
                piece = self.board.piece_at(square_index)
                if piece:
                    piece_symbol = self.pieces.get(piece.symbol(), piece.symbol())
                    square_button.config(text=piece_symbol)
                else:
                    square_button.config(text="")
        
        # Update status
        self.update_status()
    
    def update_status(self):
        """Update game status"""
        if self.board.is_game_over():
            if self.board.is_checkmate():
                winner = "Black" if self.board.turn == chess.WHITE else "White"
                self.status_label.config(text=f"Checkmate! {winner} wins!")
            elif self.board.is_stalemate():
                self.status_label.config(text="Stalemate - Draw!")
            else:
                self.status_label.config(text="Game Over!")
        else:
            current_player = "White" if self.board.turn == chess.WHITE else "Black"
            if self.board.is_check():
                self.status_label.config(text=f"{current_player} in CHECK!")
            else:
                self.status_label.config(text=f"{current_player} to move")
    
    def is_legal_destination(self, to_square):
        """Check if moving to this square is legal"""
        if self.selected_square is None:
            return False
        
        move = chess.Move(self.selected_square, to_square)
        return move in self.board.legal_moves
    
    def square_clicked(self, square_index):
        """Handle square click"""
        if self.game_mode == "ai_vs_ai" or self.board.is_game_over():
            return
        
        # Only allow moves on human's turn
        if self.board.turn != self.human_color and self.game_mode == "human_vs_ai":
            return
        
        if self.selected_square is None:
            # Select a piece
            piece = self.board.piece_at(square_index)
            if piece and piece.color == self.board.turn:
                self.selected_square = square_index
                self.update_display()
        else:
            # Try to make a move
            if self.is_legal_destination(square_index):
                move = chess.Move(self.selected_square, square_index)
                
                # Handle pawn promotion (auto-promote to Queen for simplicity)
                piece = self.board.piece_at(self.selected_square)
                if (piece.piece_type == chess.PAWN and
                    ((piece.color == chess.WHITE and chess.square_rank(square_index) == 7) or
                     (piece.color == chess.BLACK and chess.square_rank(square_index) == 0))):
                    move = chess.Move(self.selected_square, square_index, chess.QUEEN)
                
                self.make_move(move)
                
                # Schedule AI move
                if self.game_mode == "human_vs_ai" and not self.board.is_game_over():
                    self.root.after(300, self.make_ai_move)
            
            # Deselect
            self.selected_square = None
            self.update_display()
    
    def make_move(self, move):
        """Make a move on the board"""
        move_text = format_move(self.board, move)
        self.board.push(move)
        
        # Add to move history
        move_number = (len(self.board.move_stack) + 1) // 2
        if self.board.turn == chess.BLACK:  # White just moved
            display_text = f"{move_number}. {move_text}"
        else:  # Black just moved
            display_text = f"   {move_text}"
        
        self.move_listbox.insert(tk.END, display_text)
        self.move_listbox.see(tk.END)
        
        self.update_display()
    
    def make_ai_move(self):
        """Make an AI move"""
        self.ai_label.config(text="AI is thinking...")
        self.root.update()
        
        ai_move = self.engine.get_best_move(self.board)
        
        if ai_move:
            move_text = format_move(self.board, ai_move)
            self.ai_label.config(text=f"AI played: {move_text}\n"
                                    f"Evaluated: {self.engine.nodes_evaluated:,} nodes")
            self.make_move(ai_move)
        else:
            messagebox.showerror("Error", "AI couldn't find a move!")
    
    def new_game(self, human_color):
        """Start a new game"""
        self.human_color = human_color
        self.game_mode = "human_vs_ai"
        self.reset_board()
        
        color_name = "White" if human_color == chess.WHITE else "Black"
        messagebox.showinfo("New Game", f"New game started!\nYou are playing as {color_name}.")
        
        # If playing as Black, AI goes first
        if human_color == chess.BLACK:
            self.root.after(1000, self.make_ai_move)
    
    def ai_vs_ai(self):
        """Start AI vs AI game"""
        self.game_mode = "ai_vs_ai"
        self.reset_board()
        messagebox.showinfo("AI vs AI", "Starting AI vs AI game.\nClick OK to begin.")
        self.ai_vs_ai_loop()
    
    def ai_vs_ai_loop(self):
        """AI vs AI game loop"""
        if self.game_mode != "ai_vs_ai" or self.board.is_game_over():
            return
        
        self.make_ai_move()
        
        # Continue the loop
        if not self.board.is_game_over():
            self.root.after(2000, self.ai_vs_ai_loop)
    
    def undo_move(self):
        """Undo the last move(s)"""
        if len(self.board.move_stack) == 0:
            messagebox.showwarning("Undo", "No moves to undo!")
            return
        
        # Undo AI move
        if len(self.board.move_stack) > 0:
            self.board.pop()
            self.move_listbox.delete(tk.END)
        
        # Undo human move in human vs AI mode
        if (self.game_mode == "human_vs_ai" and 
            len(self.board.move_stack) > 0 and 
            self.board.turn == self.human_color):
            self.board.pop()
            self.move_listbox.delete(tk.END)
        
        self.selected_square = None
        self.ai_label.config(text="")
        self.update_display()
    
    def reset_board(self):
        """Reset to starting position"""
        self.board = chess.Board()
        self.selected_square = None
        self.move_listbox.delete(0, tk.END)
        self.ai_label.config(text="")
        self.update_display()
    
    def get_hint(self):
        """Get a move hint from the AI"""
        if self.board.is_game_over() or self.board.turn != self.human_color:
            messagebox.showinfo("Hint", "No hint available right now.")
            return
        
        self.ai_label.config(text="Calculating hint...")
        self.root.update()
        
        hint_move = self.engine.get_best_move(self.board)
        if hint_move:
            hint_text = format_move(self.board, hint_move)
            messagebox.showinfo("Hint", f"Consider playing: {hint_text}")
            self.ai_label.config(text="")
        else:
            messagebox.showinfo("Hint", "No good moves found!")
    
    def set_difficulty(self):
        """Set AI difficulty"""
        difficulty_window = tk.Toplevel(self.root)
        difficulty_window.title("Set Difficulty")
        difficulty_window.geometry("300x250")
        
        tk.Label(difficulty_window, text="Choose AI Difficulty:", 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        difficulty_var = tk.IntVar(value=self.engine.depth)
        
        difficulties = [
            (1, "Beginner (Depth 1)"),
            (2, "Easy (Depth 2)"),
            (3, "Medium (Depth 3)"),
            (4, "Hard (Depth 4)"),
            (5, "Expert (Depth 5)"),
            (6, "Master (Depth 6)")
        ]
        
        for depth, name in difficulties:
            tk.Radiobutton(difficulty_window, text=name, variable=difficulty_var, 
                          value=depth).pack(anchor="w", padx=20)
        
        def apply_difficulty():
            new_depth = difficulty_var.get()
            self.engine.set_depth(new_depth)
            difficulty_window.destroy()
            messagebox.showinfo("Difficulty", f"Difficulty set to depth {new_depth}")
        
        tk.Button(difficulty_window, text="Apply", command=apply_difficulty).pack(pady=20)
    
    def show_help(self):
        """Show help information"""
        help_text = """How to Play:

1. Click on a piece to select it
2. Click on a highlighted square to move
3. The game follows standard chess rules

Controls:
• Use the Game menu to start new games
• Undo Move: Take back your last move
• Get Hint: Ask the AI for a suggestion
• Set Difficulty: Adjust AI strength

The AI uses Minimax with Alpha-Beta pruning
to find the best moves. Higher difficulty
levels search deeper but take longer."""
        
        messagebox.showinfo("How to Play", help_text)
    
    def show_about(self):
        """Show about information"""
        about_text = """Chess AI - Minimax Algorithm

This chess game features:
• Complete chess rule implementation
• AI using Minimax with Alpha-Beta pruning
• Adjustable difficulty levels
• Human vs AI and AI vs AI modes

The AI evaluates positions using:
• Material count
• Piece positioning
• Mobility and tactics

Created for educational purposes to
demonstrate game AI algorithms."""
        
        messagebox.showinfo("About Chess AI", about_text)
    
    def run(self):
        """Start the GUI"""
        self.root.geometry("650x500")
        self.root.resizable(False, False)
        
        # Welcome message
        messagebox.showinfo("Welcome", "Welcome to Chess AI!\n\nUse the Game menu to start playing.")
        
        self.root.mainloop()

if __name__ == "__main__":
    game = ChessGUI()
    game.run()