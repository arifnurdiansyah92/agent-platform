"""Factory for creating different agent types."""

from typing import Literal

from livekit.agents import Agent

from src.assistants import Assistant, MathTeacherAssistant

AgentType = Literal["default", "math_teacher"]


def create_agent(agent_type: AgentType = "default", custom_instructions: str | None = None) -> Agent:
    """Create an agent instance based on the specified type.

    Args:
        agent_type: The type of agent to create. Options:
            - "default": Standard voice assistant (Vyna)
            - "math_teacher": Math teacher with canvas capabilities
        custom_instructions: Optional custom instructions to override defaults

    Returns:
        An Agent instance configured for the specified type

    Examples:
        >>> # Create default agent
        >>> agent = create_agent()

        >>> # Create math teacher agent
        >>> agent = create_agent("math_teacher")

        >>> # Create with custom instructions
        >>> agent = create_agent("math_teacher", "You are a geometry specialist...")
    """
    if agent_type == "math_teacher":
        if custom_instructions:
            return MathTeacherAssistant(instructions=custom_instructions)
        return MathTeacherAssistant()

    elif agent_type == "default":
        if custom_instructions:
            return Assistant(instructions=custom_instructions)
        return Assistant()

    else:
        raise ValueError(
            f"Unknown agent type: {agent_type}. "
            f"Valid options are: 'default', 'math_teacher'"
        )


# Convenience functions for specific agent types
def create_default_agent(custom_instructions: str | None = None) -> Assistant:
    """Create a default voice assistant agent.

    Args:
        custom_instructions: Optional custom instructions

    Returns:
        Assistant instance
    """
    return create_agent("default", custom_instructions)


def create_math_teacher_agent(custom_instructions: str | None = None) -> MathTeacherAssistant:
    """Create a math teacher agent with canvas capabilities.

    Args:
        custom_instructions: Optional custom instructions

    Returns:
        MathTeacherAssistant instance
    """
    return create_agent("math_teacher", custom_instructions)
