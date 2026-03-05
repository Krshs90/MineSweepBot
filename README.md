# 🤖 MineSweepBot — The Stockfish of Minesweeper

An advanced algorithmic Minesweeper bot that plays Expert mode on [minesweeperonline.com](https://minesweeperonline.com/) with mathematically perfect precision.

> Created by **[Krshs90](https://github.com/Krshs90)**
>
> Bug fixed by **Google Antigravity**

---

## 🧠 How It Works

This bot doesn't use machine learning or guesswork — it uses **pure mathematics** to solve Minesweeper optimally.

### Core Algorithm

1. **Deterministic Pass** — Scans all numbered cells and instantly identifies tiles that are 100% safe or 100% mines using simple constraint logic.

2. **CSP Island Decomposition** — Groups all frontier cells (unknown cells touching numbers) into independent "islands" using graph connectivity. Each island is solved separately, preventing exponential blowup.

3. **Exhaustive Backtracking** — For each island, the solver tests every valid mine configuration against the numbered constraints, collecting exact statistics.

4. **Global Subset-Sum DP** — Combines island results using polynomial multiplication and cross-references against the global mine count (99 mines in Expert). This produces the **exact probability** of a mine at every single unrevealed tile on the board — including "ocean" cells (tiles not touching any number).

5. **Mathematically Perfect Guesses** — When forced to guess, the bot clicks the tile with the absolute lowest mine probability across the entire board, calculated to exact decimal precision.

6. **O(N) Heuristic Fallback** — If an island exceeds 30,000 backtracking iterations (NP-Complete edge case), the solver gracefully falls back to a fast local probability heuristic to keep execution under 2ms.

### Browser Automation

- Uses **Playwright** to control a real Chromium browser
- Reads the entire 16×30 grid in a single JavaScript injection (~1ms)
- Clicks cells at maximum Playwright speed
- Auto-restarts on losses, pauses on wins for user review

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/Krshs90/MineSweepBot.git
cd MineSweepBot

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Run the Bot

```bash
python main.py
```

A Chromium window will open, navigate to Minesweeper Online, and the bot will start solving Expert boards automatically. On a win, it will pause and ask if you want to continue. On a loss, it instantly restarts.

---

## 📁 Project Structure

| File | Description |
|---|---|
| `main.py` | Game loop — orchestrates scraping, solving, and clicking |
| `solver.py` | Advanced CSP + DP probability engine |
| `scraper.py` | Playwright browser automation and DOM parsing |

---

## 📊 Performance

| Metric | Value |
|---|---|
| Target | Expert mode (16×30, 99 mines) |
| Solve Speed | ~5–15 seconds per game |
| Algorithm | Exact combinatorial probability |
| Fallback | O(N) local heuristic on massive frontiers |

---

## 🛠 Tech Stack

- **Python 3.10+**
- **Playwright** — Headless browser automation
- **NumPy** — Board state representation

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
