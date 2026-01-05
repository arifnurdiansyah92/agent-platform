"""Session configuration and setup for the agent."""

import logging

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    MetricsCollectedEvent,
    RoomInputOptions,
    metrics,
)
from livekit.plugins import elevenlabs, noise_cancellation, openai
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from src.agent_factory import AgentType, create_agent
from src.config import RPC_METHOD_TOGGLE_COMPONENT
from src.models import UserData
from src.rpc_handlers import create_toggle_component_handler

logger = logging.getLogger("agent.session")


async def create_agent_session(ctx: JobContext) -> AgentSession[UserData]:
    """Create and configure an agent session with all components.

    Args:
        ctx: The job context

    Returns:
        A configured AgentSession instance
    """
    # Set up user data
    userdata = UserData(ctx=ctx)

    # Create the session with STT, LLM, TTS, and turn detection
    session = AgentSession[UserData](
        userdata=userdata,
        # Speech-to-text (STT) is your agent's ears
        stt=openai.STT(model="gpt-4o-mini-transcribe", language="id"),
        # Large Language Model (LLM) is your agent's brain
        llm=openai.LLM(model="gpt-4.1-mini", temperature=0.4),
        # Text-to-speech (TTS) is your agent's voice
        tts=elevenlabs.TTS(
            model="eleven_multilingual_v2",
            voice_id="iWydkXKoiVtvdn4vLKp9",
            language="id",
        ),
        # VAD and turn detection
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # Allow the LLM to generate a response while waiting for the end of turn
        preemptive_generation=True,
    )

    # Set up metrics collection
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    return session


async def start_agent_session(
    session: AgentSession[UserData],
    ctx: JobContext,
    agent_type: AgentType = "default",
    agent: Agent | None = None
) -> None:
    """Start the agent session and register RPC handlers.

    Args:
        session: The agent session to start
        ctx: The job context
        agent_type: Type of agent to create (if agent is None)
        agent: Optional pre-configured agent instance
    """
    userdata = session.userdata

    # Create agent if not provided
    if agent is None:
        agent = create_agent(agent_type)

    # Start the session
    await session.start(
        agent=agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Connect to the room
    await ctx.connect()

    # Register RPC methods
    logger.info("Registering RPC methods")
    toggle_handler = create_toggle_component_handler(session, userdata)
    ctx.room.local_participant.register_rpc_method(
        RPC_METHOD_TOGGLE_COMPONENT, toggle_handler
    )
    logger.info(f"Registered RPC method: {RPC_METHOD_TOGGLE_COMPONENT}")
