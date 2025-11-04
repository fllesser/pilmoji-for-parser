from abc import ABC, abstractmethod
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Any, ClassVar
from urllib.parse import quote_plus

from aiofiles import open as aopen
from emoji import EMOJI_DATA
from httpx import AsyncClient, HTTPError

__all__ = (
    "BaseSource",
    "DiscordEmojiSourceMixin",
    "EmojiCDNSource",
    "HTTPBasedSource",
)


class BaseSource(ABC):
    """The base class for an emoji image source."""

    @abstractmethod
    async def get_emoji(self, emoji: str) -> BytesIO | None:
        """Retrieves a :class:`io.BytesIO` stream for the image of the given emoji.

        Parameters
        ----------
        emoji: str
            The emoji to retrieve.

        Returns
        -------
        :class:`io.BytesIO`
            A bytes stream of the emoji.
        None
            An image for the emoji could not be found.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_discord_emoji(self, id: int) -> BytesIO | None:
        """Retrieves a :class:`io.BytesIO` stream for the image of the given Discord emoji.

        Parameters
        ----------
        id: int
            The snowflake ID of the Discord emoji.

        Returns
        -------
        :class:`io.BytesIO`
            A bytes stream of the emoji.
        None
            An image for the emoji could not be found.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class HTTPBasedSource(BaseSource):
    """Represents an HTTP-based source."""

    REQUEST_KWARGS: ClassVar[dict[str, Any]] = {"headers": {"User-Agent": "Mozilla/5.0"}}

    def __init__(self, cache_dir: Path | None = None) -> None:
        self.cache_dir: Path = cache_dir or (Path.home() / ".cache" / "pilmoji")
        if cache_dir is not None:
            cache_dir.mkdir(parents=True, exist_ok=True)
        self.client = AsyncClient(**self.REQUEST_KWARGS)

    async def download(self, url: str) -> bytes:
        response = await self.client.get(url)
        response.raise_for_status()
        return response.content


class EmojiStyle(str, Enum):
    APPLE = "apple"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    SAMSUNG = "samsung"
    WHATSAPP = "whatsapp"
    FACEBOOK = "facebook"
    MESSENGER = "messenger"
    JOYPIXELS = "joypixels"
    OPENMOJI = "openmoji"
    EMOJIDEX = "emojidex"
    MOZILLA = "mozilla"

    def __str__(self) -> str:
        return self.value


class LocalEmojiSource:
    BASE_DISCORD_EMOJI_URL: ClassVar[str] = "https://cdn.discordapp.com/emojis/"
    BASE_EMOJI_CDN_URL: ClassVar[str] = "https://emojicdn.elk.sh/"

    def __init__(self, style: EmojiStyle, cache_dir: Path | None = None) -> None:
        self.style = style.value
        self.cache_dir: Path = cache_dir or Path.home() / ".cache" / "pilmoji"
        if cache_dir is not None:
            cache_dir.mkdir(parents=True, exist_ok=True)

    async def download_all_emojis(self) -> None:
        from asyncio import create_task, gather

        async def download_emoji(client: AsyncClient, emj: str) -> None:
            file_path = self.cache_dir / self.style / f"{emj}.png"
            if file_path.exists():
                return
            url = self.BASE_EMOJI_CDN_URL + quote_plus(emj) + "?style=" + quote_plus(self.style)
            response = await client.get(url)
            response.raise_for_status()
            async with aopen(file_path, "wb") as f:
                await f.write(response.content)

        async with AsyncClient(headers={"User-Agent": "Mozilla/5.0"}) as client:
            tasks = [create_task(download_emoji(client, emj)) for emj, _ in EMOJI_DATA.items()]
            await gather(*tasks, return_exceptions=True)

    def get_emoji(self, emoji: str) -> BytesIO | None:
        return BytesIO(open(self.cache_dir / self.style / f"{emoji}.png", "rb").read())

    def get_discord_emoji(self, id: int) -> BytesIO | None:
        return BytesIO(open(self.cache_dir / "discord" / f"{id}.png", "rb").read())


class DiscordEmojiSourceMixin(HTTPBasedSource):
    """A mixin that adds Discord emoji functionality to another source."""

    BASE_DISCORD_EMOJI_URL: ClassVar[str] = "https://cdn.discordapp.com/emojis/"

    async def get_discord_emoji(self, id: int) -> BytesIO | None:
        file_path = self.cache_dir / "discord" / f"{id}.png"
        if file_path.exists():
            async with aopen(file_path, "rb") as f:
                return BytesIO(await f.read())

        url = self.BASE_DISCORD_EMOJI_URL + str(id) + ".png"

        try:
            bytes = await self.download(url)
            async with aopen(file_path, "wb") as f:
                await f.write(bytes)
            return BytesIO(bytes)
        except HTTPError:
            return None


class EmojiCDNSource(DiscordEmojiSourceMixin):
    """A base source that fetches emojis from https://emojicdn.elk.sh/."""

    BASE_EMOJI_CDN_URL: ClassVar[str] = "https://emojicdn.elk.sh/"
    STYLE: ClassVar[EmojiStyle] = EmojiStyle.MICROSOFT

    async def get_emoji(self, emoji: str) -> BytesIO | None:
        file_path = self.cache_dir / self.STYLE.value / f"{emoji}.png"
        if file_path.exists():
            async with aopen(file_path, "rb") as f:
                return BytesIO(await f.read())

        url = self.BASE_EMOJI_CDN_URL + quote_plus(emoji) + "?style=" + quote_plus(self.STYLE.value)

        try:
            bytes = await self.download(url)
            async with aopen(file_path, "wb") as f:
                await f.write(bytes)
            return BytesIO(bytes)
        except HTTPError:
            return None
