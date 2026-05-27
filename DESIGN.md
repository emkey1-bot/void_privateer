# Void Privateer - Game Design Document

**Title:** Void Privateer  
**Genre:** Turn-Based Retro Space Trading and Exploration CLI Game  
**Target Platform:** Python CLI / Terminal  
**Vibe:** Retro BBS Dial-up Door Game (ASCII/ANSI graphics, numbered menus, terse readouts, tactical choices)

---

## 1. Overview & Vision
*Void Privateer* is an original space-trading and privateer simulation designed to run directly in the user's terminal. Drawing inspiration from classic 1980s and 90s dial-up BBS (Bulletin Board System) door games, the player takes on the role of a lone pilot in a procedurally generated, connected network of star sectors. Through trading, tactical combat, and ship customization, the player builds an empire from humble beginnings.

This game is strictly original: it does not use copyrighted text, names, sector layouts, or proprietary terms from existing franchises.

---

## 2. Core Systems
1. **Procedural Galaxy Generator:** Generates a consistent 100-sector network of stars using a random seed. Connections (warp lanes) are represented as an adjacency graph.
2. **Economic Market Engine:** Simulates 8 distinct trade goods across different port categories (e.g., Agricultural, Industrial, High-Tech, Military) with varying buy/sell prices, supply/demand, and random daily fluctuations.
3. **Turn/Action Budget:** The player starts each game day/cycle with a set budget of "Fuel / Energy" (e.g., 50 units) representing actions. Moving, scanning, or combat consumes fuel.
4. **Combat Engine (Turn-Based):** An interactive encounter loop where players can fight, evade, surrender, or flee from random pirate encounters. Combat state dynamically checks ship weapons, shields, and integrity.
5. **Ship Customization & Repair:** Ports offer services to repair hull damage and purchase permanent ship upgrades (cargo capacity, shield capacity, weapon power, engine fuel efficiency).
6. **Save/Load System:** State is persisted to a local JSON file (`savegame.json`), allowing seamless pause and resume.

---

## 3. Data Model

### Player / Ship State
```json
{
  "credits": 5000,
  "fuel": 50,
  "max_fuel": 50,
  "hull": 100,
  "max_hull": 100,
  "shields": 50,
  "max_shields": 50,
  "weapon_power": 15,
  "cargo_capacity": 10,
  "cargo": {
    "Food": 0,
    "Ore": 0,
    "Machinery": 0,
    "Medicine": 0,
    "Fuel Cells": 0,
    "Luxury Goods": 0,
    "Weapons": 0,
    "Electronics": 0
  },
  "current_sector": 1,
  "explored_sectors": [1],
  "net_worth_goal": 100000
}
```

### Sector Node
```json
{
  "id": 42,
  "name": "Epsilon Prime",
  "connections": [12, 15, 84],
  "port": {
    "name": "Epsilon Refinery",
    "economy_type": "Industrial",
    "market": {
      "Ore": {"buy": 12, "sell": 15, "stock": 120},
      "Machinery": {"buy": 140, "sell": 160, "stock": 10}
    }
  },
  "planet": null,
  "hazard": "None"
}
```

---

## 4. Development Plan

### Phase 1: Minimum Viable Product (MVP) - *Current Implementation*
* [x] Procedural galaxy graph with 100 sectors and warp lanes.
* [x] Connected sector movement (warp consuming fuel).
* [x] 8 trade goods with randomized price modeling.
* [x] Port generation (at least 20 ports across sectors).
* [x] Command-Line numbered menu UI.
* [x] Standard Cargo Management (Buy/Sell loops).
* [x] Ship stats, repair services, and upgrade shop.
* [x] Random pirate ambushes with turn-based combat.
* [x] JSON-based game saving/loading.
* [x] Win condition based on achieving a net worth of 100,000 credits.

### Phase 2: Polish & Ergonomics (Planned)
* [x] ANSI color coding for retro terminal flavor.
* [x] Short-path routing helper / navigation aid.
* [x] Daily news feed (port events, economic booms, blockade sectors).

### Phase 3: Expansion Features (Planned)
* [x] Deployable planetary colonies.
* [x] Smuggling items (Contraband) with patrol scans.
* [x] simulated rival AI traders moving between sectors.
