class TetrisVisualization {
    constructor(containerId, width, height) {
        this.container = d3.select(`#${containerId}`);
        this.width = width;
        this.height = height;
        this.cellSize = 20;
        this.board = [];
        this.currentMove = -1;
        this.moves = [];

        this.svg = this.container.append('svg')
            .attr('width', this.width * this.cellSize)
            .attr('height', this.height * this.cellSize);
    }

    setBoard(board) {
        this.board = board;
        this.drawBoard();
    }

    setMoves(moves) {
        this.moves = moves;
        this.currentMove = -1;
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
    }

    nextMove() {
        if (this.currentMove < this.moves.length - 1) {
            this.currentMove++;
            this.applyMove(this.moves[this.currentMove]);
            this.drawBoard();
        }
    }

    previousMove() {
        if (this.currentMove > -1) {
            this.undoMove(this.moves[this.currentMove]);
            this.currentMove--;
            this.drawBoard();
        }
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

    undoMove(move) {
        // For simplicity, we'll just revert to the initial board state
        // and replay all moves up to the current one
        this.board = this.moves[0].slice();
        for (let i = 0; i < this.currentMove; i++) {
            this.applyMove(this.moves[i + 1]);
        }
    }

    getTetromino(tetromino, rotation) {
        // Implement this method to return the correct tetromino shape
        // based on the tetromino type and rotation
        // This is a placeholder implementation
        return [[1, 1], [1, 1]];
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
        let linesCleared = 0;
        for (let r = this.height - 1; r >= 0; r--) {
            if (this.board[r].every(cell => cell === 1)) {
                this.board.splice(r, 1);
                this.board.unshift(new Array(this.width).fill(0));
                linesCleared++;
            }
        }
    }
}
