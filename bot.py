import nextcord
from nextcord.ext import commands
import asyncio
import re

intents = nextcord.Intents.all()
intents.message_content = True

bot = commands.Bot(intents=intents)

POKEVENTURE_BOT_ID = "1428761819563950271"
RARESPAWN_CHANNEL_ID = 0  # Enter your channel ID here
processed_message_ids = set()

# HELPER FUNCTIONS
def wild_cooldown(description):
    if "A wild" in description:            
        return 9

def raid_cooldown(description):
    pattern = r"again in (\d+) seconds" 
    match = re.search(pattern, description)
    if match:
        cooldown_seconds_str = match.group(1)
        return int(cooldown_seconds_str)

def reward_cooldown(description):
    if description.startswith("Reward:"):
        return 3600

@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Game("Pokeventure"))
    print("Bot Online")

@bot.event
async def on_raw_message_edit(payload):
    channel = bot.get_channel(payload.channel_id)

    if payload.data.get("author", {}).get("id") != POKEVENTURE_BOT_ID:
        return
    
    message_id = payload.message_id
    if message_id in processed_message_ids:
        return
    
    if "embeds" not in payload.data or not payload.data["embeds"] or "description" not in payload.data["embeds"][0]:
        return

    interaction_data = payload.data.get("interaction")
    if interaction_data:
        
        command_name = interaction_data["name"]
        user_id = interaction_data["user"]["id"]
        description = payload.data["embeds"][0]["description"]

        if command_name == "wild":
            cooldown = wild_cooldown(description)
            if cooldown is not None:
                processed_message_ids.add(message_id)
                await asyncio.sleep(cooldown)
                await channel.send(f"**<@{user_id}>** You can find another wild Pokemon")
                processed_message_ids.discard(message_id)

        elif command_name == "raid":
            cooldown = raid_cooldown(description)
            if cooldown:
                await asyncio.sleep(cooldown)
                await channel.send(f"**<@{user_id}>** You can hit the raid again")

        elif command_name == "megaraid":
            cooldown = raid_cooldown(description)
            if cooldown:
                await asyncio.sleep(cooldown)
                await channel.send(f"**<@{user_id}>** You can hit the megaraid again")

        elif command_name == "reward":
            cooldown = reward_cooldown(description)
            if cooldown:
                await asyncio.sleep(cooldown)
                await channel.send(f"**<@{user_id}>** You can find claim your hourly reward") 

    else:
        description = payload.data["embeds"][0]["description"]
        if "You caught a <:lr:" in description:
            channel = bot.get_channel(RARESPAWN_CHANNEL_ID)
            pattern = r">(.*?)\!"
            match = re.search(pattern, description)
            if match:
                pokemon = match.group(1).strip()
                username = payload.data["interaction_metadata"]["user"]["username"]
                embed = nextcord.Embed(title="Pokeventure Rarespawn", color=nextcord.Colour.blue())
                embed.add_field(name = f"{username} caught a <:lr:1448981944800116812> {pokemon}", value="")
                image_url = payload.data["embeds"][0]["image"]["url"]
                embed.set_image(url=image_url)
                await channel.send(embed=embed)

BOT_TOKEN = ""
bot.run(BOT_TOKEN)
