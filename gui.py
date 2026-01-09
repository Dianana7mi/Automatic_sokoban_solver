import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import json
import threading
import os
import sys

# Modern Color Palette (Flat UI)
COLORS = {
    'bg': '#2c3e50',        # Dark Blue-Grey Background
    'sidebar': '#34495e',   # Slightly lighter sidebar
    'text': '#ecf0f1',      # White-ish text
    'accent': '#e74c3c',    # Red accent
    'button': '#2980b9',    # Blue buttons
    'button_hover': '#3498db',
    
    # Game Elements
    'wall': '#34495e',      # Dark Slate
    'floor': '#ecf0f1',     # Light Grey
    'target': '#e74c3c',    # Red Target
    'box': '#d35400',       # Pumpkin/Brown Box
    'box_inner': '#e67e22', # Lighter Box Face
    'box_done': '#27ae60',  # Green Box (Success)
    'box_done_in': '#2ecc71',
    'player': '#2980b9',    # Blue Player
    'player_head': '#3498db'
}

TILE_SIZE = 50

class SokobanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sokoban Solver AI")
        self.root.configure(bg=COLORS['bg'])
        
        # Set window icon if available (skip for now to avoid errors)
        
        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom styles
        self.style.configure('TFrame', background=COLORS['bg'])
        self.style.configure('Sidebar.TFrame', background=COLORS['sidebar'], relief='flat')
        self.style.configure('TLabel', background=COLORS['sidebar'], foreground=COLORS['text'], font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', background=COLORS['sidebar'], foreground=COLORS['accent'], font=('Segoe UI', 14, 'bold'))
        self.style.configure('Status.TLabel', background=COLORS['bg'], foreground='#95a5a6', font=('Consolas', 9))
        
        # Button Styles
        self.style.configure('TButton', font=('Segoe UI', 10, 'bold'), borderwidth=0, focuscolor='none')
        self.style.map('TButton', background=[('active', COLORS['button_hover'])], foreground=[('active', 'white')])
        
        # Radio Button Styles
        self.style.configure('TRadiobutton', background=COLORS['sidebar'], foreground=COLORS['text'], font=('Segoe UI', 10))
        self.style.map('TRadiobutton', background=[('active', COLORS['sidebar'])])

        # === Main Layout (Sidebar + Main Content) ===
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill="both", expand=True)

        # --- Left Sidebar (Controls) ---
        self.sidebar = ttk.Frame(self.main_container, style='Sidebar.TFrame', padding=20)
        self.sidebar.pack(side="left", fill="y")
        
        # Title
        ttk.Label(self.sidebar, text="SOKOBAN\nSOLVER", style='Header.TLabel', justify="center").pack(pady=(0, 20))

        # File Selection Section
        self._create_section_label("Map Configuration")
        self.file_path_var = tk.StringVar()
        self.file_entry = tk.Entry(self.sidebar, textvariable=self.file_path_var, bg="#ecf0f1", fg="#2c3e50", relief="flat", font=('Segoe UI', 9))
        self.file_entry.pack(fill="x", pady=(5, 5), ipady=3)
        ttk.Button(self.sidebar, text="📂 Browse Map", command=self.browse_file).pack(fill="x", pady=(0, 15))

        # Algorithm Section
        self._create_section_label("Algorithm")
        self.algo_var = tk.IntVar(value=0)
        ttk.Radiobutton(self.sidebar, text="A* (Optimal)", variable=self.algo_var, value=0).pack(anchor="w", pady=2)
        ttk.Radiobutton(self.sidebar, text="DFS (Deep)", variable=self.algo_var, value=1).pack(anchor="w", pady=2)
        ttk.Radiobutton(self.sidebar, text="BFS (Fast)", variable=self.algo_var, value=2).pack(anchor="w", pady=2)
        
        # Memory Section
        ttk.Label(self.sidebar, text="Memory (MB):", style='TLabel').pack(anchor="w", pady=(15, 5))
        self.mem_var = tk.StringVar(value="100")
        tk.Entry(self.sidebar, textvariable=self.mem_var, bg="#ecf0f1", fg="#2c3e50", width=10, relief="flat", font=('Segoe UI', 9)).pack(anchor="w", ipady=2)

        # Solve Button
        self.run_btn = tk.Button(self.sidebar, text="⚡ CALCULATE SOLUTION", command=self.run_solver, 
                                 bg=COLORS['accent'], fg="white", font=('Segoe UI', 11, 'bold'), 
                                 relief="flat", cursor="hand2", activebackground="#c0392b", activeforeground="white")
        self.run_btn.pack(fill="x", pady=(30, 10), ipady=8)

        # Progress / Status in Sidebar
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.sidebar, textvariable=self.status_var, style='Status.TLabel', wraplength=180).pack(fill="x", pady=10)

        # --- Right Area (Canvas + Playback) ---
        self.right_panel = tk.Frame(self.main_container, bg=COLORS['bg'])
        self.right_panel.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Canvas Frame (for centering)
        self.canvas_container = tk.Frame(self.right_panel, bg=COLORS['bg'], bd=2, relief="flat")
        self.canvas_container.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(self.canvas_container, bg=COLORS['floor'], highlightthickness=0)
        self.canvas.pack(expand=True) # Center in container

        # Playback Controls Bar
        self.controls_frame = tk.Frame(self.right_panel, bg=COLORS['bg'], pady=15)
        self.controls_frame.pack(fill="x", side="bottom")

        # Center the buttons
        self.btn_container = tk.Frame(self.controls_frame, bg=COLORS['bg'])
        self.btn_container.pack()

        # Custom Control Buttons
        self._create_control_btn("⏮", self.go_start)
        self._create_control_btn("◀", self.go_prev)
        self.play_btn = tk.Button(self.btn_container, text="▶ PLAY", command=self.toggle_play, 
                                  bg=COLORS['button'], fg="white", font=('Segoe UI', 10, 'bold'), width=10,
                                  relief="flat", cursor="hand2")
        self.play_btn.pack(side="left", padx=5)
        self._create_control_btn("▶", self.go_next)
        self._create_control_btn("⏭", self.go_end)
        
        self.step_label = tk.Label(self.controls_frame, text="Step: 0 / 0", bg=COLORS['bg'], fg="#95a5a6", font=('Consolas', 12))
        self.step_label.pack(side="right")

        # Logic Variables
        self.solution_steps = []
        self.current_step = 0
        self.is_playing = False
        self.play_job = None

        # Set default file
        default_file = os.path.join("automatic-sokoban-solver-master", "box.txt")
        if os.path.exists(default_file):
            self.file_path_var.set(os.path.abspath(default_file))
            
        # Initial draw (empty board or placeholder)
        self.canvas.create_text(200, 200, text="Load a map to start", fill=COLORS['wall'], font=('Segoe UI', 14))

    def _create_section_label(self, text):
        lbl = ttk.Label(self.sidebar, text=text.upper(), style='TLabel', font=('Segoe UI', 8, 'bold'))
        lbl.pack(anchor="w", pady=(15, 5))
        
    def _create_control_btn(self, text, cmd):
        btn = tk.Button(self.btn_container, text=text, command=cmd, 
                        bg="#34495e", fg="white", font=('Segoe UI', 12), width=4,
                        relief="flat", cursor="hand2", activebackground=COLORS['button'])
        btn.pack(side="left", padx=2)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            self.file_path_var.set(filename)

    def run_solver(self):
        filename = self.file_path_var.get()
        if not filename or not os.path.exists(filename):
            messagebox.showerror("Error", "Please select a valid map file.")
            return
            
        algo = self.algo_var.get()
        try:
            mem = int(self.mem_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid memory value.")
            return
            
        self.run_btn.config(state="disabled", text="Computing...", bg="#7f8c8d")
        self.status_var.set("Engine is thinking...")
        
        threading.Thread(target=self._execute_solver, args=(algo, mem, filename)).start()

    def _execute_solver(self, algo, mem, filename):
        exe_path = "sokoban_solver.exe"
        if not os.path.exists(exe_path):
            if os.path.exists("./sokoban_solver.exe"):
                exe_path = "./sokoban_solver.exe"
            else:
                self.root.after(0, lambda: self._on_solver_error("Executable 'sokoban_solver.exe' not found."))
                return

        cmd = [exe_path, str(algo), str(mem), filename]
        
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                encoding='utf-8',
                startupinfo=startupinfo
            )
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                 self.root.after(0, lambda: self._on_solver_error(f"Solver failed:\n{stderr if stderr else stdout}"))
                 return
                 
            self.root.after(0, lambda: self._parse_output(stdout))
            
        except Exception as e:
            self.root.after(0, lambda: self._on_solver_error(str(e)))

    def _on_solver_error(self, msg):
        self.run_btn.config(state="normal", text="⚡ CALCULATE SOLUTION", bg=COLORS['accent'])
        self.status_var.set("Error Occurred")
        messagebox.showerror("Solver Error", msg)

    def _parse_output(self, output):
        try:
            start_marker = "---JSON_START---"
            end_marker = "---JSON_END---"
            start_idx = output.find(start_marker)
            end_idx = output.find(end_marker)
            
            if start_idx == -1 or end_idx == -1:
                self._on_solver_error("No solution found or invalid output.")
                return

            json_str = output[start_idx + len(start_marker):end_idx].strip()
            data = json.loads(json_str)
            
            self.solution_steps = data
            self.current_step = 0
            self.status_var.set(f"Solution Found! Steps: {len(self.solution_steps)}")
            self.run_btn.config(state="normal", text="⚡ CALCULATE SOLUTION", bg=COLORS['accent'])
            
            self.update_canvas()
            
        except Exception as e:
            self._on_solver_error(f"Data Error: {e}")

    def draw_board(self, matrix):
        self.canvas.delete("all")
        if not matrix:
            return
            
        rows = len(matrix)
        cols = len(matrix[0]) if rows > 0 else 0
        
        # Calculate dynamic tile size
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        
        # Add some margin
        draw_w = cw - 20
        draw_h = ch - 20
        
        if cols > 0 and rows > 0:
            ts = min(draw_w / cols, draw_h / rows, 60)
            ts = max(ts, 15) # Minimum size
        else:
            ts = TILE_SIZE

        # Center the board
        board_w = cols * ts
        board_h = rows * ts
        offset_x = (cw - board_w) / 2
        offset_y = (ch - board_h) / 2

        # Draw Grid Background
        self.canvas.create_rectangle(offset_x, offset_y, offset_x+board_w, offset_y+board_h, fill=COLORS['floor'], outline="")

        for r in range(rows):
            for c in range(cols):
                val = matrix[r][c]
                x1 = offset_x + c * ts
                y1 = offset_y + r * ts
                x2 = x1 + ts
                y2 = y1 + ts
                
                # Enum: WALL=0, FINAL=1, BLANK=2, BOX=3, REDBOX=4, PERSON=5, PERSONF=6
                
                # 1. Draw Floor Details (Targets)
                if val in [1, 4, 6]: # Final, RedBox, PersonF
                    # Draw target marker
                    m = ts * 0.35
                    self.canvas.create_oval(x1+m, y1+m, x2-m, y2-m, fill=COLORS['target'], outline="")
                
                # 2. Draw Objects
                if val == 0: # WALL
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=COLORS['wall'], outline=COLORS['bg'], width=1)
                    # Add subtle detail to wall
                    self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, fill="", outline="#465b6e", width=1)
                
                elif val == 3 or val == 4: # BOX or REDBOX
                    # Box Color
                    c_fill = COLORS['box_done'] if val == 4 else COLORS['box']
                    c_inner = COLORS['box_done_in'] if val == 4 else COLORS['box_inner']
                    
                    # Main crate
                    gap = ts * 0.05
                    self.canvas.create_rectangle(x1+gap, y1+gap, x2-gap, y2-gap, fill=c_fill, outline="#7f8c8d", width=1)
                    
                    # Inner "wood" detail
                    igap = ts * 0.15
                    self.canvas.create_rectangle(x1+igap, y1+igap, x2-igap, y2-igap, fill=c_inner, outline=c_fill, width=1)
                    
                    # Diagonal cross
                    self.canvas.create_line(x1+igap, y1+igap, x2-igap, y2-igap, fill=c_fill, width=2)
                    self.canvas.create_line(x2-igap, y1+igap, x1+igap, y2-igap, fill=c_fill, width=2)
                    
                elif val == 5 or val == 6: # PERSON or PERSONF
                    # Draw Person (Simple body + head)
                    margin = ts * 0.2
                    
                    # Body
                    self.canvas.create_arc(x1+margin, y1+ts*0.4, x2-margin, y2-ts*0.1, start=0, extent=180, fill=COLORS['player'], outline="")
                    # Head
                    head_r = ts * 0.15
                    cx = x1 + ts/2
                    cy = y1 + ts*0.35
                    self.canvas.create_oval(cx-head_r, cy-head_r, cx+head_r, cy+head_r, fill=COLORS['player_head'], outline="")

    def update_canvas(self):
        if 0 <= self.current_step < len(self.solution_steps):
            self.draw_board(self.solution_steps[self.current_step])
            self.step_label.config(text=f"STEP: {self.current_step + 1} / {len(self.solution_steps)}")

    def go_start(self):
        self.stop_play()
        self.current_step = 0
        self.update_canvas()

    def go_end(self):
        self.stop_play()
        self.current_step = len(self.solution_steps) - 1
        self.update_canvas()

    def go_prev(self):
        self.stop_play()
        if self.current_step > 0:
            self.current_step -= 1
            self.update_canvas()

    def go_next(self):
        if self.current_step < len(self.solution_steps) - 1:
            self.current_step += 1
            self.update_canvas()

    def toggle_play(self):
        if self.is_playing:
            self.stop_play()
        else:
            self.is_playing = True
            self.play_btn.config(text="⏸ PAUSE", bg="#f39c12") # Orange for pause
            self.play_step()

    def stop_play(self):
        self.is_playing = False
        self.play_btn.config(text="▶ PLAY", bg=COLORS['button'])
        if self.play_job:
            self.root.after_cancel(self.play_job)
            self.play_job = None

    def play_step(self):
        if self.is_playing and self.current_step < len(self.solution_steps) - 1:
            self.go_next()
            # Loop again
            if self.current_step < len(self.solution_steps) - 1:
                self.play_job = self.root.after(150, self.play_step) # 150ms delay for smoother anim
            else:
                self.stop_play()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x700")
    # Try to center window
    try:
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - 1000) // 2
        y = (screen_height - 700) // 2
        root.geometry(f"1000x700+{x}+{y}")
    except:
        pass
        
    app = SokobanGUI(root)
    root.mainloop()