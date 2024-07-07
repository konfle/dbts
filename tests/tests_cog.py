import pytest
import pytest_asyncio
import discord.ext.test as dpytest
from bot import create_bot
from data.historical_data import closes
from cogs.commands import (CommandCog,
                           test_status_response,
                           test_mode_enable_response,
                           test_mode_disable_response,
                           test_alert_with_test_mode_disabled,
                           test_alert_with_test_mode_enabled,
                           response_calculated_rsi,
                           response_calculate_rsi_failed)


@pytest_asyncio.fixture
async def bot():
    bot = create_bot()
    await bot._async_setup_hook()  # Set up the loop
    await bot.add_cog(CommandCog(bot))

    dpytest.configure(bot)

    yield bot

    # Teardown
    await dpytest.empty_queue()  # Empty the global message queue as test teardown


@pytest_asyncio.fixture
async def enable_test_mode(bot):
    await dpytest.message("!testmode True")
    assert dpytest.verify().message().contains().embed(embed=test_mode_enable_response)


@pytest_asyncio.fixture
def closes_list(request):
    # Preparation of data for the "closes" list
    original_closes = closes[:]

    # Decide on the basis of the request.param argument
    if request.param == "14":
        test_data = [136.63, 136.62, 136.66,
                     136.6, 136.74, 136.74,
                     136.86, 137.05, 136.81,
                     136.68, 136.5, 136.36,
                     136.35, 136.4]
    else:
        test_data = [136.63, 136.62, 136.66]

    closes.clear()
    closes.extend(test_data)

    yield closes

    # Data cleaning after the test
    closes.clear()
    closes.extend(original_closes)


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


@pytest.mark.asyncio
async def test_alert_low_rsi_with_test_mode_disabled(bot):
    await dpytest.message("!testalert 25")
    assert dpytest.verify().message().contains().embed(embed=test_alert_with_test_mode_disabled)


@pytest.mark.asyncio
async def test_alert_high_rsi_with_test_mode_disabled(bot):
    await dpytest.message("!testalert 75")
    assert dpytest.verify().message().contains().embed(embed=test_alert_with_test_mode_disabled)


@pytest.mark.asyncio
async def test_alert_low_rsi_with_test_mode_enabled(bot, enable_test_mode):
    await dpytest.message("!testalert 25")
    assert dpytest.verify().message().contains().embed(embed=test_alert_with_test_mode_enabled)


@pytest.mark.asyncio
async def test_alert_high_rsi_with_test_mode_enabled(bot, enable_test_mode):
    await dpytest.message("!testalert 75")
    assert dpytest.verify().message().contains().embed(embed=test_alert_with_test_mode_enabled)


@pytest.mark.parametrize("closes_list", ["14"], indirect=True)
@pytest.mark.asyncio
async def test_rsi_calculation_with_test_mode_enabled(bot, enable_test_mode, closes_list):
    await dpytest.message("!rsi")
    assert dpytest.verify().message().contains().embed(embed=response_calculated_rsi)


@pytest.mark.parametrize("closes_list", ["less than 14 closes"], indirect=True)
@pytest.mark.asyncio
async def test_rsi_calculation_with_test_mode_enabled(bot, enable_test_mode, closes_list):
    await dpytest.message("!rsi")
    assert dpytest.verify().message().contains().embed(embed=response_calculate_rsi_failed)
