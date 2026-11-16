"""Start Streamlit on this PC only."""
import os
from pathlib import Path
import sys

app = Path(__file__).with_name("app.py").resolve()
os.execv(sys.executable, [sys.executable, "-m", "streamlit", "run", str(app),
                         "--server.address=127.0.0.1", "--server.port=8514",
                         "--server.headless=true", "--browser.gatherUsageStats=false"])
