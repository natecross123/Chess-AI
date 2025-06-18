"""
main.py
Main entry point for the chess program
"""

import chess
from game_manager import GameManager


def main_menu():
    """
    Display and handle the main menu
    """
    print("\n" + "="*50)
    print("CHESS AI WITH MINIMAX AND ALPHA-BETA PRUNING")
    print("="*50)
    
    while True:
        print("\nMain Menu:")
        print("1. Play as White against AI")
        print("2. Play as Black against AI")
        print("3. Watch AI vs AI")
        print("4. Set difficulty level")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            play_game(chess.WHITE)
        elif choice == '2':
            play_game(chess.BLACK)
        elif choice == '3':
            ai_vs_ai()
        elif choice == '4':
            set_difficulty()
        elif choice == '5':
            print("\nThank you for playing! Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


def play_game(human_color: chess.Color):
    """
    Start a game between human and AI
    
    Args:
        human_color: Color for the human player
    """
    depth = get_current_difficulty()
    game = GameManager(engine_depth=depth)
    game.play_human_vs_ai(human_color)


def ai_vs_ai():
    """
    Start a game between two AI engines
    """
    print("\nAI vs AI Setup")
    
    try:
        depth1 = int(input("Enter depth for White AI (1-8): "))
        depth1 = max(1, min(depth1, 8))
        
        depth2 = int(input("Enter depth for Black AI (1-8): "))
        depth2 = max(1, min(depth2, 8))
        
        game = GameManager()
        game.play_ai_vs_ai(depth1, depth2)
    except ValueError:
        print("Invalid input. Using default depths (3 vs 3)")
        game = GameManager()
        game.play_ai_vs_ai(3, 3)


# Global difficulty setting
current_difficulty = 3


def get_current_difficulty() -> int:
    """Get the current difficulty level"""
    global current_difficulty
    return current_difficulty


def set_difficulty():
    """
    Set the AI difficulty level
    """
    global current_difficulty
    
    print(f"\nCurrent difficulty: {current_difficulty}")
    print("Difficulty levels:")
    print("1 - Beginner (depth 1)")
    print("2 - Easy (depth 2)")
    print("3 - Medium (depth 3)")
    print("4 - Hard (depth 4)")
    print("5 - Expert (depth 5)")
    print("6 - Master (depth 6)")
    
    try:
        level = int(input("Enter difficulty level (1-6): "))
        if 1 <= level <= 6:
            current_difficulty = level
            print(f"Difficulty set to level {level}")
        else:
            print("Invalid level. Keeping current difficulty.")
    except ValueError:
        print("Invalid input. Keeping current difficulty.")


if __name__ == "__main__":
    # Print instructions
    print("\nWelcome to Chess AI!")
    print("\nThis chess engine uses the Minimax algorithm with Alpha-Beta pruning")
    print("to search for the best moves. The search depth determines the")
    print("strength of the AI - higher depths mean stronger play but slower moves.")
    
    print("\nFeatures:")
    print("- Complete chess game implementation")
    print("- Minimax algorithm with Alpha-Beta pruning")
    print("- Advanced position evaluation")
    print("- Move ordering for better pruning efficiency")
    print("- Adjustable difficulty levels")
    
    # Start the main menu
    main_menu()