import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import json
import os

DATA_FILE = "data.json"

class BrainstormApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Brainstorm Tracker")
        self.root.configure(bg="#121212")
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")

        self.data = self.load_data()
        self.cell_buttons = {}

        # Title
        tk.Label(root, text="🧠 Brainstorm Tracker", font=("Segoe UI", 18, "bold"),
                 bg="#121212", fg="white").pack(pady=10)

        # Buttons
        btn_frame = tk.Frame(root, bg="#121212")
        btn_frame.pack(pady=5)
        self.make_modern_button(btn_frame, "➕ Add Thing", self.add_thing, "#1E88E5", "#1565C0").pack(side=tk.LEFT, padx=5)
        self.make_modern_button(btn_frame, "📌 Add Strategy", self.add_strategy, "#43A047", "#2E7D32").pack(side=tk.LEFT, padx=5)

        # Canvas with scrollbars
        canvas_frame = tk.Frame(root, bg="#121212")
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="#121212", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Stylish ttk scrollbars
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Vertical.TScrollbar", gripcount=0,
                        background="#616161", darkcolor="#616161", lightcolor="#616161",
                        troughcolor="#2E2E2E", bordercolor="#2E2E2E", arrowcolor="white", width=12)
        style.configure("Horizontal.TScrollbar", gripcount=0,
                        background="#616161", darkcolor="#616161", lightcolor="#616161",
                        troughcolor="#2E2E2E", bordercolor="#2E2E2E", arrowcolor="white", width=12)

        y_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview, style="Vertical.TScrollbar")
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar = ttk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.canvas.xview, style="Horizontal.TScrollbar")
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        # Table frame inside canvas
        self.table_frame = tk.Frame(self.canvas, bg="#121212", padx=20, pady=10)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")

        # Update scroll region
        self.table_frame.bind("<Configure>", lambda e: self.canvas.config(scrollregion=self.canvas.bbox("all")))

        # Bind mouse wheel for scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_linux_scroll)
        self.canvas.bind_all("<Button-5>", self._on_linux_scroll)

        self.draw_table()

    # Scroll handling
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_shift_mousewheel(self, event):
        self.canvas.xview_scroll(int(-1*(event.delta/120)), "units")

    def _on_linux_scroll(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    # Modern button
    def make_modern_button(self, parent, text, command, bg_color, hover_color):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 10, "bold"),
                        bg=bg_color, fg="white", relief="flat", padx=12, pady=5,
                        activebackground=hover_color, activeforeground="white",
                        command=command)
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_color))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg_color))
        return btn

    # Load/save
    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return {"strategies": [], "things": {}}

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    # Add items
    def add_thing(self):
        name = simpledialog.askstring("New Thing", "Enter thing name:")
        if name and name.strip() and name not in self.data["things"]:
            self.data["things"][name.strip()] = {s: False for s in self.data["strategies"]}
            self.save_data()
            self.draw_table()

    def add_strategy(self):
        name = simpledialog.askstring("New Strategy", "Enter strategy name:")
        if name and name.strip() and name not in self.data["strategies"]:
            self.data["strategies"].append(name.strip())
            for thing in self.data["things"]:
                self.data["things"][thing][name.strip()] = False
            self.save_data()
            self.draw_table()

    # Toggle completion
    def toggle_completion(self, thing, strategy):
        self.data["things"][thing][strategy] = not self.data["things"][thing][strategy]
        self.save_data()
        self.update_cell(thing, strategy)

    def update_cell(self, thing, strategy):
        btn = self.cell_buttons.get((thing, strategy))
        if btn:
            btn.config(text="✔" if self.data["things"][thing][strategy] else "")

    # Draw table
    def draw_table(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.cell_buttons.clear()

        # Header
        tk.Label(self.table_frame, text="Thing Name", font=("Segoe UI", 11, "bold"),
                 bg="#1976D2", fg="white", borderwidth=1, relief="solid",
                 width=20, padx=5, pady=5).grid(row=0, column=0, sticky="nsew")

        for col, strategy in enumerate(self.data["strategies"], start=1):
            tk.Label(self.table_frame, text=strategy, font=("Segoe UI", 11, "bold"),
                     bg="#1976D2", fg="white", borderwidth=1, relief="solid",
                     width=15, padx=5, pady=5).grid(row=0, column=col, sticky="nsew")

        # Rows
        for row_index, thing in enumerate(self.data["things"], start=1):
            row_color = "#1E1E1E" if row_index % 2 == 0 else "#2E2E2E"
            tk.Label(self.table_frame, text=thing, font=("Segoe UI", 10, "bold"),
                     bg=row_color, fg="white", borderwidth=1, relief="solid",
                     width=20, padx=5, pady=5).grid(row=row_index, column=0, sticky="nsew")

            for col, strategy in enumerate(self.data["strategies"], start=1):
                status = "✔" if self.data["things"][thing][strategy] else ""
                btn = tk.Button(self.table_frame, text=status, font=("Segoe UI", 11, "bold"),
                                bg=row_color, fg="#00E676", borderwidth=1, relief="solid",
                                activebackground="#444444",
                                command=lambda t=thing, s=strategy: self.toggle_completion(t, s))
                btn.grid(row=row_index, column=col, sticky="nsew", padx=2, pady=2)
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#444444"))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=row_color))
                self.cell_buttons[(thing, strategy)] = btn


if __name__ == "__main__":
    root = tk.Tk()
    app = BrainstormApp(root)
    root.mainloop()
