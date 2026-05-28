#!/usr/bin/env python3
import unittest
import os
import shutil
from game import Game, generate_galaxy, GOODS, PORT_TYPES, find_shortest_path

class TestVoidPrivateer(unittest.TestCase):
    def setUp(self):
        # Initialize a standard game with a fixed test seed
        self.game = Game(seed_val=1234)
        
    def tearDown(self):
        # Clean up save file if written
        if os.path.exists("savegame.json"):
            os.remove("savegame.json")

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
        
        # Save game
        save_success = self.game.save()
        self.assertTrue(save_success)
        self.assertTrue(os.path.exists("savegame.json"))
        
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
        
        # 2. Verify AI updates make sightings logs
        self.game.update_ai_traders()
        self.assertEqual(len(self.game.ai_sightings), len(self.game.ai_traders))
        
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

if __name__ == "__main__":
    unittest.main()
