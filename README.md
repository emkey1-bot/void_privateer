# 🛰️ Void Privateer

```text
 __   __   ___   ___  ___
 \ \ / /  / _ \ |_ _||   \
  \ V /  | | | | | | | |) |
   \_/    \___/ |___||___/

 ___   ___   ___ __   __  _   _____  _____  _____  ___
| _ \ | _ \ |_ _|\ \ / / /_\ |_   _||  ___||  ___|| _ \
|  _/ |   /  | |  \ V / / _ \  | |  |  __| |  __| |   /
|_|   |_|_\ |___|  \_/ /_/ \_\ |_|  |_____||_____||_|_\
               == [ THE RETRO BBS COLD WAR SPACE SANDBOX ] ==
```

Welcome to **Void Privateer**, a turn-based retro space trading and exploration game designed for the terminal. Inspired by the classic dial-up BBS (Bulletin Board System) door games of the 1980s and 90s, *Void Privateer* puts you in command of a starship navigating a cold, procedural, 100-sector network of stars.

Build your fortune through market trading, tactical planetary colonizing, daring smuggling runs, and avoiding (or destroying) hostile pirate ambushes. Achieved through modular, clean Python architecture with 100% test coverage.

---

## 🚀 Key Features

* **Procedural Galaxy Adjacency Graph:** Explores a vast network of 100 sectors with random seed generation, persistent warp-lane links, and distinct planetary features.
* **Dynamic Market & Daily Port Events:** Trade 8 distinct commodities across specialized port economies (Agricultural, Industrial, High-Tech, Military). Economic loops are influenced by daily random sector events such as *Space Plagues*, *Weapons Shortages*, *Industrial Surpluses*, and *Military Blockades*.
* **Central Colony Management Console:** Survey planets and deploy central colonies. Upgrade defenses, manage population growth, and collect daily credits in a unified, spreadsheet-style ledger.
* **Hyperspace Navigation Computer:** Features an in-game BFS shortest-path solver. Automatically sweep routes, analyze sector hazards, and calculate fuel-to-warp requirements.
* **Simulated Autonomous AI Traders:** Three rival AI captains (*Soren's Hauler*, *Void Ranger*, and *Orion Venture*) roam the galaxy, execute cargo transactions, alter port stocks, and leave actionable visual logs in your Galactic Intel status feed.
* **Border Controls & Smuggling:** Profit off high-risk contraband items, but prepare for Navy patrol corvettes executing scan checkpoints. Bribe officers, pay fines, or risk high-speed warp escapes.
* **Tactical Ship Customization & Combat:** Face random pirate ambushes in an interactive, turn-based combat loop. Upgrade your cargo hold, weapons output, shield generators, and engine efficiency at deep-space ports.
* **Robust Save/Load System:** Saves automatically to `savegame.json` after every turn so you never lose your progress.

---

## 🎮 How to Play

### Installation & Prerequisites
You only need a standard Python 3.10+ environment (no external runtime dependencies are required to run the game).

1. Clone or download this repository:
   ```bash
   git clone git@github.com:emkey1-bot/void_privateer.git
   cd void_privateer
   ```
2. Launch the game:
   ```bash
   python3 game.py
   ```

### 🧪 Running the Test Suite
The codebase includes comprehensive unit tests verifying market fluctuations, AI trading state updates, shortest-path calculation, colonial accounting, and movement integrity.

Run the test suite with:
```bash
python3 -m unittest test_game.py
```

---

## 🛸 Game Manual

When you boot into the terminal, you will be met with the main menu dashboard:
```text
=== [ COMMAND CONSOLE ] ===  (Sector 1: Sol)
1. Scan Local Sector
2. Warp to Connected Sector
3. Planetary Colonies & Survey Console
4. Galactic Market Exchange (Buy/Sell)
5. Hyperspace Navigation Computer
6. Port Shipyards (Repairs & Upgrades)
7. Save Game
8. Quit
Your Action? [1-8]:
```

1. **Sector Exploration:** Keep your eyes peeled for Sector Hazards (e.g. Solar Flares, Radiation Storms) which degrade shields and hulls during warp jumps.
2. **Fuel and Day Budgets:** Every warp jump, planet survey, or combat round consumes **Fuel / Energy**. End your day at a friendly port to replenish actions and trigger the galaxy-wide daily simulation.
3. **Colony Ledger:** Accessible via Option 3. You can see your active settlements, defense levels, population count, and collect revenues in one place.

---

## 🎨 Social & Aesthetics
The repository includes a custom, high-resolution vintage CRT visual preview for link sharing (`social_preview.png`).

---

## 📜 License
This software is provided under the MIT License. Developed for retro terminal enthusiasts and space simulation lovers.
