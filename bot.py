GUILD_ID = 0 # your guild id here

import discord
from discord.ext import commands
from urllib.parse import urlparse
import asyncio
import textwrap
import datetime
import time
import json
import sys
import os
import re
import string
import traceback
import io
import inspect
import random
from contextlib import redirect_stdout
from .bot import BlobGivingBot
from .config import Config
import config

class Modmail(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=self.get_pre)
        self.uptime = datetime.datetime.utcnow()
        self._add_commands()

    def _add_commands(self):
        '''Adds commands automatically'''
        for attr in dir(self):
            cmd = getattr(self, attr)
            if isinstance(cmd, commands.Command):
                self.add_command(cmd)

    @property
    def token(self):
        '''Returns your token wherever it is'''
        try:
            with open('config.json') as f:
                config = json.load(f)
                if config.get('TOKEN') == "your_token_here":
                    if not os.environ.get('TOKEN'):
                        self.run_wizard()
                else:
                    token = config.get('TOKEN').strip('\"')
        except FileNotFoundError:
            token = None
        return os.environ.get('TOKEN') or token
    
    @staticmethod
    async def get_pre(bot, message):
        '''Returns the prefix.'''
        with open('config.json') as f:
            prefix = json.load(f).get('PREFIX')
        return os.environ.get('PREFIX') or prefix or 'm.'

    @staticmethod
    def run_wizard():
        '''Wizard for first start'''
        print('------------------------------------------')
        token = input('Enter your token:\n> ')
        print('------------------------------------------')
        data = {
                "TOKEN" : token,
            }
        with open('config.json','w') as f:
            f.write(json.dumps(data, indent=4))
        print('------------------------------------------')
        print('Restarting...')
        print('------------------------------------------')
        os.execv(sys.executable, ['python'] + sys.argv)

    @classmethod
    def init(cls, token=None):
        '''Starts the actual bot'''
        bot = cls()
        if token:
            to_use = token.strip('"')
        else:
            to_use = bot.token.strip('"')
        try:
            bot.run(to_use, activity=discord.Game(os.getenv('STATUS')), reconnect=True)
        except Exception as e:
            raise e

    async def on_connect(self):
        print('---------------')
        print('Modmail connected!')
        status = os.getenv('STATUS')
        if status:
            print(f'Setting Status to {status}')
        else:
            print('No status set.')

    @property
    def guild_id(self):
        from_heroku = os.environ.get('GUILD_ID')
        return int(from_heroku) if from_heroku else GUILD_ID

    async def on_ready(self):
        '''Bot startup, sets uptime.'''
        self.guild = discord.utils.get(self.guilds, id=self.guild_id)
        print(textwrap.dedent(f'''
        ---------------
        Client is ready!
        ---------------
        Author: Kyb3r#7220
        ---------------
        Logged in as: {self.user}
        User ID: {self.user.id}
        ---------------
        '''))

    def overwrites(self, ctx, modrole=None):
        '''Permision overwrites for the guild.'''
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False)
        }

        if modrole:
            overwrites[modrole] = discord.PermissionOverwrite(read_messages=True)
        else:
            for role in self.guess_modroles(ctx):
                overwrites[role] = discord.PermissionOverwrite(read_messages=True)
        return overwrites
    
    def rules_embed(self, prefix):
        em = discord.Embed(color=0x00FFFF)
        em.set_author(name='Rules', icon_url=self.user.avatar_url)
        em.description = 'You should follow the rules mentioned below' 
                 

        cmds = '1) Be respectful.\n' \
               '2) Sending/Linking any harmful material such as viruses, IP grabbers or harmware results in an immediate and permanent ban.\n' \
               '3) Use proper grammar and spelling and never do spammaing.' \
               '4) Usage of excessive extreme innapropriate langauge is prohibited.\n' \
               '5) Mentioning @everyone or @here , the Moderators or a specific person without proper reason is prohibited.\n' \
               '6) Act civil in Voice Chat.\n' \
               '7) Post content in the correct channels.\n' \
               '8) Don not post personal information of anyone without permission.\n' \
               '9) Listen to what Staff & Moderator says.\n' \
               '10) Do not post graphic pictures of minors (<18yo)'               
               
        warn = 'Never Try to break any rules otherwise you will be punished for your violation '
        em.add_field(name='Warning', value=warn)
        em.add_field(name='Github', value='https://github.com/uksoftworld/modmail')
        em.set_footer(text='Thanks for adding our bot')
        return em

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setupserver(self, ctx, *, modrole: discord.Role=None):
        '''Sets up a server'''
        if discord.utils.get(ctx.guild.categories, name='<Information For All>'):
            return await ctx.send('This server is already set up.')

        infocateg = await ctx.guild.create_category(
            name='<Information For All>', 
            overwrites=self.overwrites(ctx, modrole=modrole)
            )
        gencateg = await ctx.guild.create_category(
            name='<General Zone>', 
            overwrites=self.overwrites(ctx)
            )
        botcateg = await ctx.guild.create_category(
            name='<BOTS Zone>', 
            overwrites=self.overwrites(ctx)
            )
        concateg = await ctx.guild.create_category(
            name='<Content Zone>', 
            overwrites=self.overwrites(ctx)
            )
        mucateg = await ctx.guild.create_category(
            name='<Music Zone>', 
            overwrites=self.overwrites(ctx)
            )
        vccateg = await ctx.guild.create_category(
            name='<Music Zone>', 
            overwrites=self.overwrites(ctx)
            )
        await infocateg.edit(position=0)
        c = await ctx.guild.create_text_channel(name='🎉welcome🎉', category=infocateg)
        a = await ctx.guild.create_text_channel(name='🎯rules🎯', category=infocateg)
        c = await ctx.guild.create_text_channel(name='🎥featured-content🎥', category=infocateg)
        c = await ctx.guild.create_text_channel(name='📢announcements📢', category=infocateg)
        c = await ctx.guild.create_text_channel(name='📢vote_polls📢', category=infocateg)
        c = await ctx.guild.create_text_channel(name='🎮general_chat🎮', category=gencateg)
        c = await ctx.guild.create_text_channel(name='🎮general_media🎮', category=gencateg)
        c = await ctx.guild.create_text_channel(name='👍bots_zone👍', category=botcateg)
        c = await ctx.guild.create_text_channel(name='🎥youtube_links🎥', category=concateg)
        c = await ctx.guild.create_text_channel(name='🎥giveaway_links🎥', category=concateg)
        c = await ctx.guild.create_text_channel(name='🎥other_links🎥', category=concateg)
        c = await ctx.guild.create_voice_channel(name='🔥Music Zone🔥', category=mucateg)
        c = await ctx.guild.create_text_channel(name='🔥music_commands🔥', category=mucateg)
        c = await ctx.guild.create_voice_channel(name='🔥Chill Voice🔥', category=vccateg)
        c = await ctx.guild.create_voice_channel(name='🔥General Voice🔥', category=vccateg)
        c = await ctx.guild.create_voice_channel(name='🔥Youtube Talks🔥', category=vccateg)

        await c.edit(topic='Manually add user id\'s to block users.\n\n'
                           'Blocked\n-------\n\n')
        await a.send(embed=self.rules_embed(ctx.prefix))
        await ctx.send('Successfully set up server.')
        
    def help_embed(self, prefix):
        em = discord.Embed(color=0x00FFFF)
        em.set_author(name='Mod Mail - Help', icon_url=self.user.avatar_url)
        em.description = 'This bot is a python implementation of a stateless "Mod Mail" bot. ' \
                         'Improved by the suggestions of others. This bot ' \
                         'saves no data and utilises channel topics for storage and syncing.' 
                 

        cmds = f'`{prefix}setup [modrole] <- (optional)` - Command that sets up the bot.\n' \
               f'`{prefix}reply <message...>` - Sends a message to the current thread\'s recipient.\n' \
               f'`{prefix}close` - Closes the current thread and deletes the channel.\n' \
               f'`{prefix}disable` - Closes all threads and disables modmail for the server.\n' \
               f'`{prefix}block` - Blocks a user from using modmail!' \
               f'`{prefix}unblock` - Unblocks a user from using modmail!'

        warn = 'Do not manually delete the category or channels as it will break the system. ' \
               'Modifying the channel topic will also break the system.'
        em.add_field(name='Commands', value=cmds)
        em.add_field(name='Warning', value=warn)
        em.add_field(name='Github', value='https://github.com/uksoftworld/modmail')
        em.set_footer(text='Star the repository to unlock hidden features!')

        return em

    @commands.command()
    async def rolldice(self, ctx):
        """Rolls a 6 sided die."""
        choices = ['1', '2', '3', '4', '5', '6']
        color = discord.Color(value=0x00ff00)
        em = discord.Embed(color=color, title='Rolled! (1 6-sided die)', description=random.choice(choices))
        await ctx.send(embed=em)
    @commands.command()
    async def giveaway(self, ctx: commands.Context, *, description: str):
        """Start a new Giveaway."""
        ends_at = ctx.message.created_at + config.giveaway_duration

        embed = discord.Embed(
            title=description,
            description=f'React with {self.emoji} to win!',
            color=discord.Color.magenta(),
            timestamp=ends_at,
        )
        embed.set_footer(text='Ends at')

        msg = await self.channel.send(embed=embed)
        await msg.add_reaction(self.emoji)

        await self.config.put(ends_at.timestamp(), msg.id)
        await ctx.send('Giveaway started!')

        if self._giveaway_task.done():
            self._giveaway_task = self.bot.loop.create_task(self.giveaway_loop())

    @commands.command()
    async def reroll(self, ctx: commands.Context, *, message_id: int):
        """Reroll a giveaway based on a message/giveaway ID."""
        try:
            message = await self.channel.get_message(message_id)
        except discord.NotFound:
            return await ctx.send(f'Couldn\'t find message with ID {message_id} in the giveaway channel!')

        # don't allow rerolling a giveaway which is running
        if message.created_at > ctx.message.created_at - config.giveaway_duration:
            return await ctx.send('This giveaway is still running! Rerolling can only be done after it has ended.')

        try:
            winner = await self.roll_user(message)
        except NoWinnerFound as e:
            await ctx.send(e)
        else:
            embed = message.embeds[0]
            giveaway_desc = embed.title

            embed.description = f'{winner.mention} is the new winner!'
            await message.edit(embed=embed)

            await ctx.send(f'Rerolled! {winner.mention} is the new winner for **{giveaway_desc}**!')

    async def giveaway_loop(self):
        # channels / emoji aren't loaded before being ready
        await self.bot.wait_until_ready()

        # run until Config.__len__ returns 0
        while self.config:
            # the keys of the config are unix timestamps so we can easily sort them
            oldest = min(self.config.all())

            until_end = float(oldest) - datetime.datetime.utcnow().timestamp()
            await asyncio.sleep(until_end)

            message_id = self.config.get(oldest)

            try:
                message = await self.channel.get_message(message_id)
            except discord.NotFound:
                # giveaways might be removed for moderation purposes, we don't want to post anything in this case
                log.warning(f'Couldn\'t find message associated with giveaway {message_id}, skipping')
                await self.config.remove(oldest)
                continue

            # prepare editing the embed
            embed = message.embeds[0]
            embed.set_footer(text='Ended at')

            # the name / title of this giveaway
            giveaway_desc = embed.title

            try:
                winner = await self.roll_user(message)
            except NoWinnerFound:
                embed.description = f'No one won this giveaway!'
                await message.edit(embed=embed)

                await self.channel.send(f'No winner found for **{giveaway_desc}**!')
            else:
                embed.description = f'{winner.mention} won this giveaway!'
                await message.edit(embed=embed)

                await self.channel.send(f'Congratulations {winner.mention}! You won **{giveaway_desc}**!')
            finally:
                await self.config.remove(oldest)

    async def roll_user(self, message: discord.Message) -> discord.Member:
        try:
            reaction = next(x for x in message.reactions if getattr(x.emoji, 'id', None) == self.emoji.id)
        except StopIteration:  # if a moderator deleted the emoji for some reason
            raise NoWinnerFound('Couldn\'t find giveaway emoji on specified message')

        users = await reaction.users().filter(lambda x: not x.bot).flatten()
        if not users:
            raise NoWinnerFound('No human reacted with the giveaway emoji on this message')
        else:
            return random.choice(users)


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def dm(self, ctx, user: discord.Member, *, msg: str):
        """Escort your DM to someone thru the bot. Usage: *dm [tag person] [msg]"""
        try:
            await user.send(msg)
            await ctx.message.delete()            
            await ctx.send("Success! Your DM has made it! :white_check_mark: ")
        except discord.ext.commands.MissingPermissions:
            await ctx.send("Aw, come on! You thought you could get away with DM'ing people without permissions.")
        except:
            await ctx.send("Error :x:. Make sure your message is shaped in this way: *dm [tag person] [msg]")
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def mute(self, ctx, user: discord.Member, mutetime=None):
        '''Forces someone to shut up. Usage: *mute [user] [time in mins]'''
        try:
            if mutetime is None:
                await ctx.channel.set_permissions(user, send_messages=False)
                await ctx.send(f"{user.mention} is now forced to shut up. :zipper_mouth: ")
            else:
                try:
                    mutetime =int(mutetime)
                    mutetime = mutetime * 60
                except ValueError:
                    return await ctx.send("Your time is an invalid number. Make sure...it is a number.")
                await ctx.channel.set_permissions(user, send_messages=False)
                await ctx.channel.send(f"{user.mention} is now forced to shut up. :zipper_mouth: ")
                await asyncio.sleep(mutetime)
                await ctx.channel.set_permissions(user, send_messages=True)
                await ctx.channel.send(f"{user.mention} is now un-shutted up.")
        except discord.Forbidden:
            return await ctx.send("I could not mute the user. Make sure I have the manage channels permission.")
        except discord.ext.commands.MissingPermissions:
            await ctx.send("Aw, come on! You thought you could get away with shutting someone up without permissions.")


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unmute(self, ctx, user: discord.Member):
        '''Allows someone to un-shut up. Usage: *unmute [user]'''
        await ctx.channel.set_permissions(user, send_messages=True)
        await ctx.channel.send(f"{user.mention} is now un-shutted up.")

    @commands.command()
    async def flipcoin(self, ctx):
        """Flip a coin. Any coin."""
        choices = ['Heads', 'Tails', 'Coin self-destructed.']
        color = discord.Color(value=0x00ff00)
        em=discord.Embed(color=color, title='Flipped a coin!')
        em.description = random.choice(choices)
        await ctx.send(embed=em)
    @commands.command(aliases=['av'])
    async def avatar(self, ctx, user: discord.Member):
        """Returns a user's avatar url. Use *av [user], or just *av for your own."""
        if user is None:
            await ctx.send(ctx.message.author.avatar_url)                   
        else:
            await ctx.send(user.avatar_url)      
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setupmail(self, ctx, *, modrole: discord.Role=None):
        '''Sets up a server for modmail'''
        if discord.utils.get(ctx.guild.categories, name='Mod Mail'):
            return await ctx.send('This server is already set up.')

        categ = await ctx.guild.create_category(
            name='Mod Mail', 
            overwrites=self.overwrites(ctx, modrole=modrole)
            )
        await categ.edit(position=0)
        c = await ctx.guild.create_text_channel(name='bot-info', category=categ)
        await c.edit(topic='Manually add user id\'s to block users.\n\n'
                           'Blocked\n-------\n\n')
        await c.send(embed=self.help_embed(ctx.prefix))
        await ctx.send('Successfully set up server.')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx):
        '''Close all threads and disable modmail.'''
        categ = discord.utils.get(ctx.guild.categories, name='Mod Mail')
        if not categ:
            return await ctx.send('This server is not set up.')
        for category, channels in ctx.guild.by_category():
            if category == categ:
                for chan in channels:
                    if 'User ID:' in str(chan.topic):
                        user_id = int(chan.topic.split(': ')[1])
                        user = self.get_user(user_id)
                        await user.send(f'**{ctx.author}** has closed this modmail session.')
                    await chan.delete()
        await categ.delete()
        await ctx.send('Disabled modmail.')


    @commands.command(name='close')
    @commands.has_permissions(manage_channels=True)
    async def _close(self, ctx):
        '''Close the current thread.'''
        if 'User ID:' not in str(ctx.channel.topic):
            return await ctx.send('This is not a modmail thread.')
        user_id = int(ctx.channel.topic.split(': ')[1])
        user = self.get_user(user_id)
        em = discord.Embed(title='Thread Closed')
        em.description = f'**{ctx.author}** has closed this modmail session.'
        em.color = discord.Color.red()
        try:
            await user.send(embed=em)
        except:
            pass
        await ctx.channel.delete()

    @commands.command()
    async def ping(self, ctx):
        """Pong! Returns your websocket latency."""
        em = discord.Embed()
        em.title ='Pong! Websocket Latency:'
        em.description = f'{self.ws.latency * 1000:.4f} ms'
        em.color = 0x00FF00
        await ctx.send(embed=em)

    def guess_modroles(self, ctx):
        '''Finds roles if it has the manage_guild perm'''
        for role in ctx.guild.roles:
            if role.permissions.manage_guild:
                yield role

    def format_info(self, message):
        '''Get information about a member of a server
        supports users from the guild or not.'''
        user = message.author
        server = self.guild
        member = self.guild.get_member(user.id)
        avi = user.avatar_url
        time = datetime.datetime.utcnow()
        desc = 'Modmail thread started.'
        color = 0

        if member:
            roles = sorted(member.roles, key=lambda c: c.position)
            rolenames = ', '.join([r.name for r in roles if r.name != "@everyone"]) or 'None'
            member_number = sorted(server.members, key=lambda m: m.joined_at).index(member) + 1
            for role in roles:
                if str(role.color) != "#000000":
                    color = role.color

        em = discord.Embed(colour=color, description=desc, timestamp=time)

        em.add_field(name='Account Created', value=str((time - user.created_at).days)+' days ago.')
        em.set_footer(text='User ID: '+str(user.id))
        em.set_thumbnail(url=avi)
        em.set_author(name=user, icon_url=server.icon_url)
      

        if member:
            em.add_field(name='Joined', value=str((time - member.joined_at).days)+' days ago.')
            em.add_field(name='Member No.',value=str(member_number),inline = True)
            em.add_field(name='Nick', value=member.nick, inline=True)
            em.add_field(name='Roles', value=rolenames, inline=True)
        
        em.add_field(name='Message', value=message.content, inline=False)

        return em

    async def send_mail(self, message, channel, mod):
        author = message.author
        fmt = discord.Embed()
        fmt.description = message.content
        fmt.timestamp = message.created_at

        urls = re.findall(r'(https?://[^\s]+)', message.content)

        types = ['.png', '.jpg', '.gif', '.jpeg', '.webp']

        for u in urls:
            if any(urlparse(u).path.endswith(x) for x in types):
                fmt.set_image(url=u)
                break

        if mod:
            fmt.color=discord.Color.green()
            fmt.set_author(name=str(author), icon_url=author.avatar_url)
            fmt.set_footer(text='Moderator')
        else:
            fmt.color=discord.Color.gold()
            fmt.set_author(name=str(author), icon_url=author.avatar_url)
            fmt.set_footer(text='User')

        embed = None

        if message.attachments:
            fmt.set_image(url=message.attachments[0].url)

        await channel.send(embed=fmt)

    async def process_reply(self, message):
        try:
            await message.delete()
        except discord.errors.NotFound:
            pass
        await self.send_mail(message, message.channel, mod=True)
        user_id = int(message.channel.topic.split(': ')[1])
        user = self.get_user(user_id)
        await self.send_mail(message, user, mod=True)

    def format_name(self, author):
        name = author.name
        new_name = ''
        for letter in name:
            if letter in string.ascii_letters + string.digits:
                new_name += letter
        if not new_name:
            new_name = 'null'
        new_name += f'-{author.discriminator}'
        return new_name

    @property
    def blocked_em(self):
        em = discord.Embed(title='Message not sent!', color=discord.Color.red())
        em.description = 'You have been blocked from using modmail.'
        return em

    async def process_modmail(self, message):
        '''Processes messages sent to the bot.'''
        try:
            await message.add_reaction('✅')
        except:
            pass

        guild = self.guild
        author = message.author
        topic = f'User ID: {author.id}'
        channel = discord.utils.get(guild.text_channels, topic=topic)
        categ = discord.utils.get(guild.categories, name='Mod Mail')
        top_chan = categ.channels[0] #bot-info
        blocked = top_chan.topic.split('Blocked\n-------')[1].strip().split('\n')
        blocked = [x.strip() for x in blocked]

        if str(message.author.id) in blocked:
            return await message.author.send(embed=self.blocked_em)

        em = discord.Embed(title='Thanks for the message!')
        em.description = 'The moderation team will get back to you as soon as possible!'
        em.color = discord.Color.green()

        if channel is not None:
            await self.send_mail(message, channel, mod=False)
        else:
            await message.author.send(embed=em)
            channel = await guild.create_text_channel(
                name=self.format_name(author),
                category=categ
                )
            await channel.edit(topic=topic)
            await channel.send('@here', embed=self.format_info(message))

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)
        if isinstance(message.channel, discord.DMChannel):
            await self.process_modmail(message)

    @commands.command()
    async def reply(self, ctx, *, msg):
        '''Reply to users using this command.'''
        categ = discord.utils.get(ctx.guild.categories, id=ctx.channel.category_id)
        if categ is not None:
            if categ.name == 'Mod Mail':
                if 'User ID:' in ctx.channel.topic:
                    ctx.message.content = msg
                    await self.process_reply(ctx.message)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def block(self, ctx, id=None):
        '''Block a user from using modmail.'''
        if id is None:
            if 'User ID:' in str(ctx.channel.topic):
                id = ctx.channel.topic.split('User ID: ')[1].strip()
            else:
                return await ctx.send('No User ID provided.')

        categ = discord.utils.get(ctx.guild.categories, name='Mod Mail')
        top_chan = categ.channels[0] #bot-info
        topic = str(top_chan.topic)
        topic += id + '\n'

        if id not in top_chan.topic:  
            await top_chan.edit(topic=topic)
            await ctx.send('User successfully blocked!')
        else:
            await ctx.send('User is already blocked.')

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unblock(self, ctx, id=None):
        '''Unblocks a user from using modmail.'''
        if id is None:
            if 'User ID:' in str(ctx.channel.topic):
                id = ctx.channel.topic.split('User ID: ')[1].strip()
            else:
                return await ctx.send('No User ID provided.')

        categ = discord.utils.get(ctx.guild.categories, name='Mod Mail')
        top_chan = categ.channels[0] #bot-info
        topic = str(top_chan.topic)
        topic = topic.replace(id+'\n', '')

        if id in top_chan.topic:
            await top_chan.edit(topic=topic)
            await ctx.send('User successfully unblocked!')
        else:
            await ctx.send('User is not already blocked.')

    @commands.command(hidden=True, name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates python code"""
        allowed = [int(x) for x in os.getenv('OWNERS', '').split(',')]
        if ctx.author.id not in allowed: 
            return
        
        env = {
            'bot': self,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            'source': inspect.getsource
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()
        err = out = None

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            err = await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
            return await err.add_reaction('\u2049')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            err = await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            if ret is None:
                if value:
                    try:
                        out = await ctx.send(f'```py\n{value}\n```')
                    except:
                        await ctx.send('```Result is too long to send.```')
            else:
                self._last_result = ret
                try:
                    out = await ctx.send(f'```py\n{value}{ret}\n```')
                except:
                    await ctx.send('```Result is too long to send.```')
        if out:
            await ctx.message.add_reaction('\u2705') #tick
        if err:
            await ctx.message.add_reaction('\u2049') #x
        else:
            await ctx.message.add_reaction('\u2705')

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')
        
if __name__ == '__main__':
    Modmail.init()
