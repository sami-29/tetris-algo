/* =============================================
   main.js – Tetris Solver UI Logic
   ============================================= */

let tetrisVis = null;

// ── Tab management ──────────────────────────────────────────────────────────

function setTab(newTab) {
    Alpine.store('tab', newTab);
    updateURL(newTab);
    if (newTab === 'single-game') {
        if (tetrisVis) tetrisVis.reset();
        resetPlaceholders();
    }
}

function updateURL(tab) {
    const url = new URL(window.location);
    url.searchParams.set('tab', tab);
    window.history.pushState({ tab }, '', url);
}

function loadTabFromURL() {
    const tab = new URLSearchParams(window.location.search).get('tab');
    if (tab === 'simulation' || tab === 'single-game') setTab(tab);
}

window.addEventListener('load', loadTabFromURL);
window.addEventListener('popstate', (e) => {
    if (e.state?.tab) setTab(e.state.tab);
    else loadTabFromURL();
});

// ── Simulation form loading state ────────────────────────────────────────────

const simulationForm = document.querySelector('form[hx-post="/run_simulation"]');
if (simulationForm) {
    simulationForm.addEventListener('htmx:beforeRequest', () => {
        const resultsEl = document.getElementById('simulation-results');
        if (resultsEl) resultsEl.innerHTML = '';
        showSimulationLoader(true);
    });
}

function showSimulationLoader(show) {
    const loader = document.getElementById('simulation-loader');
    if (loader) loader.classList.toggle('visible', show);
}

// ── Single game form loading state ───────────────────────────────────────────

const singleGameForm = document.querySelector('form[hx-post="/run_single_game"]');
if (singleGameForm) {
    singleGameForm.addEventListener('htmx:beforeRequest', () => {
        d3.select('#tetris-board').html('');
        updateSequencePlaceholder('Loading...');
        setGameInfoPlaceholder('Loading...');
        hideControls();
        showSingleGameLoader(true);
    });
}

function showSingleGameLoader(show) {
    const loader = document.getElementById('single-game-loader');
    if (loader) loader.classList.toggle('visible', show);
}

// ── HTMX response handlers ───────────────────────────────────────────────────

htmx.on('htmx:afterSwap', (event) => {
    const targetId = event.detail.target.id;

    if (targetId === 'simulation-results') {
        showSimulationLoader(false);
        try {
            const data = JSON.parse(event.detail.xhr.response);
            if (data.error) {
                renderErrorMessage('simulation-results', data.error);
                return;
            }
            renderSimulationResults(data);
        } catch {
            renderErrorMessage('simulation-results', 'Failed to parse server response.');
        }
    }

    if (targetId === 'single-game-results') {
        showSingleGameLoader(false);
        try {
            const data = JSON.parse(event.detail.xhr.response);
            if (data.error) {
                renderErrorMessage('single-game-results', data.error);
                setGameInfoPlaceholder('Error – see message above.');
                return;
            }
            renderSingleGame(data);
        } catch {
            renderErrorMessage('single-game-results', 'Failed to parse server response.');
        }
    }
});

htmx.on('htmx:responseError', (event) => {
    showSimulationLoader(false);
    showSingleGameLoader(false);
    const targetId = event.detail.target?.id;
    const msg = 'Server error. Please try again.';
    if (targetId) renderErrorMessage(targetId, msg);
});

htmx.on('htmx:sendError', (event) => {
    showSimulationLoader(false);
    showSingleGameLoader(false);
    const targetId = event.detail.target?.id;
    const msg = 'Network error. Check your connection.';
    if (targetId) renderErrorMessage(targetId, msg);
});

// ── Simulation results renderer ──────────────────────────────────────────────

function renderSimulationResults(data) {
    const total = data.total_games;
    const won = data.winnable_games;
    const rate = total > 0 ? ((won / total) * 100).toFixed(1) : 0;

    const container = d3.select('#simulation-results');
    container.html('');

    const panel = container.append('div').attr('class', 'results-panel');
    panel.append('div').attr('class', 'results-panel-header').text('Simulation Results');

    const body = panel.append('div').attr('class', 'results-panel-body');
    const grid = body.append('div').attr('class', 'stat-grid');

    const stats = [
        { label: 'Winnable', value: won, sub: `of ${total} games` },
        { label: 'Win Rate', value: `${rate}%`, sub: 'solvable' },
        { label: 'Avg Time', value: `${data.average_time.toFixed(3)}s`, sub: 'per game' },
        { label: 'Avg Attempts', value: Math.round(data.average_attempts), sub: 'solver calls' },
    ];

    stats.forEach(({ label, value, sub }) => {
        const card = grid.append('div').attr('class', 'stat-card');
        card.append('div').attr('class', 'stat-label').text(label);
        card.append('div').attr('class', 'stat-value').text(value);
        if (sub) card.append('div').attr('class', 'stat-sub').text(sub);
    });

    // Win-rate bar
    const barWrap = body.append('div').attr('class', 'winrate-bar-wrap');
    const barLabel = barWrap.append('div').attr('class', 'winrate-bar-label');
    barLabel.append('span').text('Win Rate');
    barLabel.append('span').text(`${rate}%`);
    const track = barWrap.append('div').attr('class', 'winrate-bar-track');
    track.append('div').attr('class', 'winrate-bar-fill').style('width', '0%');
    // Animate after DOM update
    setTimeout(() => {
        d3.select('.winrate-bar-fill').style('width', `${rate}%`);
    }, 50);

    if (data.total_time !== undefined) {
        body.append('p')
            .style('font-size', '0.75rem')
            .style('color', 'var(--color-text-muted)')
            .style('margin', '12px 0 0')
            .text(`Total time: ${data.total_time}s`);
    }
}

// ── Single game renderer ─────────────────────────────────────────────────────

function renderSingleGame(data) {
    d3.select('#tetris-board').html('');
    d3.select('#single-game-results').html('');

    tetrisVis = new TetrisVisualization('tetris-board', 10, 20);
    tetrisVis.setBoard(data.initialBoard);
    tetrisVis.setMoves(data.moves);
    tetrisVis.setSequence(data.sequence);
    tetrisVis.setGoal(parseInt(data.goal));

    renderGameInfo(data);
    renderSequence(data.sequence);
    setupControlButtons();
    showControls();
}

function renderGameInfo(data) {
    const container = d3.select('#game-info');
    container.html('');

    const rows = [
        { label: 'Result', value: data.result ? 'Winnable' : 'Not Winnable', cls: data.result ? 'success' : 'failure' },
        { label: 'Failed Attempts', value: data.failedAttempts },
        { label: 'Lines Cleared', value: `0 / ${data.goal}`, id: 'lines-cleared' },
        { label: 'Total Moves', value: data.moves?.length ?? 0 },
    ];

    rows.forEach(({ label, value, cls, id }) => {
        const row = container.append('div').attr('class', 'info-row');
        row.append('span').attr('class', 'info-label').text(label);
        const valEl = row.append('span').attr('class', 'info-value');
        if (cls) valEl.classed(cls, true);
        if (id) valEl.attr('id', id);
        valEl.text(value);
    });
}

function renderSequence(sequence) {
    const display = d3.select('#sequence-display');
    display.html('<h3>Tetromino Sequence</h3>');
    const items = display.append('div').attr('class', 'sequence-items');
    sequence.forEach((piece, i) => {
        items.append('span')
            .attr('class', `tetromino-chip chip-${piece}`)
            .attr('data-index', i)
            .attr('title', `Piece ${i + 1}: ${piece}`)
            .text(piece);
    });
}

// ── Controls ─────────────────────────────────────────────────────────────────

function setupControlButtons() {
    d3.select('#prev-move-btn').on('click', () => tetrisVis?.previousMove());
    d3.select('#play-pause-btn').on('click', () => tetrisVis?.togglePlayPause());
    d3.select('#next-move-btn').on('click', () => tetrisVis?.nextMove());
    d3.select('#speed-slider').on('input', function () {
        tetrisVis?.setAnimationSpeed(this.value);
        updateSliderBackground(this);
    });
    updateSliderBackground(document.getElementById('speed-slider'));
    tetrisVis?.updateControlButtons();
}

function showControls() {
    const controls = document.querySelector('.controls');
    if (controls) controls.classList.add('visible');
}

function hideControls() {
    const controls = document.querySelector('.controls');
    if (controls) controls.classList.remove('visible');
}

function updateSliderBackground(slider) {
    if (!slider) return;
    const pct = ((slider.value - slider.min) / (slider.max - slider.min)) * 100;
    slider.style.background = `linear-gradient(to right, var(--color-accent) 0%, var(--color-accent) ${pct}%, var(--color-bg) ${pct}%, var(--color-bg) 100%)`;
}

// ── Error rendering ───────────────────────────────────────────────────────────

function renderErrorMessage(containerId, message) {
    d3.select(`#${containerId}`).html('').append('div')
        .attr('class', 'message message-error')
        .text(`Error: ${message}`);
}

// ── Placeholder helpers ───────────────────────────────────────────────────────

function resetPlaceholders() {
    d3.select('#tetris-board').html(
        '<div class="board-placeholder">' +
        '<div class="board-placeholder-icon">▦</div>' +
        '<div>Run a game to see the Tetris board</div>' +
        '</div>'
    );
    d3.select('#sequence-display').html(
        '<h3>Tetromino Sequence</h3>' +
        '<div class="sequence-items" style="color:var(--color-text-muted);font-size:0.8rem;padding:8px 0;">Run a game to see the sequence</div>'
    );
    d3.select('#game-info').html(
        '<div class="info-row" style="grid-column:1/-1;color:var(--color-text-muted);font-size:0.8rem;">Run a game to see game information</div>'
    );
    d3.select('#single-game-results').html('');
    hideControls();
}

function updateSequencePlaceholder(text) {
    d3.select('#sequence-display').html(
        `<h3>Tetromino Sequence</h3><div class="sequence-items" style="color:var(--color-text-muted);font-size:0.8rem;padding:8px 0;">${text}</div>`
    );
}

function setGameInfoPlaceholder(text) {
    d3.select('#game-info').html(
        `<div class="info-row" style="grid-column:1/-1;color:var(--color-text-muted);font-size:0.8rem;">${text}</div>`
    );
}

// ── Live board preview on input change ───────────────────────────────────────

const singleGameTab = document.getElementById('single-game-tab-content');
if (singleGameTab) {
    ['seed', 'sg-initialHeightMax', 'sg-goal', 'sg-tetrominoes'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('change', updateInitialBoard);
    });
}

function updateInitialBoard() {
    const seed = document.getElementById('seed')?.value ?? 42;
    const initialHeightMax = document.getElementById('sg-initialHeightMax')?.value ?? 7;
    const goal = document.getElementById('sg-goal')?.value ?? 8;
    const tetrominoes = document.getElementById('sg-tetrominoes')?.value ?? 40;

    fetch('/generate_initial_board', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seed, initialHeightMax, goal, tetrominoes }),
    })
        .then(res => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        })
        .then(data => {
            if (!tetrisVis) {
                tetrisVis = new TetrisVisualization('tetris-board', 10, 20);
            }
            tetrisVis.setBoard(data.board);
        })
        .catch(err => console.warn('Board preview failed:', err));
}

// ── Keyboard shortcuts ────────────────────────────────────────────────────────

document.addEventListener('keydown', (e) => {
    if (!tetrisVis) return;
    // Don't fire when typing in an input
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;
    if (Alpine.store('tab') !== 'single-game') return;

    if (e.key === 'ArrowRight') { e.preventDefault(); tetrisVis.nextMove(); }
    if (e.key === 'ArrowLeft')  { e.preventDefault(); tetrisVis.previousMove(); }
    if (e.key === ' ')          { e.preventDefault(); tetrisVis.togglePlayPause(); }
});

// Initial slider background on page load
document.addEventListener('DOMContentLoaded', () => {
    const slider = document.getElementById('speed-slider');
    if (slider) updateSliderBackground(slider);
});
