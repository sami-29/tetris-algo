/* =============================================
   tetris_visualization.js – D3 board renderer
   ============================================= */

const TETROMINO_SHAPES = {
    I: [[[1, 1, 1, 1]], [[1], [1], [1], [1]]],
    J: [[[1, 0, 0], [1, 1, 1]], [[1, 1], [1, 0], [1, 0]], [[1, 1, 1], [0, 0, 1]], [[0, 1], [0, 1], [1, 1]]],
    L: [[[0, 0, 1], [1, 1, 1]], [[1, 0], [1, 0], [1, 1]], [[1, 1, 1], [1, 0, 0]], [[1, 1], [0, 1], [0, 1]]],
    O: [[[1, 1], [1, 1]]],
    S: [[[0, 1, 1], [1, 1, 0]], [[1, 0], [1, 1], [0, 1]]],
    T: [[[0, 1, 0], [1, 1, 1]], [[1, 0], [1, 1], [1, 0]], [[1, 1, 1], [0, 1, 0]], [[0, 1], [1, 1], [0, 1]]],
    Z: [[[1, 1, 0], [0, 1, 1]], [[0, 1], [1, 1], [1, 0]]],
};

const PIECE_COLORS = {
    I: '#00cfcf',
    O: '#f0d000',
    T: '#9a00cf',
    S: '#00a000',
    Z: '#d00000',
    J: '#0050f0',
    L: '#e06000',
    empty: '#0d1a0d',
    initial: '#3a4a3a',
    falling: '#ff4081',
};

class TetrisVisualization {
    constructor(containerId, width, height) {
        this.containerId = containerId;
        this.container = d3.select(`#${containerId}`);
        this.width = width;
        this.height = height;
        this.cellSize = 30;
        this.board = [];
        this.colorBoard = [];
        this.initialFilled = [];
        this.currentMove = -1;
        this.moves = [];
        this.initialBoard = [];
        this.sequence = [];
        this.animationSpeed = 5;
        this.isPlaying = false;
        this.animationInterval = null;
        this.isAnimating = false;
        this.linesCleared = 0;
        this.goal = 0;
        this.fallingPiece = null;

        this._initSvg();
    }

    _initSvg() {
        const vw = this.width * this.cellSize;
        const vh = this.height * this.cellSize;
        this.svg = this.container.append('svg')
            .attr('viewBox', `0 0 ${vw} ${vh}`)
            .attr('preserveAspectRatio', 'xMidYMid meet')
            .style('width', '100%')
            .style('height', 'auto')
            .style('display', 'block');
    }

    // ── Public setters ───────────────────────────────────────────────────────

    setBoard(board) {
        this.initialBoard = JSON.parse(JSON.stringify(board));
        this.board = JSON.parse(JSON.stringify(board));
        // Track which cells were pre-filled so we can colour them distinctly
        this.initialFilled = board.map(row => row.map(cell => cell === 1));
        this.colorBoard = board.map(row => row.map(() => null));
        this.drawBoard();
    }

    setMoves(moves) {
        this.moves = moves;
        this.currentMove = -1;
        this.updateControlButtons();
    }

    setSequence(sequence) {
        this.sequence = sequence;
        this.updateSequenceDisplay();
    }

    setGoal(goal) {
        this.goal = goal;
        this.updateGameInfo();
    }

    setAnimationSpeed(speed) {
        this.animationSpeed = speed;
        if (this.isPlaying) {
            clearInterval(this.animationInterval);
            this._playAnimation();
        }
    }

    // ── Drawing ──────────────────────────────────────────────────────────────

    drawBoard() {
        const flatData = this.board.flat().map((val, i) => {
            const row = Math.floor(i / this.width);
            const col = i % this.width;
            let color = PIECE_COLORS.empty;
            if (val === 1) {
                color = this.colorBoard[row]?.[col] || (this.initialFilled[row]?.[col] ? PIECE_COLORS.initial : PIECE_COLORS.I);
            }
            return { val, row, col, color };
        });

        const cells = this.svg.selectAll('rect.cell').data(flatData);

        cells.enter()
            .append('rect')
            .attr('class', 'cell')
            .merge(cells)
            .attr('x', d => d.col * this.cellSize + 1)
            .attr('y', d => d.row * this.cellSize + 1)
            .attr('width', this.cellSize - 2)
            .attr('height', this.cellSize - 2)
            .attr('rx', 2)
            .attr('fill', d => d.color)
            .attr('stroke', d => d.val === 1 ? 'rgba(255,255,255,0.15)' : 'rgba(0,255,0,0.04)')
            .attr('stroke-width', 0.5);

        cells.exit().remove();

        // Always sync falling-piece overlay: draw if present, remove if not
        if (this.fallingPiece) {
            this._drawFallingPiece();
        } else {
            this.svg.selectAll('rect.falling-piece').remove();
        }
    }

    _drawFallingPiece() {
        const { shape, row, col, pieceType } = this.fallingPiece;
        const fallData = shape.flat().map((val, i) => ({
            val,
            x: (col + (i % shape[0].length)) * this.cellSize + 1,
            y: (row + Math.floor(i / shape[0].length)) * this.cellSize + 1,
        }));

        const fallingCells = this.svg.selectAll('rect.falling-piece').data(fallData);

        fallingCells.enter()
            .append('rect')
            .attr('class', 'falling-piece')
            .merge(fallingCells)
            .attr('x', d => d.x)
            .attr('y', d => d.y)
            .attr('width', this.cellSize - 2)
            .attr('height', this.cellSize - 2)
            .attr('rx', 2)
            .attr('fill', d => d.val === 1 ? PIECE_COLORS[pieceType] || PIECE_COLORS.falling : 'transparent')
            .attr('stroke', d => d.val === 1 ? 'rgba(255,255,255,0.3)' : 'none')
            .attr('stroke-width', 0.5)
            .attr('opacity', 0.85);

        fallingCells.exit().remove();
    }

    // ── Move navigation ──────────────────────────────────────────────────────

    nextMove() {
        if (this.currentMove < this.moves.length - 1 && !this.isAnimating) {
            this.currentMove++;
            this._animateMove(this.moves[this.currentMove]);
            this.updateControlButtons();
        }
    }

    previousMove() {
        if (this.currentMove > -1 && !this.isAnimating) {
            this.currentMove--;
            this.board = JSON.parse(JSON.stringify(this.initialBoard));
            this.colorBoard = this.initialBoard.map(row => row.map(() => null));
            this.initialFilled = this.initialBoard.map(row => row.map(cell => cell === 1));
            this.linesCleared = 0;
            for (let i = 0; i <= this.currentMove; i++) {
                this._applyMove(this.moves[i]);
            }
            this.drawBoard();
            this.updateSequenceDisplay();
            this.updateControlButtons();
            this.updateGameInfo();
        }
    }

    _animateMove(move) {
        this.isAnimating = true;
        const [pieceType, rotation, col] = move;
        const shape = TETROMINO_SHAPES[pieceType][rotation % TETROMINO_SHAPES[pieceType].length];
        this.fallingPiece = { shape, row: 0, col, pieceType };

        const dropInterval = setInterval(() => {
            if (this._canPlace(shape, this.fallingPiece.row + 1, col)) {
                this.fallingPiece.row++;
                this.drawBoard();
            } else {
                clearInterval(dropInterval);
                this._placePiece(shape, this.fallingPiece.row, col, pieceType);
                this.fallingPiece = null;
                // drawBoard() will call svg.selectAll('rect.falling-piece').remove()
                // because fallingPiece is now null — ghost rects are cleaned up here
                this._clearLines();
                this.drawBoard();
                this.updateSequenceDisplay();
                this.updateGameInfo();
                this.isAnimating = false;
                this.updateControlButtons();
            }
        }, 1000 / (this.animationSpeed * 2));
    }

    _applyMove(move) {
        const [pieceType, rotation, col] = move;
        const shape = TETROMINO_SHAPES[pieceType][rotation % TETROMINO_SHAPES[pieceType].length];
        let row = 0;
        while (this._canPlace(shape, row + 1, col)) row++;
        this._placePiece(shape, row, col, pieceType);
        this._clearLines();
    }

    // ── Board logic ──────────────────────────────────────────────────────────

    _canPlace(shape, row, col) {
        for (let r = 0; r < shape.length; r++) {
            for (let c = 0; c < shape[r].length; c++) {
                if (shape[r][c] === 1) {
                    if (
                        row + r >= this.height ||
                        col + c < 0 ||
                        col + c >= this.width ||
                        this.board[row + r][col + c] === 1
                    ) return false;
                }
            }
        }
        return true;
    }

    _placePiece(shape, row, col, pieceType) {
        for (let r = 0; r < shape.length; r++) {
            for (let c = 0; c < shape[r].length; c++) {
                if (shape[r][c] === 1) {
                    this.board[row + r][col + c] = 1;
                    if (this.colorBoard[row + r]) {
                        this.colorBoard[row + r][col + c] = PIECE_COLORS[pieceType] || PIECE_COLORS.falling;
                    }
                    // Once a solver-placed piece lands, it is no longer "initial"
                    if (this.initialFilled[row + r]) {
                        this.initialFilled[row + r][col + c] = false;
                    }
                }
            }
        }
    }

    _clearLines() {
        let cleared = 0;
        for (let r = this.height - 1; r >= 0; r--) {
            if (this.board[r].every(cell => cell === 1)) {
                this.board.splice(r, 1);
                this.board.unshift(new Array(this.width).fill(0));
                this.colorBoard.splice(r, 1);
                this.colorBoard.unshift(new Array(this.width).fill(null));
                this.initialFilled.splice(r, 1);
                this.initialFilled.unshift(new Array(this.width).fill(false));
                cleared++;
                r++; // re-check the same index after shift
            }
        }
        this.linesCleared += cleared;
        if (cleared) this.updateGameInfo();
    }

    // ── Playback ─────────────────────────────────────────────────────────────

    togglePlayPause() {
        this.isPlaying = !this.isPlaying;
        if (this.isPlaying) {
            if (this.currentMove >= this.moves.length - 1) this.reset();
            this._playAnimation();
        } else {
            clearInterval(this.animationInterval);
        }
        this.updateControlButtons();
    }

    _playAnimation() {
        this.animationInterval = setInterval(() => {
            if (!this.isAnimating) this.nextMove();
            if (this.currentMove >= this.moves.length - 1) {
                this.isPlaying = false;
                clearInterval(this.animationInterval);
                this.updateControlButtons();
            }
        }, 1000 / this.animationSpeed);
    }

    reset() {
        this.currentMove = -1;
        this.board = JSON.parse(JSON.stringify(this.initialBoard));
        this.colorBoard = this.initialBoard.map(row => row.map(() => null));
        this.initialFilled = this.initialBoard.map(row => row.map(cell => cell === 1));
        this.linesCleared = 0;
        this.isPlaying = false;
        clearInterval(this.animationInterval);
        this.fallingPiece = null;
        this.drawBoard();
        this.updateSequenceDisplay();
        this.updateControlButtons();
        this.updateGameInfo();
    }

    // ── UI updates ────────────────────────────────────────────────────────────

    updateSequenceDisplay() {
        d3.selectAll('.tetromino-chip').each(function () {
            const el = d3.select(this);
            const idx = parseInt(el.attr('data-index'));
            const current = idx === tetrisVis?.currentMove + 1;
            const placed = idx <= tetrisVis?.currentMove;
            el.classed('current', current);
            el.classed('placed', placed);
        });

        const currentChip = document.querySelector('.tetromino-chip.current');
        if (currentChip) {
            currentChip.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }

    updateControlButtons() {
        const isLast = this.currentMove >= this.moves.length - 1;
        const total = this.moves.length;

        d3.select('#prev-move-btn').attr('disabled', (this.currentMove <= -1 || this.isAnimating) ? true : null);
        d3.select('#next-move-btn').attr('disabled', (isLast || this.isAnimating) ? true : null);
        d3.select('#play-pause-btn')
            .text(isLast ? 'Restart' : (this.isPlaying ? 'Pause' : 'Play'))
            .classed('btn-primary', !isLast);

        const counter = document.getElementById('move-counter');
        if (counter) {
            const current = this.currentMove < 0 ? 0 : this.currentMove + 1;
            counter.textContent = `Move ${current} / ${total}`;
        }
    }

    updateGameInfo() {
        const el = document.getElementById('lines-cleared');
        if (el) el.textContent = `${this.linesCleared} / ${this.goal}`;
    }
}
