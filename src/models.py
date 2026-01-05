"""Core data models for the agent platform."""

import uuid
from dataclasses import dataclass, field
from typing import Optional

from livekit.agents import JobContext


@dataclass
class UserInfo:
    """Class to represent a user information"""

    id: str
    name: str
    age: int | None


@dataclass
class Component:
    """Class to represent a FE component"""

    id: str
    content: str
    is_showed: bool = False


@dataclass
class UserData:
    """Class to store user data during a session"""

    ctx: Optional[JobContext] = None
    name: str = field(default_factory=str)
    age: int = field(default_factory=int)
    components: list[Component] = field(default_factory=list)
    # Canvas-related data
    last_canvas_drawing: Optional[dict] = None
    canvas_history: list[dict] = field(default_factory=list)

    def set_user_info(self, name: str, age: int) -> UserInfo:
        """Set user information"""
        user_info = UserInfo(id=str(uuid.uuid4()), name=name, age=age)
        self.name = name
        self.age = age
        return user_info

    def get_user_info(self) -> Optional[UserInfo]:
        """Get the user information (name and age)"""
        if self.name and (self.age is not None):
            return UserInfo(id=str(uuid.uuid4()), name=self.name, age=self.age)
        return None

    def add_component(self, content: str) -> Component:
        """Add a new component to the collection"""
        component = Component(id=str(uuid.uuid4()), content=content)
        self.components.append(component)
        return component

    def get_component(self, action_id: str) -> Optional[Component]:
        """Get a component by ID"""
        for component in self.components:
            if component.id == action_id:
                return component
        return None

    def toggle_component(self, action_id: str) -> Optional[Component]:
        """Toggle display of the component by ID"""
        component = self.get_component(action_id)
        if component:
            component.is_showed = not component.is_showed
            return component
        return None

    def save_canvas_to_history(self) -> None:
        """Save current canvas drawing to history"""
        if self.last_canvas_drawing:
            self.canvas_history.append(self.last_canvas_drawing.copy())

    def clear_canvas_data(self) -> None:
        """Clear current canvas drawing"""
        self.last_canvas_drawing = None
