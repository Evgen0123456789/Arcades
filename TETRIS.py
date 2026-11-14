import asyncio
import numpy as np
import random

# Global state
field = None
piece = None
pos = None
score = 0
game_running = True

SHAPES = [
    np.array([[1, 1, 1, 1]], dtype=np.int8),
    np.array([[1, 1], [1, 1]], dtype=np.int8),
    np.array([[0, 1, 0], [1, 1, 1]], dtype=np.int8),
    np.array([[1, 0, 0], [1, 1, 1]], dtype=np.int8),
    np.array([[0, 0, 1], [1, 1, 1]], dtype=np.int8),
    np.array([[0, 1, 1], [1, 1, 0]], dtype=np.int8),
    np.array([[1, 1, 0], [0, 1, 1]], dtype=np.int8),
]

def init_game(H, W):
    global field, score, game_running
    field = np.zeros((H, W), dtype=np.int8)
    score = 0
    game_running = True

def spawn_piece():
    global piece, pos
    piece = random.choice(SHAPES).copy()
    w = piece.shape[1]
    pos = (0, field.shape[1] // 2 - w // 2)

def can_place(y, x):
    h, w = piece.shape
    H, W = field.shape
    if y < 0 or x < 0 or y + h > H or x + w > W:
        return False
    return not np.any(field[y:y+h, x:x+w] & piece)

def lock_piece():
    global score
    y, x = pos
    h, w = piece.shape
    H, W = field.shape
    
    # Fix structure at old coordinates
    field[y:y+h, x:x+w] |= piece
    
    # Check lines only within the height of the fallen structure
    rows_to_check = range(y, min(y + h, H))
    full_rows = [r for r in rows_to_check if np.all(field[r])]
    
    if full_rows:
        mask = np.ones(H, dtype=bool)
        mask[full_rows] = False
        kept = field[mask]
        new_rows = np.zeros((len(full_rows), W), dtype=np.int8)
        field[:] = np.vstack((new_rows, kept))
        score += len(full_rows) * 100

def render():
    display = field.copy()
    if piece is not None and pos is not None:
        y, x = pos
        h, w = piece.shape
        y_end = min(y + h, display.shape[0])
        x_end = min(x + w, display.shape[1])
        y_start = max(y, 0)
        x_start = max(x, 0)
        
        p_y_start = max(0, -y)
        p_x_start = max(0, -x)
        p_y_end = p_y_start + (y_end - y_start)
        p_x_end = p_x_start + (x_end - x_start)
        
        display[y_start:y_end, x_start:x_end] |= piece[p_y_start:p_y_end, p_x_start:p_x_end]
        
    print("\033[H\033[J", end="")
    print("\n".join("".join("█" if cell else "." for cell in row) for row in display))
    print(f"Score: {score} | Commands: l, r, cw, ccw, q (press Enter)")

async def input_loop():
    global piece, pos, game_running
    loop = asyncio.get_running_loop()
    while game_running:
        cmd = await loop.run_in_executor(None, input)
        cmd = cmd.strip().lower()
        
        if cmd == 'l':
            if can_place(pos[0], pos[1] - 1):
                pos = (pos[0], pos[1] - 1)
        elif cmd == 'r':
            if can_place(pos[0], pos[1] + 1):
                pos = (pos[0], pos[1] + 1)
        elif cmd == 'cw':
            rotated = np.fliplr(piece.T)
            old_piece = piece
            piece = rotated
            if not can_place(pos[0], pos[1]):
                piece = old_piece
        elif cmd == 'ccw':
            rotated = np.flipud(piece.T)
            old_piece = piece
            piece = rotated
            if not can_place(pos[0], pos[1]):
                piece = old_piece
        elif cmd == 'q':
            game_running = False
            
        render()

async def timer_loop(speed):
    global piece, pos, game_running
    while game_running:
        await asyncio.sleep(speed)
        if not game_running:
            break
            
        if can_place(pos[0] + 1, pos[1]):
            pos = (pos[0] + 1, pos[1])
        else:
            lock_piece()
            spawn_piece()
            if not can_place(pos[0], pos[1]):
                game_running = False
                print(f"\nGame Over! Final Score: {score}")
                break
        render()

async def main():
    H, W = 20, 10
    speed = 1 #1 -- easy, 0.5 -- hardcore
    init_game(H, W)
    spawn_piece()
    render()
    
    await asyncio.gather(input_loop(), timer_loop(speed))

if __name__ == "__main__":
    asyncio.run(main())
