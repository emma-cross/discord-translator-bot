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
async def on_shard_ready(shard_id):
    print(f"{client.user} is online at {shard_id}")

@client.event
async def on_message(incoming_message):
    # early reject any empty messages / messages from bot itself
    if incoming_message.content == "":
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

    # check if the message comes from one of the translator channels
    server = servers[servers.index(server_name)]
    try:
        # get channel where message is coming from (if registered)
        index = server.channels.index(f"<#{str(incoming_message.channel.id)}>")
        original_channel = server.channels[index]
        # translate message into every registered channel
        for channel in server.channels:
            if channel == original_channel: continue
            #print(f"translating {original_channel.cid} => {channel.cid}")
            discord_channel = client.get_channel(channel.getID())
            translated_message = Translate(message, original_channel.language, channel.language)
            pfp = await GetPFP(incoming_message.guild, username)
            await discord_channel.send(f"{pfp} `{nickname}`  {translated_message}")
    except ValueError:
        # ignore msg if not in registered channel
        None

# init bot
TOKEN = open("token.txt").read()
client.run(TOKEN)
