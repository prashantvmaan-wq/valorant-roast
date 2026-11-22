
const API_BASE_URL = "https://valorant-roast.onrender.com";


// ==================================
// 1. RIOT ID SUBMISSION
// ==================================

const searchButton = document.getElementById("searchButton");

if (searchButton) {

    searchButton.addEventListener("click", function () {

        const riotId = document.getElementById("riotId").value.trim();
        const tagline = document.getElementById("tagline").value.trim();

        if (!riotId || !tagline) {
            alert("Please enter both Riot ID and Tagline!");
            return;
        }

        sessionStorage.setItem("riotId", riotId);
        sessionStorage.setItem("tagline", tagline);

        window.location.href = "player.html";
    });
}


// ==================================
// 2. DISPLAY PLAYER INFORMATION
// ==================================

const displayName = document.getElementById("displayName");

if (displayName) {

    const riotId = sessionStorage.getItem("riotId");
    const tagline = sessionStorage.getItem("tagline");

    displayName.textContent = riotId || "Unknown Player";

    document.getElementById("displayTag").textContent =
        tagline ? "#" + tagline : "";

}


// ==================================
// 3. FETCH REAL PLAYER STATS AND ROAST
// ==================================

async function loadPlayerStats() {

    const roastElement = document.getElementById("roast");

    if (!roastElement) return;

    const riotId = sessionStorage.getItem("riotId");
    const tagline = sessionStorage.getItem("tagline");

    if (!riotId || !tagline) {
        alert("Player information not found!");
        return;
    }

    try {

        roastElement.textContent = "GENERATING YOUR ROAST...";

        const response = await fetch(
            `${API_BASE_URL}/roast/${encodeURIComponent(riotId)}/${encodeURIComponent(tagline)}`
        );

        if (!response.ok) {
            throw new Error("Could not fetch player statistics");
        }

        const data = await response.json();

        const stats = data.stats;

        // Display player information

        document.getElementById("agent").textContent =
            "AGENT: " + data.agent;

        document.getElementById("kills").textContent =
            stats.kills;

        document.getElementById("deaths").textContent =
            stats.deaths;

        document.getElementById("assists").textContent =
            stats.assists;

        document.getElementById("kd").textContent =
            stats.kd_ratio;

        document.getElementById("headshot").textContent =
            stats.headshot_percentage + "%";

        document.getElementById("acs").textContent =
            stats.acs;

        // Display actual backend-generated roast

        roastElement.textContent = data.roast;

    }
    catch (error) {

        console.error("Error:", error);

        roastElement.textContent =
            "Unable to generate roast. Please try again.";

        alert("Unable to load player data. Check your backend.");

    }
}

loadPlayerStats();
