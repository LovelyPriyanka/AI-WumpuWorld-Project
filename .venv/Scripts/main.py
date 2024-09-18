import tkinter as tk
import random
import pygame

class WumpusWorld:
    def __init__(self, size=4):  # Corrected __init__ method
        self.size = size
        self.grid = [['' for _ in range(size)] for _ in range(size)]
        self.revealed = [[False for _ in range(size)] for _ in range(size)]  # Track revealed cells
        self.player_pos = [0, 0]
        self.wumpus_pos = [random.randint(0, size - 1), random.randint(0, size - 1)]
        self.gold_pos = [random.randint(0, size - 1), random.randint(0, size - 1)]
        self.pits = []
        for _ in range(size - 1):
            pit_pos = [random.randint(0, size - 1), random.randint(0, size - 1)]
            if pit_pos != self.player_pos and pit_pos != self.wumpus_pos and pit_pos != self.gold_pos:
                self.pits.append(pit_pos)
        self.stench_pos = self._get_adjacent(self.wumpus_pos)
        self.breeze_pos = []
        for pit in self.pits:
            self.breeze_pos.extend(self._get_adjacent(pit))
        self.move_count = 0  # Initialize move counter

        self.revealed[0][0] = True  # Reveal the starting position

    def _get_adjacent(self, pos):
        adjacent = []
        if pos[0] > 0:
            adjacent.append([pos[0] - 1, pos[1]])
        if pos[0] < self.size - 1:
            adjacent.append([pos[0] + 1, pos[1]])
        if pos[1] > 0:
            adjacent.append([pos[0], pos[1] - 1])
        if pos[1] < self.size - 1:
            adjacent.append([pos[0], pos[1] + 1])
        return adjacent

    def move_player(self, direction):
        if direction == 'up' and self.player_pos[0] > 0:
            self.player_pos[0] -= 1
        elif direction == 'down' and self.player_pos[0] < self.size - 1:
            self.player_pos[0] += 1
        elif direction == 'left' and self.player_pos[1] > 0:
            self.player_pos[1] -= 1
        elif direction == 'right' and self.player_pos[1] < self.size - 1:
            self.player_pos[1] += 1
        self.move_count += 1  # Increment move counter
        self.revealed[self.player_pos[0]][self.player_pos[1]] = True  # Reveal the new position
        return self.check_status()

    def check_status(self):
        if self.player_pos == self.wumpus_pos:
            return "You've been eaten by the Wumpus!"
        elif self.player_pos in self.pits:
            return "You've fallen into a pit!"
        elif self.player_pos == self.gold_pos:
            return "Congratulations! You've found the gold!"
        else:
            warnings = []
            if self.player_pos in self.stench_pos:
                warnings.append("You smell a stench, an adjacent room has a Wumpus.")
            if self.player_pos in self.breeze_pos:
                warnings.append("You feel a breeze, an adjacent room has a pit.")
            if warnings:
                return " ".join(warnings)
            return "You are safe for now."


class WumpusWorldGUI:
    def __init__(self, root, world):  # Corrected __init__ method
        pygame.init()  # Initialize pygame for sound
        self.load_sounds()  # Load sounds
        self.buttons = None
        self.info_label = None
        self.grid_frame = None
        self.root = root
        self.world = world
        self.move_count_label = None  # Label to display move count
        self.create_widgets()
        self.update_grid()

    def load_sounds(self):
        self.sound_move = pygame.mixer.Sound("sounds/move.wav")
        self.sound_wumpus = pygame.mixer.Sound("sounds/wumpus.wav")
        self.sound_pit = pygame.mixer.Sound("sounds/pit.wav")
        self.sound_gold = pygame.mixer.Sound("sounds/gold.wav")
        self.sound_warning = pygame.mixer.Sound("sounds/warning.wav")

    def create_widgets(self):
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack()

        self.buttons = [
            [tk.Button(self.grid_frame, width=10, height=5, font=("Helvetica", 16), command=lambda r=r, c=c: None)
             for c in range(self.world.size)] for r in range(self.world.size)]
        for r in range(self.world.size):
            for c in range(self.world.size):
                self.buttons[r][c].grid(row=r, column=c)

        self.info_label = tk.Label(self.root, text="Move using buttons or arrow keys", font=("Helvetica", 16))
        self.info_label.pack()

        self.move_count_label = tk.Label(self.root, text=f"Moves: {self.world.move_count}", font=("Helvetica", 16))
        self.move_count_label.pack()

        instructions = ("Instructions:\n"
                        "- Use arrow keys or buttons to move.\n"
                        "- Find the gold (G) to win.\n"
                        "- Avoid the Wumpus (W) and pits (O).\n"
                        "- Stench (S) indicates a nearby Wumpus.\n"
                        "- Breeze (B) indicates a nearby pit.")
        self.instructions_label = tk.Label(self.root, text=instructions, font=("Helvetica", 12), justify="left")
        self.instructions_label.pack()

        self.root.bind("<Up>", lambda event: self.move("up"))
        self.root.bind("<Down>", lambda event: self.move("down"))
        self.root.bind("<Left>", lambda event: self.move("left"))
        self.root.bind("<Right>", lambda event: self.move("right"))

    def update_grid(self):
        for r in range(self.world.size):
            for c in range(self.world.size):
                if not self.world.revealed[r][c]:  # Hide unrevealed cells
                    self.buttons[r][c].config(text="", bg="grey")
                elif [r, c] == self.world.player_pos:
                    self.buttons[r][c].config(text="You", bg="blue")
                elif [r, c] == self.world.wumpus_pos:
                    self.buttons[r][c].config(text="W", bg="red")
                elif [r, c] == self.world.gold_pos:
                    self.buttons[r][c].config(text="G", bg="yellow")
                elif [r, c] in self.world.pits:
                    self.buttons[r][c].config(text="O", bg="black")
                elif [r, c] in self.world.stench_pos:
                    self.buttons[r][c].config(text="S", bg="green")
                elif [r, c] in self.world.breeze_pos:
                    self.buttons[r][c].config(text="B", bg="light blue")
                else:
                    self.buttons[r][c].config(text="", bg="white")
        self.info_label.config(text="Move using buttons or arrow keys")
        self.move_count_label.config(text=f"Moves: {self.world.move_count}")

    def move(self, direction):
        result = self.world.move_player(direction)
        self.update_grid()
        self.play_sound(result)
        if result != "You are safe for now.":
            self.info_label.config(text=result)

    def play_sound(self, result):
        if result == "You've been eaten by the Wumpus!":
            self.sound_wumpus.play()
        elif result == "You've fallen into a pit!":
            self.sound_pit.play()
        elif result == "Congratulations! You've found the gold!":
            self.sound_gold.play()
        elif "stench" in result or "breeze" in result:
            self.sound_warning.play()
        else:
            self.sound_move.play()


def main():
    root = tk.Tk()
    root.title("Wumpus World")
    root.geometry("1200x1200")  # Set larger window size
    world = WumpusWorld()
    gui = WumpusWorldGUI(root, world)
    root.mainloop()


if __name__ == "__main__":  # Corrected name check
    main()
