import requests
import pandas as pd
import time
import matplotlib.pyplot as plt

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
# REPLACE THIS WITH YOUR NEW API KEY!
API_KEY = "*************************" 

# THE CONTROL GROUP: 10 Games representing the "Average" Steam Gamer
# We use this to establish a baseline for normal gaming habits.
CONTROL_GAME_IDS = [
    "730",      # Counter-Strike 2 (The Competitive FPS Standard)
    "570",      # Dota 2 (The Hardcore Strategy/MOBA Standard)
    "1086940",  # Baldur's Gate 3 (The Modern RPG Standard)
    "1245620",  # Elden Ring (The "Core" Action Gamer)
    "413150",   # Stardew Valley (The Cozy/Sim Demographic)
    "105600",   # Terraria (The Sandbox/Creative Survivor)
    "1172470",  # Apex Legends (The Fast-Paced Battle Royale)
    "1091500",  # Cyberpunk 2077 (The AAA Graphics Enthusiast)
    "550",      # Left 4 Dead 2 (The "Heritage" PC Gamer)
    "1966720"   # Lethal Company (The Viral/Social Horror Crowd)
]

# Same sample size as your experimental group for fair comparison
TARGET_USER_COUNT = 200 

# ==========================================
# 🛠️ HELPER FUNCTIONS
# ==========================================

def get_reviews(app_id):
    """Fetches recent reviewers for a game."""
    url = f"https://store.steampowered.com/appreviews/{app_id}?json=1"
    params = {'filter': 'recent', 'language': 'english', 'num_per_page': 100}
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if 'reviews' in data:
            return [r['author']['steamid'] for r in data['reviews']]
    except:
        pass
    return []

def get_most_played_game(steam_id):
    """
    Finds the user's #1 played game.
    NOTE: Unlike the Adult script, we DO NOT exclude the seed games here.
    We want to know if their favorite game is indeed CS2, Elden Ring, etc.
    """
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {'key': API_KEY, 'steamid': steam_id, 'format': 'json', 'include_appinfo': True}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'response' in data and 'games' in data['response']:
            games = data['response']['games']
            
            # Filter: Must have played > 2 hours (120 mins)
            played_games = [g for g in games if g['playtime_forever'] > 120]
            
            if not played_games: return None 
            
            # Sort by playtime (descending)
            sorted_games = sorted(played_games, key=lambda x: x['playtime_forever'], reverse=True)
            
            # Just take the #1 game immediately
            top_game = sorted_games[0]
            
            return {
                'appid': top_game['appid'], 
                'game_name': top_game['name'],
                'playtime_hours': round(top_game['playtime_forever'] / 60, 1)
            }
    except:
        return None
    return None

def get_game_genre(appid):
    """
    FINAL GENRE MAPPER v7 (Destiny 2 Fix):
    - Forces Destiny 2, Warframe, Elder Scrolls Online to be 'MMORPG'.
    - Checks 'MMORPG' tags BEFORE 'Shooter' tags for all other games.
    """
    if str(appid) == "1085660": # Destiny 2
        return "MMORPG"
    if str(appid) == "230410":  # Warframe 
        return "MMORPG"
    if str(appid) == "306130":  # Elder Scrolls Online 
        return "MMORPG"
    url = f"https://steamspy.com/api.php?request=appdetails&appid={appid}"
    
    GENRE_MAP = {
        # ============================================
        # 0. UTILITY (Absolute Top Priority)
        # ============================================
        "Utilities": "Utility / Software",
        "Software": "Utility / Software",
        "Design & Illustration": "Utility / Software",
        "Web Publishing": "Utility / Software",
        "Animation & Modeling": "Utility / Software",

        # ============================================
        # 1. STRICT ADULT (Explicit Porn Only)
        # ============================================
        # We use 'Hentai' and 'NSFW' but NOT 'Mature' 
        # to avoid catching GTA V or Witcher 3.
        "Hentai": "Adult / NSFW",
        "NSFW": "Adult / NSFW", 
        "Sexual Content": "Adult / NSFW", # Use with caution, usually implies explicit on Steam

        # ============================================
        # 2. SHOOTERS (Reflexes)
        # ============================================
        "FPS": "Shooter",
        "Shooter": "Shooter",
        "Third-Person Shooter": "Shooter", 
        "Battle Royale": "Shooter",
        "Looter Shooter": "Shooter",
        "Sniper": "Shooter",
        "Arena Shooter": "Shooter",

        # ============================================
        # 3. STRATEGY & MOBA (Tactics)
        # ============================================
        "MOBA": "Strategy & MOBA",
        "Strategy": "Strategy & MOBA",
        "RTS": "Strategy & MOBA",
        "Grand Strategy": "Strategy & MOBA",
        "4X": "Strategy & MOBA",
        "Card Game": "Strategy & MOBA",
        "Deckbuilding": "Strategy & MOBA",
        "Tower Defense": "Strategy & MOBA",
        "Turn-Based Tactics": "Strategy & MOBA",

        # ============================================
        # 4. MMORPG (Lifestyle / Social)
        # ============================================
        "MMORPG": "MMORPG",
        "Massively Multiplayer": "MMORPG", 

        # ============================================
        # 5. ROGUELIKE (Looping)
        # ============================================
        "Roguelike": "Roguelike",
        "Roguelite": "Roguelike",
        "Action Roguelike": "Roguelike",
        "Bullet Hell": "Roguelike",
        "Dungeon Crawler": "Roguelike",

        # ============================================
        # 6. HARDCORE ACTION (Mastery)
        # ============================================
        "Souls-like": "Hardcore Action",
        "Metroidvania": "Hardcore Action",
        "Fighting": "Hardcore Action",
        "Spectacle Fighter": "Hardcore Action",
        "Hack and Slash": "Hardcore Action",

        # ============================================
        # 7. SURVIVAL & HORROR (Tension)
        # ============================================
        "Survival": "Survival / Horror",
        "Open World Survival Craft": "Survival / Horror",
        "Crafting": "Survival / Horror",
        "Horror": "Survival / Horror",
        "Survival Horror": "Survival / Horror",
        "Zombies": "Survival / Horror",

        # ============================================
        # 8. SPORTS & RACING (Competition)
        # ============================================
        "Sports": "Sports & Racing",
        "Racing": "Sports & Racing",
        "Soccer": "Sports & Racing",
        "Football": "Sports & Racing",
        "Basketball": "Sports & Racing",
        "Automobile Sim": "Sports & Racing", 
        "Driving": "Sports & Racing",

        # ============================================
        # 9. RPG (Single Player / Narrative)
        # ============================================
        "RPG": "RPG",
        "JRPG": "RPG",
        "CRPG": "RPG",
        "Action RPG": "RPG",

        # ============================================
        # 10. SIMULATION (Relaxation)
        # ============================================
        "Simulation": "Simulation",
        "Farming Sim": "Simulation",
        "Life Sim": "Simulation",
        "City Builder": "Simulation",
        "Management": "Simulation",
        "Automation": "Simulation",
        "Colony Sim": "Simulation",

        # ============================================
        # 11. CASUAL / ARCADE / ACTION (The Rest)
        # ============================================
        "Crime": "Action / Adventure", 
        "Open World": "Action / Adventure",
        "Platformer": "Casual / Arcade",
        "Puzzle": "Casual / Arcade",
        "Visual Novel": "Casual / Arcade",
        "Rhythm": "Casual / Arcade",
        "Party Game": "Casual / Arcade",
        "Point & Click": "Casual / Arcade"
    }
    
    try:
        time.sleep(1.1) 
        response = requests.get(url)
        data = response.json()
        
        if 'tags' in data and isinstance(data['tags'], dict):
            top_tags = list(data['tags'].keys())
            
            # Check for a match
            for tag in top_tags:
                if tag in GENRE_MAP:
                    return GENRE_MAP[tag]

        # Final Fallback
        return "Action / Adventure"

    except Exception:
        return "Unknown"


# ==========================================
# 🚀 MAIN EXECUTION
# ==========================================

def main():
    print("--- STARTING CONTROL GROUP ANALYSIS ---")
    
    # 1. Collect Users
    unique_users = set()
    print(f"Step 1: Finding users who reviewed 'Average Gamer' titles...")
    for app_id in CONTROL_GAME_IDS:
        users = get_reviews(app_id)
        unique_users.update(users)
        print(f" -> Scraped AppID {app_id}: Found {len(users)} reviewers.")
        time.sleep(1)
    
    print(f"Total Unique Users Found: {len(unique_users)}")
    
    # 2. Analyze Libraries
    print(f"\nStep 2: Scanning libraries for {TARGET_USER_COUNT} users...")
    print(f"--------------------------------------------------")
    results = []
    users_found = 0
    total_scanned = 0
    
    user_list = list(unique_users)
    
    while users_found < TARGET_USER_COUNT and total_scanned < len(user_list):
        steam_id = user_list[total_scanned]
        total_scanned += 1
        
        print(f"[{users_found}/{TARGET_USER_COUNT}] Scanning User {total_scanned}... ", end='', flush=True)
        
        try:
            top_game_data = get_most_played_game(steam_id)
            
            if top_game_data:
                genre = get_game_genre(top_game_data['appid'])
                
                results.append({
                    'user_id': steam_id,
                    'top_game': top_game_data['game_name'],
                    'genre': genre,
                    'hours_played': top_game_data['playtime_hours']
                })
                
                print(f"✅ FOUND: {top_game_data['game_name']} ({genre})")
                users_found += 1
            else:
                print(f"❌ Skipped (Private)")
                
        except Exception as e:
            print(f"⚠️ Error: {e}")
            
        time.sleep(0.2) 
        
    # 3. Save & Visualize
    if results:
        df = pd.DataFrame(results)
        # DIFFERENT FILENAME so you don't overwrite your other data!
        df.to_csv("steam_control_group.csv", index=False)
        print(f"\nControl Data saved to 'steam_control_group.csv'")
        
        # Chart
        plt.figure(figsize=(10, 8))
        genre_counts = df['genre'].value_counts()
        
        if len(genre_counts) > 8:
            main = genre_counts[:8]
            main['Other'] = genre_counts[8:].sum()
            genre_counts = main
            
        genre_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, cmap='Set3') # Different color scheme
        plt.title(f'Genre Preferences of Mainstream Gamers (n={users_found})')
        plt.ylabel('')
        plt.tight_layout()
        plt.savefig("control_group_chart.png")
        print("Chart saved as 'control_group_chart.png'")
    else:
        print("No data found.")

if __name__ == "__main__":
    main()