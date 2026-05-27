#!/usr/bin/env python3
import os
import sys
import json
import random
import time

# --- CONSTANTS ---
SAVE_FILE = "savegame.json"
TOTAL_SECTORS = 100
WIN_NET_WORTH = 100000

GOODS = [
    "Food",
    "Ore",
    "Machinery",
    "Medicine",
    "Fuel Cells",
    "Luxury Goods",
    "Weapons",
    "Electronics"
]

PORT_TYPES = ["Agricultural", "Mining", "Industrial", "High-Tech", "Military"]

# Base pricing guidelines for goods by economy type
# (Produces cheap, Demands high)
MARKET_PROFILES = {
    "Agricultural": {
        "Food": {"base_price": 10, "volatility": 2, "stock_range": (30, 80)},
        "Medicine": {"base_price": 25, "volatility": 5, "stock_range": (15, 40)},
        "Machinery": {"base_price": 180, "volatility": 30, "stock_range": (2, 8)},
        "Electronics": {"base_price": 280, "volatility": 40, "stock_range": (1, 5)},
        "Ore": {"base_price": 35, "volatility": 5, "stock_range": (10, 30)},
        "Fuel Cells": {"base_price": 45, "volatility": 8, "stock_range": (5, 15)},
        "Luxury Goods": {"base_price": 150, "volatility": 25, "stock_range": (2, 10)},
        "Weapons": {"base_price": 200, "volatility": 30, "stock_range": (1, 6)}
    },
    "Mining": {
        "Ore": {"base_price": 12, "volatility": 2, "stock_range": (50, 100)},
        "Food": {"base_price": 28, "volatility": 6, "stock_range": (10, 35)},
        "Machinery": {"base_price": 150, "volatility": 20, "stock_range": (3, 10)},
        "Medicine": {"base_price": 50, "volatility": 8, "stock_range": (5, 15)},
        "Fuel Cells": {"base_price": 50, "volatility": 10, "stock_range": (10, 25)},
        "Luxury Goods": {"base_price": 130, "volatility": 20, "stock_range": (2, 8)},
        "Weapons": {"base_price": 220, "volatility": 30, "stock_range": (1, 5)},
        "Electronics": {"base_price": 250, "volatility": 35, "stock_range": (2, 6)}
    },
    "Industrial": {
        "Machinery": {"base_price": 80, "volatility": 10, "stock_range": (15, 30)},
        "Fuel Cells": {"base_price": 25, "volatility": 4, "stock_range": (30, 70)},
        "Ore": {"base_price": 50, "volatility": 8, "stock_range": (5, 15)},
        "Electronics": {"base_price": 220, "volatility": 30, "stock_range": (3, 12)},
        "Food": {"base_price": 25, "volatility": 5, "stock_range": (10, 25)},
        "Medicine": {"base_price": 45, "volatility": 8, "stock_range": (5, 15)},
        "Luxury Goods": {"base_price": 140, "volatility": 20, "stock_range": (2, 8)},
        "Weapons": {"base_price": 190, "volatility": 25, "stock_range": (2, 6)}
    },
    "High-Tech": {
        "Electronics": {"base_price": 120, "volatility": 15, "stock_range": (20, 45)},
        "Luxury Goods": {"base_price": 80, "volatility": 10, "stock_range": (15, 30)},
        "Food": {"base_price": 35, "volatility": 8, "stock_range": (5, 20)},
        "Medicine": {"base_price": 30, "volatility": 5, "stock_range": (10, 30)},
        "Fuel Cells": {"base_price": 60, "volatility": 12, "stock_range": (10, 20)},
        "Ore": {"base_price": 40, "volatility": 6, "stock_range": (5, 15)},
        "Machinery": {"base_price": 130, "volatility": 18, "stock_range": (3, 10)},
        "Weapons": {"base_price": 240, "volatility": 35, "stock_range": (1, 5)}
    },
    "Military": {
        "Weapons": {"base_price": 100, "volatility": 15, "stock_range": (15, 35)},
        "Fuel Cells": {"base_price": 55, "volatility": 10, "stock_range": (15, 30)},
        "Electronics": {"base_price": 240, "volatility": 30, "stock_range": (3, 10)},
        "Food": {"base_price": 30, "volatility": 6, "stock_range": (10, 25)},
        "Medicine": {"base_price": 40, "volatility": 8, "stock_range": (10, 25)},
        "Ore": {"base_price": 45, "volatility": 8, "stock_range": (5, 20)},
        "Machinery": {"base_price": 140, "volatility": 20, "stock_range": (2, 8)},
        "Luxury Goods": {"base_price": 160, "volatility": 25, "stock_range": (2, 8)}
    }
}

# --- RETRO ANSI COLORS ---
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_CYAN = "\033[36m"
COLOR_YELLOW = "\033[33m"
COLOR_RED = "\033[31m"
COLOR_MAGENTA = "\033[35m"
COLOR_WHITE = "\033[37m"
COLOR_BLUE = "\033[34m"
COLOR_BOLD = "\033[1m"


# --- GALAXY GENERATION ---
def generate_galaxy(seed_val=None):
    if seed_val is not None:
        random.seed(seed_val)
    
    galaxy = {}
    
    # 1. Create a baseline connected ring structure to guarantee connectedness
    for i in range(1, TOTAL_SECTORS + 1):
        galaxy[i] = {
            "id": i,
            "name": f"Sector {i}",
            "connections": [],
            "port": None,
            "planet": None,
            "hazard": "None"
        }
    
    for i in range(1, TOTAL_SECTORS + 1):
        next_id = i + 1 if i < TOTAL_SECTORS else 1
        galaxy[i]["connections"].append(next_id)
        galaxy[next_id]["connections"].append(i)
        
    # 2. Add organic extra connections (warp lanes)
    for i in range(1, TOTAL_SECTORS + 1):
        num_lanes = random.randint(1, 3)
        attempts = 0
        while len(galaxy[i]["connections"]) < num_lanes + 1 and attempts < 10:
            target = random.randint(1, TOTAL_SECTORS)
            if target != i and target not in galaxy[i]["connections"]:
                # Ensure no nodes exceed 6 connections
                if len(galaxy[target]["connections"]) < 6:
                    galaxy[i]["connections"].append(target)
                    galaxy[target]["connections"].append(i)
            attempts += 1
            
    # 3. Populate Ports (about 35% of sectors)
    port_names_pool = [
        "Aegis Station", "Sovereign Deep", "Helios Depot", "Nexus-9",
        "Apex Refinery", "Kestrel Foundry", "New Hope Biosphere", "Zenith Core",
        "Outpost Omega", "Triton Shipyard", "Gideon Colony", "Perseus Bazaar",
        "Vanguard Armory", "Equinox Vault", "Chronos Port", "Elysium Hub",
        "Astra Hub", "Ragnar Outpost", "Hydra Haven", "Serenity Docks",
        "Terminus Station", "Titan Foundry", "Obsidian Core", "Nova Citadel",
        "Phoenix Anchorage", "Cygnus Gateway", "Vector Depot", "Borealis Hub",
        "Horizon Silo", "Gorgon Outpost", "Tectonic Mines", "Vortex Array",
        "Exodus Terminal", "Aurora Market", "Siren Depths"
    ]
    random.shuffle(port_names_pool)
    
    sectors_for_ports = random.sample(range(1, TOTAL_SECTORS + 1), min(len(port_names_pool), 35))
    for idx, sec_id in enumerate(sectors_for_ports):
        p_type = random.choice(PORT_TYPES)
        p_name = port_names_pool[idx]
        
        # Build market prices based on profile
        market = {}
        for good in GOODS:
            profile = MARKET_PROFILES[p_type][good]
            base = profile["base_price"]
            vol = profile["volatility"]
            stock = random.randint(*profile["stock_range"])
            
            # Random initial price variation
            price = max(1, base + random.randint(-vol, vol))
            market[good] = {
                "buy_price": price,
                "sell_price": max(1, int(price * 0.85)), # Sell price is 85% of buy price
                "stock": stock
            }
            
        galaxy[sec_id]["port"] = {
            "name": p_name,
            "type": p_type,
            "market": market
        }
        
    # 4. Populate Planets (about 20% of sectors)
    planet_names = [
        "Gaea", "Ceti Alpha IV", "Arrakis Minor", "Zion", "Tatooine Delta",
        "Centauri III", "Xerxes", "Nirvana", "Styx", "Tantalus",
        "Hyperion", "Midgard", "Valhalla", "Olympus", "Erebus",
        "Avalon", "Asgard", "Krypton Prime", "Pristine", "Shatter"
    ]
    sectors_for_planets = random.sample([s for s in range(1, TOTAL_SECTORS + 1) if s not in sectors_for_ports], len(planet_names))
    for idx, sec_id in enumerate(sectors_for_planets):
        galaxy[sec_id]["planet"] = {
            "name": planet_names[idx],
            "claimed": False,
            "defense": 0,
            "colonists": 0,
            "income": 0
        }
        
    # 5. Add hazards (about 10% of sectors)
    sectors_for_hazards = random.sample([s for s in range(1, TOTAL_SECTORS + 1) if s not in sectors_for_ports and s not in sectors_for_planets], 10)
    hazards = ["Asteroid Belt", "Nebula Anomaly", "Radiation Flux", "Minefield"]
    for sec_id in sectors_for_hazards:
        galaxy[sec_id]["hazard"] = random.choice(hazards)
        
    return galaxy


# --- GAME STATE ---
class Game:
    def __init__(self, seed_val=None):
        self.seed = seed_val if seed_val is not None else random.randint(1000, 9999)
        self.galaxy = generate_galaxy(self.seed)
        
        # Player stats
        self.credits = 1000
        self.fuel = 40
        self.max_fuel = 40
        self.hull = 100
        self.max_hull = 100
        self.shields = 50
        self.max_shields = 50
        self.weapon_power = 15
        self.cargo_capacity = 10
        
        self.cargo = {good: 0 for good in GOODS + ["Space Spice"]}
        self.current_sector = 1
        self.explored_sectors = {1}
        self.days_elapsed = 1
        
        # Keep track of purchased upgrades for net worth calculation
        self.upgrades_value = 0
        
        # Daily Economic Events / news
        self.active_event = None
        self.active_event_text = ""
        self.active_event_sector = None
        self.generate_daily_event()
        
        # Rival AI Traders
        self.ai_traders = {
            "Soren's Hauler": {"current_sector": random.randint(1, TOTAL_SECTORS), "credits": 5000},
            "Void Ranger": {"current_sector": random.randint(1, TOTAL_SECTORS), "credits": 4000},
            "Orion Venture": {"current_sector": random.randint(1, TOTAL_SECTORS), "credits": 6000}
        }
        self.ai_sightings = []
        self.update_ai_traders()
        
    def update_ai_traders(self):
        self.ai_sightings = []
        for name, data in self.ai_traders.items():
            curr = data["current_sector"]
            # Warp to random adjacent connection
            conn = self.galaxy[curr]["connections"]
            nxt = random.choice(conn)
            data["current_sector"] = nxt
            
            # Interact with local Port if one exists
            sec = self.galaxy[nxt]
            if sec["port"]:
                port = sec["port"]
                # AI random trade action
                acted_good = random.choice(GOODS)
                m_data = port["market"][acted_good]
                
                if random.random() < 0.50:
                    # AI Buys
                    if m_data["stock"] > 0:
                        qty = random.randint(1, min(5, m_data["stock"]))
                        port["market"][acted_good]["stock"] -= qty
                        self.ai_sightings.append(f"{name} warped to Sector {nxt} and purchased {qty} {acted_good} from {port['name']}.")
                else:
                    # AI Sells
                    qty = random.randint(1, 5)
                    port["market"][acted_good]["stock"] += qty
                    self.ai_sightings.append(f"{name} warped to Sector {nxt} and sold {qty} {acted_good} to {port['name']}.")
            else:
                self.ai_sightings.append(f"{name} was spotted scanning empty space in Sector {nxt}.")
        
    def generate_daily_event(self):
        self.active_event = None
        self.active_event_text = ""
        self.active_event_sector = None
        
        if random.random() < 0.20:
            return
            
        event_type = random.choice(["Plague", "IndustrialBoom", "WeaponsShortage", "Blockade"])
        port_sectors = [s_id for s_id, s in self.galaxy.items() if s["port"] is not None]
        if not port_sectors:
            return
            
        if event_type == "Plague":
            sec_id = random.choice(port_sectors)
            self.active_event = "Plague"
            self.active_event_sector = sec_id
            self.active_event_text = f"😷 SPACE PLAGUE OUTBREAK in Sector {sec_id}! Medicine prices are shooting through the roof (3.5x normal sell price)!"
        elif event_type == "IndustrialBoom":
            ind_sectors = [s_id for s_id in port_sectors if self.galaxy[s_id]["port"]["type"] == "Industrial"]
            if ind_sectors:
                sec_id = random.choice(ind_sectors)
                self.active_event = "IndustrialBoom"
                self.active_event_sector = sec_id
                self.active_event_text = f"🏭 INDUSTRIAL SURPLUS in Sector {sec_id}! Machinery can be purchased at a massive 50% discount!"
        elif event_type == "WeaponsShortage":
            mil_sectors = [s_id for s_id in port_sectors if self.galaxy[s_id]["port"]["type"] == "Military"]
            if mil_sectors:
                sec_id = random.choice(mil_sectors)
                self.active_event = "WeaponsShortage"
                self.active_event_sector = sec_id
                self.active_event_text = f"⚔️ WEAPONS SHORTAGE in Sector {sec_id}! Military command is offering 2.5x normal sell price for plasma weaponry!"
        elif event_type == "Blockade":
            sec_id = random.choice(port_sectors)
            self.active_event = "Blockade"
            self.active_event_sector = sec_id
            self.active_event_text = f"🛑 MILITARY BLOCKADE in Sector {sec_id}! Shug system navy has blockaded the sector port. Prices are doubled (2x), but entering triggers a guaranteed sensor scan or pirate ambush!"

    def get_net_worth(self):
        # Net worth = credits + value of cargo at typical base prices + spent upgrades
        cargo_value = 0
        for good, qty in self.cargo.items():
            base_val = 50 if good != "Space Spice" else 500
            cargo_value += qty * base_val # flat average base value for simplicity
        return self.credits + cargo_value + self.upgrades_value

    def save(self):
        state = {
            "seed": self.seed,
            "credits": self.credits,
            "fuel": self.fuel,
            "max_fuel": self.max_fuel,
            "hull": self.hull,
            "max_hull": self.max_hull,
            "shields": self.shields,
            "max_shields": self.max_shields,
            "weapon_power": self.weapon_power,
            "cargo_capacity": self.cargo_capacity,
            "cargo": self.cargo,
            "current_sector": self.current_sector,
            "explored_sectors": list(self.explored_sectors),
            "days_elapsed": self.days_elapsed,
            "upgrades_value": self.upgrades_value,
            "active_event": self.active_event,
            "active_event_text": self.active_event_text,
            "active_event_sector": self.active_event_sector,
            "ai_traders": self.ai_traders,
            "ai_sightings": self.ai_sightings
        }
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(state, f, indent=2)
            return True
        except Exception:
            return False

    def load(self):
        if not os.path.exists(SAVE_FILE):
            return False
        try:
            with open(SAVE_FILE, "r") as f:
                state = json.load(f)
            
            self.seed = state["seed"]
            self.galaxy = generate_galaxy(self.seed) # Regenerate galaxy layout with saved seed
            
            self.credits = state["credits"]
            self.fuel = state["fuel"]
            self.max_fuel = state["max_fuel"]
            self.hull = state["hull"]
            self.max_hull = state["max_hull"]
            self.shields = state["shields"]
            self.max_shields = state["max_shields"]
            self.weapon_power = state["weapon_power"]
            self.cargo_capacity = state["cargo_capacity"]
            self.cargo = state["cargo"]
            if "Space Spice" not in self.cargo:
                self.cargo["Space Spice"] = 0
            self.current_sector = state["current_sector"]
            self.explored_sectors = set(state["explored_sectors"])
            self.days_elapsed = state["days_elapsed"]
            self.upgrades_value = state.get("upgrades_value", 0)
            self.active_event = state.get("active_event", None)
            self.active_event_text = state.get("active_event_text", "")
            self.active_event_sector = state.get("active_event_sector", None)
            self.ai_traders = state.get("ai_traders", {
                "Soren's Hauler": {"current_sector": random.randint(1, TOTAL_SECTORS), "credits": 5000},
                "Void Ranger": {"current_sector": random.randint(1, TOTAL_SECTORS), "credits": 4000},
                "Orion Venture": {"current_sector": random.randint(1, TOTAL_SECTORS), "credits": 6000}
            })
            self.ai_sightings = state.get("ai_sightings", [])
            return True
        except Exception:
            return False


# --- UTILITIES ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print(fr"""{COLOR_CYAN}{COLOR_BOLD}
 __   __   ___   ___  ___
 \ \ / /  / _ \ |_ _||   \
  \ V /  | | | | | | | |) |
   \_/    \___/ |___||___/

 ___   ___   ___ __   __  _   _____  _____  _____  ___
| _ \ | _ \ |_ _|\ \ / / /_\ |_   _||  ___||  ___|| _ \
|  _/ |   /  | |  \ V / / _ \  | |  |  __| |  __| |   /
|_|   |_|_\ |___|  \_/ /_/ \_\ |_|  |_____||_____||_|_\

{COLOR_RESET}               == [ THE RETRO BBS COLD WAR SPACE SANDBOX ] ==
    """)

def press_enter():
    input(f"\n{COLOR_YELLOW}[Press ENTER to continue...]{COLOR_RESET}")


# --- GAME ACTIONS ---
def show_status(game):
    sec = game.galaxy[game.current_sector]
    if game.active_event_text:
        print(f"\n{COLOR_YELLOW}{COLOR_BOLD}📰 GALACTIC NEWS FLASH:{COLOR_RESET} {COLOR_MAGENTA}{game.active_event_text}{COLOR_RESET}")
    print(f"\n{COLOR_CYAN}======== SYSTEM REPORT (Day {game.days_elapsed}) ========{COLOR_RESET}")
    print(f"Current Sector: {COLOR_WHITE}{sec['name']}{COLOR_RESET} | Connections: {COLOR_WHITE}{', '.join(map(str, sorted(sec['connections'])))}{COLOR_RESET}")
    print(f"Credits: {COLOR_GREEN}{game.credits:,} CR{COLOR_RESET} | Net Worth: {COLOR_GREEN}{game.get_net_worth():,} CR{COLOR_RESET} (Goal: {WIN_NET_WORTH:,} CR)")
    print(f"Fuel/Range: {COLOR_YELLOW}{game.fuel}/{game.max_fuel} LY{COLOR_RESET}")
    print(f"Integrity: Hull {COLOR_GREEN if game.hull > 40 else COLOR_RED}{game.hull}%{COLOR_RESET} / Shields {COLOR_BLUE if game.shields > 15 else COLOR_RED}{game.shields}%{COLOR_RESET} | Weapons: {COLOR_RED}{game.weapon_power} MW{COLOR_RESET}")
    
    cargo_used = sum(game.cargo.values())
    print(f"Cargo Bay: {COLOR_MAGENTA}{cargo_used}/{game.cargo_capacity} m³{COLOR_RESET}")
    for item, qty in game.cargo.items():
        if qty > 0:
            print(f"  - {item}: {qty} unit(s)")
            
    if sec["port"]:
        print(f"Sector Port: {COLOR_GREEN}{sec['port']['name']} ({sec['port']['type']} Economy){COLOR_RESET}")
    if sec["planet"]:
        claimed_str = "Claimed by you" if sec["planet"]["claimed"] else "Unexplored / Wild"
        print(f"Sector Planet: {COLOR_CYAN}{sec['planet']['name']} ({claimed_str}){COLOR_RESET}")
    if sec["hazard"] != "None":
        print(f"{COLOR_RED}⚠️ WARNING: Local {sec['hazard']} present in this sector!{COLOR_RESET}")
    print(f"{COLOR_CYAN}=========================================={COLOR_RESET}")
    
    if game.ai_sightings:
        print(f"\n{COLOR_CYAN}📡 GALACTIC INTEL & RIVAL ACTIVITY:{COLOR_RESET}")
        for sighting in game.ai_sightings[:3]:
            print(f"  - {COLOR_WHITE}{sighting}{COLOR_RESET}")


def visit_black_market(game):
    sec = game.galaxy[game.current_sector]
    port = sec["port"]
    if not port:
        return
        
    # Shady pricing
    buy_price = 300
    sell_price = 650
    
    if port["type"] == "Military":
        buy_price = 180
        sell_price = 450
    elif port["type"] == "High-Tech":
        buy_price = 350
        sell_price = 850
    elif port["type"] == "Agricultural":
        buy_price = 320
        sell_price = 780
        
    while True:
        clear_screen()
        print_banner()
        print(f"{COLOR_MAGENTA}--- PORT CANTINA & BLACK MARKET ---{COLOR_RESET}")
        print("The air is thick with smoke and quiet whispers of smugglers.")
        print(f"Credits: {COLOR_GREEN}{game.credits} CR{COLOR_RESET} | Space Spice owned: {game.cargo['Space Spice']}")
        print(f"Current Black Market Pricing for {COLOR_YELLOW}Space Spice{COLOR_RESET}:")
        print(f"  - Buy Spice:  {COLOR_GREEN}{buy_price} CR / unit{COLOR_RESET}")
        print(f"  - Sell Spice: {COLOR_GREEN}{sell_price} CR / unit{COLOR_RESET}")
        print(f"\n{COLOR_RED}⚠️ WARNING: Carrying Space Spice inside port-controlled systems triggers Navy Patrol Scans!{COLOR_RESET}")
        
        print("\nCommands:")
        print("1. Buy Space Spice")
        print("2. Sell Space Spice")
        print("3. Listen to rumors (Smuggler hints)")
        print("4. Return to main dockyards")
        
        choice = input(f"\n{COLOR_YELLOW}Select choice (1-4): {COLOR_RESET}").strip()
        if choice == "1":
            cargo_space = game.cargo_capacity - sum(game.cargo.values())
            if cargo_space <= 0:
                print(f"{COLOR_RED}Your cargo holds are completely full!{COLOR_RESET}")
                press_enter()
                continue
                
            qty_str = input(f"How many units of Space Spice to buy? ").strip()
            if not qty_str.isdigit(): continue
            qty = int(qty_str)
            if qty <= 0: continue
            if qty > cargo_space:
                qty = cargo_space
                
            total_cost = qty * buy_price
            if total_cost > game.credits:
                print(f"{COLOR_RED}Insufficient credits!{COLOR_RESET}")
            else:
                game.credits -= total_cost
                game.cargo["Space Spice"] += qty
                print(f"{COLOR_GREEN}Transaction complete! Purchased {qty} units of Spice.{COLOR_RESET}")
            press_enter()
            
        elif choice == "2":
            if game.cargo["Space Spice"] <= 0:
                print(f"{COLOR_RED}You don't have any Space Spice to sell!{COLOR_RESET}")
                press_enter()
                continue
                
            qty_str = input(f"How many units of Space Spice to sell? ").strip()
            if not qty_str.isdigit(): continue
            qty = int(qty_str)
            if qty <= 0: continue
            if qty > game.cargo["Space Spice"]:
                qty = game.cargo["Space Spice"]
                
            total_gain = qty * sell_price
            game.credits += total_gain
            game.cargo["Space Spice"] -= qty
            print(f"{COLOR_GREEN}Transaction complete! Sold {qty} units of Spice for {total_gain} CR.{COLOR_RESET}")
            press_enter()
            
        elif choice == "3":
            print(f"\n{COLOR_CYAN}A shady smuggler leans in and whispers rumors:{COLOR_RESET}")
            if game.active_event_sector is not None:
                print(f"  - \"I hear there's a {game.active_event} happening in Sector {game.active_event_sector}... high profit margins if you navigate correctly!\"")
            else:
                print("  - \"All clear right now, captain. Keep your jump drives primed.\"")
            press_enter()
            
        elif choice == "4":
            break

def dock_at_port(game):
    sec = game.galaxy[game.current_sector]
    if not sec["port"]:
        print(f"{COLOR_RED}There is no trading port in this sector.{COLOR_RESET}")
        press_enter()
        return

    port = sec["port"]
    while True:
        clear_screen()
        print_banner()
        print(f"{COLOR_GREEN}--- WELCOME TO {port['name'].upper()} ---{COLOR_RESET}")
        print(f"Profile: {COLOR_WHITE}{port['type']} Economy{COLOR_RESET} | Credits: {COLOR_GREEN}{game.credits} CR{COLOR_RESET}")
        
        # Display market
        print(f"\n{COLOR_CYAN}{'Good':<15} {'Buy Price':<12} {'Sell Price':<12} {'In Stock':<10} {'You Own':<8}{COLOR_RESET}")
        print("-" * 62)
        for good in GOODS:
            m_data = port["market"][good]
            buy_p = m_data['buy_price']
            sell_p = m_data['sell_price']
            
            # Apply dynamic event multipliers
            if game.active_event_sector == game.current_sector:
                if game.active_event == "Plague" and good == "Medicine":
                    sell_p = int(sell_p * 3.5)
                elif game.active_event == "IndustrialBoom" and good == "Machinery":
                    buy_p = int(buy_p * 0.5)
                elif game.active_event == "WeaponsShortage" and good == "Weapons":
                    sell_p = int(sell_p * 2.5)
                elif game.active_event == "Blockade":
                    buy_p = int(buy_p * 2.0)
                    sell_p = int(sell_p * 2.0)
            print(f"{good:<15} {buy_p:<12} {sell_p:<12} {m_data['stock']:<10} {game.cargo[good]:<8}")
            
        print("\nCommands:")
        print("1. Buy Cargo")
        print("2. Sell Cargo")
        print("3. Shipyards & Upgrades")
        print("4. Visit Space Bar & Black Market")
        print("5. Undock and Return to Main Controls")
        
        choice = input(f"\n{COLOR_YELLOW}Select dock command (1-5): {COLOR_RESET}").strip()
        if choice == "1":
            # Buy Loop
            good_num = select_good()
            if good_num is None: continue
            good = GOODS[good_num]
            m_data = port["market"][good]
            buy_p = m_data['buy_price']
            
            # Apply event multiplier
            if game.active_event_sector == game.current_sector:
                if game.active_event == "IndustrialBoom" and good == "Machinery":
                    buy_p = int(buy_p * 0.5)
                elif game.active_event == "Blockade":
                    buy_p = int(buy_p * 2.0)
            
            if m_data["stock"] <= 0:
                print(f"{COLOR_RED}Port is completely out of {good}!{COLOR_RESET}")
                press_enter()
                continue
                
            qty_str = input(f"How many units of {good} to buy (Price: {buy_p} CR)? ").strip()
            if not qty_str.isdigit(): continue
            qty = int(qty_str)
            
            if qty <= 0: continue
            if qty > m_data["stock"]:
                qty = m_data["stock"]
                
            total_cost = qty * buy_p
            cargo_space = game.cargo_capacity - sum(game.cargo.values())
            
            if total_cost > game.credits:
                print(f"{COLOR_RED}You do not have enough credits to purchase {qty} units!{COLOR_RESET}")
                press_enter()
            elif qty > cargo_space:
                print(f"{COLOR_RED}Your cargo holds cannot fit {qty} units! Free space: {cargo_space}{COLOR_RESET}")
                press_enter()
            else:
                game.credits -= total_cost
                game.cargo[good] += qty
                port["market"][good]["stock"] -= qty
                print(f"{COLOR_GREEN}Success! Purchased {qty} {good} for {total_cost} CR.{COLOR_RESET}")
                press_enter()
                
        elif choice == "2":
            # Sell Loop
            good_num = select_good()
            if good_num is None: continue
            good = GOODS[good_num]
            m_data = port["market"][good]
            sell_p = m_data['sell_price']
            
            # Apply event multiplier
            if game.active_event_sector == game.current_sector:
                if game.active_event == "Plague" and good == "Medicine":
                    sell_p = int(sell_p * 3.5)
                elif game.active_event == "WeaponsShortage" and good == "Weapons":
                    sell_p = int(sell_p * 2.5)
                elif game.active_event == "Blockade":
                    sell_p = int(sell_p * 2.0)
            
            if game.cargo[good] <= 0:
                print(f"{COLOR_RED}You don't have any {good} in your cargo hold!{COLOR_RESET}")
                press_enter()
                continue
                
            qty_str = input(f"How many units of {good} to sell (Price: {sell_p} CR)? ").strip()
            if not qty_str.isdigit(): continue
            qty = int(qty_str)
            
            if qty <= 0: continue
            if qty > game.cargo[good]:
                qty = game.cargo[good]
                
            total_gain = qty * sell_p
            game.credits += total_gain
            game.cargo[good] -= qty
            port["market"][good]["stock"] += qty
            print(f"{COLOR_GREEN}Success! Sold {qty} {good} for {total_gain} CR.{COLOR_RESET}")
            press_enter()
            
        elif choice == "3":
            # Upgrade Loop
            open_shipyard(game)
        elif choice == "4":
            visit_black_market(game)
        elif choice == "5":
            break


def select_good():
    print(f"\n{COLOR_CYAN}Select Commodity:{COLOR_RESET}")
    for idx, good in enumerate(GOODS):
        print(f" {idx + 1}. {good}")
    choice = input(f"Select choice (1-{len(GOODS)}): ").strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(GOODS):
            return idx
    return None


def open_shipyard(game):
    while True:
        clear_screen()
        print_banner()
        print(f"{COLOR_CYAN}--- TRITON DOCK & SHIPYARDS ---{COLOR_RESET}")
        print(f"Credits: {COLOR_GREEN}{game.credits} CR{COLOR_RESET} | Shield Level: {game.max_shields} | Cargo Bay: {game.cargo_capacity} m³")
        print(f"Hull Damage: {100 - game.hull}% (Full repair cost: {int((100 - game.hull) * 8)} CR)")
        print("\nUpgrades Available:")
        print("1. Repair Ship Hull (8 CR per 1% point)")
        print("2. Expand Cargo Holds (+5 Capacity) - Cost: 2,500 CR")
        print("3. Supercharged Shield Generator (+25 Max Shields) - Cost: 3,000 CR")
        print("4. High-Yield Plasma Blaster (+5 MW Weapons) - Cost: 4,000 CR")
        print("5. High-Efficiency Engine Recalibration (+10 Max Fuel) - Cost: 2,000 CR")
        print("6. Exit Shipyard")
        
        choice = input(f"\n{COLOR_YELLOW}Select shipyard choice (1-6): {COLOR_RESET}").strip()
        if choice == "1":
            points_needed = 100 - game.hull
            if points_needed <= 0:
                print("Your hull is already completely pristine!")
                press_enter()
            else:
                total_cost = points_needed * 8
                if total_cost <= game.credits:
                    game.credits -= total_cost
                    game.hull = 100
                    print(f"{COLOR_GREEN}Ship hull repaired to 100%!{COLOR_RESET}")
                else:
                    # Partial repair
                    affordable_points = int(game.credits / 8)
                    if affordable_points > 0:
                        game.credits -= affordable_points * 8
                        game.hull += affordable_points
                        print(f"{COLOR_GREEN}Hull repaired by {affordable_points}% (Max budget utilized).{COLOR_RESET}")
                    else:
                        print(f"{COLOR_RED}You don't even have enough credits to repair 1% of the hull!{COLOR_RESET}")
                press_enter()
                
        elif choice == "2":
            if game.credits >= 2500:
                game.credits -= 2500
                game.cargo_capacity += 5
                game.upgrades_value += 2500
                print(f"{COLOR_GREEN}Cargo hold expanded! New capacity: {game.cargo_capacity} m³{COLOR_RESET}")
            else:
                print(f"{COLOR_RED}Insufficient credits for Cargo upgrade!{COLOR_RESET}")
            press_enter()
            
        elif choice == "3":
            if game.credits >= 3000:
                game.credits -= 3000
                game.max_shields += 25
                game.shields = game.max_shields
                game.upgrades_value += 3000
                print(f"{COLOR_GREEN}Shields supercharged! Max shields now {game.max_shields}{COLOR_RESET}")
            else:
                print(f"{COLOR_RED}Insufficient credits for Shield upgrade!{COLOR_RESET}")
            press_enter()
            
        elif choice == "4":
            if game.credits >= 4000:
                game.credits -= 4000
                game.weapon_power += 5
                game.upgrades_value += 4000
                print(f"{COLOR_GREEN}Plasma blaster installed! Weapons power is now {game.weapon_power} MW{COLOR_RESET}")
            else:
                print(f"{COLOR_RED}Insufficient credits for Weapon upgrade!{COLOR_RESET}")
            press_enter()
            
        elif choice == "5":
            if game.credits >= 2000:
                game.credits -= 2000
                game.max_fuel += 10
                game.fuel = game.max_fuel
                game.upgrades_value += 2000
                print(f"{COLOR_GREEN}Engine recalibrated! Max Range: {game.max_fuel} LY{COLOR_RESET}")
            else:
                print(f"{COLOR_RED}Insufficient credits for Engine upgrade!{COLOR_RESET}")
            press_enter()
            
        elif choice == "6":
            break


def colonize_planet(game):
    sec = game.galaxy[game.current_sector]
    if not sec["planet"]:
        print(f"{COLOR_RED}There is no claimable planet in this sector.{COLOR_RESET}")
        press_enter()
        return
        
    p = sec["planet"]
    while True:
        clear_screen()
        print_banner()
        print(f"{COLOR_CYAN}--- PLANETARY SECTOR SURVEY: {p['name'].upper()} ---{COLOR_RESET}")
        print(f"Claim status: {COLOR_WHITE if not p['claimed'] else COLOR_GREEN}{'Claimed by you' if p['claimed'] else 'Unexplored Colony Candidates'}{COLOR_RESET}")
        print(f"Colony Population: {p['colonists']} scientists/pioneers")
        print(f"Orbital Batteries Defense level: {p['defense']} MW")
        print(f"Passive Revenue Generation: {p['income']} CR per cycle/turn")
        
        print("\nCommands:")
        if not p["claimed"]:
            print(f"1. Establish Base (Claim Planet) - Cost: {COLOR_GREEN}1,500 CR{COLOR_RESET}")
        else:
            print(f"1. Recruit Colonists (Add 50 Colonists) - Cost: {COLOR_GREEN}400 CR{COLOR_RESET}")
            print(f"2. Build Orbital Defenses (+1 Defense Level) - Cost: {COLOR_GREEN}600 CR{COLOR_RESET}")
            print(f"3. Commission Industry Upgrades (Increase Income by 100 CR/Day) - Cost: {COLOR_GREEN}1,000 CR{COLOR_RESET}")
        print("4. Return to Main Orbit Controls")
        
        choice = input(f"\n{COLOR_YELLOW}Select choice (1-4): {COLOR_RESET}").strip()
        if choice == "1":
            if not p["claimed"]:
                if game.credits >= 1500:
                    game.credits -= 1500
                    p["claimed"] = True
                    p["colonists"] = 100
                    p["income"] = 200
                    game.upgrades_value += 1500
                    print(f"{COLOR_GREEN}Success! You have founded a colony on {p['name']}.{COLOR_RESET}")
                else:
                    print(f"{COLOR_RED}You don't have enough credits to claim this planet!{COLOR_RESET}")
                press_enter()
            else:
                if game.credits >= 400:
                    game.credits -= 400
                    p["colonists"] += 50
                    p["income"] += 50
                    print(f"{COLOR_GREEN}Transport shuttles have landed. New colony population: {p['colonists']}{COLOR_RESET}")
                else:
                    print(f"{COLOR_RED}Insufficient credits to fund colonist transports!{COLOR_RESET}")
                press_enter()
        elif choice == "2":
            if p["claimed"]:
                if game.credits >= 600:
                    game.credits -= 600
                    p["defense"] += 1
                    print(f"{COLOR_GREEN}Planetary defense grids augmented successfully.{COLOR_RESET}")
                else:
                    print(f"{COLOR_RED}Insufficient credits for defense array!{COLOR_RESET}")
                press_enter()
            else:
                print("Invalid command.")
        elif choice == "3":
            if p["claimed"]:
                if game.credits >= 1000:
                    game.credits -= 1000
                    p["income"] += 100
                    print(f"{COLOR_GREEN}Planetary industry upgraded! Net daily return: {p['income']} CR{COLOR_RESET}")
                else:
                    print(f"{COLOR_RED}Insufficient credits for industry upgrades!{COLOR_RESET}")
                press_enter()
            else:
                print("Invalid command.")
        elif choice == "4":
            break


def show_colonial_ledger(game):
    clear_screen()
    print_banner()
    print(f"{COLOR_GREEN}--- GALACTIC COLONIAL LEDGER ---{COLOR_RESET}")
    
    # Gather all claimed planets
    colonies = []
    for sec_id, node in game.galaxy.items():
        if node["planet"] and node["planet"]["claimed"]:
            colonies.append((sec_id, node["planet"]))
            
    if not colonies:
        print(f"\n{COLOR_YELLOW}You have not established any planetary colonies yet!{COLOR_RESET}")
        print("Establish a base by surveying a sector with a claimable planet and spending 1,500 CR.")
        press_enter()
        return
        
    print(f"\n{COLOR_CYAN}{'Sector':<8} {'Planet Name':<15} {'Population':<12} {'Defenses':<10} {'Daily Income':<12}{COLOR_RESET}")
    print("-" * 62)
    
    total_pop = 0
    total_income = 0
    for sec_id, p in colonies:
        print(f"{sec_id:<8} {p['name']:<15} {p['colonists']:<12} {p['defense']} MW{'' if p['defense'] >= 10 else ' ':<6} {p['income']} CR")
        total_pop += p["colonists"]
        total_income += p["income"]
        
    print("-" * 62)
    print(f"{COLOR_WHITE}Total Established Colonies: {len(colonies)}{COLOR_RESET}")
    print(f"Total Combined Population:  {COLOR_WHITE}{total_pop:,} Pioneers{COLOR_RESET}")
    print(f"Total Daily Revenue Stream:  {COLOR_GREEN}{total_income:,} CR / Day{COLOR_RESET}")
    press_enter()


def colony_management_console(game):
    while True:
        clear_screen()
        print_banner()
        print(f"{COLOR_CYAN}--- PLANETARY COLONIES & SURVEY CONSOLE ---{COLOR_RESET}")
        print("1. Survey Planet in Current Sector")
        print("2. Access Colonial Ledger & Central Command")
        print("3. Return to Main Orbit Controls")
        
        choice = input(f"\n{COLOR_YELLOW}Select navigational option (1-3): {COLOR_RESET}").strip()
        if choice == "1":
            colonize_planet(game)
        elif choice == "2":
            show_colonial_ledger(game)
        elif choice == "3":
            break


# --- SYSTEM COMBAT ENGINE ---
def handle_combat_encounter(game):
    # Determine local environment and spawn pirate
    clear_screen()
    print_banner()
    
    pirate_hull = random.randint(30, 80)
    pirate_weapons = random.randint(8, 20)
    
    print(f"\n{COLOR_RED}🚨 RED ALERT! Pirate interception detected!{COLOR_RESET}")
    print(f"Hostile fighter closing fast. Scanner estimates:")
    print(f"  - Target Hull Integrity: {pirate_hull}%")
    print(f"  - Threat Rating: {pirate_weapons} MW Weapon Arrays")
    
    # Recharge half of the shield pool at the start of a combat turn
    game.shields = min(game.max_shields, game.shields + int(game.max_shields * 0.2))
    
    while pirate_hull > 0 and game.hull > 0:
        print(f"\n{COLOR_CYAN}--- COMBAT SITUATION ---{COLOR_RESET}")
        print(f"YOUR SHIP: Hull {game.hull}% | Shields {game.shields}/{game.max_shields}% | Weapons {game.weapon_power} MW")
        print(f"PIRATE: Hull {pirate_hull}%")
        print("\nCommands:")
        print("1. Fire Plasma Blasters (Attack)")
        print("2. Tactical Evade (Increase defense, reload shields)")
        print("3. Flee to Connected Sector (Consumes 2 Fuel/Range)")
        print("4. Pay Off Pirate (Jettison half of all credits)")
        
        choice = input(f"\n{COLOR_YELLOW}Choose tactical order (1-4): {COLOR_RESET}").strip()
        if choice == "1":
            # Player attack
            damage = int(game.weapon_power * random.uniform(0.8, 1.4))
            pirate_hull -= damage
            print(f"{COLOR_GREEN}You landed a direct hit on the pirate! Target hull took {damage}% damage.{COLOR_RESET}")
            
            # Pirate attack
            if pirate_hull > 0:
                pirate_attack(game, pirate_weapons)
                
        elif choice == "2":
            # Tactical evade
            recharge = int(game.max_shields * 0.3)
            game.shields = min(game.max_shields, game.shields + recharge)
            print(f"{COLOR_BLUE}Executing defensive rolls. Shields recharged by {recharge}%.{COLOR_RESET}")
            # Pirate attack deals 50% damage
            pirate_attack(game, pirate_weapons, evaded=True)
            
        elif choice == "3":
            if game.fuel >= 2:
                game.fuel -= 2
                escape_sector = random.choice(game.galaxy[game.current_sector]["connections"])
                game.current_sector = escape_sector
                game.explored_sectors.add(escape_sector)
                print(f"{COLOR_GREEN}Success! You hyperspace warped to Sector {escape_sector} and escaped the ambush!{COLOR_RESET}")
                press_enter()
                return
            else:
                print(f"{COLOR_RED}Your jump drives don't have enough fuel to execute emergency warp!{COLOR_RESET}")
                press_enter()
                
        elif choice == "4":
            bribe = int(game.credits * 0.5)
            game.credits -= bribe
            print(f"{COLOR_YELLOW}You paid a bribe of {bribe} CR. The pirate laughs and disengages.{COLOR_RESET}")
            press_enter()
            return
            
    if game.hull <= 0:
        print(f"\n{COLOR_RED}💥 HULL COLLAPSE DETECTED! Your vessel is shattered to scrap.{COLOR_RESET}")
        game.hull = 20
        loss = int(game.credits * 0.25)
        game.credits -= loss
        print(f"A corporate salvage drone rescue shuttle recovers you... but it costs a {loss} CR fee.")
        print("Your cargo bay is completely empty.")
        for g in game.cargo:
            game.cargo[g] = 0
        press_enter()
    elif pirate_hull <= 0:
        reward = random.randint(300, 1200)
        game.credits += reward
        print(f"\n{COLOR_GREEN}🎯 TARGET OBLITERATED! You salvage the pirate's debris field for {reward} CR.{COLOR_RESET}")
        press_enter()


def pirate_attack(game, pirate_power, evaded=False):
    factor = 0.5 if evaded else 1.0
    raw_damage = int(pirate_power * random.uniform(0.8, 1.2) * factor)
    
    if game.shields > 0:
        if raw_damage <= game.shields:
            game.shields -= raw_damage
            print(f"{COLOR_YELLOW}Pirate fired back. Your shields absorbed all {raw_damage}% damage.{COLOR_RESET}")
        else:
            overflow = raw_damage - game.shields
            game.shields = 0
            game.hull -= overflow
            print(f"{COLOR_RED}Pirate fired back. Your shields collapsed! Hull integrity took {overflow}% damage.{COLOR_RESET}")
    else:
        game.hull -= raw_damage
        print(f"{COLOR_RED}Pirate fired back directly on your hull! Hull took {raw_damage}% damage.{COLOR_RESET}")


def trigger_patrol_scan(game):
    spice_qty = game.cargo.get("Space Spice", 0)
    if spice_qty <= 0:
        return
        
    clear_screen()
    print_banner()
    print(f"{COLOR_RED}{COLOR_BOLD}🚨 ALERT: SYSTEM PATROL INTERCEPT IN PROGRESS! 🚨{COLOR_RESET}")
    print(f"Federal Navy Corvette has locked tractor beams on your vessel in Sector {game.current_sector}!")
    print("Scanner sweeps have detected illegal contraband in your cargo hold!")
    print(f"Illegal cargo detected: {COLOR_MAGENTA}{spice_qty} unit(s) of Space Spice{COLOR_RESET}")
    
    while True:
        print("\nOptions:")
        print("1. Yield Cargo and Pay Fine (Consumes 20% credits, all Space Spice confiscated)")
        print("2. Attempt to Bribe Officer (Costs 500 CR, 60% success rate)")
        print("3. Hyperspace Flight (Attempt emergency run, risk hull damage)")
        
        choice = input(f"\n{COLOR_YELLOW}Enter choice (1-3): {COLOR_RESET}").strip()
        if choice == "1":
            fine = int(game.credits * 0.20)
            game.credits -= fine
            game.cargo["Space Spice"] = 0
            print(f"\n{COLOR_YELLOW}You surrendered your spice. The Patrol fines you {fine} CR and leaves.{COLOR_RESET}")
            press_enter()
            return
        elif choice == "2":
            if game.credits >= 500:
                game.credits -= 500
                if random.random() < 0.60:
                    print(f"\n{COLOR_GREEN}Success! The officer accepts your bribe and deletes the scan log. \"Safe flights, captain...\"{COLOR_RESET}")
                    press_enter()
                    return
                else:
                    print(f"\n{COLOR_RED}Bribe Rejected! \"Are you trying to corrupt a federal officer?!\" the scanner blares.{COLOR_RESET}")
                    print("Your cargo is confiscated, and you are heavily fined!")
                    fine = int(game.credits * 0.35)
                    game.credits -= fine
                    game.cargo["Space Spice"] = 0
                    game.hull = max(20, game.hull - 15)
                    print(f"Fined: {fine} CR. Hull took 15% shock charge damage during arrest.")
                    press_enter()
                    return
            else:
                print(f"{COLOR_RED}You do not have 500 Credits to offer a bribe!{COLOR_RESET}")
                press_enter()
        elif choice == "3":
            print(f"\n{COLOR_RED}Engaging thrusters! The patrol corvette opens fire as you spool warp drives!{COLOR_RESET}")
            damage = random.randint(15, 30)
            game.hull -= damage
            print(f"Warp successful, but hull took {damage}% laser fire damage!")
            
            # Force jump to a random neighbor
            sec = game.galaxy[game.current_sector]
            escape_sector = random.choice(sec["connections"])
            game.current_sector = escape_sector
            game.explored_sectors.add(escape_sector)
            print(f"Warped into Sector {escape_sector}!")
            press_enter()
            
            if game.hull <= 0:
                game.hull = 20
                print(f"{COLOR_RED}Your ship was heavily damaged and rescued by corporate drones.{COLOR_RESET}")
                press_enter()
            return


def execute_warp_landing(game, dest):
    game.current_sector = dest
    game.explored_sectors.add(dest)
    new_sec = game.galaxy[dest]
    
    # 1. Apply Blockade guaranteed hazard/pirates if blockade active in dest
    if game.active_event_sector == dest and game.active_event == "Blockade":
        print(f"\n{COLOR_RED}🚨 ALERT! Entering a MILITARY BLOCKADE zone in Sector {dest}!{COLOR_RESET}")
        if game.cargo.get("Space Spice", 0) > 0:
            print("Blockade scanners have detected your contraband! Guaranteed intercept!")
            trigger_patrol_scan(game)
            return
        elif random.random() < 0.50:
            print("System blockading warships mistake your vessel for a blockade runner!")
            handle_combat_encounter(game)
            return
            
    # 2. Apply Hazards
    if new_sec["hazard"] != "None":
        hz = new_sec["hazard"]
        print(f"\n{COLOR_RED}🚨 ALERT! Warp completed into an active {hz}!{COLOR_RESET}")
        if hz == "Asteroid Belt":
            game_damage = random.randint(5, 15)
            game.hull -= game_damage
            print(f"Impact! Hull collided with asteroid. Integrity took {game_damage}% damage.")
        elif hz == "Nebula Anomaly":
            game.shields = 0
            print("Nebula discharges completely depleted your shield reserves.")
        elif hz == "Radiation Flux":
            game.fuel = max(0, game.fuel - 2)
            print("Intense solar radiation drained your engines by 2 range cells.")
        elif hz == "Minefield":
            mine_dmg = random.randint(10, 25)
            game.hull -= mine_dmg
            print(f"Explosion! Warped onto deep space mine! Hull took {mine_dmg}% damage.")
        press_enter()
        
        if game.hull <= 0:
            game.hull = 20
            print(f"{COLOR_RED}Your ship was rescued by emergency drones.{COLOR_RESET}")
            press_enter()
            
    # 3. Apply Smuggling Scan
    elif game.cargo.get("Space Spice", 0) > 0 and new_sec["port"] is not None and random.random() < 0.15:
        trigger_patrol_scan(game)
        
    # 4. Standard Pirate Ambush (12%)
    elif random.random() < 0.12:
        handle_combat_encounter(game)
        
    else:
        print(f"\n{COLOR_GREEN}Successful jump to Sector {dest}!{COLOR_RESET}")
        press_enter()


def find_shortest_path(galaxy, start, dest):
    queue = [[start]]
    visited = {start}
    
    while queue:
        path = queue.pop(0)
        curr = path[-1]
        
        if curr == dest:
            return path
            
        for neighbor in galaxy[curr]["connections"]:
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path) + [neighbor]
                queue.append(new_path)
    return None


def plot_warp_route(game):
    clear_screen()
    print_banner()
    print(f"{COLOR_CYAN}--- HYPERSPACE NAVIGATION COMPUTER ---{COLOR_RESET}")
    print(f"Current Position: Sector {game.current_sector}")
    print(f"Engine Fuel Cells: {game.fuel} / {game.max_fuel}")
    
    dest_str = input(f"\nEnter destination sector (1-{TOTAL_SECTORS}): ").strip()
    if not dest_str.isdigit():
        print(f"{COLOR_RED}Invalid sector number.{COLOR_RESET}")
        press_enter()
        return
        
    dest = int(dest_str)
    if dest < 1 or dest > TOTAL_SECTORS:
        print(f"{COLOR_RED}Sector number must be between 1 and {TOTAL_SECTORS}.{COLOR_RESET}")
        press_enter()
        return
        
    if dest == game.current_sector:
        print(f"{COLOR_YELLOW}You are already in Sector {dest}!{COLOR_RESET}")
        press_enter()
        return
        
    # BFS to find shortest path using helper
    start = game.current_sector
    shortest_path = find_shortest_path(game.galaxy, start, dest)
                
    if not shortest_path:
        print(f"{COLOR_RED}No warp connection path found to Sector {dest}!{COLOR_RESET}")
        press_enter()
        return
        
    # Print the route details
    print(f"\n{COLOR_GREEN}Shortest path plotted successfully!{COLOR_RESET}")
    print("Route: ", end="")
    route_strs = []
    for node_id in shortest_path:
        if node_id == start:
            route_strs.append(f"{COLOR_YELLOW}Sector {node_id}{COLOR_RESET}")
        elif node_id == dest:
            route_strs.append(f"{COLOR_CYAN}Sector {node_id}{COLOR_RESET}")
        else:
            route_strs.append(f"Sector {node_id}")
    print(" -> ".join(route_strs))
    
    hops = len(shortest_path) - 1
    print(f"\nTotal hops: {COLOR_WHITE}{hops}{COLOR_RESET}")
    print(f"Fuel cost:  {COLOR_WHITE}{hops} Cells{COLOR_RESET}")
    
    # Analyze sector details along path
    print(f"\n{COLOR_CYAN}Route Reconnaissance Info:{COLOR_RESET}")
    for idx, node_id in enumerate(shortest_path[1:], 1):
        node = game.galaxy[node_id]
        detail = "Empty Deep Space"
        if node["port"]:
            detail = f"Trade Port ({node['port']['name']} - {node['port']['type']})"
        elif node["planet"]:
            detail = f"Planet ({node['planet']['name']})"
        elif node["hazard"] != "None":
            detail = f"{COLOR_RED}Hazard! ({node['hazard']}){COLOR_RESET}"
        print(f" Jump {idx:<2}: Sector {node_id:<3} | Contents: {detail}")
        
    if game.fuel >= hops:
        print(f"\n{COLOR_GREEN}Status: Propulsion systems are fully prepared. Optimal range cell budget exists!{COLOR_RESET}")
    else:
        print(f"\n{COLOR_RED}Status: Warning! Fuel reserves insufficient ({game.fuel}/{hops} required) to complete total route.{COLOR_RESET}")
        
    # Ask to make the first warp hop
    next_sector = shortest_path[1]
    ans = input(f"\nWould you like to initiate hyperspace warp to Sector {next_sector} (1st jump)? (y/n): ").strip().lower()
    if ans == 'y':
        if game.fuel >= 1:
            game.fuel -= 1
            execute_warp_landing(game, next_sector)
        else:
            print(f"{COLOR_RED}Not enough fuel cells left! Advance day to recharge.{COLOR_RESET}")
            press_enter()


# --- MAIN ENGINE CONTROL LOOP ---
def run_game_loop():
    clear_screen()
    print_banner()
    print("Welcome Privateer!")
    print("\n1. Start a New Campaign")
    print("2. Load Existing Save File")
    print("3. Read Pilot Manual & Tutorial")
    print("4. Exit")
    
    choice = input(f"\n{COLOR_YELLOW}Select path (1-4): {COLOR_RESET}").strip()
    if choice == "2":
        g = Game()
        if g.load():
            print(f"{COLOR_GREEN}Save game loaded successfully! Resuming campaign...{COLOR_RESET}")
            time.sleep(1)
        else:
            print(f"{COLOR_RED}No save file found or file corrupted. Starting a clean campaign...{COLOR_RESET}")
            g = Game()
            time.sleep(1.5)
    elif choice == "3":
        show_manual()
        g = Game()
    elif choice == "4":
        sys.exit(0)
    else:
        g = Game()
        print(f"{COLOR_GREEN}Galaxy procedural seed generated: {g.seed}. Ready to warp!{COLOR_RESET}")
        time.sleep(1.5)
        
    while True:
        # Check Win Condition
        if g.get_net_worth() >= WIN_NET_WORTH:
            clear_screen()
            print_banner()
            print(f"""{COLOR_GREEN}{COLOR_BOLD}
   __   ______  _    _  __          _______ _   _ 
   \\ \\ / / __ \\| |  | | \\ \\        / /_   _| \\ | |
    \\ V / |  | | |  | |  \\ \\  /\\  / /  | | |  \\| |
     | || |__| | |__| |   \\ \\/  \\/ /  _| |_| |\\  |
     |_| \\____/ \\____/     \\_/\\_/  |_____|_| \\_|
{COLOR_RESET}
🏆 CONGRATULATIONS CAPTAIN! 🏆
You have accumulated a net worth of {g.get_net_worth():,} CR!
You have successfully built an empire, secured high-yield assets,
and achieved ultimate economic dominance in this galaxy!
            """)
            break
            
        clear_screen()
        print_banner()
        show_status(g)
        
        print("\nCommands:")
        print("1. Dock at Port & Trade / Upgrade")
        print("2. Hyperspace Warp (Move to connected Sector)")
        print("3. Planetary Colonies & Survey Console")
        print("4. Solar Scanner (Map out adjacent sectors)")
        print("5. Navigation Computer (Plot Route to any Sector)")
        print("6. End Day / Recharge Fuel (Saves state, advances cycle)")
        print("7. Save Game Status")
        print("8. Abandon Game and Exit")
        
        cmd = input(f"\n{COLOR_YELLOW}Enter navigational choice (1-8): {COLOR_RESET}").strip()
        
        if cmd == "1":
            dock_at_port(g)
            
        elif cmd == "2":
            sec = g.galaxy[g.current_sector]
            print(f"\nAdjacent warp lane exits: {COLOR_WHITE}{', '.join(map(str, sorted(sec['connections'])))}{COLOR_RESET}")
            dest_str = input("Jump to which sector number? ").strip()
            if dest_str.isdigit():
                dest = int(dest_str)
                if dest in sec["connections"]:
                    if g.fuel >= 1:
                        # Execution of warp
                        g.fuel -= 1
                        execute_warp_landing(g, dest)
                    else:
                        print(f"{COLOR_RED}Not enough fuel cells left! Advance day to recharge.{COLOR_RESET}")
                        press_enter()
                else:
                    print(f"{COLOR_RED}No warp lane connects current location directly to Sector {dest}!{COLOR_RESET}")
                    press_enter()
                    
        elif cmd == "3":
            colony_management_console(g)
            
        elif cmd == "4":
            sec = g.galaxy[g.current_sector]
            print(f"\n{COLOR_CYAN}--- SOLAR SENSORS RADAR ---{COLOR_RESET}")
            for conn in sorted(sec["connections"]):
                node = g.galaxy[conn]
                detail = "Empty Deep Space"
                if node["port"]:
                    detail = f"Trade Port ({node['port']['name']})"
                elif node["planet"]:
                    detail = f"Planet ({node['planet']['name']})"
                elif node["hazard"] != "None":
                    detail = f"Hazard Warning! ({node['hazard']})"
                    
                print(f" Sector {conn:<3} Exits: {len(node['connections']):<1} | Contents: {detail}")
            press_enter()
            
        elif cmd == "5":
            plot_warp_route(g)
            
        elif cmd == "6":
            # End Day & Recharge
            g.days_elapsed += 1
            # Earn passive income from claimed planets
            passive_income = 0
            for sec_id, node in g.galaxy.items():
                if node["planet"] and node["planet"]["claimed"]:
                    passive_income += node["planet"]["income"]
            
            g.credits += passive_income
            g.fuel = g.max_fuel
            g.shields = g.max_shields
            
            # Generate new random daily event
            g.generate_daily_event()
            g.update_ai_traders()
            
            # Save game state automatically
            g.save()
            print(f"\n{COLOR_GREEN}Day concluded!{COLOR_RESET}")
            print(f" - Engines fully refueled to {g.max_fuel} range units.")
            print(f" - Shields completely recycled and recharged to {g.max_shields}%.")
            if passive_income > 0:
                print(f" - Collected {COLOR_GREEN}{passive_income} CR{COLOR_RESET} of colonial passive income from planets!")
            if g.active_event_text:
                print(f" - {COLOR_YELLOW}{COLOR_BOLD}DAILY EVENT INCOMING:{COLOR_RESET} {g.active_event_text}")
            print(f"Campaign state automatically cached to '{SAVE_FILE}'.")
            press_enter()
            
        elif cmd == "7":
            if g.save():
                print(f"\n{COLOR_GREEN}Campaign saved successfully! Location: '{SAVE_FILE}'{COLOR_RESET}")
            else:
                print(f"\n{COLOR_RED}Error saving progress to filesystem.{COLOR_RESET}")
            press_enter()
            
        elif cmd == "8":
            print("\nSafe travels, Privateer!")
            break


def show_manual():
    clear_screen()
    print_banner()
    print(f"""{COLOR_CYAN}======== SPACE MERCHANT MANUAL & TUTORIAL ========
{COLOR_WHITE}
1. THE OBJECTIVE
   Accumulate a total Net Worth of 100,000 Credits (CR). Your Net Worth is
   the sum of your current credits, cargo value, and your ship's installed upgrades.

2. WARP LANES & TRAVEL
   The galaxy consists of 100 sectors connected by two-way warp lanes.
   Each jump to a connected sector consumes 1 Fuel/Range unit.
   If you run out of range, select "End Day" to fully refit and refuel.

3. THE TRADING ECONOMY
   Ports have specialized economies. Buy goods in ports where they are plentiful
   and cheap, and sell them in sectors where they are in heavy demand:
   - Agricultural: Food is cheap. High demand for Machinery and Electronics.
   - Mining: Ore is cheap. High demand for Food and Machinery.
   - Industrial: Machinery and Fuel Cells are cheap. High demand for Ore.
   - High-Tech: Electronics and Luxury Goods are cheap. High demand for Fuel/Meds.
   - Military: Weapons are cheap. High demand for Electronics and Fuel Cells.

4. SECTOR HAZARDS & COMBAT
   Watch out for radiation belts, asteriods, and pirate factions.
   Warping into a sector with a Hazard will trigger hull damage or shield drain.
   Pirates have a random chance to ambush you during hyperjumps. Keep your shields
   and hull well-repaired at Triton Dockyards!

5. SMUGGLING CONTRABAND (HIGH RISK)
   You can buy and sell illegal "Space Spice" by visiting the local Space Bar
   & Black Market inside docked ports. It is highly lucrative, but carries
   extreme risk! Warping into systems with ports while carrying spice has a
   15% chance to trigger federal Navy Patrol Scans. If caught, you will face
   hefty fines, cargo confiscation, or combat!

6. DAILY NEWS & EVENTS
   Each day, the galaxy shifts. Keep your eyes on the "DAILY NEWS FLASH" at
   the top of your report for:
   - Space Plagues (Medicine sells for 3.5x!)
   - Industrial Surpluses (Machinery is 50% off!)
   - Weapons Shortages (Weapons sell for 2.5x!)
   - Military Blockades (Port prices are doubled, but highly dangerous!)
{COLOR_RESET}""")
    press_enter()


if __name__ == "__main__":
    try:
        run_game_loop()
    except KeyboardInterrupt:
        print("\nAbrupt core dump shutdown. Safe travels, Privateer!")
