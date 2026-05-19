import nextcord
from nextcord.ext import commands
import asyncio
import re

intents = nextcord.Intents.all()
intents.message_content = True

bot = commands.Bot(intents=intents)

POKEVENTURE_BOT_ID = "1428761819563950271"
RARESPAWN_CHANNEL_ID = 948098661794062366  # Enter your channel ID here

#Replace the values with your own bot emojis, or just put text if you dont want emojis
rarity_dict = {
    "n_": "<:n_:1505074943652659231>",
    "u_": "<:u_:1505074997184565348>",
    "r_": "<:r_:1505074992709107813>",
    "sr": "<:sr:1505074995095801947>",
    "ur": "<:ur:1505074999386701856>",
    "lr": "<:lr:1448981944800116812>"
}

@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Game("Pokeventure"))
    print("Bot Online")

@bot.event
async def on_raw_message_edit(payload):
    channel = bot.get_channel(payload.channel_id)
    if payload.data.get("author", {}).get("id") != POKEVENTURE_BOT_ID:
        return
    
    if "embeds" not in payload.data or not payload.data["embeds"] or "description" not in payload.data["embeds"][0]:
        return
    
    description = payload.data["embeds"][0]["description"]
    
    interaction_metadata = payload.data.get("interaction_metadata", {})
    if not interaction_metadata:
        return
        
    command_name = interaction_metadata.get("name")
    user_id = interaction_metadata.get("user", {}).get("id")

    if command_name == "wild":
        image_data = payload.data["embeds"][0].get("image", {})
        if "A wild" in description and image_data.get("height") == 0:
            await asyncio.sleep(9)
            await channel.send(f"**<@{user_id}>** You can find another wild Pokemon")
    
    elif command_name == "raid":
        pattern = r"again in (\d+) seconds" 
        match = re.search(pattern, description)
        if match:
            await asyncio.sleep(int(match.group(1)))
            await channel.send(f"**<@{user_id}>** You can hit the raid again")

    elif command_name == "megaraid":
        pattern = r"again in (\d+) seconds" 
        match = re.search(pattern, description)
        if match:
            await asyncio.sleep(int(match.group(1)))
            await channel.send(f"**<@{user_id}>** You can hit the megaraid again")

    elif command_name == "clan raid":
        if "You dealt" in description:
            await asyncio.sleep(9)
            await channel.send(f"**<@{user_id}>** You can hit the clan raid again")
    
    elif command_name == "reward":
        if description.startswith("Reward:"):
            await asyncio.sleep(3600)
            await channel.send(f"**<@{user_id}>** You can claim your hourly reward")
    
    if "You caught a <:lr:" in description or "✨" in description:
        channel = bot.get_channel(RARESPAWN_CHANNEL_ID)
        image_data = payload.data["embeds"][0].get("image", {})
        if image_data.get("height") == 0:
            return
        if not channel:
            return
        rarity_match = re.search(r"<:(n_|u_|r_|sr|ur|lr):", description)
        rarity = rarity_match.group(1) if rarity_match else ""
        rarity_emoji = rarity_dict.get(rarity, "Unknown")

        pokemon_match = re.search(r">(.*?)\!", description)
        pokemon = pokemon_match.group(1).strip() if pokemon_match else "Pokémon"

        username = payload.data.get("interaction_metadata", {}).get("user", {}).get("username")
        rare_spawn_embed = nextcord.Embed(title="Pokeventure Rarespawn", color=nextcord.Colour.blue())
        rare_spawn_embed.add_field(name = f"{username} caught a {rarity_emoji} {pokemon}", value="")
        image_url = image_data.get("url")
        if image_url:
            rare_spawn_embed.set_image(url=image_url)
        await channel.send(embed=rare_spawn_embed)

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
bot.run(BOT_TOKEN)
