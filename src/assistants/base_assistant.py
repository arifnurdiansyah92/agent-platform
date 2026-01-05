"""Base assistant agent implementation."""

from livekit.agents import Agent

from src.config import AGENT_INSTRUCTIONS
from src.tools import (
    create_component,
    get_user_data,
    hide_illustration,
    set_user_data,
    show_illustration,
    toggle_component,
)


class Assistant(Agent):
    """Base assistant agent with standard tools registered."""

    def __init__(self, instructions: str = AGENT_INSTRUCTIONS) -> None:
        """Initialize the assistant with instructions and tools.

        Args:
            instructions: Custom instructions for the agent. Defaults to AGENT_INSTRUCTIONS.
        """
        super().__init__(instructions=instructions)

    # Register all standard tools as methods
    set_user_data = set_user_data
    get_user_data = get_user_data
    create_component = create_component
    toggle_component = toggle_component
    show_illustration = show_illustration
    hide_illustration = hide_illustration
