import numpy as np

# Map the visual elements to internal representations
TILE_UNKNOWN = -1
TILE_EMPTY = 0
TILE_MINE = -2 # Not visible typically, but good for internal
TILE_FLAG = -3
# Numbers 1 through 8 map directly

class MinesweeperScraper:
    def __init__(self, page):
        self.page = page
        self.rows = 16
        self.cols = 30
        self.board = np.full((self.rows, self.cols), TILE_UNKNOWN, dtype=int)

    async def initialize(self):
        """Navigate to website and handle popups/starting logic"""
        await self.page.goto("https://minesweeperonline.com/")
        # Select expert mode or handle UI
        # By default minesweeperonline is Expert usually, or we can force it
        print("Connected to Minesweeper Online")

    async def get_board_state(self):
        """Parse the DOM to get the current state of all cells"""
        # Execute a single JS query to get all class names instantly
        classes = await self.page.evaluate('''() => {
            let res = {};
            for (let r=1; r<=16; r++) {
                for (let c=1; c<=30; c++) {
                    let el = document.getElementById(r + "_" + c);
                    if (el) res[r + "_" + c] = el.className;
                }
            }
            return res;
        }''')

        for r in range(1, self.rows + 1):
            for c in range(1, self.cols + 1):
                cls = classes.get(f"{r}_{c}", "")
                
                if not cls: continue
                
                if "blank" in cls:
                    val = TILE_UNKNOWN
                elif "flagged" in cls: # square bombflagged
                    val = TILE_FLAG
                elif "open" in cls:
                    # Extracts number from "square openX"
                    parts = cls.split(" ")
                    val = TILE_EMPTY # default
                    for p in parts:
                        if p.startswith("open"):
                            num_str = p[4:]
                            if num_str.isdigit():
                                val = int(num_str)
                elif "bomb" in cls:
                    val = TILE_MINE
                else:
                    val = TILE_UNKNOWN
                    
                self.board[r-1, c-1] = val
                
        return self.board

    async def click_cell(self, row, col, right_click=False):
        """Simulate clicking a cell at row, col. row and col are 0-indexed internally."""
        element = self.page.locator(f"id={row+1}_{col+1}")
        if right_click:
            await element.click(button="right")
        else:
            await element.click()
    
    async def is_game_over(self):
        """Check if face is dead or sunglasses"""
        face = self.page.locator("id=face")
        cls = await face.get_attribute("class")
        if cls and "facedead" in cls:
            return -1 # Loss
        elif cls and "facewin" in cls:
            return 1 # Win
        return 0 # In progress
    
    async def restart_game(self):
        """Click the face to restart"""
        face = self.page.locator("id=face")
        await face.click()
