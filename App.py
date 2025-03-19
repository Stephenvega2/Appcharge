from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Line, Color, Ellipse
from kivy.clock import Clock
import random


class ChargingGameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target = random.randint(300, 900)  # Target "charge level"
        self.player_power = 0  # Current charge simulation
        self.score = 0
        self.temperature = 30  # Simulated temperature
        self.holding = False
        self.hold_time = 0  # Time the button was held

        self.canvas.clear()
        with self.canvas:
            # Target visualization
            Color(1, 0, 0, 1)  # Red for target
            self.target_line = Line(points=[self.target, 100, self.target, 700], width=2)

            # Power level visualization
            Color(0, 0, 1, 1)  # Blue for player power
            self.power_dot = Ellipse(pos=(100, 100), size=(30, 30))

            # Temperature bar visualization
            Color(0, 1, 0, 1)  # Green for temperature
            self.temperature_bar = Line(points=[50, 50, 50 + self.temperature * 5, 50], width=5)

    def start_action(self):
        """Start holding."""
        self.holding = True
        self.hold_time = 0
        Clock.schedule_interval(self.charge_up, 0.05)

    def stop_action(self):
        """Stop holding and calculate results."""
        self.holding = False
        Clock.unschedule(self.charge_up)

        # Calculate score based on proximity to target
        diff = abs(self.target - self.player_power)
        self.score += max(0, 100 - diff)
        reward = "Reward!" if diff < 100 else "Penalty!"

        # Reset player power and temperature
        self.player_power = 0
        self.temperature = 30

        # Update display with results
        self.update_display()
        return f"Hold Time: {self.hold_time:.2f}s, Distance to Target: {diff}, {reward}"

    def charge_up(self, dt):
        """Increase power while holding, and simulate temperature rise."""
        self.hold_time += dt
        self.player_power = min(1000, self.player_power + random.randint(10, 30))
        self.temperature += random.uniform(0.1, 0.5)  # Simulate overheating
        self.update_display()

    def update_display(self):
        """Redraw game elements visually."""
        self.canvas.clear()
        with self.canvas:
            # Redraw target
            Color(1, 0, 0, 1)
            self.target_line = Line(points=[self.target, 100, self.target, 700], width=2)

            # Redraw player power dot (rises with power)
            Color(0, 0, 1, 1)
            power_height = 100 + (self.player_power / 1000) * 600
            self.power_dot = Ellipse(pos=(100, power_height), size=(30, 30))

            # Redraw temperature bar (indicates overheating)
            Color(0, 1, 0, 1 if self.temperature < 50 else 0)  # Turns red if overheating
            self.temperature_bar = Line(points=[50, 50, 50 + self.temperature * 5, 50], width=5)


class ChargingGameApp(App):
    """Main app integrating visual feedback and instructions."""
    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Game widget
        self.game = ChargingGameWidget()
        layout.add_widget(self.game)

        # Control buttons
        button_box = BoxLayout(size_hint=(1, 0.2))
        start_btn = Button(text="Hold", on_press=lambda x: self.game.start_action())
        stop_btn = Button(text="Release", on_press=lambda x: self.show_results())
        button_box.add_widget(start_btn)
        button_box.add_widget(stop_btn)
        layout.add_widget(button_box)

        # Instruction label
        self.instruction_label = Label(
            text="Instructions: Hold the button to charge power. Release to hit the target!"
        )
        layout.add_widget(self.instruction_label)

        # Score and feedback label
        self.feedback_label = Label(text="Score: 0")
        layout.add_widget(self.feedback_label)

        # Regular updates
        Clock.schedule_interval(self.update_score, 1)

        return layout

    def show_results(self):
        """Show results after releasing."""
        results = self.game.stop_action()
        self.feedback_label.text = f"Results: {results}"

    def update_score(self, dt):
        """Update the score and instructions."""
        self.feedback_label.text = f"Score: {self.game.score}"


if __name__ == "__main__":
    ChargingGameApp().run()
