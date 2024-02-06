"""API for interacting with Senziio Devices."""

import asyncio

from homeassistant.components.mqtt import async_publish, async_subscribe
from homeassistant.core import HomeAssistant


class Senziio:
    """Handle Senziio sensor."""

    TIMEOUT_IS_ALIVE = 10

    def __init__(self, hass: HomeAssistant, unique_id: str) -> None:
        """Initialize instance."""
        self.hass = hass
        self.topics = {
            "ping": f"senziio/ping/{unique_id}",
            "pong": f"senziio/pong/{unique_id}",
        }

    async def is_alive(self):
        """Test aliveness by publishing a message and waiting for response."""
        response = asyncio.Event()

        async def handle_response(message):
            """Handle pong response."""
            response.set()

        unsubscribe_callback = await async_subscribe(
            self.hass,
            self.topics["pong"],
            handle_response,
        )

        await async_publish(
            self.hass,
            self.topics["ping"],
            "Are you alive?",
            qos=1,
            retain=False,
        )

        try:
            await asyncio.wait_for(response.wait(), self.TIMEOUT_IS_ALIVE)
            return True
        except asyncio.TimeoutError:
            return False
        finally:
            if unsubscribe_callback:
                unsubscribe_callback()
