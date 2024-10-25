import tkinter as tk
import random
from tkinter import messagebox

class Minesweeper:
    def __init__(self, root):
        self.root = root
        self.root.title("Minesweeper")
        self.hints_remaining = 3  # Hints allowed per game
        self.flags_remaining = 81  # Limit flags to 81 per game
        self.show_menu()

    def show_menu(self):
        """Display the starting menu with difficulty options."""
        for widget in self.root.winfo_children():
            widget.destroy()

        menu_frame = tk.Frame(self.root)
        menu_frame.pack(pady=50)

        tk.Label(menu_frame, text="Welcome to Minesweeper!", font=("Arial", 24)).pack(pady=10)
        tk.Label(menu_frame, text="Select Difficulty", font=("Arial", 18)).pack(pady=5)

        tk.Button(menu_frame, text="Easy (9x9, 10 mines)", font=("Arial", 14),
                  command=lambda: self.start_game(9, 9, 10)).pack(pady=5)

        tk.Button(menu_frame, text="Medium (16x16, 40 mines)", font=("Arial", 14),
                  command=lambda: self.start_game(16, 16, 40)).pack(pady=5)

        tk.Button(menu_frame, text="Hard (16x30, 99 mines)", font=("Arial", 14),
                  command=lambda: self.start_game(16, 30, 99)).pack(pady=5)

    def start_game(self, rows, cols, mines):
        """Initialize the Minesweeper grid with the selected difficulty."""
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.hints_remaining = 3
        self.flags_remaining = 81  # Reset flags on new game
        self.reset_game()

    def reset_game(self):
        """Reset the game state for a new round."""
        self.grid = [[None] * self.cols for _ in range(self.rows)]
        self.buttons = [[None] * self.cols for _ in range(self.rows)]
        self.mine_locations = set()
        self.create_widgets()
        self.place_mines()
        self.calculate_neighbor_mines()

    def create_widgets(self):
        """Create the game grid, hint button, and flag counter."""
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack()

        for row in range(self.rows):
            for col in range(self.cols):
                btn = tk.Button(
                    frame, width=2, height=1, font=("Arial", 18),
                    command=lambda r=row, c=col: self.cell_clicked(r, c),
                    relief=tk.RAISED, bg="lightgray"
                )
                btn.bind("<Button-3>", lambda e, r=row, c=col: self.right_click(r, c))
                btn.grid(row=row, column=col)
                self.buttons[row][col] = btn

        controls_frame = tk.Frame(self.root)
        controls_frame.pack(pady=10)

        self.hint_label = tk.Label(controls_frame, text=f"Hints Remaining: {self.hints_remaining}", font=("Arial", 14))
        self.hint_label.pack(side=tk.LEFT, padx=5)

        self.flag_label = tk.Label(controls_frame, text=f"Flags Remaining: {self.flags_remaining}", font=("Arial", 14))
        self.flag_label.pack(side=tk.LEFT, padx=5)

        tk.Button(controls_frame, text="Use Hint", font=("Arial", 14), command=self.use_hint).pack(side=tk.RIGHT)

    def place_mines(self):
        """Place mines randomly on the board."""
        while len(self.mine_locations) < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if (row, col) not in self.mine_locations:
                self.mine_locations.add((row, col))
                self.grid[row][col] = "M"

    def calculate_neighbor_mines(self):
        """Calculate the number of mines adjacent to each cell."""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] != "M":
                    self.grid[row][col] = self.count_mines_around(row, col)

    def count_mines_around(self, row, col):
        """Count the number of mines surrounding the given cell."""
        count = 0
        for r in range(max(0, row - 1), min(self.rows, row + 2)):
            for c in range(max(0, col - 1), min(self.cols, col + 2)):
                if (r, c) in self.mine_locations:
                    count += 1
        return count

    def cell_clicked(self, row, col):
        """Handle a left-click on a cell."""
        if (row, col) in self.mine_locations:
            self.buttons[row][col].config(text="💣", bg="red")
            self.reveal_all_cells()
            self.show_end_game_popup(win=False)
        else:
            self.reveal_cell(row, col)
            if self.check_win():
                self.show_end_game_popup(win=True)

    def right_click(self, row, col):
        """Handle a right-click to place or remove a flag."""
        btn = self.buttons[row][col]
        if btn["text"] == "" and self.flags_remaining > 0:
            btn.config(text="🚩", fg="red")
            self.flags_remaining -= 1
        elif btn["text"] == "🚩":
            btn.config(text="")
            self.flags_remaining += 1
        self.flag_label.config(text=f"Flags Remaining: {self.flags_remaining}")

    def reveal_cell(self, row, col):
        """Reveal the content of a cell."""
        if self.buttons[row][col]["state"] == tk.DISABLED:
            return

        self.buttons[row][col].config(
            text=str(self.grid[row][col]) if self.grid[row][col] > 0 else "",
            relief=tk.SUNKEN, bg="white", state=tk.DISABLED
        )

        if self.grid[row][col] == 0:
            for r in range(max(0, row - 1), min(self.rows, row + 2)):
                for c in range(max(0, col - 1), min(self.cols, col + 2)):
                    if (r, c) != (row, col):
                        self.reveal_cell(r, c)

    def use_hint(self):
        """Use a hint to reveal a cell containing a mine."""
        if self.hints_remaining <= 0:
            messagebox.showinfo("No Hints", "No more hints available!")
            return

        hint_cells = [(r, c) for r, c in self.mine_locations if self.buttons[r][c]["text"] == ""]
        if hint_cells:
            row, col = random.choice(hint_cells)
            self.buttons[row][col].config(text="💣", fg="blue", bg="yellow")
            self.hints_remaining -= 1
            self.hint_label.config(text=f"Hints Remaining: {self.hints_remaining}")

    def reveal_all_cells(self):
        """Reveal the entire grid when the game is lost."""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == "M":
                    self.buttons[row][col].config(text="💣", bg="red")
                else:
                    self.buttons[row][col].config(
                        text=str(self.grid[row][col]) if self.grid[row][col] > 0 else "",
                        relief=tk.SUNKEN, bg="white"
                    )
                self.buttons[row][col].config(state=tk.DISABLED)

    def check_win(self):
        """Check if the player has won by revealing all non-mine cells."""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] != "M" and self.buttons[row][col]["state"] != tk.DISABLED:
                    return False
        return True

    def show_end_game_popup(self, win):
        """Show a popup window with options to restart or quit."""
        message = "Congratulations! You win!" if win else "Boom! You hit a mine."
        result = messagebox.askquestion("Game Over", f"{message}\nDo you want to play again?")

        if result == "yes":
            self.show_menu()
        else:
            self.root.quit()

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = Minesweeper(root)
    root.mainloop()
