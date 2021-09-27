import discord
from discord.ext        import commands

from cogs.base_cog      import BaseCog

from utils              import (JSON_DATA_PATH, get_json_data, set_json_data, 
                                get_emoji, get_mentioned_member, create_progress_bar, 
                                create_black_embed)

import asyncio

class ExpeditionCog(BaseCog):
    def __init__(self, bot):
        super().__init__(bot, category="Expedition")

    @commands.command(
    )
    @commands.guild_only()
    async def expedition(self, ctx, *args):
        await ctx.send("Expedition started!")
        asyncio.create_task(self.inner(ctx))

    async def inner(self, ctx):
        await asyncio.sleep(1)
        await ctx.send("Expedition completed!")



def setup(bot):
    bot.add_cog(ExpeditionCog(bot))
