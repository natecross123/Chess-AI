"""
main.py
main entry point for Chess AI 
"""

import chess
import os
import time
import sys
from game_manager import GameManager


class EnhancedTerminalUI:
    
    def __init__(self):
        # Detect terminal capabilities
        self.colors_supported = self._detect_color_support()
        self.unicode_supported = self._detect_unicode_support()
        
        # Colors for terminal output (with fallbacks)
        if self.colors_supported:
            self.colors = {
                'reset': '\033[0m', 'bold': '\033[1m', 'dim': '\033[2m',
                'red': '\033[91m', 'green': '\033[92m', 'yellow': '\033[93m',
                'blue': '\033[94m', 'purple': '\033[95m', 'cyan': '\033[96m',
                'white': '\033[97m', 'gray': '\033[90m',
                'bg_light': '\033[47m\033[30m', 'bg_dark': '\033[100m\033[37m',
            }
        else:
            # No color support - use empty strings
            self.colors = {key: '' for key in ['reset', 'bold', 'dim', 'red', 'green', 
                          'yellow', 'blue', 'purple', 'cyan', 'white', 'gray', 
                          'bg_light', 'bg_dark']}
        
        # Unicode pieces with ASCII fallback
        if self.unicode_supported:
            try:
                self.pieces = {
                    chess.PAWN: {"white": "♙", "black": "♟"},
                    chess.ROOK: {"white": "♖", "black": "♜"},
                    chess.KNIGHT: {"white": "♘", "black": "♞"},
                    chess.BISHOP: {"white": "♗", "black": "♝"},
                    chess.QUEEN: {"white": "♕", "black": "♛"},
                    chess.KING: {"white": "♔", "black": "♚"}
                }
                # Test if Unicode actually works
                test = "♔♕♖♗♘♙"
            except:
                self.unicode_supported = False
        
        if not self.unicode_supported:
            self.pieces = {
                chess.PAWN: {"white": "P", "black": "p"},
                chess.ROOK: {"white": "R", "black": "r"},
                chess.KNIGHT: {"white": "N", "black": "n"},
                chess.BISHOP: {"white": "B", "black": "b"},
                chess.QUEEN: {"white": "Q", "black": "q"},
                chess.KING: {"white": "K", "black": "k"}
            }
    
    def _detect_color_support(self):
        """Detect if terminal supports colors"""
        if os.getenv('NO_COLOR'):
            return False
        if os.getenv('FORCE_COLOR'):
            return True
        
        # Check if we're in a proper terminal
        if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
            return False
        
        # Check TERM environment variable
        term = os.getenv('TERM', '').lower()
        if any(color_term in term for color_term in ['color', 'ansi', 'xterm', 'screen']):
            return True
        
        return False
    
    def _detect_unicode_support(self):
        """Detect if terminal supports Unicode"""
        try:
            # Check locale settings
            import locale
            encoding = locale.getpreferredencoding()
            if 'utf' in encoding.lower():
                return True
        except:
            pass
        
        # Check environment variables
        for var in ['LC_ALL', 'LC_CTYPE', 'LANG']:
            value = os.getenv(var, '').lower()
            if 'utf' in value:
                return True
        
        return False
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_colored(self, text, color='reset'):
        """Print colored text with fallback"""
        color_code = self.colors.get(color, '')
        reset_code = self.colors.get('reset', '')
        print(f"{color_code}{text}{reset_code}")
    
    def print_header(self):
        """Print the main header"""
        self.clear_screen()
        
        if self.colors_supported:
            print("\n" + "="*70)
            self.print_colored("🏆 CHESS AI WITH MINIMAX AND ALPHA-BETA PRUNING 🏆", 'bold')
            print("="*70)
            
            self.print_colored("🧠 Features:", 'cyan')
            print("   • Complete chess game implementation")
            print("   • Minimax algorithm with Alpha-Beta pruning")
            print("   • Advanced position evaluation")
            print("   • Move ordering for better pruning efficiency")
            print("   • Adjustable difficulty levels (1-6)")
            print("   • Human vs AI and AI vs AI modes")
            
            if self.unicode_supported:
                self.print_colored("   • Beautiful Unicode chess pieces ♔♕♖♗♘♙", 'green')
            else:
                self.print_colored("   • ASCII chess piece display", 'yellow')
                
            print("="*70)
        else:
            # Simple header without colors
            print("\n" + "="*70)
            print("          CHESS AI WITH MINIMAX AND ALPHA-BETA PRUNING")
            print("="*70)
            print("\nFeatures:")
            print("  * Complete chess game implementation")
            print("  * Minimax algorithm with Alpha-Beta pruning")
            print("  * Advanced position evaluation")
            print("  * Adjustable difficulty levels (1-6)")
            print("  * Human vs AI and AI vs AI modes")
            print("="*70)
    
    def print_board_beautiful(self, board):
        """Print a beautiful chess board"""
        if self.colors_supported:
            print(f"\n{self.colors['cyan']}    a   b   c   d   e   f   g   h{self.colors['reset']}")
            print(f"  {self.colors['cyan']}┌───┬───┬───┬───┬───┬───┬───┬───┐{self.colors['reset']}")
        else:
            print("\n    a   b   c   d   e   f   g   h")
            print("  +---+---+---+---+---+---+---+---+")
        
        for rank in range(7, -1, -1):
            if self.colors_supported:
                row_str = f"{self.colors['cyan']}{rank + 1} │{self.colors['reset']}"
            else:
                row_str = f"{rank + 1} |"
            
            for file in range(8):
                square = chess.square(file, rank)
                piece = board.piece_at(square)
                
                # Get piece symbol
                if piece:
                    color_key = "white" if piece.color == chess.WHITE else "black"
                    symbol = self.pieces[piece.piece_type][color_key]
                    
                    # Color the pieces if supported
                    if self.colors_supported:
                        if piece.color == chess.WHITE:
                            piece_colored = f"{self.colors['white']}{symbol}{self.colors['reset']}"
                        else:
                            piece_colored = f"{self.colors['red']}{symbol}{self.colors['reset']}"
                    else:
                        piece_colored = symbol
                else:
                    piece_colored = " "
                
                # Add square with appropriate formatting
                if self.colors_supported:
                    if (rank + file) % 2 == 0:
                        square_str = f" {piece_colored} "
                    else:
                        square_str = f"{self.colors['bg_dark']} {piece_colored} {self.colors['reset']}"
                    row_str += square_str + f"{self.colors['cyan']}│{self.colors['reset']}"
                else:
                    row_str += f" {piece_colored} |"
            
            if self.colors_supported:
                row_str += f" {self.colors['cyan']}{rank + 1}{self.colors['reset']}"
            else:
                row_str += f" {rank + 1}"
            
            print(row_str)
            
            if rank > 0:
                if self.colors_supported:
                    print(f"  {self.colors['cyan']}├───┼───┼───┼───┼───┼───┼───┼───┤{self.colors['reset']}")
                else:
                    print("  +---+---+---+---+---+---+---+---+")
        
        if self.colors_supported:
            print(f"  {self.colors['cyan']}└───┴───┴───┴───┴───┴───┴───┴───┘{self.colors['reset']}")
            print(f"{self.colors['cyan']}    a   b   c   d   e   f   g   h{self.colors['reset']}\n")
        else:
            print("  +---+---+---+---+---+---+---+---+")
            print("    a   b   c   d   e   f   g   h\n")
    
    def get_difficulty_choice(self):
        """Get difficulty choice from user"""
        while True:
            if self.colors_supported:
                self.print_colored("\n⚙️  Choose AI Difficulty:", 'yellow')
            else:
                print("\nChoose AI Difficulty:")
            
            difficulties = [
                ("1", "Beginner", "Depth 1", "Instant moves, very easy"),
                ("2", "Easy", "Depth 2", "Quick thinking, easy to beat"),
                ("3", "Medium", "Depth 3", "Balanced play (~1 second)"),
                ("4", "Hard", "Depth 4", "Strong play (~3 seconds)"),
                ("5", "Expert", "Depth 5", "Very strong (~10 seconds)"),
                ("6", "Master", "Depth 6", "Extremely strong (~30 seconds)")
            ]
            
            for num, name, depth, desc in difficulties:
                if self.colors_supported:
                    self.print_colored(f"   {num}. {name} ({depth})", 'cyan')
                    print(f"      {desc}")
                else:
                    print(f"   {num}. {name} ({depth}) - {desc}")
            
            if self.colors_supported:
                choice = input(f"\n{self.colors['bold']}Enter difficulty (1-6): {self.colors['reset']}").strip()
            else:
                choice = input("\nEnter difficulty (1-6): ").strip()
            
            if choice in "123456":
                level = int(choice)
                name = difficulties[level-1][1]
                if self.colors_supported:
                    self.print_colored(f" Difficulty set to {name}!", 'green')
                else:
                    print(f"Difficulty set to {name}!")
                return level
            else:
                if self.colors_supported:
                    self.print_colored(" Please enter a number between 1 and 6", 'red')
                else:
                    print("Please enter a number between 1 and 6")


def main_menu():
    """Enhanced main menu with better UI"""
    ui = EnhancedTerminalUI()
    
    while True:
        ui.print_header()
        
        if ui.colors_supported:
            ui.print_colored("\n🎮 MAIN MENU", 'yellow')
            print("="*25) 
        else:
            print("\nMAIN MENU")
            print("="*25)
        
        menu_options = [
            ("1", "Play as White vs AI", "You control the white pieces"),
            ("2", "Play as Black vs AI", "You control the black pieces"),
            ("3", "Watch AI vs AI", "Watch two AIs play each other"),
            ("4", "Set Difficulty Level", "Adjust AI strength (1-6)"),
            ("5", "How to Play", "Game instructions and help"),
            ("6", "Exit", "Quit the program")
        ]
        
        for num, title, desc in menu_options:
            if ui.colors_supported:
                ui.print_colored(f"   {num}. {title}", 'cyan')
                print(f"      {desc}")
            else:
                print(f"   {num}. {title} - {desc}")
        
        if ui.colors_supported:
            choice = input(f"\n{ui.colors['bold']}Enter your choice (1-6): {ui.colors['reset']}").strip()
        else:
            choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            play_game(chess.WHITE, ui)
        elif choice == '2':
            play_game(chess.BLACK, ui)
        elif choice == '3':
            ai_vs_ai(ui)
        elif choice == '4':
            set_difficulty(ui)
        elif choice == '5':
            show_instructions(ui)
        elif choice == '6':
            ui.clear_screen()
            if ui.colors_supported:
                ui.print_colored("👋 Thank you for playing Chess AI! Goodbye!", 'green')
                print("\n🎮 Come back anytime for more chess fun!")
            else:
                print("Thank you for playing Chess AI! Goodbye!")
                print("Come back anytime for more chess fun!")
            break
        else:
            if ui.colors_supported:
                ui.print_colored("❌ Invalid choice. Please try again.", 'red')
            else:
                print("Invalid choice. Please try again.")
            time.sleep(1)


def play_game(human_color: chess.Color, ui: EnhancedTerminalUI):
    """Start a game between human and AI"""
    color_name = "White" if human_color == chess.WHITE else "Black"
    ai_color_name = "Black" if human_color == chess.WHITE else "White"
    
    ui.clear_screen()
    if ui.colors_supported:
        ui.print_colored(f"🎯 Starting Game: You ({color_name}) vs AI ({ai_color_name})", 'green')
    else:
        print(f"Starting Game: You ({color_name}) vs AI ({ai_color_name})")
    
    difficulty = ui.get_difficulty_choice()
    
    if ui.colors_supported:
        ui.print_colored(f"\n🚀 Starting game... Good luck!", 'yellow')
    else:
        print("\nStarting game... Good luck!")
    
    time.sleep(1)
    
    # Create enhanced game manager
    game = EnhancedGameManager(engine_depth=difficulty, ui=ui)
    game.play_human_vs_ai(human_color)
    
    input(f"\nPress Enter to return to main menu...")


def ai_vs_ai(ui: EnhancedTerminalUI):
    """Start a game between two AI engines"""
    ui.clear_screen()
    if ui.colors_supported:
        ui.print_colored("🤖 AI vs AI Battle Setup", 'yellow')
        print("="*30)
    else:
        print("AI vs AI Battle Setup")
        print("="*30)
    
    try:
        if ui.colors_supported:
            ui.print_colored("\nWhite AI Configuration:", 'cyan')
        else:
            print("\nWhite AI Configuration:")
        depth1 = ui.get_difficulty_choice()
        
        if ui.colors_supported:
            ui.print_colored("\nBlack AI Configuration:", 'purple')
        else:
            print("\nBlack AI Configuration:")
        depth2 = ui.get_difficulty_choice()
        
        if ui.colors_supported:
            ui.print_colored(f"\n🥊 Battle: Depth {depth1} vs Depth {depth2}", 'green')
            ui.print_colored("🍿 Sit back and enjoy the show!", 'yellow')
        else:
            print(f"\nBattle: Depth {depth1} vs Depth {depth2}")
            print("Sit back and enjoy the show!")
        
        time.sleep(2)
        
        game = EnhancedGameManager(ui=ui)
        game.play_ai_vs_ai(depth1, depth2)
        
    except ValueError:
        if ui.colors_supported:
            ui.print_colored("❌ Invalid input. Using default depths (3 vs 3)", 'red')
        else:
            print("Invalid input. Using default depths (3 vs 3)")
        game = EnhancedGameManager(ui=ui)
        game.play_ai_vs_ai(3, 3)
    
    input(f"\nPress Enter to return to main menu...")


def show_instructions(ui: EnhancedTerminalUI):
    """Show detailed game instructions"""
    ui.clear_screen()
    if ui.colors_supported:
        ui.print_colored("📚 HOW TO PLAY CHESS AI", 'yellow')
    else:
        print("HOW TO PLAY CHESS AI")
    print("="*50)
    
    instructions = [
        ("Basic Controls", [
            "• Enter moves using standard chess notation",
            "• Examples: e4, Nf3, Bxc4, O-O, e8=Q",
            "• Or use UCI format: e2e4, g1f3, etc.",
            "• Type 'quit' to exit anytime",
            "• Type 'board' to redraw the board"
        ]),
        
        ("Move Notation Examples", [
            "• e4      - Move pawn to e4",
            "• Nf3     - Move knight to f3", 
            "• Bxc4    - Bishop captures on c4",
            "• O-O     - Kingside castling",
            "• O-O-O   - Queenside castling", 
            "• e8=Q    - Pawn promotion to queen",
            "• e2e4    - UCI format (from-to)"
        ]),
        
        ("AI Difficulty Levels", [
            "• Beginner (1): Instant moves, random play",
            "• Easy (2): Quick moves, basic strategy",
            "• Medium (3): Balanced, good for learning",
            "• Hard (4): Strong play, thinks ahead",
            "• Expert (5): Very strong, few mistakes",
            "• Master (6): Extremely strong, near-perfect"
        ]),
        
        ("Game Modes", [
            "• Human vs AI: Test your skills against the computer",
            "• AI vs AI: Watch and learn from computer games",
            "• Adjustable difficulty: Find your perfect challenge"
        ]),
        
        ("Tips for Success", [
            "• Start with Medium difficulty (3)",
            "• Learn from your mistakes",
            "• Watch AI vs AI games to see good moves",
            "• Practice basic openings like e4 or d4",
            "• Don't rush - think before you move"
        ])
    ]
    
    for title, items in instructions:
        if ui.colors_supported:
            ui.print_colored(f"\n{title}:", 'cyan')
        else:
            print(f"\n{title}:")
        for item in items:
            print(f"  {item}")
    
    input(f"\nPress Enter to return to main menu...")


def set_difficulty(ui: EnhancedTerminalUI):
    """Set the global AI difficulty level"""
    global current_difficulty
    
    ui.clear_screen()
    if ui.colors_supported:
        ui.print_colored("⚙️  DIFFICULTY SETTINGS", 'yellow')
    else:
        print("DIFFICULTY SETTINGS")
    print("="*30)
    
    print(f"\nCurrent difficulty: {current_difficulty}")
    
    new_difficulty = ui.get_difficulty_choice()
    current_difficulty = new_difficulty
    
    if ui.colors_supported:
        ui.print_colored(f"\n✅ Global difficulty updated to level {current_difficulty}!", 'green')
    else:
        print(f"\nGlobal difficulty updated to level {current_difficulty}!")
    
    time.sleep(1)


class EnhancedGameManager(GameManager):
    """Enhanced game manager with better terminal integration"""
    
    def __init__(self, engine_depth: int = 3, ui=None):
        super().__init__(engine_depth)
        self.ui = ui or EnhancedTerminalUI()
    
    def print_board(self, board):
        """Use the enhanced board printing"""
        self.ui.print_board_beautiful(board)
    
    def print_status(self, board):
        """Print enhanced game status"""
        if board.is_game_over():
            if board.is_checkmate():
                winner = "White" if board.turn == chess.BLACK else "Black"
                if self.ui.colors_supported:
                    self.ui.print_colored(f"🏆 CHECKMATE! {winner} wins! 🏆", 'green')
                else:
                    print(f"CHECKMATE! {winner} wins!")
            elif board.is_stalemate():
                if self.ui.colors_supported:
                    self.ui.print_colored("🤝 STALEMATE! The game is a draw.", 'yellow')
                else:
                    print("STALEMATE! The game is a draw.")
            else:
                if self.ui.colors_supported:
                    self.ui.print_colored("🏁 Game Over!", 'yellow')
                else:
                    print("Game Over!")
        else:
            turn = "White" if board.turn == chess.WHITE else "Black"
            if board.is_check():
                if self.ui.colors_supported:
                    self.ui.print_colored(f"👑 {turn} to move - CHECK!", 'red')
                else:
                    print(f"{turn} to move - CHECK!")
            else:
                if self.ui.colors_supported:
                    self.ui.print_colored(f"⚡ {turn} to move", 'cyan')
                else:
                    print(f"{turn} to move")


# Global difficulty setting
current_difficulty = 3


def get_current_difficulty() -> int:
    """Get the current difficulty level"""
    global current_difficulty
    return current_difficulty


if __name__ == "__main__":
    # Print system info for  users
    ui = EnhancedTerminalUI()
    
    if ui.colors_supported:
        ui.print_colored("\n🍎 Chess AI - Optimized for Apple Silicon!", 'green')
        if ui.unicode_supported:
            ui.print_colored("✅ Unicode chess pieces supported", 'green')
        else:
            ui.print_colored("⚠️  Using ASCII pieces (Unicode not supported)", 'yellow')
    else:
        print("\nChess AI - Terminal Mode")
        print("Colors not supported - using plain text")
    
    print("\nThis chess engine uses the Minimax algorithm with Alpha-Beta pruning")
    print("to search for the best moves. The search depth determines the")
    print("strength of the AI - higher depths mean stronger play but slower moves.")
    
    print("\nFeatures:")
    print("- Complete chess game implementation")
    print("- Minimax algorithm with Alpha-Beta pruning")
    print("- Advanced position evaluation")
    print("- Move ordering for better pruning efficiency")
    print("- Adjustable difficulty levels")
    print("- Optimized for M4 Mac performance")
    
    # Start the main menu
    main_menu()