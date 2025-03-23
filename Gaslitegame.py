import sqlite3
import numpy as np
import os
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Line, Color, Ellipse, Rectangle
from kivy.clock import Clock
import secrets
import json

class GaslightTokenWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # SQLite setup
        self.setup_database()
        # Game state
        self.real_target = secrets.randbelow(601) + 300
        self.fake_target = self.real_target + secrets.randbelow(201) - 100
        self.player_power = 0
        self.tokens = []
        self.token_price = 100
        self.holding = False
        self.hold_time = 0
        self.temperature = 30
        self.max_temperature = 70
        self.wallet = 1000
        self.level = 1
        self.load_tokens()
        self.update_display()

    def setup_database(self):
        self.conn = sqlite3.connect("tokens.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sigma_x REAL,
                sigma_y REAL,
                sigma_z REAL,
                rare INTEGER,
                level INTEGER,
                metadata TEXT
            )
        ''')
        self.conn.commit()

    def start_action(self):
        if not self.holding:
            self.holding = True
            self.hold_time = 0
            Clock.schedule_interval(self.charge_up, 0.05)

    def stop_action(self):
        if not self.holding:
            return None
        self.holding = False
        Clock.unschedule(self.charge_up)
        real_diff = abs(self.real_target - self.player_power)
        if real_diff < 150:
            self.mint_token(real_diff)
            self.save_tokens()
        else:
            print("Missed target! No token minted.")
        self.reset_round()
        return f"Hold: {self.hold_time:.2f}s, Diff: {real_diff}"

    def charge_up(self, dt):
        self.hold_time += dt
        self.player_power = min(1000, self.player_power + secrets.randbelow(21) + 10)
        self.temperature = min(self.max_temperature, self.temperature + secrets.randbelow(5) / 10 + 0.1)
        if self.temperature >= self.max_temperature:
            self.token_price -= 10
            self.stop_action()
        self.update_display()

    def mint_token(self, real_diff):
        entropy_seed = os.urandom(16)
        seed_value = int.from_bytes(entropy_seed, 'big') % (2**32)
        sigma_matrix = np.random.RandomState(seed=seed_value).rand(3, 3)
        eigenvalues = np.linalg.eigvals(sigma_matrix)
        sigma_x, sigma_y, sigma_z = [float(val.real) for val in eigenvalues.round(2)]  # Ensure real numbers
        rare = real_diff < 10
        metadata = {"sigma_x": sigma_x, "sigma_y": sigma_y, "sigma_z": sigma_z, "rare": rare, "level": self.level}
        token = {"sigma_x": sigma_x, "sigma_y": sigma_y, "sigma_z": sigma_z, "metadata": metadata}
        self.tokens.append(token)
        if rare:
            print("Legendary token minted!")
        self.token_price += secrets.randbelow(6)
        # Save to SQLite
        self.cursor.execute('''
            INSERT INTO tokens (sigma_x, sigma_y, sigma_z, rare, level, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (sigma_x, sigma_y, sigma_z, int(rare), self.level, json.dumps(metadata)))
        self.conn.commit()

    def buy_token(self):
        if self.wallet >= self.token_price and len(self.tokens) < 5:
            self.mint_token(150)  # Simulate a purchased token with max diff
            self.wallet -= self.token_price
            self.token_price += secrets.randbelow(21) - 10
            self.save_tokens()

    def sell_token(self):
        if self.tokens:
            token = self.tokens.pop(0)  # Sell oldest token
            self.wallet += self.token_price
            if secrets.randbelow(100) < 10:  # 10% surge chance
                price_raise = self.token_price * (secrets.randbelow(11) + 5) / 100
                self.token_price += int(price_raise)
                print(f"Price surged by {int(price_raise)}!")
            else:
                base_change = secrets.randbelow(21) - 10
                self.token_price += base_change
            self.token_price = max(10, self.token_price)
            self.save_tokens()

    def load_tokens(self):
        self.cursor.execute("SELECT sigma_x, sigma_y, sigma_z, rare, level, metadata FROM tokens")
        rows = self.cursor.fetchall()
        self.tokens = [
            {
                "sigma_x": row[0],
                "sigma_y": row[1],
                "sigma_z": row[2],
                "metadata": json.loads(row[5])
            } for row in rows
        ]

    def save_tokens(self):
        # JSON backup (optional, since SQLite is primary now)
        with open("tokens.json", "w") as f:
            json.dump(self.tokens, f)

    def reset_round(self):
        self.player_power = 0
        self.temperature = 30
        self.real_target = secrets.randbelow(601) + 300
        self.fake_target = self.real_target + secrets.randbelow(201) - 100
        if len(self.tokens) % 5 == 0 and self.tokens:
            self.level += 1
            self.real_target = max(300, self.real_target - 50)  # Difficulty increase
        self.update_display()

    def update_display(self):
        self.canvas.clear()
        with self.canvas:
            Color(1, 0, 0, 0.2)
            Rectangle(pos=(self.fake_target - 50, 100), size=(100, 600))
            Color(1, 0, 0, 1)
            Line(points=[self.fake_target, 100, self.fake_target, 700], width=2)
            Color(0, 0, 1, 1)
            power_height = 100 + (self.player_power / 1000) * 600
            Ellipse(pos=(self.fake_target - 15, power_height), size=(30, 30))
            temp_ratio = (self.temperature - 30) / (self.max_temperature - 30)
            Color(temp_ratio, 1 - temp_ratio, 0, 1)
            Line(points=[50, 50, 50 + (self.temperature - 30) * 5, 50], width=5)

class GaslightTokenApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.game = GaslightTokenWidget()
        layout.add_widget(self.game)
        button_box = BoxLayout(size_hint=(1, 0.2))
        charge_btn = Button(text="Charge", on_press=lambda x: self.game.start_action())
        release_btn = Button(text="Release", on_press=lambda x: self.show_results())
        buy_btn = Button(text="Buy", on_press=lambda x: self.game.buy_token())
        sell_btn = Button(text="Sell", on_press=lambda x: self.game.sell_token())
        for btn in (charge_btn, release_btn, buy_btn, sell_btn):
            button_box.add_widget(btn)
        layout.add_widget(button_box)
        self.feedback_label = Label(text="Wallet: 1000 | Price: 100 | Level: 1")
        layout.add_widget(self.feedback_label)
        Clock.schedule_interval(self.update_ui, 0.5)
        return layout

    def show_results(self):
        result = self.game.stop_action()
        if result:
            self.feedback_label.text = f"Results: {result}"

    def update_ui(self, dt):
        self.feedback_label.text = (
            f"Wallet: {self.game.wallet} | Price: {self.game.token_price} | "
            f"Power: {self.game.player_power}W | Temp: {self.game.temperature:.1f}°C | Level: {self.game.level}"
        )

    def on_stop(self):
        if hasattr(self.game, 'conn'):
            self.game.conn.close()

if __name__ == "__main__":
    GaslightTokenApp().run()
