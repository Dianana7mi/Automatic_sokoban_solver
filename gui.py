import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import json
import threading
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# === Minimalist Light Theme Palette ===
THEME = {
    'window_bg': '#f9fafb',      # Off-white background
    'sidebar_bg': '#ffffff',     # Pure white sidebar
    'content_bg': '#f3f4f6',     # Light gray for content area
    
    'text_primary': '#1f2937',   # Dark gray (almost black)
    'text_secondary': '#6b7280', # Medium gray
    'border': '#e5e7eb',         # Very light border
    
    'primary_btn': '#3b82f6',    # Soft Blue
    'primary_btn_hover': '#2563eb',
    
    'control_btn': '#ffffff',    # White buttons
    'control_btn_text': '#374151',
    'control_btn_hover': '#f3f4f6',

    # Game Elements (Pastel/Soft tones)
    'g_floor': '#ffffff',
    'g_wall': '#9ca3af',         # Soft Gray
    'g_wall_border': '#6b7280',
    'g_target': '#fecaca',       # Soft Red/Pink
    'g_target_dot': '#ef4444',   # Red dot
    'g_box': '#fcd34d',          # Soft Yellow/Wood
    'g_box_border': '#d97706',
    'g_box_done': '#86efac',     # Soft Green
    'g_box_done_border': '#16a34a',
    'g_player': '#60a5fa',       # Soft Blue
    'g_player_border': '#2563eb'
}

TILE_SIZE = 50

class SokobanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sokoban Solver Pro")
        self.root.configure(bg=THEME['window_bg'])
        
        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # General Styles
        self.style.configure('TFrame', background=THEME['sidebar_bg'])
        self.style.configure('Content.TFrame', background=THEME['content_bg'])
        
        self.style.configure('TLabel', background=THEME['sidebar_bg'], foreground=THEME['text_primary'], font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', background=THEME['sidebar_bg'], foreground=THEME['text_primary'], font=('Segoe UI', 16, 'bold'))
        self.style.configure('SubHeader.TLabel', background=THEME['sidebar_bg'], foreground=THEME['text_secondary'], font=('Segoe UI', 9, 'bold'))
        
        # Radio Buttons
        self.style.configure('TRadiobutton', background=THEME['sidebar_bg'], foreground=THEME['text_primary'], font=('Segoe UI', 10))
        self.style.map('TRadiobutton', background=[('active', THEME['sidebar_bg'])])
        
        # Separator
        self.style.configure('TSeparator', background=THEME['border'])

        # === Main Layout ===
        self.main_container = tk.Frame(root, bg=THEME['window_bg'])
        self.main_container.pack(fill="both", expand=True)

        # --- Sidebar (Left) ---
        self.sidebar = tk.Frame(self.main_container, bg=THEME['sidebar_bg'], width=280, padx=25, pady=25)
        self.sidebar.pack(side="left", fill="y")
        # Add right border to sidebar
        tk.Frame(self.main_container, bg=THEME['border'], width=1).pack(side="left", fill="y")

        # Header
        ttk.Label(self.sidebar, text="Sokoban Solver", style='Header.TLabel').pack(anchor="w", pady=(0, 5))
        ttk.Label(self.sidebar, text="Automatic Path Finder", style='TLabel', foreground=THEME['text_secondary']).pack(anchor="w", pady=(0, 30))

        # 1. Map Selection
        self._create_section_header("GAME MAP")
        
        self.file_frame = tk.Frame(self.sidebar, bg=THEME['sidebar_bg'])
        self.file_frame.pack(fill="x", pady=(5, 15))
        
        self.file_path_var = tk.StringVar()
        self.file_entry = tk.Entry(self.file_frame, textvariable=self.file_path_var, 
                                   bg=THEME['window_bg'], fg=THEME['text_primary'], 
                                   relief="flat", highlightthickness=1, highlightbackground=THEME['border'],
                                   font=('Segoe UI', 9))
        self.file_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 5))
        
        self.browse_btn = tk.Button(self.file_frame, text="...", command=self.browse_file,
                                    bg=THEME['control_btn'], fg=THEME['text_primary'],
                                    relief="flat", bd=0, highlightthickness=1, highlightbackground=THEME['border'],
                                    width=3, cursor="hand2")
        self.browse_btn.pack(side="right", ipady=2)

        # 2. Algorithm Selection
        self._create_section_header("ALGORITHM")
        self.algo_var = tk.IntVar(value=0)
        
        self.algo_frame = tk.Frame(self.sidebar, bg=THEME['sidebar_bg'])
        self.algo_frame.pack(fill="x", pady=5)
        
        self._create_radio_btn("A* Search (Optimal)", 0)
        self._create_radio_btn("DFS (Deep Search)", 1)
        self._create_radio_btn("BFS (Breadth First)", 2)
        
        # 3. Memory
        tk.Frame(self.sidebar, bg=THEME['sidebar_bg'], height=15).pack() # Spacer
        self._create_section_header("MEMORY LIMIT (MB)")
        self.mem_var = tk.StringVar(value="100")
        self.mem_entry = tk.Entry(self.sidebar, textvariable=self.mem_var,
                                  bg=THEME['window_bg'], fg=THEME['text_primary'],
                                  relief="flat", highlightthickness=1, highlightbackground=THEME['border'],
                                  font=('Segoe UI', 9))
        self.mem_entry.pack(fill="x", pady=(5, 20), ipady=5)

        # Calculate Button
        self.run_btn = tk.Button(self.sidebar, text="Calculate Solution", command=self.run_solver, 
                                 bg=THEME['primary_btn'], fg="white", 
                                 font=('Segoe UI', 10, 'bold'),
                                 relief="flat", bd=0, cursor="hand2", 
                                 activebackground=THEME['primary_btn_hover'], activeforeground="white")
        self.run_btn.pack(fill="x", pady=(10, 20), ipady=10)
        
        # Status
        self.status_var = tk.StringVar(value="Ready to solve")
        self.status_lbl = tk.Label(self.sidebar, textvariable=self.status_var, 
                                   bg=THEME['sidebar_bg'], fg=THEME['text_secondary'], 
                                   font=('Segoe UI', 9), anchor="w", justify="left")
        self.status_lbl.pack(fill="x", side="bottom")

        # --- Content Area (Right) ---
        self.content_area = tk.Frame(self.main_container, bg=THEME['content_bg'])
        self.content_area.pack(side="right", fill="both", expand=True, padx=30, pady=30)
        
        # Card-like container for canvas
        self.canvas_card = tk.Frame(self.content_area, bg="white", bd=0, padx=10, pady=10)
        self.canvas_card.pack(fill="both", expand=True)
        # Add subtle shadow effect using a bottom border frame? (Simulated)
        # Using simple white card for now.
        
        self.canvas = tk.Canvas(self.canvas_card, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Control Bar (Floating above bottom or separate?)
        self.controls_frame = tk.Frame(self.content_area, bg=THEME['content_bg'], pady=20)
        self.controls_frame.pack(fill="x")
        
        # Center controls
        self.ctrl_center = tk.Frame(self.controls_frame, bg=THEME['content_bg'])
        self.ctrl_center.pack()

        # Step Counter
        self.step_label = tk.Label(self.ctrl_center, text="Step 0 / 0", 
                                   bg=THEME['content_bg'], fg=THEME['text_secondary'], 
                                   font=('Segoe UI', 11))
        self.step_label.pack(side="top", pady=(0, 10))

        # Buttons Row
        self.btn_row = tk.Frame(self.ctrl_center, bg=THEME['content_bg'])
        self.btn_row.pack()

        self._create_player_btn("First", self.go_start)
        self._create_player_btn("Prev", self.go_prev)
        
        self.play_btn = tk.Button(self.btn_row, text="Play", command=self.toggle_play,
                                  bg=THEME['control_btn'], fg=THEME['primary_btn'],
                                  font=('Segoe UI', 10, 'bold'), width=10,
                                  relief="flat", highlightthickness=1, highlightbackground=THEME['border'],
                                  cursor="hand2")
        self.play_btn.pack(side="left", padx=8)
        
        self._create_player_btn("Next", self.go_next)
        self._create_player_btn("Last", self.go_end)

        # Logic
        self.solution_steps = []
        self.current_step = 0
        self.is_playing = False
        self.play_job = None
        
        # Set default file
        # Check bundled location first, then dev location
        bundled_box = resource_path(os.path.join("automatic-sokoban-solver-master", "box.txt"))
        dev_box = os.path.join("automatic-sokoban-solver-master", "box.txt")
        
        if os.path.exists(bundled_box):
             self.file_path_var.set(os.path.abspath(bundled_box))
        elif os.path.exists(dev_box):
             self.file_path_var.set(os.path.abspath(dev_box))
        
        # Initial text
        self.canvas.create_text(300, 200, text="Please load a map and solve", fill=THEME['text_secondary'], font=('Segoe UI', 12))

    def _create_section_header(self, text):
        ttk.Label(self.sidebar, text=text, style='SubHeader.TLabel').pack(anchor="w", pady=(0, 5))

    def _create_radio_btn(self, text, val):
        ttk.Radiobutton(self.algo_frame, text=text, variable=self.algo_var, value=val).pack(anchor="w", pady=3)

    def _create_player_btn(self, text, cmd):
        btn = tk.Button(self.btn_row, text=text, command=cmd,
                        bg=THEME['control_btn'], fg=THEME['control_btn_text'],
                        activebackground=THEME['control_btn_hover'],
                        font=('Segoe UI', 9), relief="flat", 
                        highlightthickness=1, highlightbackground=THEME['border'],
                        width=6, cursor="hand2")
        btn.pack(side="left", padx=4)

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
            
        self.run_btn.config(state="disabled", text="Thinking...", bg=THEME['text_secondary'])
        self.status_var.set("Engine is computing solution...")
        
        threading.Thread(target=self._execute_solver, args=(algo, mem, filename)).start()

    def _execute_solver(self, algo, mem, filename):
        # Look for solver in resource path (bundled) or current dir
        exe_name = "sokoban_solver.exe"
        exe_path = resource_path(exe_name)
        
        if not os.path.exists(exe_path):
             # Fallback to local dir if resource_path returned temp but exe is in CWD (dev mode)
             if os.path.exists(exe_name):
                 exe_path = os.path.abspath(exe_name)
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
        self.run_btn.config(state="normal", text="Calculate Solution", bg=THEME['primary_btn'])
        self.status_var.set("Error Occurred")
        messagebox.showerror("Solver Error", msg)

    def _parse_output(self, output):
        try:
            start_marker = "---JSON_START---"
            end_marker = "---JSON_END---"
            start_idx = output.find(start_marker)
            end_idx = output.find(end_marker)
            
            if start_idx == -1 or end_idx == -1:
                self._on_solver_error("No solution found.")
                return

            json_str = output[start_idx + len(start_marker):end_idx].strip()
            data = json.loads(json_str)
            
            if isinstance(data, dict) and "error" in data:
                self._on_solver_error(data["error"])
                return
            
            self.solution_steps = data
            self.current_step = 0
            self.status_var.set(f"Solved! Total steps: {len(self.solution_steps)}")
            self.run_btn.config(state="normal", text="Calculate Solution", bg=THEME['primary_btn'])
            
            self.update_canvas()
            
        except Exception as e:
            self._on_solver_error(f"Data Error: {e}")

    def draw_board(self, matrix):
        self.canvas.delete("all")
        if not matrix:
            return
            
        rows = len(matrix)
        cols = len(matrix[0]) if rows > 0 else 0
        
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        
        draw_w = cw - 40
        draw_h = ch - 40
        
        if cols > 0 and rows > 0:
            ts = min(draw_w / cols, draw_h / rows, 60)
            ts = max(ts, 20)
        else:
            ts = TILE_SIZE

        # Center board
        board_w = cols * ts
        board_h = rows * ts
        ox = (cw - board_w) / 2
        oy = (ch - board_h) / 2

        for r in range(rows):
            for c in range(cols):
                val = matrix[r][c]
                x1 = ox + c * ts
                y1 = oy + r * ts
                x2 = x1 + ts
                y2 = y1 + ts
                
                # Enum: WALL=0, FINAL=1, BLANK=2, BOX=3, REDBOX=4, PERSON=5, PERSONF=6
                
                # 1. Background (Floor)
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=THEME['g_floor'], outline=THEME['border'], width=1)
                
                # 2. Target (Final/RedBox/PersonF)
                if val in [1, 4, 6]:
                    m = ts * 0.35
                    self.canvas.create_oval(x1+m, y1+m, x2-m, y2-m, fill=THEME['g_target_dot'], outline="")

                # 3. Objects
                if val == 0: # Wall
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=THEME['g_wall'], outline=THEME['g_wall_border'], width=0)
                    
                elif val == 3 or val == 4: # Box
                    b_color = THEME['g_box_done'] if val == 4 else THEME['g_box']
                    b_border = THEME['g_box_done_border'] if val == 4 else THEME['g_box_border']
                    
                    gap = ts * 0.1
                    self.canvas.create_rectangle(x1+gap, y1+gap, x2-gap, y2-gap, 
                                                 fill=b_color, outline=b_border, width=2)
                    
                elif val == 5 or val == 6: # Player
                    p_gap = ts * 0.15
                    self.canvas.create_oval(x1+p_gap, y1+p_gap, x2-p_gap, y2-p_gap, 
                                            fill=THEME['g_player'], outline=THEME['g_player_border'], width=2)

    def update_canvas(self):
        if 0 <= self.current_step < len(self.solution_steps):
            self.draw_board(self.solution_steps[self.current_step])
            self.step_label.config(text=f"Step {self.current_step + 1} / {len(self.solution_steps)}")

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
            self.play_btn.config(text="Pause", fg="#e11d48") # Rose color for pause
            self.play_step()

    def stop_play(self):
        self.is_playing = False
        self.play_btn.config(text="Play", fg=THEME['primary_btn'])
        if self.play_job:
            self.root.after_cancel(self.play_job)
            self.play_job = None

    def play_step(self):
        if self.is_playing and self.current_step < len(self.solution_steps) - 1:
            self.go_next()
            if self.current_step < len(self.solution_steps) - 1:
                self.play_job = self.root.after(150, self.play_step)
            else:
                self.stop_play()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x700")
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
