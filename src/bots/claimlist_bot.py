import discord
from replit import db
import rollbar

success_color = 0x0027FF
error_color = 0xFF0000
valid_color = 0x00FF00

class ClaimlistBot:
  def __init__(self, channel_id: str):
    self.channel_id = channel_id
    self.commands = {
      "!dreamclaim": self.run_check_db
    }

  async def run(self, message):
    author_id = message.author.id
    
    if message.content.startswith("!dreamclaim"):
      await message.reply(embed = self.run_check_db(author_id))
      return True
    else:
      # other commands go here...
      return False

  def run_check_db(self, author_id: int) -> discord.Embed:
    try:
      user_in_kv = db[str(author_id)]
      if user_in_kv and user_in_kv["claims_invocation"]:
        return discord.Embed(
                        title="Hoorah! Here's your claim details. ~",
                        description=
                        """<@{username}> you are on the claim list \n\nClaim address: [{address}](https://etherscan.io/address/{address})\n\Total Claims: {claims}, Claim Date: 21/04/22"""
                        .format(username=author_id,
                                address=user_in_kv["address"],
                                claims=user_in_kv["claims_invocation"]),
                        color=valid_color)
    except:
          # do_something
          rollbar.report_exc_info()
          return discord.Embed(title="Sorry, this address is not part of the claim list ~",
                                        description="""Reach out to team if there is an issue""",
                                        color=error_color)
    