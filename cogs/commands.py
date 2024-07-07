import discord
import logging

from discord.ext import commands

from utils.rsi_calculator import calculate_rsi
from data.historical_data import closes, RSI_PERIOD

test_mode = False
rsi = 25
latest_rsi = 42

test_status_response = discord.Embed(
    title="Test Mode Status",
    description=f"Test mode is currently {'enabled' if test_mode else 'disabled'}.",
    color=discord.Color.orange()
)

test_mode_enable_response = discord.Embed(
    title="Test Mode Updated",
    description="Test mode is now enabled.",
    color=discord.Color.green()
)

test_mode_disable_response = discord.Embed(
    title="Test Mode Updated",
    description="Test mode is now disabled.",
    color=discord.Color.red()
)

test_alert_with_test_mode_disabled = discord.Embed(
    title="Test Alert",
    description=f"Test mode is not enabled. Use !testmode True to enable test mode.",
    color=discord.Color.red()
)

test_alert_with_test_mode_enabled = discord.Embed(
    title="Test Alert Sent",
    description=f"Test alert sent with RSI value: {rsi}",
    color=discord.Color.green()
)

response_calculated_rsi = discord.Embed(
    title="Current RSI",
    description=f"The current RSI is: {latest_rsi}",
    color=discord.Color.blue()
)

response_calculate_rsi_failed = discord.Embed(
    title="Current RSI",
    description=f"Not enough data to calculate RSI. Current closes: {len(closes)}",
    color=discord.Color.yellow()
)

# Configuration of logging
logger = logging.getLogger(__name__)


class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Test commands loaded successfully!")

    @commands.command(name="teststatus")
    async def test_status(self, ctx):
        """
        Toggles and displays the current test mode status.
        """
        test_status_response.description = f"Test mode is currently {'enabled' if test_mode else 'disabled'}."
        await ctx.send(embed=test_status_response)

    @commands.command(name="testmode")
    async def toggle_test_mode(self, ctx, mode: bool):
        """
        Toggles the test mode setting and displays the updated status.
        """
        global test_mode
        test_mode = mode
        if test_mode:
            embed = test_mode_enable_response
        else:
            embed = test_mode_disable_response
        await ctx.send(embed=embed)

    @commands.command(name="testalert")
    async def send_test_alert(self, ctx, rsi: float):
        """
        Sends a test alert message to the Discord channel if test mode is enabled.
        """
        if test_mode:
            test_alert_with_test_mode_enabled.description = f"Test alert sent with RSI value: {rsi}"
            embed = test_alert_with_test_mode_enabled
        else:
            embed = test_alert_with_test_mode_disabled
        await ctx.send(embed=embed)

    @commands.command(name="rsi")
    async def show_rsi(self, ctx):
        """
        Displays the current Relative Strength Index (RSI) in a Discord embedded message.
        """
        if test_mode:
            if len(closes) >= RSI_PERIOD:
                rsi = calculate_rsi(closes)
                latest_rsi = rsi[-1]
                response_calculated_rsi.description = f"The current RSI is: {latest_rsi}"
                embed = response_calculated_rsi
                await ctx.send(embed=embed)
            else:
                embed = response_calculate_rsi_failed
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Current RSI",
                description=f"Test mode is not enabled. Use command: !testmode True to enable test mode.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CommandCog(bot))
