"""Canvas interaction tools for drawing and visual math problems."""

import asyncio
import json
import logging

from livekit.agents import RunContext, function_tool

from src.config import RPC_METHOD_CANVAS, RPC_TIMEOUT
from src.models import UserData

logger = logging.getLogger("agent.tools.canvas")


@function_tool
async def get_canvas_drawing(context: RunContext[UserData]):
    """Request the current canvas drawing from the user. Use this when you need to analyze what the user has drawn.

    This will ask the frontend to send a snapshot of the canvas, including:
    - Drawing data (strokes, shapes)
    - Canvas image as base64
    - Drawing metadata

    No arguments required.
    """
    userdata = context.userdata

    # Get the room from the userdata
    if not userdata.ctx or not userdata.ctx.room:
        return "Cannot get canvas: couldn't access the room"
    room = userdata.ctx.room

    # Get the first participant in the room (should be the client)
    participants = room.remote_participants
    if not participants:
        return "Cannot get canvas: no participants found in the room"

    participant = next(iter(participants.values()), None)
    if not participant:
        return "Cannot get canvas: couldn't get the first participant"

    try:
        payload = json.dumps({"action": "get_drawing"})
        logger.info(f"Requesting canvas drawing: {payload}")

        result = await asyncio.wait_for(
            room.local_participant.perform_rpc(
                destination_identity=participant.identity,
                method=RPC_METHOD_CANVAS,
                payload=payload,
            ),
            timeout=RPC_TIMEOUT,
        )

        response = json.loads(result)
        logger.info(f"[Canvas] Get drawing result: {response}")

        if response.get("ok"):
            drawing_data = response.get("drawing_data", {})
            # Store the canvas data in userdata for analysis
            userdata.last_canvas_drawing = drawing_data
            return f"I can see your drawing. It contains {len(drawing_data.get('strokes', []))} strokes. Let me analyze it."
        else:
            error = response.get("error", "Unknown error")
            return f"I couldn't get your canvas drawing: {error}"

    except asyncio.TimeoutError:
        logger.error("Get canvas timed out - frontend may not be ready")
        return "The canvas request timed out. Please make sure you've drawn something on the canvas."
    except Exception as e:
        logger.error(f"Failed to get canvas: {e!s}")
        return "I encountered an error while trying to get your drawing. Please try again."


@function_tool
async def clear_canvas(context: RunContext[UserData]):
    """Clear the canvas drawing. Use this when starting a new problem or when the user asks to clear.

    No arguments required.
    """
    userdata = context.userdata

    if not userdata.ctx or not userdata.ctx.room:
        return "Cannot clear canvas: couldn't access the room"
    room = userdata.ctx.room

    participants = room.remote_participants
    if not participants:
        return "Cannot clear canvas: no participants found in the room"

    participant = next(iter(participants.values()), None)
    if not participant:
        return "Cannot clear canvas: couldn't get the first participant"

    try:
        payload = json.dumps({"action": "clear"})
        logger.info(f"Clearing canvas: {payload}")

        result = await asyncio.wait_for(
            room.local_participant.perform_rpc(
                destination_identity=participant.identity,
                method=RPC_METHOD_CANVAS,
                payload=payload,
            ),
            timeout=RPC_TIMEOUT,
        )

        response = json.loads(result)
        logger.info(f"[Canvas] Clear result: {response}")

        if response.get("ok"):
            # Clear stored canvas data
            userdata.last_canvas_drawing = None
            return "I've cleared the canvas. You can start drawing a new problem."
        else:
            error = response.get("error", "Unknown error")
            return f"I couldn't clear the canvas: {error}"

    except asyncio.TimeoutError:
        logger.error("Clear canvas timed out")
        return "The clear request timed out. Please try again."
    except Exception as e:
        logger.error(f"Failed to clear canvas: {e!s}")
        return "I encountered an error while clearing the canvas."


@function_tool
async def analyze_math_drawing(context: RunContext[UserData]):
    """Analyze the current canvas drawing to identify mathematical shapes, equations, or diagrams.

    This tool will:
    1. Get the canvas drawing
    2. Use image recognition to identify mathematical elements
    3. Return a description of what was found

    Use this when the user draws something and wants you to solve it or provide feedback.

    No arguments required.
    """
    userdata = context.userdata

    # First, get the canvas drawing
    if not userdata.last_canvas_drawing:
        # Try to fetch it
        get_result = await get_canvas_drawing(context)
        if "couldn't" in get_result.lower() or "error" in get_result.lower():
            return get_result

    drawing_data = userdata.last_canvas_drawing
    if not drawing_data:
        return "There's no drawing on the canvas yet. Please draw something first."

    # Analyze the drawing
    # In a real implementation, you would:
    # 1. Send the base64 image to a vision model (GPT-4 Vision, Claude Vision, etc.)
    # 2. Extract mathematical elements (equations, shapes, graphs)
    # 3. Return structured analysis

    # For now, return mock analysis
    strokes = drawing_data.get("strokes", [])
    image_base64 = drawing_data.get("image", "")

    analysis = {
        "detected_elements": [],
        "suggestions": [],
    }

    # Simple heuristic analysis based on stroke count
    if len(strokes) < 5:
        analysis["detected_elements"].append("Simple shape or number")
        analysis["suggestions"].append(
            "Try drawing more complex mathematical expressions"
        )
    elif len(strokes) < 20:
        analysis["detected_elements"].append("Mathematical equation or expression")
        analysis["suggestions"].append("Make sure numbers and operators are clear")
    else:
        analysis["detected_elements"].append("Complex diagram or graph")
        analysis["suggestions"].append("This looks like a detailed mathematical concept")

    # TODO: Integrate with GPT-4 Vision API
    # response = await openai_vision.analyze(image_base64, prompt="Identify mathematical elements")

    return f"I can see you've drawn something with {len(strokes)} strokes. {' '.join(analysis['detected_elements'])}. {analysis['suggestions'][0]}"


@function_tool
async def highlight_canvas_area(
    context: RunContext[UserData], x: int, y: int, width: int, height: int, color: str = "yellow"
):
    """Highlight a specific area on the canvas to draw attention to it.

    Use this to point out specific parts of the drawing, like errors or areas to focus on.

    Args:
        x: X coordinate of the top-left corner
        y: Y coordinate of the top-left corner
        width: Width of the highlight area
        height: Height of the highlight area
        color: Color of the highlight (default: yellow)
    """
    userdata = context.userdata

    if not userdata.ctx or not userdata.ctx.room:
        return "Cannot highlight: couldn't access the room"
    room = userdata.ctx.room

    participants = room.remote_participants
    if not participants:
        return "Cannot highlight: no participants found"

    participant = next(iter(participants.values()), None)
    if not participant:
        return "Cannot highlight: couldn't get participant"

    try:
        payload = json.dumps({
            "action": "highlight",
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "color": color,
        })
        logger.info(f"Highlighting canvas area: {payload}")

        result = await asyncio.wait_for(
            room.local_participant.perform_rpc(
                destination_identity=participant.identity,
                method=RPC_METHOD_CANVAS,
                payload=payload,
            ),
            timeout=RPC_TIMEOUT,
        )

        response = json.loads(result)
        logger.info(f"[Canvas] Highlight result: {response}")

        if response.get("ok"):
            return f"I've highlighted the area at ({x}, {y}) to draw your attention to it."
        else:
            error = response.get("error", "Unknown error")
            return f"I couldn't highlight the area: {error}"

    except asyncio.TimeoutError:
        logger.error("Highlight timed out")
        return "The highlight request timed out."
    except Exception as e:
        logger.error(f"Failed to highlight: {e!s}")
        return "I encountered an error while highlighting."
