import pytest

COMPLEX_TEXT = """
Hello World! 👋
This is a complex test text with multiple lines.
We have standard emojis: 😂, 🚀, 🐍, 💻.
And some more: 🌟✨🔥💯.
Even some text in between: A B C 1 2 3.
Discord emojis are also supported <:rooThink:596576798351949847>
"""


@pytest.mark.asyncio
async def test_pilmoji(font_path, cache_dir):
    from PIL import Image, ImageFont

    from pilmoji import Pilmoji, EmojiCDNSource

    font = ImageFont.truetype(font_path, 24)
    async with Pilmoji(source=EmojiCDNSource(cache_dir=cache_dir)) as pilmoji:
        image = Image.new("RGB", (300, 200), (255, 255, 255))
        for y in range(10, 170, 30):
            await pilmoji.text(image, (10, y), "Hello 👍 world 😎", font, (0, 0, 0))

        assert image is not None
        image.save(cache_dir / "test_pilmoji.png")


@pytest.mark.asyncio
async def test_text(font_path, cache_dir):
    from PIL import Image, ImageFont

    from pilmoji import Pilmoji, EmojiCDNSource

    font = ImageFont.truetype(font_path, 24)
    async with Pilmoji(source=EmojiCDNSource(cache_dir=cache_dir)) as pilmoji:
        image = Image.new("RGB", (800, 300), (255, 255, 255))
        await pilmoji.text(image, (10, 10), COMPLEX_TEXT, font, (0, 0, 0))
        assert image is not None
        image.save(cache_dir / "text.png")


@pytest.mark.asyncio
async def test_text_with_discord_emoji(font_path, cache_dir):
    from PIL import Image, ImageFont

    from pilmoji import Pilmoji, EmojiCDNSource

    font = ImageFont.truetype(font_path, 24)
    async with Pilmoji(source=EmojiCDNSource(cache_dir=cache_dir)) as pilmoji:
        image = Image.new("RGB", (600, 300), (255, 255, 255))
        await pilmoji.text_with_discord_emoji(
            image, (10, 10), COMPLEX_TEXT, font, (0, 0, 0)
        )
        assert image is not None
        image.save(cache_dir / "text_with_discord_emoji.png")


@pytest.mark.asyncio
async def test_text_without_context_manager(font_path, cache_dir):
    from PIL import Image, ImageFont

    from pilmoji import Pilmoji, EmojiCDNSource

    font = ImageFont.truetype(font_path, 24)
    source = EmojiCDNSource(cache_dir=cache_dir)
    pilmoji = Pilmoji(source=source)

    try:
        image = Image.new("RGB", (300, 200), (255, 255, 255))
        for y in range(10, 170, 30):
            await pilmoji.text(image, (10, y), "Hello 👍 world 😎", font, (0, 0, 0))

        assert image is not None
    finally:
        await pilmoji.aclose()
