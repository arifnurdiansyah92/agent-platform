"""User data management tools."""

import logging

from livekit.agents import RunContext, function_tool

from src.models import UserData

logger = logging.getLogger("agent.tools.user")


@function_tool
async def set_user_data(context: RunContext[UserData], name: str, age: int):
    """Store the user's name and age in this session

    Args:
        name: Name of the user
        age: Age of the user
    """
    userdata = context.userdata
    userdata.set_user_info(name, age)

    return f"Okay, now I will remember your name is {name} and you are {age} year old."


@function_tool
async def get_user_data(context: RunContext[UserData]):
    """Get the current session user name and age"""
    userdata = context.userdata
    user_info = userdata.get_user_info()

    if user_info:
        return f"Your name: {user_info.name} and your age: {user_info.age}"
    return "I don't know your name. Please introduce your name and your age"
