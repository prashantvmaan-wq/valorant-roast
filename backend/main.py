from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "VALORANT Roast Backend is running!"
    }

@app.get("/api/player/{riot_id}")
def get_player_stats(riot_id: str):

    player_stats = {
        "riot_id": riot_id,
        "rank": "DIAMOND 2",
        "win_rate": "48%",
        "kd": 0.82,
        "headshot": "12.5%"
    }

    return player_stats

@app.get("/api/weapon/{riot_id}")
def get_weapon_stats(riot_id:str):

    weapon_stats = {
        "headshot": "8.5%",
        "accuracy": "24%",
        "worst_weapon": "JUDGE",
        "body_shots": "78%"
    }
    return weapon_stats