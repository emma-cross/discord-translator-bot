import discord
from TranslateObjs import *
from translate import Translate

# Set Process Name #
import setproctitle
setproctitle.setproctitle('translator')

intents = discord.Intents()
intents.guilds = True
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

servers = []

async def IsMedia(message):
    length = len(message)
    if length >= 4:
        # check for url
        if "http://" == message[:7] or "https://" == message[:8]:
            return True
        # check for other media
        ext = message[length-4:]
        if ext in [".png", ".jpg", "jpeg", ".mp4", ".mov", ".gif"]:
            return True
    return False

async def GetPFP(server, username):
    for emoji in server.emojis:
        if emoji.name == username:
            return f"<:{username}:{emoji.id}>"
    return ""

@client.event
async def on_ready():
    # find servers that bot has records for
    for guild in client.guilds:
        print(f"init \"{guild.name}\"")
        servers.append(TranslateServer(guild.name))
    # ok now we are online
    print(f"{client.user} is online ({len(servers)} servers)")
    for server in servers:
        print(f"{server.name}:")
        for channel in server.channels:
            print(f"  {channel.cid}")

@client.event
async def on_message(incoming_message):
    # early reject any empty messages / messages from bot itself
    if incoming_message.content == "" and 0 == len(incoming_message.attachments):
        return
    if incoming_message.author.id == client.user.id:
        return

    # parse message
    message = incoming_message.content
    tokens = message.split(" ")
    username = str(incoming_message.author)
    nickname = incoming_message.author.display_name
    server_name = incoming_message.guild.name

    ### handle message ###
    # testing
    if tokens[0].lower() == "!test":
        await incoming_message.channel.send(f"{message} {username} :3 <@{str(incoming_message.author.id)}>")
        return

    # channel registration
    if tokens[0].lower() == "!register":
        if len(tokens) >= 2 and "list" == tokens[1]:
            # display list of registered channels
            msg = "Registered Channels List:"
            server = servers[servers.index(server_name)]
            for channel in server.channels:
                msg += f"\n{channel.language}: {channel.cid}"
            await incoming_message.channel.send(msg)
        elif len(tokens) >= 3:
            channelid = tokens[1]
            language = tokens[2]
            server = servers[servers.index(server_name)]
            if "none" != language:
                retVal = server.registerChannel(TranslateChannel(channelid, language))
                if 0 == retVal:
                    server.write()
                    await incoming_message.channel.send(f"Registered {channelid} for language={language}.")
                elif -1 == retVal:
                    await incoming_message.channel.send(f"ERROR: Failed to register {channelid} - unknown language")
            else:
                server.unregisterChannel(channelid)
                await incoming_message.channel.send(f"Unregistered {channelid}.")
        else:
            await incoming_message.channel.send(f"Usage:\n\
`!register list`  view list of registered channels\n\
`!register #[channel] [language]`  register a channel\n\
`!register #[channel] none`  unregister a channel")
        return

    # get embed content from message (images, videos, etc.)
    embeds = []
    for a in incoming_message.attachments:
        embed = discord.Embed(description=a.url)
        embed.set_image(url=a.url)
        embeds.append(embed)

    # check if the message comes from one of the translator channels
    server = servers[servers.index(server_name)]
    cid = f"<#{str(incoming_message.channel.id)}>"
    if cid in server.channels:
        # get channel where message is coming from (if registered)
        original_channel = server.channels[server.channels.index(cid)]
        # translate message into every registered channel
        for channel in server.channels:
            if channel == original_channel: continue
            #print(f"translating {original_channel.cid} => {channel.cid}")
            discord_channel = client.get_channel(channel.getID())
            translated_message = message
            if not await IsMedia(message):
                translated_message = Translate(message, original_channel.language, channel.language)
            pfp = await GetPFP(incoming_message.guild, username)
            await discord_channel.send(f"{pfp} `{nickname}`  {translated_message}", embeds=embeds)

# init bot
TOKEN = open("token.txt").read()
client.run(TOKEN)
