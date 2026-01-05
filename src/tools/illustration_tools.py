"""Illustration display tools for visual learning aids."""

import asyncio
import json
import logging

from livekit.agents import RunContext, function_tool

from src.config import AVAILABLE_ILLUSTRATIONS, RPC_METHOD_ILLUSTRATION, RPC_TIMEOUT
from src.models import UserData

logger = logging.getLogger("agent.tools.illustration")


@function_tool
async def show_illustration(context: RunContext[UserData], illustration_key: str):
    """Show an illustration/image to the user. Use this when you want to display visual aids, diagrams, or educational images.

    Available illustrations:
    - "pythagoras": Pythagorean theorem diagram (a² + b² = c²) - use for geometry, triangles, mathematics
    - "trigonometry": Trigonometry - sin, cosine, and tangent

    Args:
        illustration_key: The key of the illustration to display (e.g., "pythagoras")
    """
    userdata = context.userdata

    # Validate illustration key
    if illustration_key not in AVAILABLE_ILLUSTRATIONS:
        available_keys = ", ".join(AVAILABLE_ILLUSTRATIONS.keys())
        return f"I don't have an illustration called '{illustration_key}'. Available illustrations are: {available_keys}"

    illustration = AVAILABLE_ILLUSTRATIONS[illustration_key]
    image_url = illustration["url"]
    description = illustration["description"]

    # Get the room from the userdata
    if not userdata.ctx or not userdata.ctx.room:
        return "Cannot show illustration: couldn't access the room"
    room = userdata.ctx.room

    # Get the first participant in the room (should be the client)
    participants = room.remote_participants
    if not participants:
        return "Cannot show illustration: no participants found in the room"

    # Get the first participant from the dictionary of remote participants
    participant = next(iter(participants.values()), None)
    if not participant:
        return "Cannot show illustration: couldn't get the first participant"

    # Prepare and send RPC to show the illustration
    try:
        payload = json.dumps({"state": "show", "image_url": image_url})
        logger.info(f"Sending show illustration payload: {payload}")

        # Wrap RPC call with asyncio timeout to catch errors before Rust panic
        result = await asyncio.wait_for(
            room.local_participant.perform_rpc(
                destination_identity=participant.identity,
                method=RPC_METHOD_ILLUSTRATION,
                payload=payload,
            ),
            timeout=RPC_TIMEOUT,
        )

        response = json.loads(result)
        logger.info(f"[Illustration] Show result: {response}")

        if response.get("ok"):
            desc_msg = f" showing {description}" if description else ""
            return f"I've displayed the illustration{desc_msg} to you."
        else:
            error = response.get("error", "Unknown error")
            return f"I tried to show the illustration but encountered an error: {error}"

    except asyncio.TimeoutError:
        logger.error("Show illustration timed out - frontend may not be ready")
        return "The illustration request timed out. Please make sure the frontend is connected and try again."
    except Exception as e:
        logger.error(f"Failed to show illustration: {e!s}")
        return "I encountered an error while trying to show the illustration. The frontend may not be ready to receive it."


@function_tool
async def hide_illustration(context: RunContext[UserData]):
    """Hide the currently displayed illustration from the user. Use this when you want to clear the visual display.

    No arguments required.
    """
    userdata = context.userdata

    # Get the room from the userdata
    if not userdata.ctx or not userdata.ctx.room:
        return "Cannot hide illustration: couldn't access the room"
    room = userdata.ctx.room

    # Get the first participant in the room (should be the client)
    participants = room.remote_participants
    if not participants:
        return "Cannot hide illustration: no participants found in the room"

    # Get the first participant from the dictionary of remote participants
    participant = next(iter(participants.values()), None)
    if not participant:
        return "Cannot hide illustration: couldn't get the first participant"

    # Prepare and send RPC to hide the illustration
    try:
        payload = json.dumps({"state": "hidden"})
        logger.info(f"Sending hide illustration payload: {payload}")

        # Wrap RPC call with asyncio timeout to catch errors before Rust panic
        result = await asyncio.wait_for(
            room.local_participant.perform_rpc(
                destination_identity=participant.identity,
                method=RPC_METHOD_ILLUSTRATION,
                payload=payload,
            ),
            timeout=RPC_TIMEOUT,
        )

        response = json.loads(result)
        logger.info(f"[Illustration] Hide result: {response}")

        if response.get("ok"):
            return "I've hidden the illustration."
        else:
            error = response.get("error", "Unknown error")
            return f"I tried to hide the illustration but encountered an error: {error}"

    except asyncio.TimeoutError:
        logger.error("Hide illustration timed out - frontend may not be ready")
        return "The hide illustration request timed out. Please make sure the frontend is connected."
    except Exception as e:
        logger.error(f"Failed to hide illustration: {e!s}")
        return "I encountered an error while trying to hide the illustration. The frontend may not be ready."
