import asyncio
from playwright.async_api import async_playwright
from scraper import MinesweeperScraper
from solver import CSPSolver
import time

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        scraper = MinesweeperScraper(page)
        await scraper.initialize()

        solver = CSPSolver()
        
        games_played = 0
        wins = 0
        total_time = 0.0
        start_time = time.time()
        
        while True:
            try:
                board = await scraper.get_board_state()
                game_status = await scraper.is_game_over()
                
                if game_status != 0:
                    elapsed = time.time() - start_time
                    total_time += elapsed
                    
                    if game_status == 1:
                        wins += 1
                        print(f"Game Won in {elapsed:.2f}s!")
                    else:
                        print(f"Game Lost in {elapsed:.2f}s!")
                        
                    games_played += 1
                    print(f"Stats - Played: {games_played}, Wins: {wins}, Win rate: {wins/games_played:.2%}, Avg Time: {total_time/games_played:.2f}s")
                    
                    # Only ask user if they want to play again on a win
                    if game_status == 1:
                        ans = await asyncio.to_thread(input, "Play again? (y/n): ")
                        if ans.lower().strip() != 'y':
                            print("Exiting...")
                            break
                    
                    await scraper.restart_game()
                    await asyncio.sleep(0.5) # Wait for animation
                    start_time = time.time()
                    continue

                # Check for guaranteed safe moves, mines, or the best possible guess
                safe_moves, mines, best_guess = solver.solve(board)
                
                if mines:
                    for r, c in mines:
                        await scraper.click_cell(r, c, right_click=True)

                if safe_moves:
                    # Only print if we're not spamming tiny safe moves to save terminal IO speed
                    if len(safe_moves) > 2:
                        print(f"Solver found {len(safe_moves)} 100% safe moves.")
                    for r, c in safe_moves:
                        await scraper.click_cell(r, c, right_click=False)
                    continue
                
                if best_guess:
                    r, c = best_guess
                    print(f"Forced to guess! Best mathematical guess: Row {r+1}, Col {c+1}")
                    await scraper.click_cell(r, c, right_click=False)
                    
                    await asyncio.sleep(0.1)
                    continue

                await asyncio.sleep(0.1)
                
            except Exception as e:
                # Playwright DOM disconnected mid-query (refresh race condition)
                # Ignore and retry
                await asyncio.sleep(0.1)
                continue

if __name__ == "__main__":
    asyncio.run(main())
