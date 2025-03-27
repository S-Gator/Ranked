import discord
import requests
import asyncio
from bs4 import BeautifulSoup

# Discord bot token (replace with your actual token)
TOKEN = "YOUR_DISCORD_BOT_TOKEN"

# Discord User ID for private messages (Replace with your Discord User ID)
USER_ID = 473881677828063235  # Your Discord User ID

# Tzared Website URL (Update if necessary)
TZARED_URL = "https://tza.red/"

# Threshold for player count
PLAYER_THRESHOLD = 20

# Time interval for checking (in seconds)
CHECK_INTERVAL = 60  # Check every 1 minute

# Discord client setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Function to scrape player count
def get_ranked_room_player_count():
    try:
        response = requests.get(TZARED_URL)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Locate all game listings
            games = soup.find_all('div', class_='pbl')
            for game in games:
                title = game.find('div').text.strip()
                if "RANKED" in title:
                    player_count_element = game.find('div', class_='tbplyrs')
                    if player_count_element:
                        player_count = int(player_count_element.find_all('span')[0].text.strip())
                        return player_count
    except Exception as e:
        print(f"Error fetching player count: {e}")
    return None

# Background task to monitor player count
async def monitor_players():
    await client.wait_until_ready()
    user = await client.fetch_user(USER_ID)
    
    if user is None:
        print("Invalid User ID. Check your configuration.")
        return
    
    # Send an initial message to establish DM communication
    try:
        await user.send("✅ The Tzared Ranked Notifier bot is now active and will notify you when 20+ players are in the ranked room.")
    except discord.errors.Forbidden:
        print("❌ Unable to send DM. Make sure you have allowed DMs from non-friends.")
        return
    
    notified = False  # Prevent spam
    
    while not client.is_closed():
        player_count = get_ranked_room_player_count()
        
        if player_count is not None:
            print(f"Ranked Room Players: {player_count}")
            
            if player_count > PLAYER_THRESHOLD and not notified:
                await user.send(f"⚔️ **Tzared Ranked Alert!** ⚔️\nThere are now **{player_count}** players in the Ranked room! Join now!")
                notified = True  # Prevent multiple messages
            elif player_count <= PLAYER_THRESHOLD:
                notified = False  # Reset notification when count drops
                
        await asyncio.sleep(CHECK_INTERVAL)  # Wait before next check

# Event to start bot
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    client.loop.create_task(monitor_players())

# Run bot
client.run(TOKEN)
