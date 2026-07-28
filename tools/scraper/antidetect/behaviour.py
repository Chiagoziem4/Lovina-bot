from __future__ import annotations
import asyncio, random
async def human_delay(min_sec=0.5,max_sec=2.0): await asyncio.sleep(random.uniform(min_sec,max_sec))
def compute_delay(base_delay,randomise=True): return max(base_delay+(random.uniform(0.1,0.8) if randomise else 0),0.0)
async def simulate_scroll(page,scrolls=3):
    vh=await page.evaluate("window.innerHeight")
    for _ in range(scrolls): await page.mouse.wheel(0,random.randint(max(200,vh//3),vh)); await human_delay(0.4,1.2)
async def simulate_mouse_move(page): await page.mouse.move(random.randint(120,1200),random.randint(120,800)); await human_delay(0.1,0.4)
