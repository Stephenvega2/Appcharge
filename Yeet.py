import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Line, Color, Ellipse
from kivy.clock import Clock
import secrets
import math

kivy.require('2.0.0')

MEME_FEEDBACK = {
    'great': ["Absolute chad energy—nailed it!", "Big brain move, chaos mastered!"],
    'good': ["Solid vibes, not too shabby!", "Kinda based, entropy’s friend!"],
    'bad': ["Total chaos, yeeted into the void!", "Mega oof, disorder wins!"],
    'overheat': ["Toasty vibes, it’s imploding!", "Spicy fail, too hot to handle!"],
    'level_up': ["Level up! You’re a chaos god!", "Dank ascension, keep it rollin’!"],
    'win': ["YOU WON! Chaos king crowned!", "Entropy bows to your dankness!"],
    'dank_spike': ["Dank spike—power’s lit!", "Dank spike—temp’s roasted!"]
}

DANK_SOUNDBITES = ["*boop*", "*yeet*", "*bruh*", "*womp*", "*vibes*"]

class ChargingGameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target = secrets.randbelow(601) + 300
        self.player_power = 0
        self.score = 0
        self.temperature = 30
        self.holding = False
        self.hold_time = 0
        self.chaos_factor = self.calculate_chaos()
        self.target_jitter = 0
        self.level = 1
        self.level_targets = [100, 250, 500, 750, 1000]
        Clock.schedule_interval(self.cool_down, 1)
        self.update_display()

    def calculate_chaos(self):
        a, b = secrets.randbelow(10) + 1, secrets.randbelow(10) + 1
        c, d = secrets.randbelow(10) + 1, secrets.randbelow(10) + 1
        trace = a + d
        det = a * d - b * c
        discriminant = trace**2 - 4 * det
        if discriminant < 0:
            return 1.0
        eig1 = (trace + math.sqrt(discriminant)) / 2
        return max(0.5, min(2.0, eig1 / 5))

    def start_action(self):
        self.holding = True
        self.hold_time = 0
        self.chaos_factor = self.calculate_chaos()
        Clock.schedule_interval(self.charge_up, 0.05)

    def stop_action(self):
        self.holding = False
        Clock.unschedule(self.charge_up)
        diff = abs(self.target - self.player_power)
        chaos_boost = secrets.randbelow(21) - 10

        if hasattr(self, 'dank_spike'):
            meme = self.dank_spike
            del self.dank_spike
        elif self.temperature > 50:
            self.score = max(0, self.score - 10 - chaos_boost)
            meme = secrets.choice(MEME_FEEDBACK['overheat'])
        elif diff < 50:
            self.score += int((100 - diff) * self.chaos_factor) + chaos_boost
            meme = secrets.choice(MEME_FEEDBACK['great'])
        elif diff < 100:
            self.score += int((50 - diff // 2) * self.chaos_factor) + chaos_boost
            meme = secrets.choice(MEME_FEEDBACK['good'])
        else:
            self.score = max(0, self.score - 5 - chaos_boost)
            meme = secrets.choice(MEME_FEEDBACK['bad'])

        if self.level <= 5 and self.score >= self.level_targets[self.level - 1]:
            if self.level == 5:
                meme = secrets.choice(MEME_FEEDBACK['win'])
                self.score = 1000
            else:
                self.level += 1
                meme = secrets.choice(MEME_FEEDBACK['level_up'])

        self.player_power = 0
        self.temperature = max(30, self.temperature - 5)
        self.target = secrets.randbelow(601) + 300
        self.target_jitter = 0
        self.update_display()
        soundbite = secrets.choice(DANK_SOUNDBITES)
        return f"Hold: {self.hold_time:.2f}s | Diff: {diff} | Chaos: {self.chaos_factor:.2f} | {meme} {soundbite}"

    def charge_up(self, dt):
        self.hold_time += dt
        self.player_power = min(1000, self.player_power + secrets.randbelow(26) + 5)
        self.temperature += secrets.randbelow(29) / 100 + 0.02
        if secrets.randbelow(100) < 10:  # 10% chance for dank spike
            if secrets.randbelow(2) == 0:  # 50/50 power or temp
                self.player_power = min(1000, self.player_power * 2)
                self.dank_spike = MEME_FEEDBACK['dank_spike'][0]
            else:
                self.temperature = min(100, self.temperature * 2)
                self.dank_spike = MEME_FEEDBACK['dank_spike'][1]
        self.target_jitter = secrets.randbelow(21) - 10
        self.update_display()

    def cool_down(self, dt):
        if not self.holding:
            self.temperature = max(30, self.temperature - 0.5)
            self.update_display()

    def update_display(self):
        self.canvas.clear()
        with self.canvas:
            Color(1, 0, 0, 1)
            jittered_target = self.target + self.target_jitter
            self.target_line = Line(points=[jittered_target, 100, jittered_target, 700], width=2)
            Color(0, 0, 1, 1)
            power_height = 100 + (self.player_power / 1000) * 600 * self.chaos_factor
            self.power_dot = Ellipse(pos=(100 + secrets.randbelow(11) - 5, power_height), size=(30, 30))
            Color(1 if self.temperature > 50 else 0, 1 if self.temperature < 50 else 0, 0, 1)
            self.temperature_bar = Line(points=[50, 50, 50 + self.temperature * 5, 50], width=5)

class ChargingGameApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.game = ChargingGameWidget()
        layout.add_widget(self.game)

        button_box = BoxLayout(size_hint=(1, 0.2))
        start_btn = Button(text="Yeet the Juice", on_press=lambda x: self.game.start_action())
        stop_btn = Button(text="Drop the Dank", on_press=lambda x: self.show_results())
        button_box.add_widget(start_btn)
        button_box.add_widget(stop_btn)
        layout.add_widget(button_box)

        self.instruction_label = Label(text="Yeet juice to the shaky red line! Beat 5 levels, don’t overheat!")
        layout.add_widget(self.instruction_label)
        self.feedback_label = Label(text="Score: 0 | Level: 1 | Dankness awaits!")
        layout.add_widget(self.feedback_label)

        Clock.schedule_interval(self.update_score, 1)
        return layout

    def show_results(self):
        results = self.game.stop_action()
        self.feedback_label.text = f"Score: {self.game.score} | Level: {self.game.level} | {results}"

    def update_score(self, dt):
        target = self.game.level_targets[self.game.level - 1] if self.game.level <= 5 else "WON!"
        self.feedback_label.text = f"Score: {self.game.score} | Level: {self.game.level} | Target: {target}"

if __name__ == "__main__":
    ChargingGameApp().run()
