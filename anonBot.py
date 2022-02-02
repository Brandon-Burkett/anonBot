import discord
from discord.ext import tasks, commands
import dotenv
import os
import json

dotenv.load_dotenv('.env')

bot = commands.Bot(command_prefix='!', description="Bot that allows the semi-anonymous posting of questions!",
                   help_command=commands.DefaultHelpCommand(no_category='Commands'))


@bot.event
async def on_ready():
    print(f"""I am logged in as {bot.user}""")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for !anon <message>"))


@bot.command(brief='Set the private logging channel (Admin)', description='This is an admin-only command. This command will set the private logging channel for the bot. This channel will be used to log all questions and the user who asked them. This channel must be set before the !anon command will work.')
@commands.has_permissions(administrator=True)
async def setprivate(ctx):
    f = open('db.json', "r+")
    data = json.load(f)

    privateChannelId = ctx.channel.id
    if(str(ctx.message.guild.id) in data):
        data[str(ctx.message.guild.id)]['privateChannelId'] = privateChannelId
    else:
        data[ctx.message.guild.id] = {'privateChannelId': privateChannelId}
    print(data)

    f.seek(0)
    json.dump(data, f, indent=4)

    f.close()

    await ctx.send("Private channel set!")


@bot.command(brief='Use !anon <message> to send a semi-anonymous message!', description='Using this command will delete the message you sent, and send the content of the message as the bot. The original sender and message will still be logged in the private logging channel.')
async def anon(ctx):
    f = open('db.json', "r")
    data = json.load(f)

    await ctx.message.delete()  # Delete the command message

    if(str(ctx.message.guild.id) in data):
        if(ctx.message.reference == None):  # Message isn't reply, send to channel
            # Send the message and any attachments in the channel
            await ctx.channel.send(content=ctx.message.content.replace('!anon ', ''), files=[await attachment.to_file() for attachment in ctx.message.attachments])
        else:  # Message is reply, send as reply to original message
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            await message.reply(content=ctx.message.content.replace('!anon ', ''), files=[await attachment.to_file() for attachment in ctx.message.attachments])
        await bot.get_channel(data[str(ctx.message.guild.id)]['privateChannelId']).send(content=ctx.message.author.display_name + ": " + ctx.message.content.replace('!anon ', ''), files=[await attachment.to_file() for attachment in ctx.message.attachments])
    else:
        await ctx.send("Private channel not set! Please set it with !setprivate in the channel you wish to be the private channel.")

    f.close()

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
