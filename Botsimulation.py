import secrets
import numpy as np
import os
import sqlite3
import json
import time

def custom_encoder(obj):
    if isinstance(obj, np.complex128):
        return str(obj)
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

class Simulation:
    def __init__(self):
        self.tokens = []  # List of all tokens in circulation
        self.energy_levels = {}
        self.bots = []
        self.setup_database()

    def setup_database(self):
        """Set up SQLite database to store simulation data."""
        self.conn = sqlite3.connect("simulation.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner TEXT,
                energy_level REAL,
                rare INTEGER,
                metadata TEXT
            )
        ''')
        self.conn.commit()

    def create_bots(self, num_bots):
        """Initialize bots with unique behaviors."""
        for i in range(num_bots):
            behavior = secrets.choice(["casual", "aggressive", "strategic"])
            self.bots.append({"id": f"bot_{i}", "behavior": behavior, "tokens": []})

    def generate_token(self, bot_id, rare=False):
        """Generate a token with energy attributes."""
        entropy_seed = os.urandom(16)
        seed_value = int.from_bytes(entropy_seed, 'big') % (2**32)
        sigma_matrix = np.random.RandomState(seed=seed_value).rand(3, 3)
        eigenvalues = np.linalg.eigvals(sigma_matrix)
        sigma_x, sigma_y, sigma_z = eigenvalues.round(2)

        token = {
            "owner": bot_id,
            "energy_level": secrets.randbelow(90) + 10,  # random.uniform(10, 100)
            "rare": rare,
            "metadata": {
                "sigma_x": sigma_x,
                "sigma_y": sigma_y,
                "sigma_z": sigma_z
            }
        }

        self.cursor.execute('''
            INSERT INTO tokens (owner, energy_level, rare, metadata)
            VALUES (?, ?, ?, ?)
        ''', (bot_id, token["energy_level"], int(rare), json.dumps(token["metadata"], default=custom_encoder)))
        self.conn.commit()

        self.tokens.append(token)
        return token

    def bot_action(self, bot):
        """Simulate bot decision-making."""
        if bot["behavior"] == "casual":
            self.casual_action(bot)
        elif bot["behavior"] == "aggressive":
            self.aggressive_action(bot)
        elif bot["behavior"] == "strategic":
            self.strategic_action(bot)

    def casual_action(self, bot):
        """Action for casual bots."""
        if secrets.randbelow(100) < 50:
            token = self.generate_token(bot["id"])
            bot["tokens"].append(token)

    def aggressive_action(self, bot):
        """Action for aggressive bots."""
        if secrets.randbelow(100) < 70:
            token = self.generate_token(bot["id"], rare=secrets.randbelow(100) < 10)
            bot["tokens"].append(token)
        if secrets.randbelow(100) < 50 and bot["tokens"]:
            self.burn_token(bot)

    def strategic_action(self, bot):
        """Action for strategic bots."""
        if secrets.randbelow(100) < 30:
            token = self.generate_token(bot["id"], rare=secrets.randbelow(100) < 20)
            bot["tokens"].append(token)

    def burn_token(self, bot):
        """Simulate burning a token for a boost."""
        if bot["tokens"]:
            token = bot["tokens"].pop(0)
            print(f"{bot['id']} burned a token to boost energy!")
            boost = token["energy_level"] * 1.5
            print(f"Boost: +{boost:.2f} energy!")

    def get_ecosystem_stats(self):
        """Calculate and return current ecosystem statistics."""
        total_tokens = len(self.tokens)
        rare_tokens = sum(1 for t in self.tokens if t["rare"])
        avg_energy = self.calculate_avg_energy()
        bot_token_counts = self.calculate_bot_token_counts()
        behavior_counts = self.calculate_behavior_counts()
        return {
            "total_tokens": total_tokens,
            "rare_tokens": rare_tokens,
            "avg_energy": avg_energy,
            "bot_token_counts": bot_token_counts,
            "behavior_counts": behavior_counts
        }

    def calculate_avg_energy(self):
        """Calculate average energy of tokens."""
        return np.mean([t["energy_level"] for t in self.tokens]) if self.tokens else 0

    def calculate_bot_token_counts(self):
        """Calculate the number of tokens each bot has."""
        return {bot["id"]: len(bot["tokens"]) for bot in self.bots}

    def calculate_behavior_counts(self):
        """Calculate the distribution of bot behaviors."""
        return {
            "casual": len([b for b in self.bots if b["behavior"] == "casual"]),
            "aggressive": len([b for b in self.bots if b["behavior"] == "aggressive"]),
            "strategic": len([b for b in self.bots if b["behavior"] == "strategic"])
        }

    def print_ecosystem_status(self, round_num):
        """Print current ecosystem status."""
        stats = self.get_ecosystem_stats()
        print(f"\n=== Round {round_num} ===")
        print(f"Total Tokens in Circulation: {stats['total_tokens']}")
        print(f"Rare Tokens: {stats['rare_tokens']} ({stats['rare_tokens']/max(stats['total_tokens'], 1)*100:.1f}%)")
        print(f"Average Token Energy: {stats['avg_energy']:.2f}")
        print("\nBot Behavior Distribution:")
        for behavior, count in stats['behavior_counts'].items():
            print(f"  {behavior.capitalize()}: {count}")
        print("\nTokens per Bot:")
        for bot_id, count in stats['bot_token_counts'].items():
            print(f"  {bot_id}: {count} tokens")
        print("=" * 30)

    def run_simulation(self, rounds):
        """Run the simulation for a number of rounds with ecosystem monitoring."""
        for round_num in range(1, rounds + 1):
            for bot in self.bots:
                self.bot_action(bot)
            self.print_ecosystem_status(round_num)
            time.sleep(0.5)  # Add slight delay to make output readable

    def close(self):
        """Clean up database connection."""
        self.conn.close()

# Initialize and run the simulation
sim = Simulation()
sim.create_bots(10)  # Create 10 bots
sim.run_simulation(20)  # Simulate 20 rounds
sim.close()
