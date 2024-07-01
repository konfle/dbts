import pytest
import pytest_asyncio
import discord.ext.test as dpytest
from bot import create_bot
from cogs.commands import (CommandCog,
                           test_status_response,
                           test_mode_enable_response,
                           test_mode_disable_response)


@pytest_asyncio.fixture
async def bot():
    bot = create_bot()
    await bot._async_setup_hook()  # Set up the loop
    await bot.add_cog(CommandCog(bot))

    dpytest.configure(bot)

    yield bot

    # Teardown
    await dpytest.empty_queue()  # Empty the global message queue as test teardown


@pytest.mark.asyncio
async def test_status(bot):
    await dpytest.message("!teststatus")
    assert dpytest.verify().message().contains().embed(embed=test_status_response)


@pytest.mark.asyncio
async def test_mode_enabled(bot):
    await dpytest.message("!testmode True")
    assert dpytest.verify().message().contains().embed(embed=test_mode_enable_response)


@pytest.mark.asyncio
async def test_mode_disable(bot):
    await dpytest.message("!testmode False")
    assert dpytest.verify().message().contains().embed(embed=test_mode_disable_response)
