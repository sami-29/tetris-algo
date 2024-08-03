class TetrisVisualization {
    constructor(containerId, width, height) {
        this.container = d3.select(`#${containerId}`);
        this.width = width;
        this.height = height;
        this.cellSize = 20;
        this.board = [];
        this.currentMove = 0;
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
        this.currentMove = 0;
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
        if (this.currentMove < this.moves.length) {
            // Apply the next move to the board
            // This is a placeholder, implement the actual move application logic
            this.currentMove++;
            this.drawBoard();
        }
    }

    previousMove() {
        if (this.currentMove > 0) {
            // Undo the last move on the board
            // This is a placeholder, implement the actual move undoing logic
            this.currentMove--;
            this.drawBoard();
        }
    }
}
