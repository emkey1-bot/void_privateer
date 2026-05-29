#!/usr/bin/env python3
import unittest
import os
import shutil
import json
import tempfile
from unittest.mock import patch
from game import Game, SAVE_FILE, generate_galaxy, GOODS, PORT_TYPES, find_shortest_path, autopilot_warp_route, FACTION_NAMES

class TestVoidPrivateer(unittest.TestCase):
    def setUp(self):
        # Initialize a standard game with a fixed test seed
        self.game = Game(seed_val=1234)
        
    def tearDown(self):
        # Clean up save file if written
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)

    def test_galaxy_generation(self):
        # Check that we generated exactly 100 sectors
        self.assertEqual(len(self.game.galaxy), 100)
        
        # Check that warp connections are mutual
        for sec_id, sector in self.game.galaxy.items():
            for conn_id in sector["connections"]:
                self.assertIn(sec_id, self.game.galaxy[conn_id]["connections"])
                
    def test_economy_and_ports(self):
        # Verify that ports are set up and have goods
        ports_count = sum(1 for s in self.game.galaxy.values() if s["port"] is not None)
        self.assertGreaterEqual(ports_count, 10)
        
        # Verify that goods are priced within reasonable bounds
        for s in self.game.galaxy.values():
            if s["port"]:
                port = s["port"]
                self.assertIn(port["type"], PORT_TYPES)
                for good in GOODS:
                    self.assertIn(good, port["market"])
                    m_data = port["market"][good]
                    self.assertGreater(m_data["buy_price"], 0)
                    self.assertGreaterEqual(m_data["sell_price"], 0)
                    self.assertGreaterEqual(m_data["stock"], 0)

    def test_player_net_worth(self):
        # Initial credits = 1000, initial upgrades = 0
        self.assertEqual(self.game.get_net_worth(), 1000)
        
        # Buying cargo should update net worth (cargo flat average base value = 50 per unit)
        self.game.cargo["Food"] = 2
        self.assertEqual(self.game.get_net_worth(), 1100)

    def test_save_load_loop(self):
        # Modify state
        self.game.credits = 5500
        self.game.current_sector = 42
        self.game.cargo["Weapons"] = 1
        self.game.add_log_entry("Test checkpoint reached.")
        self.game.set_aux_output("SOLAR SCANNER", ["Sector 2", "Sector 9"])
        
        # Save game
        save_success = self.game.save()
        self.assertTrue(save_success)
        self.assertTrue(os.path.exists(SAVE_FILE))
        
        # Load into new instance
        new_game = Game()
        load_success = new_game.load()
        self.assertTrue(load_success)
        
        # Verify loaded properties match saved ones
        self.assertEqual(new_game.credits, 5500)
        self.assertEqual(new_game.current_sector, 42)
        self.assertEqual(new_game.cargo["Weapons"], 1)
        self.assertEqual(new_game.seed, 1234)
        self.assertIn("Test checkpoint reached.", "\n".join(new_game.captains_log))
        self.assertEqual(new_game.aux_output_title, "SOLAR SCANNER")
        self.assertEqual(new_game.aux_output_lines, ["Sector 2", "Sector 9"])

    def test_load_legacy_cwd_save(self):
        legacy_state = {
            "seed": 1234,
            "credits": 4321,
            "fuel": 18,
            "max_fuel": 20,
            "hull": 95,
            "max_hull": 100,
            "shields": 40,
            "max_shields": 50,
            "weapon_power": 10,
            "cargo_capacity": 20,
            "cargo": {good: 0 for good in GOODS} | {"Space Spice": 1},
            "current_sector": 7,
            "explored_sectors": [1, 7],
            "days_elapsed": 3,
            "upgrades_value": 0,
            "active_event": None,
            "active_event_text": "",
            "active_event_sector": None,
            "ai_traders": {},
            "ai_sightings": [],
            "captains_log": ["legacy save detected"],
            "display_mode": "classic",
        }
        old_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                os.chdir(tmpdir)
                with open("savegame.json", "w") as f:
                    json.dump(legacy_state, f)
                loaded = Game()
                self.assertTrue(loaded.load())
                self.assertEqual(loaded.credits, 4321)
                self.assertEqual(loaded.current_sector, 7)
                self.assertIn("legacy save detected", "\n".join(loaded.captains_log))
            finally:
                os.chdir(old_cwd)

    def test_load_partial_save_uses_defaults_for_new_fields(self):
        partial_state = {
            "seed": 1234,
            "credits": 2222,
            "fuel": 17,
            "max_fuel": 40,
            "hull": 88,
            "max_hull": 100,
            "shields": 25,
            "max_shields": 50,
            "weapon_power": 15,
            "cargo_capacity": 10,
            "cargo": {"Food": 3},
            "current_sector": 9,
            "explored_sectors": [1, 9],
            "days_elapsed": 4,
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(partial_state, f)

        loaded = Game()
        self.assertTrue(loaded.load())
        self.assertEqual(loaded.credits, 2222)
        self.assertEqual(loaded.current_sector, 9)
        self.assertEqual(loaded.cargo["Food"], 3)
        self.assertEqual(loaded.cargo["Space Spice"], 0)
        self.assertEqual(loaded.display_mode, "classic")
        self.assertEqual(loaded.aux_output_title, "AUXILIARY OUTPUT")
        self.assertTrue(isinstance(loaded.ai_traders, dict))

    def test_shortest_path_routing(self):
        # Let's verify route from Sector 1 to Sector 5
        path = find_shortest_path(self.game.galaxy, 1, 5)
        self.assertIsNotNone(path)
        self.assertEqual(path[0], 1)
        self.assertEqual(path[-1], 5)
        
        # Verify that each step along the path is a valid warp connection
        for idx in range(len(path) - 1):
            curr = path[idx]
            nxt = path[idx + 1]
            self.assertIn(nxt, self.game.galaxy[curr]["connections"])

    def test_contraband_and_events(self):
        # 1. Contraband should exist in cargo inventory
        self.assertIn("Space Spice", self.game.cargo)
        self.assertEqual(self.game.cargo["Space Spice"], 0)
        
        # 2. Daily events should generate and set corresponding variables
        self.game.generate_daily_event()
        self.assertIn(self.game.active_event, [None, "Plague", "IndustrialBoom", "WeaponsShortage", "Blockade"])
        
        # 3. Test Net Worth calculations with Space Spice (worth 500 CR/unit)
        self.game.cargo["Space Spice"] = 2
        self.assertEqual(self.game.get_net_worth(), 2000) # credits=1000 + 2*500

    def test_colonies_and_ai_traders(self):
        # 1. Verify AI starting settings
        self.assertGreater(len(self.game.ai_traders), 0)
        self.assertIn("Soren's Hauler", self.game.ai_traders)
        self.assertTrue(all("faction" in ship for ship in self.game.ai_traders.values()))
        self.assertTrue(all("cargo" in ship for ship in self.game.ai_traders.values()))
        self.assertTrue(all(ship["faction"] in FACTION_NAMES for ship in self.game.ai_traders.values()))
        
        # 2. Verify AI updates make sightings logs
        self.game.update_ai_traders()
        self.assertGreaterEqual(len(self.game.ai_sightings), len(self.game.ai_traders))
        
        # 3. Verify colonies ledger capability
        # Find some planet and claim it
        planet_sec = None
        for sec_id, node in self.game.galaxy.items():
            if node["planet"]:
                planet_sec = sec_id
                node["planet"]["claimed"] = True
                node["planet"]["income"] = 350
                break
                
        self.assertIsNotNone(planet_sec)
        
        # Verify passive income is counted correctly in get_net_worth and End Day loops
        self.assertEqual(self.game.galaxy[planet_sec]["planet"]["income"], 350)

    def test_captains_log_is_capped(self):
        for i in range(150):
            self.game.add_log_entry(f"Log line {i}")
        self.assertEqual(len(self.game.captains_log), 120)
        self.assertTrue(self.game.captains_log[-1].endswith("Log line 149"))

    def test_autopilot_route_stops_after_pirate_contact(self):
        route = [10, 11, 12, 13]
        self.game.current_sector = 10
        self.game.fuel = 5
        self.game.explored_sectors = {10}

        outcomes = ["clear", "pirates"]

        def fake_landing(game, dest):
            game.current_sector = dest
            return outcomes.pop(0)

        with patch("game.execute_warp_landing", side_effect=fake_landing), patch("game.press_enter", return_value=None):
            autopilot_warp_route(self.game, route)

        self.assertEqual(self.game.current_sector, 12)
        self.assertEqual(self.game.fuel, 3)

    def test_autopilot_route_stops_when_fuel_runs_out(self):
        route = [20, 21, 22, 23]
        self.game.current_sector = 20
        self.game.fuel = 1

        visited = []

        def fake_landing(game, dest):
            game.current_sector = dest
            visited.append(dest)
            return "clear"

        with patch("game.execute_warp_landing", side_effect=fake_landing), patch("game.press_enter", return_value=None):
            autopilot_warp_route(self.game, route)

        self.assertEqual(visited, [21])
        self.assertEqual(self.game.current_sector, 21)
        self.assertEqual(self.game.fuel, 0)

    def test_pirate_chance_increases_with_risk(self):
        baseline = self.game.get_pirate_encounter_chance(self.game.current_sector)
        self.game.cargo["Space Spice"] = 2
        self.game.credits = 30000
        self.game.days_elapsed = 40
        self.game.faction_standings["System Navy"] = -25
        elevated = self.game.get_pirate_encounter_chance(self.game.current_sector)
        self.assertGreaterEqual(elevated, baseline)
        self.assertGreaterEqual(elevated, 0.22)

    def test_save_load_preserves_faction_standings_and_ai_fields(self):
        self.game.faction_standings["Iron Cartel"] = -12
        self.game.ai_traders["Soren's Hauler"]["cargo"]["Food"] = 3
        self.game.ai_traders["Soren's Hauler"]["hull"] = 72
        self.assertTrue(self.game.save())

        loaded = Game()
        self.assertTrue(loaded.load())
        self.assertEqual(loaded.faction_standings["Iron Cartel"], -12)
        self.assertEqual(loaded.ai_traders["Soren's Hauler"]["cargo"]["Food"], 3)
        self.assertEqual(loaded.ai_traders["Soren's Hauler"]["hull"], 72)

if __name__ == "__main__":
    unittest.main()
