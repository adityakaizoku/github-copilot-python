// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let hintCount = 0;
let timerInterval = null;
let timerElapsedSeconds = 0;
let timerRunning = false;
const LEADERBOARD_STORAGE_KEY = 'sudoku-leaderboard';
const THEME_STORAGE_KEY = 'sudoku-theme';

function getSelectedDifficulty() {
  return document.getElementById('difficulty-select').value;
}

function getStoredTheme() {
  try {
    const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
    return storedTheme === 'dark' ? 'dark' : 'light';
  } catch (error) {
    return 'light';
  }
}

function applyTheme(theme) {
  const selectedTheme = theme === 'dark' ? 'dark' : 'light';
  document.body.dataset.theme = selectedTheme;
  document.documentElement.style.colorScheme = selectedTheme;

  const toggleButton = document.getElementById('theme-toggle');
  if (toggleButton) {
    toggleButton.textContent = selectedTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
    toggleButton.setAttribute('aria-pressed', String(selectedTheme === 'dark'));
  }

  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, selectedTheme);
  } catch (error) {
    // Ignore storage errors so the game still works offline.
  }
}

function toggleTheme() {
  const nextTheme = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
  applyTheme(nextTheme);
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.setAttribute('data-block', (Math.floor(i / 3) + Math.floor(j / 3)) % 2 === 0 ? 'even' : 'odd');
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        updateBoardValidation();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function getBoardState() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const inp = inputs[idx];
      const val = inp.disabled ? puzzle[i][j] : (inp.value ? parseInt(inp.value, 10) : 0);
      board[i][j] = val || 0;
    }
  }
  return board;
}

function formatTime(totalSeconds) {
  const safeSeconds = Math.max(0, Math.floor(totalSeconds));
  const minutes = Math.floor(safeSeconds / 60);
  const seconds = safeSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function updateHintCounter() {
  const hintCountEl = document.getElementById('hint-count');
  if (hintCountEl) {
    hintCountEl.innerText = `Hints used: ${hintCount}`;
  }
}

function updateTimerDisplay(value) {
  const timerEl = document.getElementById('timer-display');
  if (timerEl) {
    timerEl.innerText = `Time: ${value}`;
  }
}

function stopTimer() {
  if (timerInterval !== null) {
    window.clearInterval(timerInterval);
    timerInterval = null;
  }
  timerRunning = false;
}

function startTimer() {
  stopTimer();
  timerElapsedSeconds = 0;
  timerRunning = true;
  updateTimerDisplay(formatTime(timerElapsedSeconds));
  timerInterval = window.setInterval(() => {
    if (!timerRunning) return;
    timerElapsedSeconds += 1;
    updateTimerDisplay(formatTime(timerElapsedSeconds));
  }, 1000);
}

function syncTimerFromServer(timerState) {
  if (!timerState) {
    startTimer();
    return;
  }

  stopTimer();
  timerElapsedSeconds = timerState.elapsed_seconds || 0;
  timerRunning = Boolean(timerState.running);
  updateTimerDisplay(timerState.formatted_time || formatTime(timerElapsedSeconds));

  if (timerRunning) {
    timerInterval = window.setInterval(() => {
      if (!timerRunning) return;
      timerElapsedSeconds += 1;
      updateTimerDisplay(formatTime(timerElapsedSeconds));
    }, 1000);
  }
}

function updateBoardValidation() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = getBoardState();

  for (let idx = 0; idx < inputs.length; idx++) {
    const input = inputs[idx];
    if (input.disabled || input.value === '') {
      input.classList.remove('incorrect');
      continue;
    }

    const row = parseInt(input.dataset.row, 10);
    const col = parseInt(input.dataset.col, 10);
    const value = parseInt(input.value, 10);
    let isValid = true;

    for (let c = 0; c < SIZE; c++) {
      if (c !== col && board[row][c] === value) {
        isValid = false;
        break;
      }
    }
    if (isValid) {
      for (let r = 0; r < SIZE; r++) {
        if (r !== row && board[r][col] === value) {
          isValid = false;
          break;
        }
      }
    }
    if (isValid) {
      const startRow = Math.floor(row / 3) * 3;
      const startCol = Math.floor(col / 3) * 3;
      for (let r = startRow; r < startRow + 3; r++) {
        for (let c = startCol; c < startCol + 3; c++) {
          if ((r !== row || c !== col) && board[r][c] === value) {
            isValid = false;
            break;
          }
        }
        if (!isValid) {
          break;
        }
      }
    }

    input.classList.toggle('incorrect', !isValid);
  }
}

function renderLeaderboard(entries) {
  const leaderboardList = document.getElementById('leaderboard-list');
  if (!leaderboardList) return;

  leaderboardList.innerHTML = '';
  if (!entries || entries.length === 0) {
    const emptyItem = document.createElement('li');
    emptyItem.textContent = 'No leaderboard entries yet.';
    leaderboardList.appendChild(emptyItem);
    return;
  }

  entries.forEach((entry, index) => {
    const item = document.createElement('li');
    item.innerHTML = `<span>#${index + 1}</span> <strong>${entry.player_name}</strong> — ${entry.completion_time} — ${entry.difficulty_level} — hints: ${entry.hints_used}`;
    leaderboardList.appendChild(item);
  });
}

function loadLeaderboardFromStorage() {
  try {
    const raw = window.localStorage.getItem(LEADERBOARD_STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    return [];
  }
}

function saveLeaderboardToStorage(entries) {
  window.localStorage.setItem(LEADERBOARD_STORAGE_KEY, JSON.stringify(entries));
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className = 'sudoku-cell prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.className = 'sudoku-cell';
      }
    }
  }
  updateBoardValidation();
}

async function newGame() {
  const difficulty = getSelectedDifficulty();
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  hintCount = 0;
  updateHintCounter();
  document.getElementById('message').innerText = '';
  syncTimerFromServer(data.timer);
}

async function applyHint() {
  const res = await fetch('/hint', {method: 'POST'});
  const data = await res.json();
  if (data.error) {
    document.getElementById('message').innerText = data.error;
    return;
  }

  const hint = data.hint;
  puzzle[hint.row][hint.col] = hint.value;
  const input = document.querySelector(`.sudoku-cell[data-row="${hint.row}"][data-col="${hint.col}"]`);
  if (input) {
    input.value = hint.value;
    input.disabled = true;
    input.className = 'sudoku-cell prefilled';
    input.classList.remove('incorrect');
  }
  hintCount = data.hints_used;
  updateHintCounter();
  updateBoardValidation();
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      board,
      difficulty_level: getSelectedDifficulty(),
      hints_used: hintCount,
    })
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0] * SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.classList.toggle('incorrect', incorrect.has(idx));
  }
  if (incorrect.size === 0) {
    stopTimer();
    updateTimerDisplay(formatTime(timerElapsedSeconds));
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';

    const playerName = window.prompt('Enter your name for the leaderboard:', '');
    if (playerName && playerName.trim()) {
      const leaderboardRes = await fetch('/check', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          board,
          player_name: playerName.trim(),
          difficulty_level: getSelectedDifficulty(),
          hints_used: hintCount,
        })
      });
      const leaderboardData = await leaderboardRes.json();
      if (!leaderboardData.error && leaderboardData.completed) {
        const storedEntries = loadLeaderboardFromStorage();
        const mergedEntries = [...storedEntries, ...leaderboardData.leaderboard].sort((a, b) => a.completion_time_seconds - b.completion_time_seconds).slice(0, 10);
        saveLeaderboardToStorage(mergedEntries);
        renderLeaderboard(mergedEntries);
        msg.innerText = `Congratulations! You solved it and are on the leaderboard, ${playerName.trim()}!`;
      }
    }
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-puzzle').addEventListener('click', checkSolution);
  document.getElementById('hint-button').addEventListener('click', applyHint);
  document.getElementById('difficulty-select').addEventListener('change', newGame);

  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
  }

  applyTheme(getStoredTheme());
  updateHintCounter();
  renderLeaderboard(loadLeaderboardFromStorage());
  // initialize
  newGame();
});