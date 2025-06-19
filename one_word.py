#import required dependencies
import discord
from discord.ext import commands
from discord.ext.commands.errors import MissingRequiredArgument
from discord import Embed
from apikeys import *
import re

intents = discord.Intents.all()
client = commands.Bot(command_prefix='-', intents=intents)
client.remove_command('help')
client.remove_command('finish')

BOT_TOKEN = BOTTOKEN

#  Stores channels with appropriate vars
channels = dict()

def is_discord_mention(s):
    pattern = r'^<@\d+>$'
    return bool(re.match(pattern, s))

async def is_bot_or_self(tag, ctx):
    tag_user = await client.fetch_user(int(tag[2:-1]))
    if tag_user.bot:
        await ctx.send("You cannot add a bot to the game (if you are starting the game and other users were mentioned, they will be added).")
        return True
    elif ctx.author.id == tag_user.id:
        await ctx.send("(There is no need to add yourself.)")
        return True
    else:
        return False

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game("-help"))
    print("The bot is now ready for use!")
    print("------------------------------")

#Gets the username and avatar url of the creator for the -help embed message
async def get_sushi_info(sushi_id):
    sushi_user = await client.fetch_user(sushi_id)
    sushi_username = sushi_user.name
    sushi_avatar_url = sushi_user.avatar.url
    return sushi_username, sushi_avatar_url


def increment_tags_index(channelId):
    global channels
    
    channels[channelId]['tags_index'] += 1
    if channels[channelId]['tags_index'] > len(channels[channelId]['tags_list']) - 1:
        channels[channelId]['tags_index'] = 0

#Gets the usernames of the people involved in making the story for the embed message at the end of the game
async def get_usernames(ctx):
    global channels
 
    tags_list = channels[ctx.channel.id]['tags_list']
    writers = "Authors: "
    index = 1
    punctuation = ', '
    for tag in tags_list:
        tag = int(tag[2:-1]) #removing the '<@' and '>' from the tags
        member = await ctx.guild.fetch_member(tag)
        username = member.name
        if index == len(tags_list):
            punctuation = ""
        writers += username + punctuation
        index += 1
    return writers

async def is_game_running(ctx):
    global channels

    if ctx.channel.id in channels:
        return True
    else:
        await ctx.send("There is no game running in this channel.")
        return False

#Pings the user who's turn it is
async def user_turn_ping(ctx):
    global channels

    mention = channels[ctx.channel.id]['tags_list'][channels[ctx.channel.id]['tags_index']]
    await ctx.send(f"{mention}'s turn.")


@client.command(pass_context = True)
async def start(ctx, *tags):
    global channels

    if len(tags) == 0:
        await ctx.send("Please ping the users you want to play with.")
        return
    elif len(tags) == 1 and tags[0] == '@everyone':
        await ctx.send("You cannot start a game with `@everyone`.")
        return
    elif '@everyone' in tags:
        await ctx.send("(You cannot start a game with `@everyone`, the other users you pinged they will be added).")
    
    if not ctx.channel.id in channels: #To prevent 2 games from running at the same time
        channels[ctx.channel.id] = dict(
           host_id=ctx.author.id,
           tags=[],
           tags_list=[],
           tags_index=0,
           story=""
        )

        #converting tags to a list so we dont have to deal with tuples
        tags_list = []
        tags_list.append("<@" + str(ctx.author.id) + ">")
        for t in list(tags):
            if is_discord_mention(t):
                if await is_bot_or_self(t, ctx) == False:
                    tags_list.append(t)

        if len(tags_list) < 2:
            await ctx.send ("Please ping 1 or more users you want to play with.")

        channels[ctx.channel.id]['tags_list'] = tags_list
  
        await ctx.send("The game has started!")
        await user_turn_ping(ctx)
    else:
        await ctx.send("There is already a game in progress in this channel.")

#Function to add a word
@client.command(pass_context = True)
async def a(ctx, *, phrase):
    global channels

    if await is_game_running(ctx) == False:
        return
    
    id = '<@' + str(ctx.author.id) + '>'

    if id == channels[ctx.channel.id]['tags_list'][channels[ctx.channel.id]['tags_index']]:
        if len(re.findall(r'\s', phrase)) > 3:
            await ctx.send ("Only **1 word** is allowed per turn (3 words [spaces] allowed for names and places).")
            return
        increment_tags_index(ctx.channel.id)
        add_word(ctx, phrase.strip())
        await ctx.send(f"{channels[ctx.channel.id]['tags_list'][channels[ctx.channel.id]['tags_index']]}'s turn.")
    else:
        await ctx.send("It is not your turn.")
    

def add_word(ctx, word):

    open_quote_exp = r'.*\s"$'
    end_quote_exp = r'^"\s'
    comma_exp = r'^,'
    apostrophe_s_exp = r"^'s"
    dot_exp = r'^\.'


    story = channels[ctx.channel.id]['story']
    if bool(re.match(open_quote_exp, word)):
        story += word
    elif bool(re.match(comma_exp, word)) or bool(re.match(apostrophe_s_exp, word)) or bool(re.match(dot_exp, word)) or bool(re.match(end_quote_exp, word)):
        if story[-1] == ' ':
            story = story[:-1] #removing the space that was put after the previous word
        story += word + ' '
    else:
        story += word + ' '
    channels[ctx.channel.id]['story'] = story.replace(" . ", ". ").replace("\t. ", ". ") #fixing excess spaces


@client.command(pass_context = True)
async def remove(ctx, wordcount=None):
    global channels

    if await is_game_running(ctx) == False:
        return
    
    story = channels[ctx.channel.id]['story']
    if channels[ctx.channel.id]['host_id'] == ctx.author.id and ' ' in story:
        if wordcount == None:
            wordcount = 1
        else:
            try:
                wordcount = int(wordcount)
            except ValueError:
                await ctx.send("Please enter the **number** of words to remove.")
                return
        num_words = len(re.findall(r'\s', story)) #usually the number of words would be num_spaces + 1 but that isnt needed here since theres usually always a space at the end of a word in our code

        if wordcount >= num_words:
            story = ""
        else:
            for wordnum in range (wordcount):
                for letter in range (len(story) -2, -1, -1):
                    if story[letter] == ' ':
                        story = story[:letter + 1]
                        break
            
        channels[ctx.channel.id]['story'] = story
        await ctx.send("Word(s) successfully removed.")

    elif story == '':
        await ctx.send("There are no words to remove.")

    elif not ' ' in story:
        story = ''
        await ctx.send("Word successfully removed.")

    elif not channels[ctx.channel.id]['host_id'] == ctx.author.id:
        await ctx.send("Only the host can remove words.")
    
#Adds a user to the queue
@client.command(pass_context = True)
async def push(ctx, push_id=None):
    global channels
    try:
        if push_id == None:
            await ctx.send("Please ping the user you want to push.")
            return
        if await is_game_running(ctx) == False:
            return
        if await is_bot_or_self(push_id, ctx) == True:
            return
        if push_id in channels[ctx.channel.id]['tags_list']:
            await ctx.send("This user is already in the queue.")
        elif ctx.author.id == channels[ctx.channel.id]['host_id']:
            channels[ctx.channel.id]['tags_list'].append(push_id)
            await ctx.send("User successfully added to queue.")
        else:
            await ctx.send("Only the host can add people to the queue.")
    except MissingRequiredArgument:
        await ctx.send("Please ping the user you want to push.")

#Removes a user from the queue
@client.command(pass_context = True)
async def pop(ctx, pop_id=None):
    global channels

    if await is_game_running(ctx) == False:
        return
    if pop_id == None:
        await ctx.send("Please ping the user you want to pop.")
        return

    host_id = channels[ctx.channel.id]['host_id']
    tags_list = channels[ctx.channel.id]['tags_list']
    tags_index = channels[ctx.channel.id]['tags_index']

    if not pop_id in tags_list:
        await ctx.send("The user is not in the queue.")
    elif ctx.author.id == host_id or ("<@" + str(ctx.author.id) + ">") == pop_id:
        if len(tags_list) == 2:
            await ctx.send("Ending the game as a minimum of 2 players is required.")
            await end(ctx)
            return
        
        tags_list.remove(pop_id)

        if tags_index > len(tags_list) - 1:
            tags_index = 0
        if pop_id == ("<@" + str(host_id) + ">"): #In case the host pops himself
            host_id = int((tags_list[tags_index])[2:-1])
            await ctx.send(f"The new host of the game is <@{host_id}>.")

        await ctx.send("User successfully removed from queue.")
 
        channels[ctx.channel.id]['host_id'] = host_id
        channels[ctx.channel.id]['tags_list'] = tags_list
        channels[ctx.channel.id]['tags_index'] = tags_index

        await user_turn_ping(ctx)
    else:
        await ctx.send("Only the host can remove users from the queue (unless you are trying to remove yourself).")



#Changes the host
@client.command(pass_context=True)
async def host(ctx, id_to_host=None):
    global host_id
    if await is_game_running(ctx) == False:
        return
    if id_to_host == None:
        await ctx.send("Please ping the user you want to change the host to.")
        return
    host_id = channels[ctx.channel.id]['host_id']
    if ctx.author.id == host_id:
        
        if id_to_host in channels[ctx.channel.id]['tags_list']:
            id_to_host = int(id_to_host[2:-1]) #removing '<@' and '>' from id_to_host
            host_id = id_to_host
            channels[ctx.channel.id]['host_id'] = host_id
            await ctx.send(f"The new host of the game is <@{host_id}>")
        else:
            await ctx.send("The user is not playing the game at the moment.")
    else:
        await ctx.send("Only the host can change the host.")


@client.command(pass_context = True)
async def skip(ctx):
    global channels

    if await is_game_running(ctx) == False:
        return
    if ctx.author.id == channels[ctx.channel.id]['host_id']:
        increment_tags_index(ctx.channel.id)
        await ctx.send("Turn skipped.")
        await user_turn_ping(ctx)
    else: 
        await ctx.send("Only the host can skip a users turn.")

#Displays the current queue
@client.command(pass_context = True)
async def queue(ctx):
    global channels

    if await is_game_running(ctx) == False:
        return

    if not ('<@' + str(ctx.author.id) + '>') in channels[ctx.channel.id]['tags_list']:
        await ctx.send("Only users who are playing the game can use this command.")
        return

    tags_list = channels[ctx.channel.id]['tags_list']
    tags_index = channels[ctx.channel.id]['tags_index']
    next_in_queue = ''

    for tag in range (tags_index + 1, len(tags_list)):
        next_in_queue += tags_list[tag] + ' '
    for tag in range(0, tags_index):
        next_in_queue += tags_list[tag] + ' '
    await ctx.send(f"Current turn: {tags_list[tags_index]}\nNext in queue: {next_in_queue}")


@client.command(pass_context = True)
async def view(ctx):
    global channels

    if await is_game_running(ctx) == False:
        return
    
    if not ('<@' + str(ctx.author.id) + '>') in channels[ctx.channel.id]['tags_list']:
        await ctx.send("Only users who are playing the game can use this command.")
        return

    story_embed = discord.Embed(description=channels[ctx.channel.id]['story'], color=0xff8000)
    story_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
    await ctx.send(embed=story_embed)


@client.command(pass_context = True)
async def end(ctx):
    global channels

    if await is_game_running(ctx) == False:
        return

    host_id = channels[ctx.channel.id]['host_id']
    story = channels[ctx.channel.id]['story']

    if ctx.author.id == host_id or ctx.author.guild_permissions.administrator:
        await ctx.send("Heres the final story:")
        writers = await get_usernames(ctx)
        story_embed = discord.Embed(description=story, color=0xff8000, title=writers)
        await ctx.send(embed=story_embed)
        # Resetting appropriate variables
        del channels[ctx.channel.id]
        await ctx.send("The game has ended!")
    else:
        await ctx.send("Only a host/administrator can end the game.")


@client.command(pass_context=True)
async def help(ctx):
    embed = Embed(title="Help", description="One word is a fun that you can play with your friends. Each person is allowed to say one word at a time (unless it is a name or place) and you have to try and write a story. The person who started the game is known as the **Host**.\n\n **Note:** When adding words, please avoid using single quotes (') for open and end quotes, use double quotes (\") instead. Also note that incorrect use of grammar may result in the story not coming up in the -view command as expected, as the criteria for inserting spaces is based on the grammar.\n\n **__List of commands__**", color=0x0055ff)

    sushi_username, sushi_avatar_url = await get_sushi_info(546962882047508481) #getting info for the embed author

    # Add commands info to the embed
    embed.set_author(name=sushi_username, icon_url=sushi_avatar_url)
    embed.add_field(name="-start", value="Starts the game. After -start ping the 1 or more people you want to play with, excluding yourself **(make sure there are spaces between the pings)** and they will be added to the queue.", inline=False)
    embed.add_field(name="-end", value="Ends the game. After ending it also displays the final story. An Administrator is also allowed to end the game, in case a host leaves it on. [Host/Administrator only]", inline=False)
    embed.add_field(name="-a", value="Adds a word to the story.", inline=False)
    embed.add_field(name="-remove", value="Removes a certain amount of words from the story. If an amount is not specified the most recent word in the story will be removed. [Host only]", inline=False)
    embed.add_field(name="-push", value="Adds a person to the queue. After -push ping the person you want to add to the queue (only 1 person can be added at a time). [Host only]", inline=False)
    embed.add_field(name="-pop", value="Removes a person from the queue. After -pop ping the person you want to remove from the queue (only 1 person can be removed at a time). [Host only, unless you're trying to remove yourself]", inline=False)
    embed.add_field(name="-host", value="Changes the host of the game. After -host ping the person you want to change the host to. [Host only]", inline=False)
    embed.add_field(name="-skip", value="Skips the current turn. The user can also skip their own turn using this command. [Host only]", inline=False)
    embed.add_field(name="-queue", value="Displays the current players in queue.", inline=False)
    embed.add_field(name="-view", value="View the story that has been made so far.", inline=False)

    await ctx.send(embed=embed)

client.run(BOT_TOKEN)