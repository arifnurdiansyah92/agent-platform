"""Math teacher agent entrypoint - specialized for canvas-based math learning."""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports when running directly
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
from livekit.agents import JobContext, JobProcess, WorkerOptions, cli
from livekit.plugins import silero

from src.session import create_agent_session, start_agent_session

logger = logging.getLogger("agent.math_teacher")

load_dotenv(".env.local")


def prewarm(proc: JobProcess):
    """Prewarm models before the agent starts.

    Args:
        proc: The job process
    """
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    """Main entrypoint for the math teacher agent.

    Args:
        ctx: The job context
    """
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "agent_type": "math_teacher",
    }

    logger.info("Starting Math Teacher Agent with canvas capabilities")

    # Create the agent session
    session = await create_agent_session(ctx)

    # Start session and wait for it to be ready
    # The session will handle connection and RPC registration
    await start_agent_session(session, ctx, agent_type="math_teacher")

    logger.info("Math Teacher Agent ready and listening")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
