# Refactor a Sudoku Game written in Python Flask

Use this simple Sudoku game as a starting point to practice GitHub Copilot while modernizing a Python Flask Sudoku application. The project focuses on refactoring the codebase, improving maintainability, and implementing additional gameplay features.

---

# Getting Started

## Dependencies

- Modern web browser (Chrome, Firefox, Edge, etc.)
- Python 3

## Installation

1. Fork this repository to your GitHub account.
2. Clone your forked repository.
3. Navigate to the `starter` directory.

```bash
cd starter
```

4. Create and activate a virtual environment.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

5. Install dependencies.

```bash
pip install -r requirements.txt
```

6. Start the application.

```bash
python -m starter.app
```

7. Run the test suite.

```bash
python -m pytest -q
```

8. Open:

```
http://127.0.0.1:5000
```

---

# Features Implemented

The Sudoku application includes the following features:

- Refactored Flask application structure
- Pytest testing framework
- Sudoku puzzle generator with a unique solution
- Difficulty selector (Easy, Medium, Hard)
- Immediate input validation
- Check Puzzle button
- Hint system
- Game timer
- Puzzle completion detection
- Top 10 leaderboard using browser localStorage
- Dark mode
- Responsive layout
- Alternating colors for 3×3 Sudoku blocks

---

# Responsible GitHub Copilot Use

GitHub Copilot was used as a development assistant throughout this project.

For every milestone:

- Reviewed Copilot suggestions before accepting them.
- Verified generated code manually.
- Modified or rejected suggestions when necessary.
- Tested every feature using pytest.
- Performed manual testing before keeping the generated edits.

Copilot was used to improve development productivity, while implementation decisions, debugging, testing, and validation were completed by the developer.

---

# Example of Responsible Copilot Usage

One example occurred after the application was refactored into a Python package.

Initially, running:

```bash
python app.py
```

resulted in an ImportError because the project now used relative imports.

Instead of accepting the generated solution without verification, the issue was investigated and corrected by launching the application as a package:

```bash
python -m starter.app
```

The application and all tests were then verified successfully before continuing development.

This demonstrates that Copilot suggestions were evaluated and validated instead of being accepted automatically.

---

# GitHub Copilot Development Milestones

The `Screenshots` folder documents the GitHub Copilot workflow for each milestone.

Included screenshots:

- Testing framework setup
- Refactoring project structure
- Difficulty selector
- Unique Sudoku solution generation
- Immediate input validation
- Check Puzzle button
- Hint feature
- Timer implementation
- Puzzle completion detection
- Top 10 leaderboard
- Dark mode
- Responsive layout
- Alternating 3×3 Sudoku block styling

---

# Screenshot Naming

Screenshots use descriptive filenames, including:

- copilot_testing_framework.png
- copilot_refactoring_structure.png
- copilot_difficulty_selector.png
- copilot_unique_solution_prompt.png
- copilot_live_validation.png
- copilot_check_puzzle_button.png
- copilot_hint_feature.png
- copilot_timer_feature.png
- copilot_completion_detection.png
- copilot_top10_scores.png
- copilot_dark_mode.png
- copilot_responsive_layout.png
- copilot_grid_styling.png

---

# Testing

The project was tested using Pytest throughout development.

Run:

```bash
python -m pytest -q
```

All implemented features were verified through automated tests and manual testing.

---

# References

GitHub Copilot Best Practices

https://docs.github.com/en/copilot/using-github-copilot/best-practices-for-using-github-copilot

Responsible Use of GitHub Copilot

https://docs.github.com/en/copilot/responsible-use-of-github-copilot-features

Configuring GitHub Copilot

https://docs.github.com/en/copilot/configuring-github-copilot

GitHub Blog – Copilot Instructions

https://github.blog/ai-and-ml/github-copilot/customizing-github-copilot-with-instructions/

W3C WCAG Color and Contrast Guidelines

https://www.w3.org/WAI/WCAG21/quickref/

---

# Project Instructions

The completed project includes:

- Graceful error handling
- Unique Sudoku puzzle generation
- Timer
- Solution checker
- Difficulty selector
- Hint system
- Check Puzzle button
- Immediate validation
- Top 10 leaderboard with localStorage
- Responsive design
- Accessible UI colors
- Congratulatory completion dialog with leaderboard entry