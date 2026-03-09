# MineSweepBot

An advanced algorithmic Minesweeper bot that plays Expert mode on [minesweeperonline.com](https://minesweeperonline.com/) with mathematically perfect precision.

> Created by **[Krshs90](https://github.com/Krshs90)**
>
> Bug fixed by **Google Antigravity**

---

## 🧠 How It Works


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
