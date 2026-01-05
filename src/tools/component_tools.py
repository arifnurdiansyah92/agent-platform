"""Component management tools for frontend interaction."""

import json
import logging

from livekit.agents import RunContext, function_tool

from src.config import RPC_METHOD_COMPONENT
from src.models import UserData

logger = logging.getLogger("agent.tools.component")


@function_tool
async def create_component(context: RunContext[UserData], content: str):
    """Create a component that store text and display it to the user

    Args:
        content: The text that want to be displayed
    """
    userdata = context.userdata
    component = userdata.add_component(content)

    # Get the room from the userdata
    if not userdata.ctx or not userdata.ctx.room:
        return "Created a component, but couldn't access the room to send it"
    room = userdata.ctx.room

    # Get the first participant in the room (should be the client)
    participants = room.remote_participants
    if not participants:
        return "Created a component, but no participants found to send it to"

    # Get the first participant from the dictionary of remote participant
    participant = next(iter(participants.values()), None)
    if not participant:
        return "Created a component, but couldn't get the first participant"
    payload = {
        "action": "show",
        "id": component.id,
        "content": component.content,
        "index": len(userdata.components) - 1,
    }

    # Make sure payload is properly serialized
    json_payload = json.dumps(payload)
    logger.info(f"Sending component payload: {json_payload}")
    await room.local_participant.perform_rpc(
        destination_identity=participant.identity,
        method=RPC_METHOD_COMPONENT,
        payload=json_payload,
    )

    return f"I've created a component with the content: {content}"


@function_tool
async def toggle_component(context: RunContext[UserData], component_id: str):
    """Toggle display of the component (show/hide)

    Args:
        component_id: The ID of the component to be toggled
    """
    userdata = context.userdata
    component = userdata.toggle_component(component_id)

    if not component:
        return f"Component with ID {component_id} not found"

    # Get the room from the userdata
    if not userdata.ctx or not userdata.ctx.room:
        return "Toggled the component, but couldn't access the room to send it"
    room = userdata.ctx.room

    # Get the first participant in the room (should be the client)
    participants = room.remote_participants
    if not participants:
        return "Toggled the component, but no participants found to send it to"

    # Get the first participant from the dictionary of remote participants
    participant = next(iter(participants.values()), None)
    if not participant:
        return "Toggled the component, but couldn't get the first participant."
    payload = {"action": "toggle", "id": component.id}

    # Make sure payload is properly serialized
    json_payload = json.dumps(payload)
    logger.info(f"Send toggle component payload: {json_payload}")
    await room.local_participant.perform_rpc(
        destination_identity=participant.identity,
        method=RPC_METHOD_COMPONENT,
        payload=json_payload,
    )

    return f"I've toggled the component to {'show' if component.is_showed else 'hide'} the component"
