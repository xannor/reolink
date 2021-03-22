""" BaiChuan Client """

import hashlib
import asyncio
import logging
from typing import cast
from . import models

from ..base import Api as BaseApi, DEFAULT_TIMEOUT

DEFAULT_PORT = 8000

_LOGGER = logging.getLogger(__name__)


class Client(BaseApi):
    """ BaiChuan Client """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        super().__init__(host, port, username, password, timeout=timeout)
        self._reader: asyncio.StreamReader = None
        self._writer: asyncio.StreamWriter = None

    @property
    def mac_address(self) -> str:
        """Return the mac address."""
        raise NotImplementedError()

    @property
    def serial(self) -> str:
        """Return the serial."""
        raise NotImplementedError()

    @property
    def name(self):
        """Return the camera name."""
        raise NotImplementedError()

    @property
    def sw_version(self) -> str:
        """Return the software version."""
        raise NotImplementedError()

    @property
    def model(self) -> str:
        """Return the model."""
        raise NotImplementedError()

    @property
    def channels(self) -> int:
        """Return the number of channels."""
        raise NotImplementedError()

    @property
    def channel(self) -> int:
        """Return the channel number."""
        raise NotImplementedError()

    @property
    def ptz_support(self) -> bool:
        """Return if PTZ is supported."""
        raise NotImplementedError()

    @property
    def motion_detection_state(self):
        """Return the motion detection state."""
        raise NotImplementedError()

    @property
    def session_active(self) -> bool:
        """Return if the session is active."""
        if self._reader is None or self._writer is None:
            return False

        return True

    async def get_states(self, cmd_list=None) -> bool:
        """Fetch the state objects."""
        raise NotImplementedError()

    async def get_settings(self) -> bool:
        """Fetch the settings."""
        raise NotImplementedError()

    async def get_motion_state(self) -> bool:
        """Fetch the motion state."""
        raise NotImplementedError()

    async def get_still_image(self) -> bytes:
        """Get the still image."""
        raise NotImplementedError()

    async def get_snapshot(self):
        """Get a snapshot."""
        return await self.get_still_image()

    async def _ensure_connection(self):
        if self._reader is None or self._writer is None:
            reader, writer = await asyncio.open_connection(self._host, self._port)
            self._reader = reader
            self._writer = writer

        return True

    async def login(self) -> bool:
        """Login and store the session ."""
        if self.session_active:
            return True

        _LOGGER.debug(
            "Reolink camera with host %s:%s trying to login with user %s",
            self._host,
            self._port,
            self._username,
        )

        await self._ensure_connection()

        md5_username = md5_string(self._username)
        md5_password = md5_string(self._password)

        legacy_login = models.Message.from_legacy(
            models.LegacyLogin(md5_username, md5_password)
        )

        self._writer.write(legacy_login.tobytes())
        await self._writer.drain()
        login_reply = await models.Message.async_read(self._reader.readexactly)
        nonce = cast(models.Xml, login_reply.body.xml).encryption.nonce

        md5_username = md5_string(f"{self._username}{nonce}", False)
        md5_password = md5_string(f"{self._password}{nonce}", False)

        modern_login = models.Message.login(md5_username, md5_password)
        self._writer.write(modern_login.tobytes())
        await self._writer.drain()
        login_reply = await models.Message.async_read(self._reader.readexactly)
        # device_info = cast(models.Xml, modern_reply.body.xml).device_info

        return True

    async def _ping(self):
        """ Ping camera over connection """

        await self.login()
        ping = models.Message.ping()
        self._writer.write(ping.tobytes())
        await self._writer.drain()
        await models.Message.async_read(self._reader.readexactly)
        return True

    async def _get_version(self):
        """ Get Camera verison info """

        await self.login()
        version = models.Message.version()
        self._writer.write(version.tobytes())
        await self._writer.drain()
        version_reply = await models.Message.async_read(self._reader.readexactly)

        x = cast(models.Xml, version_reply.body.xml)
        return x.version_info

    async def _get_general(self):
        """ Get Camera Info """

        await self.login()
        general = models.Message.general()
        self._writer.write(general.tobytes())
        await self._writer.drain()
        general_reply = await models.Message.async_read(self._reader.readexactly)
        x = cast(models.Xml, general_reply.body.xml)
        return x.system_general

    async def start_stream(self):
        """ Get Camera PReview Stream """

        await self.login()
        preview = models.Message.preview()

    @property
    async def _userlevel(self) -> str:
        """ User level after login """
        raise NotImplementedError()

    async def logout(self) -> None:
        """Logout from the API."""
        raise NotImplementedError()

    async def set_channel(self, channel: int):
        """Update the channel property."""
        raise NotImplementedError()


def md5_string(input: str, padzero: bool = True):
    if len(input) > 0:
        input = hashlib.md5(input).hexdigest()

    if padzero:
        return input.ljust(32, "\0")
