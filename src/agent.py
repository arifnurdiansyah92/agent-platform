"""Main agent CLI - delegates to the default agent for backward compatibility.

For production use, run specific agents directly:
    python src/agents/default.py dev
    python src/agents/math_teacher.py dev
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.default import cli, entrypoint, prewarm
from livekit.agents import WorkerOptions

# This file delegates to the default agent for backward compatibility
# Direct usage: python src/agent.py dev

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
