"""Agent tools package."""

from .canvas_tools import (
    analyze_math_drawing,
    clear_canvas,
    get_canvas_drawing,
    highlight_canvas_area,
)
from .component_tools import create_component, toggle_component
from .illustration_tools import hide_illustration, show_illustration
from .user_tools import get_user_data, set_user_data

__all__ = [
    "create_component",
    "toggle_component",
    "show_illustration",
    "hide_illustration",
    "set_user_data",
    "get_user_data",
    "get_canvas_drawing",
    "analyze_math_drawing",
    "clear_canvas",
    "highlight_canvas_area",
]
