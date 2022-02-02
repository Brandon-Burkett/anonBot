import discord
from discord.ext import tasks, commands
import dotenv
import os

dotenv.load_dotenv('.env')

bot = commands.Bot(command_prefix='!', description="Ask me anything!")

privateChannelId = os.getenv('PRIVATE_CHANNEL_ID')


@bot.event
async def on_ready():
    print(f"""I am logged in as {bot.user}""")


@bot.command()
@commands.has_permissions(administrator=True)
async def full_anon(ctx):

    await ctx.send("Full anon")
    await ctx.message.delete()


@bot.command()
@commands.has_permissions(administrator=True)
async def setprivate(ctx):
    privateChannelId = ctx.channel.id
    os.environ['PRIVATE_CHANNEL_ID'] = str(privateChannelId)
    dotenv.set_key(".env", "PRIVATE_CHANNEL_ID",
                   os.environ["PRIVATE_CHANNEL_ID"])
    await ctx.send("Private channel set!")


@bot.command()
async def anon(ctx):
    if(privateChannelId):
        await ctx.message.delete()  # Delete the command message
        if(ctx.message.reference == None):  # Message isn't reply, send to channel
            # Send the message and any attachments in the channel
            await ctx.channel.send(content=ctx.message.content.replace('!anon ', ''), files=[await attachment.to_file() for attachment in ctx.message.attachments])
        else:  # Message is reply, send as reply to original message
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            await message.reply(content=ctx.message.content.replace('!anon ', ''), files=[await attachment.to_file() for attachment in ctx.message.attachments])
        await bot.get_channel(int(privateChannelId)).send(content=ctx.message.author.display_name + ": " + ctx.message.content.replace('!anon ', ''), files=[await attachment.to_file() for attachment in ctx.message.attachments])
    else:
        await ctx.send("Private channel not set! Please set it with !setprivate in the channel you wish to be the private channel.")

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
