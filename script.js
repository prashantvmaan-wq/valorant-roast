const API_BASE_URL = "https://valorant-roast.onrender.com";
const searchButton = document.getElementById("searchButton");

if (searchButton) {

    searchButton.addEventListener("click", function () {

        const riotId = document.getElementById("riotId").value.trim();
        const tagline = document.getElementById("tagline").value.trim();

        if (riotId === "" || tagline === "") {
            alert("Please enter both Riot ID and Tagline!");
            return;
        }

        sessionStorage.setItem("riotId", riotId);
        sessionStorage.setItem("tagline", tagline);

        window.location.href = "player.html";
    });
}


// ==================================
// 2. DISPLAY PLAYER NAME AND TAGLINE
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
// 3. FETCH PLAYER STATS FROM FASTAPI
// ==================================

async function loadPlayerStats() {

    const rankElement = document.getElementById("rank");

    if (!rankElement) return;

    const riotId = sessionStorage.getItem("riotId");

    if (!riotId) {
        alert("Player information not found!");
        return;
    }

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/player/${encodeURIComponent(riotId)}`
        );

        if (!response.ok) {
            throw new Error("Could not fetch player statistics");
        }

        const data = await response.json();

        document.getElementById("rank").textContent = data.rank;
        document.getElementById("winRate").textContent = data.win_rate;
        document.getElementById("kd").textContent = data.kd;
        document.getElementById("headshot").textContent = data.headshot;

        // Generate player verdict

        const verdictElement = document.querySelector(".verdict p");

        if (data.kd < 0.5) {
            verdictElement.textContent =
                "Even the bots are questioning your aim.";
        }
        else if (data.kd < 1.0) {
            verdictElement.textContent =
                "You are donating kills more than collecting them.";
        }
        else if (data.kd < 1.5) {
            verdictElement.textContent =
                "Not bad. Occasionally, you remember how to aim.";
        }
        else {
            verdictElement.textContent =
                "Your opponents should consider uninstalling.";
        }

    }
    catch (error) {

        console.error("Error:", error);
        alert("Unable to load player statistics. Check your backend.");

    }
}

loadPlayerStats();


// ==================================
// 4. WEAPON ROAST SAMPLE DATA
// ==================================


async function loadWeaponStats() {

    const weaponElement = document.getElementById("weaponHeadshot");

    if (!weaponElement) return;

    const riotId = sessionStorage.getItem("riotId");

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/weapon/${encodeURIComponent(riotId)}`
        );

        if (!response.ok) {
            throw new Error("Could not fetch weapon statistics");
        }

        const data = await response.json();

        // Display weapon statistics
        document.getElementById("weaponHeadshot").textContent = data.headshot;
        document.getElementById("accuracy").textContent = data.accuracy;
        document.getElementById("worstWeapon").textContent = data.worst_weapon;
        document.getElementById("bodyShots").textContent = data.body_shots;

        // Generate weapon roast
        const verdict = document.querySelector(".verdict p");

        const headshot = parseFloat(data.headshot);

        if (headshot < 10) {
            verdict.textContent =
                "Are you aiming for the enemy or the ceiling?";
        }
        else if (headshot < 20) {
            verdict.textContent =
                "Your bullets know the body better than the head.";
        }
        else if (headshot < 35) {
            verdict.textContent =
                "Decent aim. Don't get too confident.";
        }
        else {
            verdict.textContent =
                "Those headshots are making people uninstall.";
        }

    }
    catch (error) {
        console.error("Weapon API Error:", error);
        alert("Unable to load weapon statistics.");
    }
}

loadWeaponStats();
