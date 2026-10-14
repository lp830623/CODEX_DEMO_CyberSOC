"""Reset the local DEMO database to deterministic fixtures. Run from repository root."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.main import app
from backend.app.store import reset
reset(app.state.engine)
print("Synthetic dataset restored.")
