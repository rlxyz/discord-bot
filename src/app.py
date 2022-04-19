from enum import Enum
from bots.claimlist_bot import ClaimlistBot
from bots.allowlist_bot import AllowlistBot
from bots.contract_snapshot_bot import ContractSnapshotBot
import os

class BotEnum(Enum):
  ALLOWLIST = 1
  CLAIMLIST = 2
  CONTRACT_SNAPSHOT = 3
  DISCORD_BACKUP = 4

class App:
  allowlist: str
  address_checker: str
  
  def __init__(self):
    self.allowlist_bot = AllowlistBot(os.environ["DISCORD_CHANNEL_ID"])
    self.claimlist_bot = ClaimlistBot(os.environ["DISCORD_CHANNEL_ID"])
    self.contract_snapshot_bot = ContractSnapshotBot(os.environ["DISCORD_CHANNEL_ID"])

    self.admins = os.environ["DISCORD_ADMIN_LIST"]

  def get_admin(self):
    pass
  
  def get_bot(self, type: BotEnum):
    if type == BotEnum.ALLOWLIST:
      return self.allowlist_bot
    elif type == BotEnum.CLAIMLIST:
      return self.claimlist_bot
    elif type == BotEnum.CONTRACT_SNAPSHOT:
      return self.contract_snapshot_bot
    