import os
from collections import namedtuple
from typing import List
import discord
import logging
import rollbar
import random
import string
from pony import orm

# Roles:
# 1. Lucky Tiger - 937283070132912149 - 2 unique codes
# 2. Javan - 937267412234043432 - 4 unique codes
# 3. Caspian - 937267656124411914 - 6 unique codes
# 4. Saber Tooth - 937267300959141918 - 8 unique codes
#
# Command: `/tigercheers`

db_host = os.environ["DB_HOST"]
db_port = os.environ["DB_PORT"]
db_user = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
db_name = os.environ["DB_NAME"]

db = orm.Database()
db.bind(provider='postgres', user=db_user, password=db_password, host=db_host, port=db_port, database=db_name)


class TigerCheersReceiver(db.Entity):
    _table_ = "tiger_cheers_receivers"
    id = orm.PrimaryKey(int, auto=True, column="id")
    author_id = orm.Required(str, column="author_id")
    unique_code = orm.Required(str, column="unique_code")
    role = orm.Required(str, column="role")


db.generate_mapping(create_tables=False)


def get_author_records(author_id: str):
    results = TigerCheersReceiver.select(lambda c: c.author_id == author_id)
    return results

def get_total_generated_codes():
    return TigerCheersReceiver.select().count()


def save_author_unique_codes(author_id: str, codes: List[str], role: str):
    for code in codes:
        TigerCheersReceiver(author_id=author_id, unique_code=code, role=role)
    orm.flush()

RolesCodeAllocation = namedtuple('RolesCodeAllocation', ['role_id', 'role_name', 'allocation' ])
role_lucky = os.environ["TIGER_LUCKY_ROLE_ID"]    # 937283070132912149
role_javan = os.environ["TIGER_JAVAN_ROLE_ID"]    # 937267412234043432
role_caspian = os.environ["TIGER_CASPIAN_ROLE_ID"]    # 937267656124411914
role_sabertooth = os.environ["TIGER_SABERTOOTH_ROLE_ID"]    # 937267300959141918
tiger_allocation = [
    RolesCodeAllocation(role_sabertooth, 'sabertooth', 8),
    RolesCodeAllocation(role_caspian, 'caspian', 6),
    RolesCodeAllocation(role_javan, 'javan', 4),
    RolesCodeAllocation(role_lucky, 'lucky', 2)
]

discord_token = os.environ["DISCORD_TOKEN"]
discord_channel = os.environ["DISCORD_CHANNEL_ID"]
rollbar_secret_key = os.environ["ROLLBAR_SECRET_KEY"]
rollbar_environment = os.environ["ROLLBAR_ENVIRONMENT"]
environment = os.environ.get("ENVIRONMENT", "development")

logging.basicConfig(level=logging.INFO)

rollbar.init(rollbar_secret_key, rollbar_environment)

client = discord.Client()
guild = discord.Guild

success_color = 0x0027FF
error_color = 0xFF0000
valid_color = 0x00FF00
allowlist_command = "/tigercheers"
discord_watching_text = "the Lucky Tigers"
max_allocation = 1000


@client.event
async def on_ready():
    logging.info(f'We have logged in {client.user}')
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=discord_watching_text))


@client.event
async def on_message(message):
    author_id = str(message.author.id)

    # ensure bots message doesn't get picked up
    if message.author == client.user:
        return

    if str(message.channel.id) == discord_channel:
        logging.info("Entering the discord channel")
        if message.content.startswith(allowlist_command):
            try:
                with orm.db_session:
                    total_generated_codes = get_total_generated_codes()
                    author_data = get_author_records(author_id)

                    logging.info(f"Total generated codes: {total_generated_codes}")
                    if total_generated_codes == max_allocation:
                        await handle_code_sold_out(message)
                        return


                    # user has claimed the unique codes
                    if author_data.count() > 0:
                        await handle_has_claimed_codes(message)
                        return

                    success = await handle_unique_codes_distribution(message, total_generated_codes)

                    if not success:
                        logging.info(f"User {author_id} not in the roles that's eligible to claim")
                        await handle_not_eligible_user(message)
                        rollbar.report_message('User not eligible to claim the code',
                                               'warning',
                                               extra_data={'user': {
                                                   "id": author_id,
                                               }})
            except Exception as e:
                logging.error(f'Error: {e}')
                if hasattr(e, 'code') and e.code == 50007:
                    await handle_user_disabled_pm(message)
                else:
                    rollbar.report_exc_info()


async def handle_unique_codes_distribution(message, total_generated_codes: int):
    author_id = str(message.author.id)
    role_ids = [str(role.id) for role in message.author.roles]
    logging.info(f'User Roles: {message.author.roles}')

    for tiger_role in tiger_allocation:
        if tiger_role.role_id in role_ids:
            if (max_allocation - total_generated_codes > tiger_role.allocation):
                allocation = tiger_role.allocation
            else:
                allocation = tiger_role.allocation - (max_allocation - total_generated_codes)

            logging.info(f'Generates {allocation} unique codes for user: {author_id}')
            codes = [random_code() for _ in range(allocation)]
            await send_unique_codes(codes, message)
            save_author_unique_codes(author_id=str(author_id), codes=codes, role=tiger_role.role_name)

            return True

    return False


async def send_unique_codes(codes, message):
    answer = discord.Embed(
        title="Hi! Here is your Tiger Cheers codes",
        description=
        f"""It might have taken a while, but here is what you asked for.\n\n`Codes` : **{', '.join(codes)}**\n`Channel` : **{message.channel.name}**""",
        colour=success_color)
    await message.author.send(embed=answer)
    await message.reply(embed=discord.Embed(title="Congrats, you have claim your Tiger Cheers Codes!",
                                            description=f"""Please Check your DM to retrieve your Tiger unique codes""",
                                            colour=success_color))

async def handle_code_sold_out(message):
    answer = discord.Embed(title="The Tiger Cheers code has been exhausted",
                           description=f"""Hi, apology, but we have run out of the unique codes""",
                           colour=success_color)
    await message.author.send(embed=answer)


async def handle_user_disabled_pm(message):
    answer = discord.Embed(title="Private Message is disabled",
                           description=f"""Hi, please enable your PM to receive the Tiger Cheers Codes!""",
                           colour=error_color)
    await message.reply(embed=answer)


async def handle_has_claimed_codes(message):
    logging.info(f"User {author_id} has claimed the unique codes")
    answer = discord.Embed(title="You have claimed the Tiger Cheers Code",
                           description=f"""Hi, apology, but you have previously claimed the Tiger Cheers Code""",
                           colour=success_color)
    await message.author.send(embed=answer)
    rollbar.report_message('User has claimed the code', 'warning', extra_data={'user': {
        "id": message.author.id,
    }})


async def handle_not_eligible_user(message):
    answer = discord.Embed(
        title="You're not eligible to claim the Tiger Cheers Code",
        description=f"""Hi, apology, but currently you're not eligible to claim the Tiger Cheers Code""",
        colour=success_color)
    await message.author.send(embed=answer)


def random_code(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


client.run(discord_token)
