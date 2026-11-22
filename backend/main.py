
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import os
import requests

from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote


def calculate_match_stats(match, player_name, player_tag):

    # Get all players from the match
    players = match["players"]["all_players"]

    # Find the requested player
    player = next(
        (
            p for p in players
            if p["name"].lower() == player_name.lower()
            and p["tag"].lower() == player_tag.lower()
        ),
        None
    )

    if player is None:
        return {"error": "Player not found in this match"}

    stats = player["stats"]

    # Extract basic statistics
    kills = stats["kills"]
    deaths = stats["deaths"]
    assists = stats["assists"]

    headshots = stats["headshots"]
    bodyshots = stats["bodyshots"]
    legshots = stats["legshots"]

    score = stats["score"]
    rounds = match["metadata"]["rounds_played"]

    # Calculate K/D
    kd = kills / deaths if deaths > 0 else kills

    # Calculate headshot percentage
    total_shots = headshots + bodyshots + legshots

    hs_percentage = (
        (headshots / total_shots) * 100
        if total_shots > 0 else 0
    )

    # Calculate ACS
    acs = score / rounds if rounds > 0 else 0

    # Get match result
    team = player["team"].lower()
    won = match["teams"][team]["has_won"]

    return {
        "player": player["name"],
        "agent": player["character"],
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "kd_ratio": round(kd, 2),
        "headshot_percentage": round(hs_percentage, 2),
        "acs": round(acs, 2),
        "result": "Win" if won else "Loss"
    }


def generate_roast(stats):

    kd = stats["kd_ratio"]
    hs = stats["headshot_percentage"]
    acs = stats["acs"]
    kills = stats["kills"]
    deaths = stats["deaths"]

    # Check player's performance
    if kd >= 2:
        roast = "You're carrying so hard, even your teammates are spectators."

    elif kd >= 1.2:
        roast = "Not bad! You're doing your job. Your teammates should take notes."

    elif kd >= 1:
        roast = "Breaking even? You're playing VALORANT, not running a charity."

    elif kd >= 0.7:
        roast = "The enemy team is getting free confidence boosts from you."

    else:
        roast = "At this point, you're the enemy team's favorite player."

    # Add a headshot-based comment
    if hs >= 50:
        roast += " Those headshots are actually impressive!"

    elif hs < 20:
        roast += " Your crosshair placement needs serious therapy."

    # Add a death-based comment
    if deaths > kills:
        roast += " Also, stop donating kills to the enemy."

    return roast



# --------------------------------
# 1. Load Environment Variables
# --------------------------------

env_path = Path(__file__).with_name(".env")
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("HENRIK_API_KEY", "").strip()


# --------------------------------
# 2. Create FastAPI Application
# --------------------------------

app = FastAPI(title="VALORANT ROAST API")


# --------------------------------
# 3. CORS Configuration
# --------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://valorant-roast-alpha.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------
# 4. HenrikDev API Helper
# --------------------------------

def henrik_request(url: str, params=None):

    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="API key not configured"
        )

    try:
        response = requests.get(
            url,
            headers={"Authorization": API_KEY},
            params=params,
            timeout=20
        )

        try:
            data = response.json()
        except ValueError:
            raise HTTPException(
                status_code=502,
                detail="Invalid response from HenrikDev"
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=data
            )

        return data

    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="HenrikDev API timed out"
        )

    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Unable to connect to HenrikDev API"
        )


# --------------------------------
# 5. Home Endpoint
# --------------------------------

@app.get("/")
def home():
    return {
        "message": "VALORANT ROAST Backend is running!"
    }


# --------------------------------
# 6. Get Player Account
# --------------------------------

@app.get("/player/{name}/{tag}")
def get_player(name: str, tag: str):

    url = (
        "https://api.henrikdev.xyz/valorant/v1/account/"
        f"{quote(name, safe='')}/{quote(tag, safe='')}"
    )

    return henrik_request(url)


# --------------------------------
# 7. Get Player Match History
# --------------------------------

@app.get("/matches/{name}/{tag}")
def get_match_history(name: str, tag: str):

    # Get player's region
    account_url = (
        "https://api.henrikdev.xyz/valorant/v1/account/"
        f"{quote(name, safe='')}/{quote(tag, safe='')}"
    )

    account_data = henrik_request(account_url)

    region = account_data["data"]["region"]

    # Fetch latest competitive match
    matches_url = (
        "https://api.henrikdev.xyz/valorant/v3/matches/"
        f"{region}/{quote(name, safe='')}/{quote(tag, safe='')}"
    )

    params = {
        "mode": "competitive",
        "size": 1
    }

    return henrik_request(matches_url, params=params)


# --------------------------------
# 8. Get Player Match Statistics
# --------------------------------

@app.get("/stats/{name}/{tag}")
def get_player_stats(name: str, tag: str):

    # Step 1: Get player's region
    account_url = (
        "https://api.henrikdev.xyz/valorant/v1/account/"
        f"{quote(name, safe='')}/{quote(tag, safe='')}"
    )

    account_data = henrik_request(account_url)

    region = account_data["data"]["region"]

    # Step 2: Fetch latest competitive match
    matches_url = (
        "https://api.henrikdev.xyz/valorant/v3/matches/"
        f"{region}/{quote(name, safe='')}/{quote(tag, safe='')}"
    )

    params = {
        "mode": "competitive",
        "size": 1
    }

    match_data = henrik_request(matches_url, params=params)

    # Step 3: Check whether match data exists
    matches = match_data.get("data", [])

    if not matches:
        raise HTTPException(
            status_code=404,
            detail="No competitive matches found"
        )

    # Step 4: Calculate player's statistics
    result = calculate_match_stats(
        matches[0],
        name,
        tag
    )

    if "error" in result:
        raise HTTPException(
            status_code=404,
            detail=result["error"]
        )

    return result

# --------------------------------
# 9. Generate Player Roast
# --------------------------------

@app.get("/roast/{name}/{tag}")
def get_player_roast(name: str, tag: str):

    # Get the player's match statistics
    stats = get_player_stats(name, tag)

    # Generate a roast using those statistics
    roast = generate_roast(stats)

    return {
        "player": stats["player"],
        "agent": stats["agent"],
        "stats": stats,
        "roast": roast
    }
