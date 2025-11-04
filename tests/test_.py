def test_dummy():
    assert True


async def test_download_all_emojis():
    from pilmoji.source import EmojiStyle, LocalEmojiSource

    source = LocalEmojiSource(EmojiStyle.APPLE)
    await source.download_all_emojis()
