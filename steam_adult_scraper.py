import requests
import pandas as pd
import time
import matplotlib.pyplot as plt

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
# REPLACE THIS WITH YOUR ACTUAL KEY!
API_KEY = "****************" 

# The "Seed" Games: Validated Adult-Only App IDs
ADULT_GAME_IDS = [
    "1034140", # Subverse
    "2458860", # Summer Clover
    "2739590", # Mad Island
    "2289720", # Kaiju Princess 2
    "2654470", # BUNNY GARDEN
    "3029750", # TurretGirls
    "2755480", # The Censor DX Edition
    "2690010", # Handyman Fantasy
    "3478650", # FreshWomen - Season 2
    "3602290"  # FEMBOY FUTA HOUSE
]

# How many users to analyze?
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
    """Finds the user's #1 played game (excluding adult titles)."""
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {'key': API_KEY, 'steamid': steam_id, 'format': 'json', 'include_appinfo': True}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'response' in data and 'games' in data['response']:
            games = data['response']['games']
            
            # Filter 1: Must have played > 2 hours (120 mins)
            played_games = [g for g in games if g['playtime_forever'] > 120]
            
            if not played_games: return None 
            
            # Sort by playtime (descending)
            sorted_games = sorted(played_games, key=lambda x: x['playtime_forever'], reverse=True)
            
            for game in sorted_games:
                # Filter 2: Skip the adult seed games
                if str(game['appid']) not in ADULT_GAME_IDS:
                    return {
                        'appid': game['appid'], 
                        'game_name': game['name'],
                        'playtime_hours': round(game['playtime_forever'] / 60, 1)
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
    print("--- STARTING STEAM AUDIENCE ANALYSIS ---")
    
    # 1. Collect Users
    unique_users = set()
    print(f"Step 1: Finding users who reviewed Top 10 Adult Games...")
    for app_id in ADULT_GAME_IDS:
        users = get_reviews(app_id)
        unique_users.update(users)
        print(f" -> Scraped AppID {app_id}: Found {len(users)} reviewers.")
        time.sleep(1)
    
    print(f"Total Unique Users Found: {len(unique_users)}")
    
    # 2. Analyze Libraries
    print(f"\nStep 2: Scanning libraries for {TARGET_USER_COUNT} users...")
    print(f"--------------------------------------------------")
    results = []
    users_processed = 0
    
    # Iterate through the collected users
    for steam_id in list(unique_users):
        if users_processed >= TARGET_USER_COUNT: 
            break
            
        top_game_data = get_most_played_game(steam_id)
        
        if top_game_data:
            # Get the clean genre
            genre = get_game_genre(top_game_data['appid'])
            
            # Store the data
            results.append({
                'user_id': steam_id,
                'top_game': top_game_data['game_name'],
                'genre': genre,
                'hours_played': top_game_data['playtime_hours']
            })
            
            # ✅ PROGRESS MONITOR (This prints while it runs!)
            print(f"[{users_processed+1}/{TARGET_USER_COUNT}] Found: {top_game_data['game_name']} -> Genre: {genre}")
            users_processed += 1
        
        time.sleep(0.5) # Rate limiting
        
    # 3. Save & Visualize
    if results:
        df = pd.DataFrame(results)
        df.to_csv("steam_adult_group.csv", index=False)
        print(f"\nData saved to 'steam_adult_group.csv'")
        
        # Generate the Pie Chart
        plt.figure(figsize=(10, 8))
        genre_counts = df['genre'].value_counts()
        
        # Group small slices into "Other"
        if len(genre_counts) > 8:
            main_genres = genre_counts[:8]
            other_count = genre_counts[8:].sum()
            # Create a new Series with 'Other' added
            main_genres['Other'] = other_count
            genre_counts = main_genres
            
        genre_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, cmap='Pastel1')
        plt.title(f'Top Mainstream Genres for Adult Game Owners (n={TARGET_USER_COUNT})')
        plt.ylabel('')
        plt.tight_layout()
        plt.savefig("clean_genre_chart.png")
        print("Chart saved as 'adult_group_chart.png'")
    else:
        print("No valid public profiles found.")

if __name__ == "__main__":
    main()
