"""Math teacher assistant with canvas interaction capabilities."""

from livekit.agents import Agent

from src.config import MATH_TEACHER_INSTRUCTIONS
from src.tools import (
    get_user_data,
    hide_illustration,
    set_user_data,
    show_illustration,
)
from src.tools.canvas_tools import (
    analyze_math_drawing,
    clear_canvas,
    get_canvas_drawing,
    highlight_canvas_area,
)


class MathTeacherAssistant(Agent):
    """Math teacher assistant with canvas and visual learning capabilities."""

    def __init__(self, instructions: str = MATH_TEACHER_INSTRUCTIONS) -> None:
        """Initialize the math teacher assistant.

        Args:
            instructions: Custom instructions. Defaults to MATH_TEACHER_INSTRUCTIONS.
        """
        super().__init__(instructions=instructions)

    # Register user tools
    set_user_data = set_user_data
    get_user_data = get_user_data

    # Register illustration tools
    show_illustration = show_illustration
    hide_illustration = hide_illustration

    # Register canvas tools
    get_canvas_drawing = get_canvas_drawing
    analyze_math_drawing = analyze_math_drawing
    clear_canvas = clear_canvas
    highlight_canvas_area = highlight_canvas_area
