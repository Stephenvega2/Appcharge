import pygame
import secrets
import random  # Added for uniform
import math
import time
import psutil
import os
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 800
BOT_COUNT = 10  # Number of bots
BOT_WIDTH = WIDTH // 5
BOT_HEIGHT = HEIGHT // (BOT_COUNT // 2 + 1)
FPS = 60
LEARNING_RATE = 0.1  # How quickly bots adapt to top performers
RANDOMNESS = 0.2  # Random variation in bot decisions

# Colors
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)  # For highlighting top bot

# Game feedback
MEME_FEEDBACK = {
    'great': ["Chad energy!", "Big brain!"],
    'good': ["Solid vibes!", "Kinda based!"],
    'bad': ["Total chaos!", "Mega oof!"],
    'overheat': ["Toasty!", "Spicy fail!"],
    'level_up': ["Chaos god!", "Dank ascension!"],
    'win': ["Chaos king!", "Entropy bows!"],
    'dank_spike': ["Dank power!", "Temp roasted!"]
}

DANK_SOUNDBITES = ["*boop*", "*yeet*", "*bruh*", "*womp*", "*vibes*"]

# Fonts
FONT = pygame.font.SysFont("comicsans", 18)
SMALL_FONT = pygame.font.SysFont("comicsans", 14)

# Bot logic class
class Bot:
    def __init__(self, bot_id, all_bots):
        self.id = bot_id
        self.all_bots = all_bots  # Reference to all bots for competition
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
        self.feedback = f"Bot {bot_id} ready!"
        self.action_timer = 0
        self.next_action = random.uniform(0.5, 2.0)  # Changed to random.uniform
        self.hold_duration = random.uniform(0.5, 2.0)  # Changed to random.uniform
        self.games_played = 0
        self.total_diff = 0
        self.avg_diff = 0
        self.skill_level = 1.0  # Multiplier for how accurately bot aims for target
        self.competitive_feedback = ""

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

    def stop_action(self):
        self.holding = False
        diff = abs(self.target - self.player_power)
        self.total_diff += diff
        self.games_played += 1
        self.avg_diff = self.total_diff / self.games_played if self.games_played > 0 else 0
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
        soundbite = secrets.choice(DANK_SOUNDBITES)
        self.feedback = f"Diff: {diff} | {meme} {soundbite}"
        self.update_competitive_feedback()

    def charge_up(self, dt):
        self.hold_time += dt
        self.player_power = min(1000, self.player_power + secrets.randbelow(26) + 5)
        self.temperature += secrets.randbelow(29) / 100 + 0.02
        if secrets.randbelow(100) < 10:
            if secrets.randbelow(2) == 0:
                self.player_power = min(1000, self.player_power * 2)
                self.dank_spike = MEME_FEEDBACK['dank_spike'][0]
            else:
                self.temperature = min(100, self.temperature * 2)
                self.dank_spike = MEME_FEEDBACK['dank_spike'][1]
        self.target_jitter = secrets.randbelow(21) - 10

    def cool_down(self, dt):
        if not self.holding:
            self.temperature = max(30, self.temperature - 0.5)

    def estimate_hold_duration(self):
        # Estimate time to hit target based on skill and average charge rate
        avg_charge_rate = 15  # Approx (5 to 30 per 0.05s)
        base_duration = (self.target / avg_charge_rate) * 0.05 / self.chaos_factor
        noise = random.uniform(-RANDOMNESS, RANDOMNESS) / self.skill_level  # Changed to random.uniform
        return max(0.1, base_duration * (1 + noise))

    def update_competitive_feedback(self):
        # Compare with other bots
        top_bot = max(self.all_bots, key=lambda b: b.score, default=self)
        avg_score = sum(b.score for b in self.all_bots) / len(self.all_bots)
        if self is top_bot:
            self.competitive_feedback = "Top Dog!"
        elif self.score > avg_score:
            self.competitive_feedback = f"Above avg! Top: {top_bot.score}"
        else:
            self.competitive_feedback = f"Behind! Top: {top_bot.score}"

        # Learn from top bot if not the best
        if self is not top_bot and self.games_played > 0:
            top_avg_diff = top_bot.avg_diff
            if top_avg_diff < self.avg_diff:
                # Improve skill by reducing randomness
                self.skill_level += LEARNING_RATE * (1 / (1 + top_avg_diff / (self.avg_diff + 1)))
                self.skill_level = min(2.0, self.skill_level)  # Cap skill level

    def update(self, dt):
        self.action_timer += dt
        if self.holding:
            self.charge_up(dt)
            if self.hold_time >= self.hold_duration:
                self.stop_action()
                self.action_timer = 0
                self.next_action = random.uniform(0.5, 2.0)  # Changed to random.uniform
                self.hold_duration = self.estimate_hold_duration()
        else:
            self.cool_down(dt)
            if self.action_timer >= self.next_action:
                self.start_action()
                self.action_timer = 0
                self.hold_duration = self.estimate_hold_duration()

# Main stress test class
class StressTest:
    def __init__(self):
        try:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("Competitive Charging Game Stress Test")
            self.clock = pygame.time.Clock()
            self.bots = [Bot(i, None) for i in range(BOT_COUNT)]
            for bot in self.bots:
                bot.all_bots = self.bots  # Set reference to all bots
            self.fps_history = deque(maxlen=100)
            self.process = psutil.Process(os.getpid())
            self.start_time = time.time()
        except Exception as e:
            print(f"Initialization error: {e}")
            pygame.quit()
            raise

    def draw_bot(self, bot, index):
        row = index // 5
        col = index % 5
        x_offset = col * BOT_WIDTH
        y_offset = row * BOT_HEIGHT

        # Highlight top bot
        is_top = bot is max(self.bots, key=lambda b: b.score, default=bot)
        border_color = GOLD if is_top else BLACK
        pygame.draw.rect(self.screen, border_color, (x_offset, y_offset, BOT_WIDTH, BOT_HEIGHT), 2)

        # Scale coordinates
        scale_x = BOT_WIDTH / 1000
        scale_y = BOT_HEIGHT / 800

        # Draw target line
        jittered_target = bot.target + bot.target_jitter
        target_x = x_offset + jittered_target * scale_x
        pygame.draw.line(self.screen, RED, (target_x, y_offset), (target_x, y_offset + BOT_HEIGHT), 2)

        # Draw power dot
        power_height = (bot.player_power / 1000) * BOT_HEIGHT * bot.chaos_factor
        power_x = x_offset + (100 + secrets.randbelow(11) - 5) * scale_x
        power_y = y_offset + power_height
        pygame.draw.circle(self.screen, BLUE, (power_x, power_y), 5)

        # Draw temperature bar
        temp_color = RED if bot.temperature > 50 else GREEN
        temp_width = bot.temperature * 2 * scale_x
        pygame.draw.line(self.screen, temp_color, (x_offset + 10, y_offset + 20),
                         (x_offset + 10 + temp_width, y_offset + 20), 3)

        # Draw text
        score_text = FONT.render(f"Bot {bot.id} | Score: {bot.score}", True, WHITE)
        level_text = FONT.render(f"Level: {bot.level} | Skill: {bot.skill_level:.2f}", True, WHITE)
        feedback_text = SMALL_FONT.render(bot.feedback, True, YELLOW)
        comp_text = SMALL_FONT.render(bot.competitive_feedback, True, GOLD if is_top else RED)
        self.screen.blit(score_text, (x_offset + 10, y_offset + 40))
        self.screen.blit(level_text, (x_offset + 10, y_offset + 60))
        self.screen.blit(feedback_text, (x_offset + 10, y_offset + 80))
        self.screen.blit(comp_text, (x_offset + 10, y_offset + 100))

    def run(self):
        running = True
        while running:
            try:
                dt = self.clock.tick(FPS) / 1000.0
                self.fps_history.append(self.clock.get_fps())

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False

                # Update all bots
                for bot in self.bots:
                    bot.update(dt)

                # Draw
                self.screen.fill(BLACK)
                for i, bot in enumerate(self.bots):
                    self.draw_bot(bot, i)

                # Draw performance metrics and leaderboard
                avg_fps = sum(self.fps_history) / len(self.fps_history) if self.fps_history else 0
                memory = self.process.memory_info().rss / 1024 / 1024
                perf_text = FONT.render(f"FPS: {avg_fps:.1f} | Memory: {memory:.1f} MB | Bots: {BOT_COUNT}", True, WHITE)
                self.screen.blit(perf_text, (10, HEIGHT - 50))

                # Draw leaderboard (top 3 bots)
                sorted_bots = sorted(self.bots, key=lambda b: b.score, reverse=True)[:3]
                for i, bot in enumerate(sorted_bots):
                    leader_text = SMALL_FONT.render(f"#{i+1}: Bot {bot.id} ({bot.score})", True, GOLD)
                    self.screen.blit(leader_text, (WIDTH - 150, 10 + i * 20))

                pygame.display.flip()

            except Exception as e:
                print(f"Runtime error: {e}")
                running = False

        # Print final stats
        try:
            total_games = sum(bot.games_played for bot in self.bots)
            avg_diff = sum(bot.total_diff for bot in self.bots) / total_games if total_games > 0 else 0
            sorted_bots = sorted(self.bots, key=lambda b: b.score, reverse=True)
            print(f"Stress Test Summary:")
            print(f"Total Games Played: {total_games}")
            print(f"Average Difference: {avg_diff:.2f}")
            print(f"Average FPS: {avg_fps:.1f}")
            print(f"Final Memory Usage: {memory:.1f} MB")
            print("\nFinal Leaderboard:")
            for i, bot in enumerate(sorted_bots[:3], 1):
                print(f"#{i}: Bot {bot.id} | Score: {bot.score} | Avg Diff: {bot.avg_diff:.2f} | Skill: {bot.skill_level:.2f}")
        except Exception as e:
            print(f"Error in final stats: {e}")
        finally:
            pygame.quit()

if __name__ == "__main__":
    try:
        StressTest().run()
    except Exception as e:
        print(f"Main execution error: {e}")
