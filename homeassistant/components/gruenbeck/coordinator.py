"""DataUpdateCoordinator for the Gruenbeck integration."""
from datetime import timedelta
import logging
from typing import Any

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError
import defusedxml.ElementTree as defET

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class SoftQLinkDataUpdateCoordinator(DataUpdateCoordinator):
    """Define an object to hold softQlink data."""

    def __init__(
        self, hass: HomeAssistant, name: str, host: str, session: ClientSession
    ) -> None:
        """Initialize."""
        self.session = session
        self.name = name
        self.host = host
        self.datacache: dict[str, Any] = {}
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            _LOGGER.info("Connecting")
            async with self.session.post(
                f"http://{self.host}/mux_http",
                timeout=2000,
                data="id=8364&show=D_A_1_1|D_A_1_2|D_A_2_2|D_A_2_3|D_A_3_1|D_A_3_2|D_Y_1|D_A_1_3|D_A_1_7|D_A_2_3|D_Y_5|D_A_2_1~",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            ) as response:
                if response.status == 200:
                    xml = await response.text()
                    if xml:
                        self.datacache = self.__parse_xml_to_dict(xml)
                _LOGGER.info(response.status)
        except ClientError as error:
            raise UpdateFailed(error) from error
        return self.datacache

    def __parse_xml_to_dict(self, xml_data):
        _LOGGER.info(xml_data)
        root = defET.fromstring(xml_data)
        data_dict = {}
        for elem in root:
            if elem.tag != "code":
                data_dict[elem.tag] = elem.text.strip()
        return data_dict
