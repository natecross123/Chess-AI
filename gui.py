"""
gui.py
Web-based chess GUI using Flask - replacement for tkinter version
"""

from flask import Flask, render_template_string, request, jsonify
import chess
import json
import threading
import webbrowser
import time
import os
import sys
from chess_engine import ChessEngine
from utils import format_move

class ChessGUI:
    def __init__(self):
        self.app = Flask(__name__)
        
        # Game state
        self.board = chess.Board()
        self.engine = ChessEngine(depth=3)
        self.human_color = chess.WHITE
        self.game_mode = "human_vs_ai"
        self.move_history = []
        
        # Setup Flask routes
        self.setup_routes()
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            return render_template_string(HTML_TEMPLATE)
        
        @self.app.route('/api/board')
        def get_board():
            """Get current board state"""
            return jsonify({
                'fen': self.board.fen(),
                'turn': 'white' if self.board.turn == chess.WHITE else 'black',
                'moves': [{'from': move.from_square, 'to': move.to_square, 'san': format_move(self.board, move)} 
                         for move in self.board.legal_moves],
                'game_over': self.board.is_game_over(),
                'in_check': self.board.is_check(),
                'move_history': self.move_history,
                'human_color': 'white' if self.human_color == chess.WHITE else 'black',
                'game_mode': self.game_mode
            })
        
        @self.app.route('/api/move', methods=['POST'])
        def make_move():
            """Make a move"""
            data = request.get_json()
            
            try:
                # Parse move from UCI format
                move = chess.Move.from_uci(data['move'])
                
                if move in self.board.legal_moves:
                    # Record move
                    move_san = format_move(self.board, move)
                    self.move_history.append({
                        'move': move_san,
                        'player': 'white' if self.board.turn == chess.WHITE else 'black'
                    })
                    
                    # Make the move
                    self.board.push(move)
                    
                    return jsonify({'success': True, 'move': move_san})
                else:
                    return jsonify({'success': False, 'error': 'Illegal move'})
                    
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/ai_move', methods=['POST'])
        def get_ai_move():
            """Get AI move"""
            try:
                ai_move = self.engine.get_best_move(self.board)
                
                if ai_move:
                    move_san = format_move(self.board, ai_move)
                    self.move_history.append({
                        'move': move_san,
                        'player': 'white' if self.board.turn == chess.WHITE else 'black'
                    })
                    
                    self.board.push(ai_move)
                    
                    return jsonify({
                        'success': True,
                        'move': ai_move.uci(),
                        'san': move_san,
                        'nodes_evaluated': self.engine.nodes_evaluated,
                        'pruning_count': self.engine.pruning_count
                    })
                else:
                    return jsonify({'success': False, 'error': 'No move found'})
                    
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/new_game', methods=['POST'])
        def new_game():
            """Start a new game"""
            data = request.get_json()
            
            self.human_color = chess.WHITE if data.get('color') == 'white' else chess.BLACK
            self.game_mode = data.get('mode', 'human_vs_ai')
            self.board = chess.Board()
            self.move_history = []
            
            return jsonify({'success': True})
        
        @self.app.route('/api/undo', methods=['POST'])
        def undo_move():
            """Undo the last move(s)"""
            try:
                if len(self.board.move_stack) > 0:
                    self.board.pop()
                    if self.move_history:
                        self.move_history.pop()
                    
                    # In human vs AI, undo AI move too
                    if (self.game_mode == 'human_vs_ai' and 
                        len(self.board.move_stack) > 0 and
                        self.board.turn == self.human_color):
                        self.board.pop()
                        if self.move_history:
                            self.move_history.pop()
                
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/hint', methods=['GET'])
        def get_hint():
            """Get a move hint"""
            try:
                hint_move = self.engine.get_best_move(self.board)
                if hint_move:
                    return jsonify({
                        'success': True,
                        'hint': format_move(self.board, hint_move),
                        'move': hint_move.uci()
                    })
                else:
                    return jsonify({'success': False, 'error': 'No hint available'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/difficulty', methods=['POST'])
        def set_difficulty():
            """Set AI difficulty"""
            data = request.get_json()
            depth = int(data.get('depth', 3))
            self.engine.set_depth(depth)
            return jsonify({'success': True, 'depth': depth})
        
        @self.app.route('/api/reset', methods=['POST'])
        def reset_board():
            """Reset the board"""
            self.board = chess.Board()
            self.move_history = []
            return jsonify({'success': True})

    def run(self):
        """Start the web GUI"""
        def open_browser():
            time.sleep(1.5)  # Wait for server to start
            webbrowser.open('http://127.0.0.1:5000')
        
        # Open browser in a separate thread
        threading.Thread(target=open_browser, daemon=True).start()
        
        print("Starting Chess AI Web GUI...")
        print("Opening browser at http://127.0.0.1:5000")
        print("Press Ctrl+C to exit")
        
        try:
            # Suppress Flask development server warnings
            import logging
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.ERROR)
            
            # Use 127.0.0.1 instead of localhost and allow threading
            self.app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False, threaded=True)
        except KeyboardInterrupt:
            print("\nShutting down Chess AI...")
            sys.exit(0)

# HTML Template with embedded CSS and JavaScript
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chess AI - Minimax Algorithm</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .game-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
            padding: 30px;
            display: flex;
            gap: 30px;
            max-width: 1200px;
            backdrop-filter: blur(10px);
        }

        .board-section {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .chess-board {
            display: grid;
            grid-template-columns: repeat(8, 60px);
            grid-template-rows: repeat(8, 60px);
            border: 4px solid #8B4513;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
        }

        .square {
            width: 60px;
            height: 60px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 36px;
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
        }

        .square:hover {
            transform: scale(1.05);
            z-index: 10;
        }

        .light-square {
            background-color: #F0D9B5;
        }

        .dark-square {
            background-color: #B58863;
        }

        .selected {
            background-color: #FFFF99 !important;
            box-shadow: inset 0 0 15px rgba(255, 215, 0, 0.8);
        }

        .legal-move {
            background-color: #98FB98 !important;
        }

        .legal-move::after {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background-color: rgba(0, 128, 0, 0.6);
        }

        .last-move {
            background-color: #FFE4B5 !important;
        }

        .rank-label {
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            height: 480px;
            margin-right: 10px;
            font-weight: bold;
            color: #8B4513;
        }

        .file-label {
            display: flex;
            justify-content: space-around;
            width: 480px;
            margin-top: 10px;
            font-weight: bold;
            color: #8B4513;
        }

        .board-with-labels {
            display: flex;
            align-items: center;
        }

        .info-panel {
            min-width: 300px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .game-status {
            text-align: center;
            padding: 15px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }

        .controls {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .btn {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: all 0.3s ease;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn-secondary {
            background: linear-gradient(45deg, #ffecd2, #fcb69f);
            color: #333;
        }

        .difficulty-selector {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin: 10px 0;
        }

        .difficulty-selector select {
            padding: 8px;
            border-radius: 5px;
            border: 2px solid #ddd;
            background: white;
            font-size: 14px;
        }

        .move-history {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            max-height: 300px;
            overflow-y: auto;
            border: 2px solid #e9ecef;
        }

        .move-history h3 {
            margin-bottom: 10px;
            color: #333;
        }

        .move-list {
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.6;
        }

        .ai-info {
            background: #e8f4f8;
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #667eea;
        }

        .ai-info h3 {
            color: #333;
            margin-bottom: 10px;
        }

        .thinking {
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        .piece {
            user-select: none;
            pointer-events: none;
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(5px);
        }

        .modal-content {
            background-color: white;
            margin: 15% auto;
            padding: 30px;
            border-radius: 15px;
            width: 400px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }

        @media (max-width: 768px) {
            .game-container {
                flex-direction: column;
                padding: 15px;
            }
            
            .chess-board {
                grid-template-columns: repeat(8, 45px);
                grid-template-rows: repeat(8, 45px);
            }
            
            .square {
                width: 45px;
                height: 45px;
                font-size: 28px;
            }
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="board-section">
            <h1 style="color: #333; margin-bottom: 20px; text-align: center;">♔ Chess AI ♛</h1>
            <div class="board-with-labels">
                <div class="rank-label">
                    <div>8</div><div>7</div><div>6</div><div>5</div><div>4</div><div>3</div><div>2</div><div>1</div>
                </div>
                <div style="display: flex; flex-direction: column;">
                    <div class="chess-board" id="chessBoard"></div>
                    <div class="file-label">
                        <div>a</div><div>b</div><div>c</div><div>d</div><div>e</div><div>f</div><div>g</div><div>h</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="info-panel">
            <div class="game-status" id="gameStatus">White to move</div>
            
            <div class="difficulty-selector">
                <label for="difficulty" style="font-weight: bold; color: #333;">AI Difficulty:</label>
                <select id="difficulty" onchange="setDifficulty()">
                    <option value="1">Beginner (Depth 1)</option>
                    <option value="2">Easy (Depth 2)</option>
                    <option value="3" selected>Medium (Depth 3)</option>
                    <option value="4">Hard (Depth 4)</option>
                    <option value="5">Expert (Depth 5)</option>
                    <option value="6">Master (Depth 6)</option>
                </select>
            </div>

            <div class="controls">
                <button class="btn" onclick="newGameAsWhite()">New Game as White</button>
                <button class="btn" onclick="newGameAsBlack()">New Game as Black</button>
                <button class="btn btn-secondary" onclick="aiVsAi()">AI vs AI</button>
                <button class="btn btn-secondary" onclick="undoMove()">Undo Move</button>
                <button class="btn btn-secondary" onclick="getHint()">Get Hint</button>
                <button class="btn btn-secondary" onclick="resetBoard()">Reset Board</button>
            </div>

            <div class="move-history">
                <h3>Move History</h3>
                <div class="move-list" id="moveHistory"></div>
            </div>

            <div class="ai-info" id="aiInfo">
                <h3>AI Information</h3>
                <div id="aiStats">Ready to play!</div>
            </div>
        </div>
    </div>

    <!-- Game Over Modal -->
    <div id="gameOverModal" class="modal">
        <div class="modal-content">
            <h2 id="gameOverTitle">Game Over!</h2>
            <p id="gameOverMessage"></p>
            <div style="margin-top: 20px;">
                <button class="btn" onclick="closeModal()">OK</button>
                <button class="btn btn-secondary" onclick="newGameAsWhite(); closeModal();" style="margin-left: 10px;">New Game</button>
            </div>
        </div>
    </div>

    <script>
        // Chess pieces in Unicode
        const pieces = {
            'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
            'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚'
        };

        // Game state
        let gameState = {
            selectedSquare: null,
            legalMoves: [],
            isThinking: false,
            lastMove: null
        };

        // Convert square index to chess notation
        function indexToSquare(index) {
            const file = String.fromCharCode(97 + (index % 8)); // a-h
            const rank = 8 - Math.floor(index / 8); // 8-1
            return file + rank;
        }

        // Convert chess notation to square index
        function squareToIndex(square) {
            const file = square.charCodeAt(0) - 97; // a=0, b=1, etc.
            const rank = parseInt(square[1]) - 1; // 1=0, 2=1, etc.
            return (7 - rank) * 8 + file;
        }

        // Initialize the game
        async function initGame() {
            createBoard();
            await updateDisplay();
        }

        function createBoard() {
            const board = document.getElementById('chessBoard');
            board.innerHTML = '';

            for (let i = 0; i < 64; i++) {
                const square = document.createElement('div');
                const rank = Math.floor(i / 8);
                const file = i % 8;
                
                square.className = `square ${(rank + file) % 2 === 0 ? 'light-square' : 'dark-square'}`;
                square.dataset.index = i;
                square.onclick = () => handleSquareClick(i);
                board.appendChild(square);
            }
        }

        async function updateDisplay() {
            try {
                const response = await fetch('/api/board');
                const data = await response.json();
                
                updateBoardDisplay(data);
                updateGameStatus(data);
                updateMoveHistory(data.move_history);
                
            } catch (error) {
                console.error('Error updating display:', error);
            }
        }

        function updateBoardDisplay(data) {
            const board = document.getElementById('chessBoard');
            const squares = board.querySelectorAll('.square');
            
            // Parse FEN to get piece positions
            const fenParts = data.fen.split(' ');
            const boardFen = fenParts[0];
            const ranks = boardFen.split('/');
            
            let squareIndex = 0;
            
            for (let rank = 0; rank < 8; rank++) {
                let fileIndex = 0;
                for (let char of ranks[rank]) {
                    if (isNaN(char)) {
                        // It's a piece
                        const square = squares[squareIndex];
                        square.innerHTML = `<span class="piece">${pieces[char] || char}</span>`;
                        squareIndex++;
                        fileIndex++;
                    } else {
                        // It's a number of empty squares
                        const emptySquares = parseInt(char);
                        for (let i = 0; i < emptySquares; i++) {
                            const square = squares[squareIndex];
                            square.innerHTML = '';
                            squareIndex++;
                            fileIndex++;
                        }
                    }
                }
            }
            
            // Clear all highlighting
            squares.forEach(square => {
                square.classList.remove('selected', 'legal-move', 'last-move');
                const rank = Math.floor(square.dataset.index / 8);
                const file = square.dataset.index % 8;
                square.className = `square ${(rank + file) % 2 === 0 ? 'light-square' : 'dark-square'}`;
            });
            
            // Highlight selected square
            if (gameState.selectedSquare !== null) {
                squares[gameState.selectedSquare].classList.add('selected');
                
                // Highlight legal moves
                gameState.legalMoves.forEach(move => {
                    if (move.from === gameState.selectedSquare) {
                        squares[move.to].classList.add('legal-move');
                    }
                });
            }
            
            // Highlight last move
            if (gameState.lastMove) {
                squares[gameState.lastMove.from].classList.add('last-move');
                squares[gameState.lastMove.to].classList.add('last-move');
            }
            
            // Store legal moves for this position
            gameState.legalMoves = data.moves.map(move => ({
                from: squareToIndex(move.san.slice(0, 2) || 'a1'),
                to: squareToIndex(move.san.slice(2, 4) || 'a1'),
                uci: move.from + '' + move.to
            }));
        }

        function updateGameStatus(data) {
            const statusElement = document.getElementById('gameStatus');
            
            if (data.game_over) {
                statusElement.textContent = "Game Over";
                statusElement.classList.remove('thinking');
                
                // Show game over modal
                showGameOverModal("Game Over!", "The game has ended.");
            } else if (data.in_check) {
                statusElement.textContent = `${data.turn.charAt(0).toUpperCase() + data.turn.slice(1)} to move - CHECK!`;
                statusElement.classList.remove('thinking');
            } else {
                statusElement.textContent = `${data.turn.charAt(0).toUpperCase() + data.turn.slice(1)} to move`;
                if (gameState.isThinking) {
                    statusElement.classList.add('thinking');
                } else {
                    statusElement.classList.remove('thinking');
                }
            }
        }

        function updateMoveHistory(moveHistory) {
            const historyElement = document.getElementById('moveHistory');
            let historyHTML = '';

            for (let i = 0; i < moveHistory.length; i += 2) {
                const moveNum = Math.floor(i / 2) + 1;
                const whiteMove = moveHistory[i];
                const blackMove = moveHistory[i + 1];

                historyHTML += `${moveNum}. ${whiteMove ? whiteMove.move : ''}`;
                if (blackMove) {
                    historyHTML += ` ${blackMove.move}`;
                }
                historyHTML += '<br>';
            }

            historyElement.innerHTML = historyHTML;
            historyElement.scrollTop = historyElement.scrollHeight;
        }

        async function handleSquareClick(squareIndex) {
            if (gameState.isThinking) return;
            
            try {
                const response = await fetch('/api/board');
                const data = await response.json();
                
                // Check if it's human's turn
                const isHumanTurn = (data.turn === data.human_color) || data.game_mode === 'ai_vs_ai';
                if (data.game_mode === 'human_vs_ai' && !isHumanTurn) return;
                
                if (gameState.selectedSquare === null) {
                    // Select a square that has a piece of the current player
                    const hasLegalMoveFromThisSquare = gameState.legalMoves.some(move => move.from === squareIndex);
                    if (hasLegalMoveFromThisSquare) {
                        gameState.selectedSquare = squareIndex;
                    }
                } else if (gameState.selectedSquare === squareIndex) {
                    // Deselect
                    gameState.selectedSquare = null;
                } else {
                    // Try to make a move
                    const move = gameState.legalMoves.find(m => 
                        m.from === gameState.selectedSquare && m.to === squareIndex
                    );
                    
                    if (move) {
                        await makeMove(indexToSquare(gameState.selectedSquare) + indexToSquare(squareIndex));
                        gameState.selectedSquare = null;
                        gameState.lastMove = { from: move.from, to: move.to };
                        
                        // If human vs AI, trigger AI move after a delay
                        if (data.game_mode === 'human_vs_ai') {
                            setTimeout(makeAIMove, 500);
                        }
                    } else {
                        // Select new square if it has legal moves
                        const hasLegalMoveFromThisSquare = gameState.legalMoves.some(move => move.from === squareIndex);
                        gameState.selectedSquare = hasLegalMoveFromThisSquare ? squareIndex : null;
                    }
                }
                
                await updateDisplay();
                
            } catch (error) {
                console.error('Error handling square click:', error);
            }
        }

        async function makeMove(moveUci) {
            try {
                const response = await fetch('/api/move', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ move: moveUci })
                });
                
                const result = await response.json();
                if (!result.success) {
                    alert('Invalid move: ' + result.error);
                }
                return result.success;
                
            } catch (error) {
                console.error('Error making move:', error);
                return false;
            }
        }

        async function makeAIMove() {
            gameState.isThinking = true;
            document.getElementById('aiStats').innerHTML = '<div class="thinking">AI is thinking...</div>';
            
            try {
                const response = await fetch('/api/ai_move', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('aiStats').innerHTML = 
                        `AI played: ${result.san}<br>Nodes evaluated: ${result.nodes_evaluated.toLocaleString()}<br>Branches pruned: ${result.pruning_count.toLocaleString()}`;
                    
                    gameState.lastMove = {
                        from: squareToIndex(result.move.slice(0, 2)),
                        to: squareToIndex(result.move.slice(2, 4))
                    };
                } else {
                    document.getElementById('aiStats').innerHTML = 'AI error: ' + result.error;
                }
                
                gameState.isThinking = false;
                await updateDisplay();
                
            } catch (error) {
                console.error('Error getting AI move:', error);
                gameState.isThinking = false;
                document.getElementById('aiStats').innerHTML = 'AI error occurred';
            }
        }

        // Game control functions
        async function newGameAsWhite() {
            await fetch('/api/new_game', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ color: 'white', mode: 'human_vs_ai' })
            });
            
            gameState.selectedSquare = null;
            gameState.lastMove = null;
            document.getElementById('aiStats').textContent = 'Ready to play!';
            await updateDisplay();
        }

        async function newGameAsBlack() {
            await fetch('/api/new_game', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ color: 'black', mode: 'human_vs_ai' })
            });
            
            gameState.selectedSquare = null;
            gameState.lastMove = null;
            document.getElementById('aiStats').textContent = 'Ready to play!';
            await updateDisplay();
            
            // AI goes first when human plays as black
            setTimeout(makeAIMove, 1000);
        }

        async function aiVsAi() {
            await fetch('/api/new_game', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: 'ai_vs_ai' })
            });
            
            gameState.selectedSquare = null;
            gameState.lastMove = null;
            await updateDisplay();
            
            // Start AI vs AI loop
            aiVsAiLoop();
        }

        async function aiVsAiLoop() {
            const response = await fetch('/api/board');
            const data = await response.json();
            
            if (data.game_mode === 'ai_vs_ai' && !data.game_over) {
                await makeAIMove();
                setTimeout(aiVsAiLoop, 2000);
            }
        }

        async function undoMove() {
            try {
                const response = await fetch('/api/undo', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    gameState.selectedSquare = null;
                    gameState.lastMove = null;
                    document.getElementById('aiStats').textContent = 'Move undone';
                    await updateDisplay();
                } else {
                    alert('Cannot undo: ' + result.error);
                }
            } catch (error) {
                console.error('Error undoing move:', error);
            }
        }

        async function getHint() {
            try {
                const response = await fetch('/api/hint');
                const result = await response.json();
                
                if (result.success) {
                    alert(`Consider playing: ${result.hint}`);
                } else {
                    alert('No hint available: ' + result.error);
                }
            } catch (error) {
                console.error('Error getting hint:', error);
            }
        }

        async function resetBoard() {
            await fetch('/api/reset', { method: 'POST' });
            gameState.selectedSquare = null;
            gameState.lastMove = null;
            document.getElementById('aiStats').textContent = 'Board reset';
            await updateDisplay();
        }

        async function setDifficulty() {
            const depth = document.getElementById('difficulty').value;
            
            try {
                await fetch('/api/difficulty', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ depth: parseInt(depth) })
                });
                
                document.getElementById('aiStats').textContent = `Difficulty set to depth ${depth}`;
            } catch (error) {
                console.error('Error setting difficulty:', error);
            }
        }

        function showGameOverModal(title, message) {
            document.getElementById('gameOverTitle').textContent = title;
            document.getElementById('gameOverMessage').textContent = message;
            document.getElementById('gameOverModal').style.display = 'block';
        }

        function closeModal() {
            document.getElementById('gameOverModal').style.display = 'none';
        }

        // Initialize the game when the page loads
        window.onload = initGame;

        // Close modal when clicking outside of it
        window.onclick = function(event) {
            const modal = document.getElementById('gameOverModal');
            if (event.target === modal) {
                closeModal();
            }
        }
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    game = ChessGUI()
    game.run()