# Tetris (Python 3 + Pygame)

Classic Tetris project updated to run with Python 3 on macOS, Windows, and Linux.

## Requirements

- Python 3.10+
- `pygame` (see `requirements.txt`)

## Setup

```bash
python3 -m pip install -r requirements.txt
```

## Run

macOS/Linux:

```bash
./start.sh
```

or:

```bash
python3 source/tetris.py
```

Windows (PowerShell):

```powershell
py -3 source\tetris.py
```

## Controls

- Left Arrow: move left
- Right Arrow: move right
- Up Arrow: rotate
- Space: drop faster

## Font mode

The game supports font fallback modes via `TETRIS_FONT_MODE`:

- `auto` (default): best effort per platform
- `original`: force original/system font rendering
- `bitmap`: force built-in bitmap font (most reliable fallback)

Examples:

```bash
TETRIS_FONT_MODE=original ./start.sh
TETRIS_FONT_MODE=bitmap ./start.sh
```
