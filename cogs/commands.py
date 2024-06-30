import discord
import logging
from discord.ext import commands
from utils.rsi_calculator import calculate_rsi
from data.historical_data import closes, RSI_PERIOD
from main import send_discord_message

test_mode = False

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
        embed = discord.Embed(
            title="Test Mode Status",
            description=f"Test mode is currently {'enabled' if test_mode else 'disabled'}.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)

    @commands.command(name="testmode")
    async def toggle_test_mode(self, ctx, mode: bool):
        """
        Toggles the test mode setting and displays the updated status.
        """
        global test_mode
        test_mode = mode
        if test_mode:
            embed = discord.Embed(
                title="Test Mode Updated",
                description="Test mode is now enabled.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="Test Mode Updated",
                description="Test mode is now disabled.",
                color=discord.Color.red()
            )
        await ctx.send(embed=embed)

    @commands.command(name="testalert")
    async def send_test_alert(self, ctx, rsi: float):
        """
        Sends a test alert message to the Discord channel if test mode is enabled.
        """
        if test_mode:
            await send_discord_message(rsi)
            embed = discord.Embed(
                title="Test Alert Sent",
                description=f"Test alert sent with RSI value: {rsi}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Test Alert",
                description=f"Test mode is not enabled. Use !testmode True to enable test mode.",
                color=discord.Color.red()
            )
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
                embed = discord.Embed(
                    title="Current RSI",
                    description=f"The current RSI is: {latest_rsi}",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="Current RSI",
                    description=f"Not enough data to calculate RSI. Current closes: {len(closes)}",
                    color=discord.Color.yellow()
                )
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
