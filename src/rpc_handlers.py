"""RPC method handlers for client-to-agent communication."""

import json
import logging

from livekit.agents import AgentSession

from src.models import UserData

logger = logging.getLogger("agent.rpc")


def create_toggle_component_handler(
    session: AgentSession[UserData], userdata: UserData
):
    """Factory function to create a toggle component RPC handler.

    Args:
        session: The agent session
        userdata: The user data instance

    Returns:
        An async function that handles toggle component RPC calls
    """

    async def handle_toggle_component(rpc_data):
        """Handle component toggle requests from the frontend.

        Args:
            rpc_data: RPC invocation data containing the payload

        Returns:
            "success" on success, or "error: <message>" on failure
        """
        try:
            logger.info(f"Received toggle component payload: {rpc_data}")

            # Extract the payload from the RpcInvocationData object
            payload_str = rpc_data.payload
            logger.info(f"Extracted quiz submission string: {payload_str}")

            # Parse the JSON payload
            payload_data = json.loads(payload_str)
            logger.info(f"Parsed clicked button data: {payload_data}")

            action_id = payload_data.get("id")

            if action_id:
                component = userdata.toggle_component(action_id)
                if component:
                    logger.info(
                        f"Toggled component {action_id}, is_showed: {component.is_showed}"
                    )
                    # Send a message to the user via the agent
                    session.generate_reply(
                        instructions=(
                            "Say to the user that they successfully toggle the component"
                        )
                    )
                else:
                    logger.error(f"Component with ID {action_id} not found")
            else:
                logger.error("No action ID found in payload")

            return "success"
        except Exception as e:
            logger.error(f"Error handling button click: {e}")
            return f"error: {str(e)}"

    return handle_toggle_component
