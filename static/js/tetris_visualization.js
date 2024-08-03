class TetrisVisualization {
    constructor(containerId, width, height) {
        this.container = d3.select(`#${containerId}`);
        this.width = width;
        this.height = height;
        this.cellSize = 20;
        this.board = [];
        this.currentMove = -1;
        this.moves = [];
        this.initialBoard = [];
        this.sequence = [];
        this.animationSpeed = 5;
        this.isPlaying = false;
        this.animationInterval = null;

        this.svg = this.container.append('svg')
            .attr('width', this.width * this.cellSize)
            .attr('height', this.height * this.cellSize);

        this.fallingPiece = null;
    }

    setBoard(board) {
        this.initialBoard = JSON.parse(JSON.stringify(board));
        this.board = JSON.parse(JSON.stringify(board));
        this.drawBoard();
    }

    setMoves(moves) {
        this.moves = moves;
        this.currentMove = -1;
    }

    setSequence(sequence) {
        this.sequence = sequence;
        this.updateSequenceDisplay();
    }

    setAnimationSpeed(speed) {
        this.animationSpeed = speed;
        if (this.isPlaying) {
            this.togglePlayPause();
            this.togglePlayPause();
        }
    }

    drawBoard() {
        const cells = this.svg.selectAll('rect')
            .data(this.board.flat());

        cells.enter()
            .append('rect')
            .merge(cells)
            .attr('x', (d, i) => (i % this.width) * this.cellSize)
            .attr('y', (d, i) => Math.floor(i / this.width) * this.cellSize)
            .attr('width', this.cellSize - 1)
            .attr('height', this.cellSize - 1)
            .attr('fill', d => d === 1 ? '#4CAF50' : '#2C3E50');

        cells.exit().remove();

        if (this.fallingPiece) {
            this.drawFallingPiece();
        }
    }

    drawFallingPiece() {
        const fallingCells = this.svg.selectAll('.falling-piece')
            .data(this.fallingPiece.shape.flat().map((value, index) => ({
                value,
                x: (this.fallingPiece.col + index % this.fallingPiece.shape[0].length) * this.cellSize,
                y: (this.fallingPiece.row + Math.floor(index / this.fallingPiece.shape[0].length)) * this.cellSize
            })));

        fallingCells.enter()
            .append('rect')
            .attr('class', 'falling-piece')
            .merge(fallingCells)
            .attr('x', d => d.x)
            .attr('y', d => d.y)
            .attr('width', this.cellSize - 1)
            .attr('height', this.cellSize - 1)
            .attr('fill', d => d.value === 1 ? '#FF4081' : 'transparent');

        fallingCells.exit().remove();
    }

    nextMove() {
        if (this.currentMove < this.moves.length - 1) {
            this.currentMove++;
            this.animateMove(this.moves[this.currentMove]);
        }
    }

    previousMove() {
        if (this.currentMove > -1) {
            this.board = JSON.parse(JSON.stringify(this.initialBoard));
            for (let i = 0; i <= this.currentMove - 1; i++) {
                this.applyMove(this.moves[i]);
            }
            this.currentMove--;
            this.drawBoard();
            this.updateSequenceDisplay();
        }
    }

    animateMove(move) {
        const [tetromino, rotation, col] = move;
        const shape = this.getTetromino(tetromino, rotation);
        this.fallingPiece = { shape, row: 0, col };

        const dropInterval = setInterval(() => {
            if (this.canPlaceTetromino(shape, this.fallingPiece.row + 1, this.fallingPiece.col)) {
                this.fallingPiece.row++;
                this.drawBoard();
            } else {
                clearInterval(dropInterval);
                this.placeTetromino(shape, this.fallingPiece.row, this.fallingPiece.col);
                this.fallingPiece = null;
                this.clearLines();
                this.drawBoard();
                this.updateSequenceDisplay();
            }
        }, 1000 / this.animationSpeed);
    }

    applyMove(move) {
        const [tetromino, rotation, col] = move;
        const shape = this.getTetromino(tetromino, rotation);
        let row = 0;
        while (this.canPlaceTetromino(shape, row + 1, col)) {
            row++;
        }
        this.placeTetromino(shape, row, col);
        this.clearLines();
    }

    getTetromino(tetromino, rotation) {
        const shapes = {
            'I': [[[1, 1, 1, 1]], [[1], [1], [1], [1]]],
            'J': [[[1, 0, 0], [1, 1, 1]], [[1, 1], [1, 0], [1, 0]], [[1, 1, 1], [0, 0, 1]], [[0, 1], [0, 1], [1, 1]]],
            'L': [[[0, 0, 1], [1, 1, 1]], [[1, 0], [1, 0], [1, 1]], [[1, 1, 1], [1, 0, 0]], [[1, 1], [0, 1], [0, 1]]],
            'O': [[[1, 1], [1, 1]]],
            'S': [[[0, 1, 1], [1, 1, 0]], [[1, 0], [1, 1], [0, 1]]],
            'T': [[[0, 1, 0], [1, 1, 1]], [[1, 0], [1, 1], [1, 0]], [[1, 1, 1], [0, 1, 0]], [[0, 1], [1, 1], [0, 1]]],
            'Z': [[[1, 1, 0], [0, 1, 1]], [[0, 1], [1, 1], [1, 0]]]
        };
        return shapes[tetromino][rotation % shapes[tetromino].length];
    }

    canPlaceTetromino(shape, row, col) {
        for (let r = 0; r < shape.length; r++) {
            for (let c = 0; c < shape[r].length; c++) {
                if (shape[r][c] === 1) {
                    if (row + r >= this.height || col + c < 0 || col + c >= this.width || this.board[row + r][col + c] === 1) {
                        return false;
                    }
                }
            }
        }
        return true;
    }

    placeTetromino(shape, row, col) {
        for (let r = 0; r < shape.length; r++) {
            for (let c = 0; c < shape[r].length; c++) {
                if (shape[r][c] === 1) {
                    this.board[row + r][col + c] = 1;
                }
            }
        }
    }

    clearLines() {
        for (let r = this.height - 1; r >= 0; r--) {
            if (this.board[r].every(cell => cell === 1)) {
                this.board.splice(r, 1);
                this.board.unshift(new Array(this.width).fill(0));
            }
        }
    }

    togglePlayPause() {
        this.isPlaying = !this.isPlaying;
        if (this.isPlaying) {
            this.playAnimation();
        } else {
            clearInterval(this.animationInterval);
        }
    }

    playAnimation() {
        this.animationInterval = setInterval(() => {
            this.nextMove();
            if (this.currentMove >= this.moves.length - 1) {
                this.togglePlayPause();
            }
        }, 1000 / this.animationSpeed);
    }

    updateSequenceDisplay() {
        const sequenceContainer = d3.select('#sequence-display').select('div');
        sequenceContainer.selectAll('span')
            .data(this.sequence)
            .style('background-color', (d, i) => i === this.currentMove + 1 ? '#004d00' : 'transparent');
    }
}
