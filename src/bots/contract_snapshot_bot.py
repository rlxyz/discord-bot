import discord
from replit import db
import rollbar
from ens import ENS
from web3 import Web3
import os

success_color = 0x0027FF
error_color = 0xFF0000
valid_color = 0x00FF00
infura_api_key = os.environ["INFURA_API_KEY"]

w3 = Web3(
    Web3.HTTPProvider("https://mainnet.infura.io/v3/{infura_api_key}".format(
        infura_api_key=infura_api_key)))

class ContractSnapshotBot:
  def __init__(self, channel_id: str):
    self.ns = ENS.fromWeb3(w3)
    self.channel_id = channel_id
    self.commands = {
      "!dreamlist": self.run_add_to_db
    }

  async def run(self, message):
    author_id = message.author.id
    
    if message.content.startswith("!dreamsnapshot"):
      # await message.reply(embed = self.run_add_to_db(author_id, message))
      return True
    else:
      # other commands go here...
      return False
  
  def run_add_to_db(self, author_id: int, message) -> discord.Embed:
    try:
      if len(message.content.split()) > 1:
        address = message.content.split()[1:][0]
        if address.endswith(".eth"):
          address = self.ns.address(address)
          invocation = 1
          if Web3.isAddress(address):
            db[str(author_id)] = {
              "address": Web3.toChecksumAddress(address),
              "invocation": invocation
            }
            return discord.Embed(
              title="A dreamer has been born ~",
              description=
              """<@{username}> you are now added into the dreamlist\n\nDreamlist address: [{address}](https://etherscan.io/address/{address})\n\nAllocation: {invocation}"""
              .format(username=author_id,
                      address=address,
                      invocation=invocation), color=success_color)
          else:
            rollbar.report_message('Invalid Address',
                                               'warning',
                                               extra_data={
                                                   'user': {
                                                       "id": author_id,
                                                       "address": address,
                                                   }
                                               })
            return discord.Embed(
                            title="Opps, You're not a dreamer ~",
                            description=
                            """Invalid address supplied. Try again.""",
                            color=error_color)
      else:
        rollbar.report_message('Invalid Address',
                                           'warning',
                                           extra_data={
                                               'user': {
                                                   "id": author_id,
                                                   "address": "not supplied",
                                               }
                                           })
        return discord.Embed(
                        title="Opps, You're not a dreamer ~",
                        description="""Address not supplied. Try again.""",
                        color=error_color)
    except:
      rollbar.report_exc_info()