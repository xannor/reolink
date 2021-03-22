""" base """

from abc import ABCMeta, abstractmethod
import logging
import aiohttp

MANUFACTURER = "Reolink"
DEFAULT_STREAM = "main"
DEFAULT_CHANNEL = 0
DEFAULT_TIMEOUT = 30

_LOGGER = logging.getLogger(__name__)


class Api(metaclass=ABCMeta):
    """ Base Api """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password[:31]

        self._timeout = aiohttp.ClientTimeout(total=timeout)

    @property
    def host(self):
        """Return the host."""
        return self._host

    @property
    def port(self):
        """Return the port."""
        return self._port

    @property
    @abstractmethod
    def mac_address(self) -> str:
        """Return the mac address."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def serial(self) -> str:
        """Return the serial."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def name(self):
        """Return the camera name."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def sw_version(self) -> str:
        """Return the software version."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def model(self) -> str:
        """Return the model."""
        raise NotImplementedError()

    @property
    def manufacturer(self):
        """Return the manufacturer name (Reolink)."""
        return MANUFACTURER

    @property
    @abstractmethod
    def channels(self) -> int:
        """Return the number of channels."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def channel(self) -> int:
        """Return the channel number."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def ptz_support(self) -> bool:
        """Return if PTZ is supported."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def motion_detection_state(self):
        """Return the motion detection state."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def session_active(self) -> bool:
        """Return if the session is active."""
        raise NotImplementedError()

    @abstractmethod
    async def get_states(self, cmd_list=None) -> bool:
        """Fetch the state objects."""
        raise NotImplementedError()

    @abstractmethod
    async def get_settings(self) -> bool:
        """Fetch the settings."""
        raise NotImplementedError()

    @abstractmethod
    async def get_motion_state(self) -> bool:
        """Fetch the motion state."""
        raise NotImplementedError()

    @abstractmethod
    async def get_still_image(self) -> bytes:
        """Get the still image."""
        raise NotImplementedError()

    async def get_snapshot(self):
        """Get a snapshot."""
        return await self.get_still_image()

    @abstractmethod
    async def login(self) -> bool:
        """Login and store the session ."""
        raise NotImplementedError()

    @property
    @abstractmethod
    async def _userlevel(self) -> str:
        """ User level after login """
        raise NotImplementedError()

    async def is_admin(self):
        """Check if the user has admin authorisation."""

        msg = f"User {self._username} has authorization level {self._userlevel}"
        if self._userlevel != "admin":
            msg += (
                "Only admin users can change camera settings! Switches will not work."
            )
            _LOGGER.warning(msg)
        else:
            _LOGGER.debug(msg)

    @abstractmethod
    async def logout(self) -> None:
        """Logout from the API."""
        raise NotImplementedError()

    @abstractmethod
    async def set_channel(self, channel: int):
        """Update the channel property."""
        raise NotImplementedError()
