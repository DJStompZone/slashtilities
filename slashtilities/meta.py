import discord

# from slashtilities import log


async def ping(self, ctx):
    """Return the latency of the bot"""
    gotten_ping = self.bot.latency * 1000
    print(f"Recorded ping: {gotten_ping} ms")
    await ctx.send(
        embed=discord.Embed(
            title=":ping_pong: Pong!",
            description=f"{gotten_ping:.4} ms",
            color=discord.Color.blue(),
        )
    )

