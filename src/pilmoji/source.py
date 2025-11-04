from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, ClassVar
from urllib.parse import quote_plus

from httpx import AsyncClient, HTTPError

__all__ = (
    "AppleEmojiSource",
    "BaseSource",
    "DiscordEmojiSourceMixin",
    "EmojiCDNSource",
    "EmojidexEmojiSource",
    "FacebookEmojiSource",
    "FacebookMessengerEmojiSource",
    "GoogleEmojiSource",
    "HTTPBasedSource",
    "JoyPixelsEmojiSource",
    "MessengerEmojiSource",
    "MicrosoftEmojiSource",
    "MozillaEmojiSource",
    "Openmoji",
    "OpenmojiEmojiSource",
    "SamsungEmojiSource",
    "Twemoji",
    "TwemojiEmojiSource",
    "TwitterEmojiSource",
    "WhatsAppEmojiSource",
)


class BaseSource(ABC):
    """The base class for an emoji image source."""

    @abstractmethod
    async def get_emoji(self, emoji: str, /) -> BytesIO | None:
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
    async def get_discord_emoji(self, id: int, /) -> BytesIO | None:
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

    def __init__(self) -> None:
        self.client = AsyncClient()

    async def request(self, url: str) -> bytes:
        response = await self.client.get(url, **self.REQUEST_KWARGS)
        return response.content


class DiscordEmojiSourceMixin(HTTPBasedSource):
    """A mixin that adds Discord emoji functionality to another source."""

    BASE_DISCORD_EMOJI_URL: ClassVar[str] = "https://cdn.discordapp.com/emojis/"

    @abstractmethod
    async def get_emoji(self, emoji: str, /) -> BytesIO | None:
        raise NotImplementedError

    async def get_discord_emoji(self, id: int, /) -> BytesIO | None:
        url = self.BASE_DISCORD_EMOJI_URL + str(id) + ".png"

        try:
            return BytesIO(await self.request(url))
        except HTTPError:
            pass


class EmojiCDNSource(DiscordEmojiSourceMixin):
    """A base source that fetches emojis from https://emojicdn.elk.sh/."""

    BASE_EMOJI_CDN_URL: ClassVar[str] = "https://emojicdn.elk.sh/"
    STYLE: ClassVar[str | None] = None

    async def get_emoji(self, emoji: str, /) -> BytesIO | None:
        if self.STYLE is None:
            raise TypeError("STYLE class variable unfilled.")

        url = self.BASE_EMOJI_CDN_URL + quote_plus(emoji) + "?style=" + quote_plus(self.STYLE)

        try:
            return BytesIO(await self.request(url))
        except HTTPError:
            pass


class TwitterEmojiSource(EmojiCDNSource):
    """A source that uses Twitter-style emojis. These are also the ones used in Discord."""

    STYLE = "twitter"


class AppleEmojiSource(EmojiCDNSource):
    """A source that uses Apple emojis."""

    STYLE = "apple"


class GoogleEmojiSource(EmojiCDNSource):
    """A source that uses Google emojis."""

    STYLE = "google"


class MicrosoftEmojiSource(EmojiCDNSource):
    """A source that uses Microsoft emojis."""

    STYLE = "microsoft"


class SamsungEmojiSource(EmojiCDNSource):
    """A source that uses Samsung emojis."""

    STYLE = "samsung"


class WhatsAppEmojiSource(EmojiCDNSource):
    """A source that uses WhatsApp emojis."""

    STYLE = "whatsapp"


class FacebookEmojiSource(EmojiCDNSource):
    """A source that uses Facebook emojis."""

    STYLE = "facebook"


class MessengerEmojiSource(EmojiCDNSource):
    """A source that uses Facebook Messenger's emojis."""

    STYLE = "messenger"


class JoyPixelsEmojiSource(EmojiCDNSource):
    """A source that uses JoyPixels' emojis."""

    STYLE = "joypixels"


class OpenmojiEmojiSource(EmojiCDNSource):
    """A source that uses Openmoji emojis."""

    STYLE = "openmoji"


class EmojidexEmojiSource(EmojiCDNSource):
    """A source that uses Emojidex emojis."""

    STYLE = "emojidex"


class MozillaEmojiSource(EmojiCDNSource):
    """A source that uses Mozilla's emojis."""

    STYLE = "mozilla"


# Aliases
Openmoji = OpenmojiEmojiSource
FacebookMessengerEmojiSource = MessengerEmojiSource
TwemojiEmojiSource = Twemoji = TwitterEmojiSource
