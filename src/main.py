import os
import discord
import logging
import pandas as pd
from replit import db
import rollbar
from app import App, BotEnum

logging.basicConfig(level=logging.INFO)

discord_token = os.environ["DISCORD_TOKEN"]
discord_channel = os.environ["DISCORD_CHANNEL_ID"]
discord_config_channel = os.environ["DISCORD_CONFIG_CHANNEL_ID"]
discord_admin = os.environ["DISCORD_ADMIN_LIST"]
rollbar_secret_key = os.environ["ROLLBAR_SECRET_KEY"]
rollbar_environment = os.environ["ROLLBAR_ENVIRONMENT"]

rollbar.init(rollbar_secret_key, rollbar_environment)

intents = discord.Intents.all() # You can use this
intents.members = True
intents.presences = True
client = discord.Client(intents=intents)
app = App()

guild = discord.Guild

success_color = 0x0027FF
error_color = 0xFF0000
valid_color = 0x00FF00

allowlist_command = "!dreamlist "
allowlist_check_command = "!dreamcheck "
allowlist_admin = "!dreamadmin"
snapshot_admin = "!snapshot"

discord_watching_text = "the Dreamers"


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name=discord_watching_text))

@client.event
async def on_message(message):
    author_id = message.author.id

    if message.author == client.user:
        return

    if str(message.channel.id) == discord_channel:
        if await app.get_bot(BotEnum.ALLOWLIST).run(message):
          pass
        elif await app.get_bot(BotEnum.CLAIMLIST).run(message):
          pass
        else:
            try:
                if str(author_id) not in discord_admin:
                    await message.delete()
            except:
                rollbar.report_exc_info()
      
    if str(message.channel.id) == discord_config_channel:
        if await app.get_bot(BotEnum.ALLOWLIST).run_admin(message):
          pass
        elif await app.get_bot(BotEnum.CLAIMLIST).run_admin(message):
          pass

          # if message.content.startswith(allowlist_admin):
        #     try:
        #         if str(author_id) in discord_admin:
        #             data = pd.DataFrame(
        #                 columns=['author', 'address', 'invocation'])
        #             keys = db.keys()
        #             for key in keys:
        #                 data = data.append(
        #                     {
        #                         'author': key,
        #                         'address': db[key]["address"],
        #                         'invocation': db[key]["invocation"]
        #                     },
        #                     ignore_index=True)

        #             file_location = f"{str(message.channel.guild.id) + '_' + str(message.channel.id)}.csv"
        #             data.to_csv(
        #                 file_location)  # Saving the file as a .csv via pandas

        #             answer = discord.Embed(
        #                 title="Hi, admin! Here is the allowlist file",
        #                 description=
        #                 f"""It might have taken a while, but here is what you asked for.\n\n`Server` : **{message.guild.name}**\n`Channel` : **{message.channel.name}**""",
        #                 colour=success_color)
        #             await message.author.send(embed=answer)
        #             await message.author.send(file=discord.File(
        #                 file_location,
        #                 filename='data.csv'))  # Sending the file
        #             os.remove(file_location)  # Deleting the file
        #         else:
        #             raise ValueError("author ${author_id} not an admin".format(
        #                 author_id=author_id))
        #     except:
        #         rollbar.report_exc_info()
              
        # elif message.content.startswith(snapshot_admin):
        #   for guild in client.guilds:
        #     if guild.id == 872755102736322610:
        #       data = pd.DataFrame(
        #         columns=['id', 'username', 'roles']
        #       )
        #       for member in guild.members:
        #         roles = ""
        #         for role in member.roles:
        #           roles += "({id}-{name})".format(
        #             id=role.id,
        #             name=role.name
        #           )
                
        #         data = data.append(
        #           {
        #             'id': member.id,
        #             'username': member.name,
        #             'roles': roles
        #           },
        #           ignore_index=True
        #         )
              
        #       file_location = f"{str(message.channel.guild.id) + '_' + str(message.channel.id)}.csv"
        #       data.to_csv(
        #                 file_location)  # Saving the file as a .csv via pandas
        #       answer = discord.Embed(
        #         title="Hi admin!, Here is the member list file",
        #         description=f"""It might have taken a while, but here is what you asked for.\n\n`Server` : **{message.guild.name}**\n`Channel` : **{message.channel.name}**""",
        #         color=success_color
        #       )
        #       await message.author.send(embed=answer)
        #       await message.author.send(file=discord.File(
        #                 file_location,
        #                 filename='data.csv'))  # Sending the file
        #       os.remove(file_location)  

          




client.run(discord_token)
