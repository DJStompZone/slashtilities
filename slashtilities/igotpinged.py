from collections import defaultdict
from typing import DefaultDict, List

import discord
from discord.ext import commands
from disputils import BotEmbedPaginator
from slashtilities import log, utils


async def make_list(stuff: List[str]) -> str:
    log.info("Making list")
    log.debug(stuff)
    output = ""
    for item in stuff:
        output += f" - [**Jump to message**]({item})\n"
    log.info("Success!")
    log.debug(repr(output))
    log.info("END OF `make_list`")
    return output


async def igotpinged(ctx: commands.Context) -> None:
    log.info("START OF `igotpinged`")
    await ctx.defer()
    log.info("Deffered.")
    try:
        last_msg = await utils.get_last_message_from(ctx.author, channel=ctx.channel)
    except discord.errors.Forbidden:
        log.info("Sending response")
        await ctx.send(
            embed=(
                await utils.errorize(
                    "How do you expect me to find your last message if "
                    "I don't even have access to this channel???",
                )
            ).set_footer(text="What an idiot")
        )
        log.info("Success!")
    else:
        if last_msg is None:
            log.info("Sending response")
            await ctx.send(
                await utils.errorize(
                    "Couldn't find your last message (maybe you didn't send any messages)"
                )
            )
            log.info("Success!")
            log.info("END OF `igotpinged`")
            return
        ping_msgs = [
            message
            async for message in ctx.channel.history(
                after=last_msg,
                limit=None,  # or 9000?
            )
            if ctx.author.mentioned_in(message)
        ]
        log.info("Ping status:")
        if len(ping_msgs) > 0:
            if len(ping_msgs) > 1:
                log.info("Found pings")
                to_paginate = [
                    discord.Embed(
                        title=":mag: Found!",
                        description="Click on the pagination buttons to see\n"
                        "who pinged you (times out *after 100 seconds*)",
                        color=discord.Color.green(),
                    ).add_field(
                        name="Your last message",
                        value=f"[**Jump to message**]({last_msg.jump_url})",
                        inline=False,
                    )
                ]
                log.info("Made initial stuff to paginate")
                log.debug(to_paginate)
                log.info("Making `author_and_pings` dictionary")
                author_and_pings: DefaultDict[discord.Member, List[str]] = defaultdict(
                    list
                )
                for message in ping_msgs:
                    author_and_pings[message.author].append(message.jump_url)
                log.info("Done")
                log.debug(author_and_pings)  # Should be allowed
                # See: https://discord.com/channels/264445053596991498/714045415707770900/830117545422880809
                to_paginate.extend(
                    [
                        discord.Embed(
                            title="",
                            description=await make_list(msgs),
                            color=discord.Color.green(),
                        ).set_author(
                            name=f"{author} pinged you in these messages:",
                            icon_url=str(author.avatar_url),
                        )
                        for author, msgs in author_and_pings.items()
                    ]
                )
                log.info("Final `to_paginate` made")
                log.debug(to_paginate)  # Should also be allowed
                log.info("Creating paginator")
                paginator = BotEmbedPaginator(ctx, to_paginate)
                log.info("Running paginator")
                await paginator.run(
                    channel=ctx  # Very hacky. It'll think ctx.send == channel.send
                )  # But it works
                log.info("Success!")
            else:
                log.info("Found ping")
                log.info("Sending response")
                await ctx.send(
                    embed=(
                        discord.Embed(
                            title=":mag: Found!",
                            description=f"{ping_msgs[0].author.mention} pinged you [**here**]({ping_msgs[0].jump_url})\n\n[**Your last message**]({last_msg.jump_url})",
                            color=discord.Color.green(),
                        )
                    )
                )
                log.info("Success!")
        else:
            log.info("Ghost pinged")
            log.info("Sending response")
            await ctx.send(
                embed=discord.Embed(
                    title=":ghost: Not found!",
                    description=f"I didn't find anyone. You probably got ***ghost pinged***\n\n[**Your last message**]({last_msg.jump_url})",
                    color=discord.Color.red(),
                ).set_footer(text="Imagine ghost pinging")
            )
            log.info("Success!")
    log.info("END OF `igotpinged`")
