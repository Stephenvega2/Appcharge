from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Line, Color, Ellipse, Rectangle
from kivy.clock import Clock
import secrets
import json
import psutil


class GaslightTokenWidget(Widget):
    """Widget for gaslight token game with battery integration and pricing."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
        self.load_tokens()
        self.update_display()

    def start_action(self):
        """Begin charging."""
        if not self.holding:
            self.holding = True
            self.hold_time = 0
            Clock.schedule_interval(self.charge_up, 0.05)

    def stop_action(self):
        """End charging, potentially mint and save token."""
        if not self.holding:
            return None
        self.holding = False
        Clock.unschedule(self.charge_up)
        real_diff = abs(self.real_target - self.player_power)
        if real_diff < 150:
            self.mint_token()
            self.save_tokens()
        self.reset_round()
        return f"Hold: {self.hold_time:.2f}s, Diff: {real_diff}"

    def charge_up(self, dt):
        """Simulate charging with battery data if accessible."""
        self.hold_time += dt
        try:
            battery = psutil.sensors_battery()
            if battery:
                self.player_power = min(1000, battery.percent * 10)  # Battery % scaled to 0-1000
                self.temperature = min(self.max_temperature, battery.power_plugged * 40 + 30)  # Temp from charge state
            else:
                self.player_power = min(1000, self.player_power + secrets.randbelow(21) + 10)
                self.temperature = min(self.max_temperature, self.temperature + secrets.randbelow(5) / 10 + 0.1)
        except (PermissionError, AttributeError):  # Handle permission denied or other psutil errors
            self.player_power = min(1000, self.player_power + secrets.randbelow(21) + 10)
            self.temperature = min(self.max_temperature, self.temperature + secrets.randbelow(5) / 10 + 0.1)
        if self.temperature >= self.max_temperature:
            self.token_price -= 10
            self.stop_action()
        self.update_display()

    def mint_token(self):
        """Mint a token and adjust price."""
        sigma_x = secrets.randbelow(101)
        sigma_y = secrets.randbelow(101)
        sigma_z = secrets.randbelow(101)
        remnant = secrets.randbelow(11) + 5
        preeminent = (sigma_x + sigma_y + sigma_z) / 3
        token = {"sigma_x": sigma_x, "sigma_y": sigma_y, "sigma_z": sigma_z, "remnant": remnant, "preeminent": preeminent}
        self.tokens.append(token)
        self.token_price += secrets.randbelow(6)

    def burn_token(self):
        """Burn oldest token."""
        if self.tokens:
            self.tokens.pop(0)
            self.save_tokens()

    def buy_token(self):
        """Buy a token at current price."""
        if self.wallet >= self.token_price and len(self.tokens) < 5:
            self.mint_token()
            self.wallet -= self.token_price
            self.token_price += secrets.randbelow(21) - 10
            self.save_tokens()

    def sell_token(self):
        """Sell a token with a chance of price surge."""
        if self.tokens:
            token = self.tokens.pop()
            self.wallet += self.token_price
            if secrets.randbelow(100) < 10:  # 10% chance
                price_raise = self.token_price * (secrets.randbelow(11) + 5) / 100  # 5-15%
                self.token_price += int(price_raise)
                print(f"Price surged by {int(price_raise)}!")
            else:
                base_change = secrets.randbelow(21) - 10 - int(token["preeminent"] / 10)
                self.token_price += base_change
            self.token_price = max(10, self.token_price)
            self.save_tokens()

    def save_tokens(self):
        """Persist tokens to file."""
        with open("tokens.json", "w") as f:
            json.dump(self.tokens, f)

    def load_tokens(self):
        """Load tokens from file."""
        try:
            with open("tokens.json", "r") as f:
                self.tokens = json.load(f)
        except FileNotFoundError:
            self.tokens = []

    def reset_round(self):
        """Reset charging state."""
        self.player_power = 0
        self.temperature = 30
        self.real_target = secrets.randbelow(601) + 300
        self.fake_target = self.real_target + secrets.randbelow(201) - 100
        self.update_display()

    def update_display(self):
        """Render game visuals."""
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
    """Appcharge-compatible gaslight token game with market."""
    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.game = GaslightTokenWidget()
        self.game.load_tokens()  # Load tokens on start
        layout.add_widget(self.game)

        button_box = BoxLayout(size_hint=(1, 0.2))
        charge_btn = Button(text="Charge", on_press=lambda x: self.game.start_action())
        release_btn = Button(text="Release", on_press=lambda x: self.show_results())
        buy_btn = Button(text="Buy", on_press=lambda x: self.game.buy_token())
        sell_btn = Button(text="Sell", on_press=lambda x: self.game.sell_token())
        for btn in (charge_btn, release_btn, buy_btn, sell_btn):
            button_box.add_widget(btn)
        layout.add_widget(button_box)

        self.token_display = BoxLayout(size_hint=(1, 0.3), orientation='vertical')
        layout.add_widget(self.token_display)

        self.instruction_label = Label(text="Charge to mint Gaslight Tokens! Buy/Sell in the market.")
        layout.add_widget(self.instruction_label)
        self.feedback_label = Label(text="Wallet: 1000 | Price: 100")
        layout.add_widget(self.feedback_label)

        Clock.schedule_interval(self.update_ui, 0.5)
        return layout

    def show_results(self):
        """Display charging results."""
        result = self.game.stop_action()
        if result:
            self.feedback_label.text = f"Results: {result}"

    def update_ui(self, dt):
        """Update token display and market info."""
        self.token_display.clear_widgets()
        token_canvas = BoxLayout(size_hint=(1, 1))
        with token_canvas.canvas:
            for i, token in enumerate(self.game.tokens):
                Color(0.2 + i * 0.1, 0.6, 0.8, 1)
                Ellipse(pos=(50 + i * 60, 10), size=(50, 50))
                Label(text=f"{token['preeminent']:.1f}", pos=(50 + i * 60, 10))
        self.token_display.add_widget(token_canvas)
        self.feedback_label.text = (
            f"Wallet: {self.game.wallet} | Price: {self.game.token_price} | "
            f"Power: {self.game.player_power}W | Temp: {self.game.temperature:.1f}°C"
        )


if __name__ == "__main__":
    GaslightTokenApp().run()
