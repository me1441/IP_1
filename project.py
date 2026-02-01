import tkinter as tk
from tkinter import messagebox
import random
import time
import math

class Particle:
    """Оптимизированная система частиц (синяя тема)"""
    def __init__(self, canvas, x, y, velocity, life, size=3, color="#3498db"):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.vx = velocity[0]
        self.vy = velocity[1]
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        
        self.id = canvas.create_oval(
            x-size, y-size, x+size, y+size,
            fill=color, outline="", stipple="gray75"
        )
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= 1
        
        if self.life > 0:
            self.canvas.coords(
                self.id, 
                self.x-self.size, self.y-self.size,
                self.x+self.size, self.y+self.size
            )
            opacity = int((self.life / self.max_life) * 75)
            stipple = f"gray{opacity}" if opacity > 0 else ""
            self.canvas.itemconfig(self.id, stipple=stipple)
            return True
        return False
    
    def delete(self):
        self.canvas.delete(self.id)

class ParticleSystem:
    def __init__(self, canvas):
        self.canvas = canvas
        self.particles = []
        self.active = True
    
    def emit(self, x, y, count=10, speed=5, color="#3498db"):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            vel = random.uniform(2, speed)
            vx = math.cos(angle) * vel
            vy = math.sin(angle) * vel
            p = Particle(
                self.canvas, x, y, (vx, vy), 
                random.randint(15, 30), 
                random.randint(2, 4),
                color
            )
            self.particles.append(p)
    
    def update(self):
        if not self.active:
            return
        
        for p in self.particles[:]:
            if not p.update():
                p.delete()
                self.particles.remove(p)
        
        if self.particles:
            self.canvas.after(16, self.update)
    
    def clear(self):
        for p in self.particles:
            p.delete()
        self.particles = []
        self.active = False

class NeonButton:
    """Кнопка в синей тематике"""
    def __init__(self, canvas, x, y, width, height, text, command, tag="ui"):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.command = command
        self.tag = tag
        self.hovered = False
        
        self.glow_ids = []
        for i in range(3):
            glow = canvas.create_rectangle(
                x-i*2, y-i*2, x+width+i*2, y+height+i*2,
                fill="", outline="#0066cc", width=2-i*0.3,
                stipple="gray50", tags=(tag, f"glow_{i}")
            )
            self.glow_ids.append(glow)
        
        self.rect = canvas.create_rectangle(
            x, y, x+width, y+height,
            fill="#0a0a0f", outline="#3498db", width=2,
            tags=(tag, "button")
        )
        
        self.txt = canvas.create_text(
            x+width/2, y+height/2, text=text,
            fill="#aed6f1", font=("Helvetica", 14, "bold"),
            tags=(tag, "text")
        )
        
        for item in [self.rect, self.txt] + self.glow_ids:
            canvas.tag_bind(item, "<Enter>", self.on_enter)
            canvas.tag_bind(item, "<Leave>", self.on_leave)
            canvas.tag_bind(item, "<Button-1>", self.on_click)
    
    def on_enter(self, event):
        self.hovered = True
        self.canvas.itemconfig(self.rect, fill="#16213e", outline="#5dade2")
        for glow in self.glow_ids:
            self.canvas.itemconfig(glow, stipple="")
    
    def on_leave(self, event):
        self.hovered = False
        self.canvas.itemconfig(self.rect, fill="#0a0a0f", outline="#3498db")
        for glow in self.glow_ids:
            self.canvas.itemconfig(glow, stipple="gray50")
    
    def on_click(self, event):
        self.command()
    
    def delete(self):
        for item in self.glow_ids + [self.rect, self.txt]:
            self.canvas.delete(item)

class GameCollection:
    def __init__(self, root):
        self.root = root
        self.root.title("BLUE ARCADE")
        self.root.geometry("1000x800")
        self.root.configure(bg="#000000")
        self.root.resizable(False, False)
        
        self.main_canvas = tk.Canvas(
            self.root, width=1000, height=800,
            bg="#000000", highlightthickness=0
        )
        self.main_canvas.pack()
        
        self.particles = ParticleSystem(self.main_canvas)
        self.current_game = None
        self.animation_id = None
        
        self.show_main_menu()
    
    def clear_screen(self):
        self.particles.clear()
        self.particles = ParticleSystem(self.main_canvas)
        
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None        
        
        for item in self.main_canvas.find_all():
            self.main_canvas.delete(item)
        
        if self.current_game:
            if hasattr(self.current_game, 'cleanup'):
                self.current_game.cleanup()
            self.current_game = None
    
    def show_main_menu(self):
        self.clear_screen()
        self.main_canvas.create_text(
            500, 100, text="🎮 Убийца времени",
            font=("Helvetica", 48, "bold"),
            fill="#ffffff"
        )
        
        self.main_canvas.create_text(
            500, 180, text="Выберите игру",
            font=("Helvetica", 16), fill="#3498db"
        )
        
        games = [
            ("🐍 ЗМЕЙКА", self.start_snake),
            ("💣 САПЕР", self.start_minesweeper),
            ("🖖 RPSLS", self.start_rps),
            ("🎯 ПРИЦЕЛЫ", self.start_targets),
            ("🏐 CATCHER", self.start_catcher)
        ]
        
        y_pos = 300
        for text, cmd in games:
            btn = NeonButton(
                self.main_canvas, 350, y_pos, 300, 60,
                text, cmd
            )
            y_pos += 90
        
        self.draw_stars()
    
    def draw_stars(self):
        for _ in range(50):
            x = random.randint(0, 1000)
            y = random.randint(0, 800)
            size = random.randint(1, 2)
            brightness = random.choice(["gray25", "gray50", "gray75"])
            self.main_canvas.create_oval(
                x, y, x+size, y+size,
                fill="#5dade2", outline="", stipple=brightness
            )
    
    def create_back_button(self):
        return NeonButton(
            self.main_canvas, 20, 20, 120, 40,
            "← МЕНЮ", self.show_main_menu
        )
    
    def start_snake(self):
        self.clear_screen()
        self.create_back_button()
        self.current_game = SnakeGame(self.main_canvas, self.particles)
    
    def start_minesweeper(self):
        self.clear_screen()
        self.create_back_button()
        self.current_game = MinesweeperGame(self.main_canvas, self.particles)
    
    def start_rps(self):
        self.clear_screen()
        self.create_back_button()
        self.current_game = RPSExtendedGame(self.main_canvas, self.particles)
    
    def start_targets(self):
        self.clear_screen()
        self.create_back_button()
        self.current_game = TargetGame(self.main_canvas, self.particles)
    
    def start_catcher(self):
        self.clear_screen()
        self.create_back_button()
        self.current_game = BallCatcherGame(self.main_canvas, self.particles)


class SnakeGame:
    def __init__(self, canvas, particles):
        self.canvas = canvas
        self.particles = particles
        self.width = 600
        self.height = 500
        self.cell_size = 20
        
        self.offset_x = 200
        self.offset_y = 150
        
        self.cleanup_flag = False
        self.after_ids = []
        
        self.draw_grid()
        
        # УБРАН СЧЕТЧИК ОЧКОВ
        
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.food = self.spawn_food()
        self.game_active = False
        self.snake_ids = []
        self.food_items = []
        
        self.start_btn = NeonButton(
            canvas, 400, 350, 200, 60,
            "START", self.start
        )
        
        self.draw_food()
        
        self.key_binding = canvas.bind("<Key>", self.change_direction)
        canvas.focus_set()
    
    def draw_grid(self):
        for i in range(0, self.width+1, self.cell_size):
            self.canvas.create_line(
                self.offset_x + i, self.offset_y,
                self.offset_x + i, self.offset_y + self.height,
                fill="#0f3460", width=1
            )
        for i in range(0, self.height+1, self.cell_size):
            self.canvas.create_line(
                self.offset_x, self.offset_y + i,
                self.offset_x + self.width, self.offset_y + i,
                fill="#0f3460", width=1
            )
        
        self.canvas.create_rectangle(
            self.offset_x-3, self.offset_y-3,
            self.offset_x+self.width+3, self.offset_y+self.height+3,
            outline="#0066cc", width=3
        )
    
    def spawn_food(self):
        while True:
            x = random.randint(0, (self.width//self.cell_size)-1)
            y = random.randint(0, (self.height//self.cell_size)-1)
            if (x, y) not in self.snake:
                return (x, y)
    
    def draw_food(self):
        for item in self.food_items:
            self.canvas.delete(item)
        
        x = self.offset_x + self.food[0]*self.cell_size + self.cell_size//2
        y = self.offset_y + self.food[1]*self.cell_size + self.cell_size//2
        
        glow = self.canvas.create_oval(
            x-12, y-12, x+12, y+12,
            fill="", outline="#3498db", width=2, stipple="gray50"
        )
        core = self.canvas.create_oval(
            x-6, y-6, x+6, y+6,
            fill="#5dade2", outline=""
        )
        self.food_items = [glow, core]
    
    def start(self):
        self.game_active = True
        self.start_btn.delete()
        self.update()
    
    def change_direction(self, event):
        key = event.keysym
        opposites = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if key in opposites and opposites[key] != self.direction:
            self.next_direction = key
    
    def update(self):
        if not self.game_active or self.cleanup_flag:
            return
        
        self.direction = self.next_direction
        
        head = self.snake[0]
        if self.direction == "Up":
            new_head = (head[0], head[1]-1)
        elif self.direction == "Down":
            new_head = (head[0], head[1]+1)
        elif self.direction == "Left":
            new_head = (head[0]-1, head[1])
        else:
            new_head = (head[0]+1, head[1])
        
        if (new_head[0] < 0 or new_head[0] >= self.width//self.cell_size or
            new_head[1] < 0 or new_head[1] >= self.height//self.cell_size or
            new_head in self.snake):
            self.game_over()
            return
        
        self.snake.insert(0, new_head)
        
        if new_head == self.food:
            # УБРАНО ОБНОВЛЕНИЕ СЧЕТА
            self.particles.emit(
                self.offset_x + new_head[0]*self.cell_size + 10,
                self.offset_y + new_head[1]*self.cell_size + 10,
                count=15, color="#5dade2", speed=6
            )
            self.food = self.spawn_food()
            self.draw_food()
        else:
            self.snake.pop()
        
        self.draw_snake()
        aid = self.canvas.after(100, self.update)
        self.after_ids.append(aid)
    
    def draw_snake(self):
        for sid in self.snake_ids:
            self.canvas.delete(sid)
        self.snake_ids = []
        
        for i, (sx, sy) in enumerate(self.snake):
            x = self.offset_x + sx*self.cell_size + 1
            y = self.offset_y + sy*self.cell_size + 1
            size = self.cell_size - 2
            
            if i == 0:
                color = "#ffffff"
            else:
                intensity = max(50, 255 - i*20)
                r_val = intensity // 4
                g_val = intensity // 3
                b_val = intensity
                color = f"#{r_val:02x}{g_val:02x}{b_val:02x}"
            
            rect = self.canvas.create_rectangle(
                x, y, x+size, y+size,
                fill=color, outline="#0066cc" if i == 0 else ""
            )
            self.snake_ids.append(rect)
    
    def game_over(self):
        self.game_active = False
        self.canvas.create_text(
            500, 400, text="GAME OVER",
            font=("Helvetica", 48, "bold"), fill="#3498db"
        )
        btn = NeonButton(
            self.canvas, 400, 500, 200, 50,
            "RESTART", lambda: SnakeGame(self.canvas, self.particles)
        )
    
    def cleanup(self):
        self.cleanup_flag = True
        self.game_active = False
        self.canvas.unbind("<Key>", self.key_binding)
        for aid in self.after_ids:
            try:
                self.canvas.after_cancel(aid)
            except:
                pass


class MinesweeperGame:
    def __init__(self, canvas, particles):
        self.canvas = canvas
        self.particles = particles
        self.rows = 8
        self.cols = 8
        self.cell_size = 55
        self.mines = 10
        
        self.offset_x = 280
        self.offset_y = 180
        
        self.cleanup_flag = False
        self.buttons = []
        self.game_over = False
        
        canvas.create_text(
            500, 80, text="💣 MINESWEEPER",
            font=("Helvetica", 32, "bold"), fill="#3498db"
        )
        
        self.counter = canvas.create_text(
            500, 130, text="MINES: 10",
            font=("Helvetica", 18), fill="#5dade2"
        )
        
        self.generate_mines()
        self.create_grid()
    
    def generate_mines(self):
        self.mine_positions = set()
        while len(self.mine_positions) < self.mines:
            r = random.randint(0, self.rows-1)
            c = random.randint(0, self.cols-1)
            self.mine_positions.add((r, c))
    
    def create_grid(self):
        self.button_refs = []
        
        for r in range(self.rows):
            row_refs = []
            for c in range(self.cols):
                x = self.offset_x + c*self.cell_size
                y = self.offset_y + r*self.cell_size
                
                shadow = self.canvas.create_rectangle(
                    x+2, y+2, x+self.cell_size, y+self.cell_size,
                    fill="#050510", outline=""
                )
                
                btn = self.canvas.create_rectangle(
                    x, y, x+self.cell_size-2, y+self.cell_size-2,
                    fill="#0a0a0f", outline="#0066cc", width=2
                )
                
                txt = self.canvas.create_text(
                    x+self.cell_size//2, y+self.cell_size//2,
                    text="", font=("Helvetica", 18, "bold"), fill="#aed6f1"
                )
                
                self.canvas.tag_bind(btn, "<Button-1>", 
                                   lambda e, r=r, c=c: self.click(r, c))
                self.canvas.tag_bind(txt, "<Button-1>", 
                                   lambda e, r=r, c=c: self.click(r, c))
                self.canvas.tag_bind(btn, "<Button-3>", 
                                   lambda e, r=r, c=c: self.right_click(r, c))
                self.canvas.tag_bind(txt, "<Button-3>", 
                                   lambda e, r=r, c=c: self.right_click(r, c))
                
                row_refs.append({
                    'shadow': shadow, 'btn': btn, 'txt': txt,
                    'revealed': False, 'flagged': False, 'mine': (r,c) in self.mine_positions
                })
            
            self.button_refs.append(row_refs)
    
    def get_neighbors(self, r, c):
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r+dr, c+dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if (nr, nc) in self.mine_positions:
                        count += 1
        return count
    
    def click(self, r, c):
        if self.game_over or self.button_refs[r][c]['revealed'] or self.button_refs[r][c]['flagged']:
            return
        
        cell = self.button_refs[r][c]
        
        if cell['mine']:
            x = self.offset_x + c*self.cell_size + self.cell_size//2
            y = self.offset_y + r*self.cell_size + self.cell_size//2
            self.particles.emit(x, y, count=30, color="#e74c3c", speed=8)
            
            self.canvas.itemconfig(cell['btn'], fill="#0f3460")
            self.canvas.itemconfig(cell['txt'], text="💣", fill="#3498db")
            self.game_over = True
            self.reveal_all()
            
            self.canvas.create_text(500, 400, text="BOOM!", 
                                   font=("Helvetica", 64, "bold"), fill="#3498db")
            return
        
        self.reveal(r, c)
    
    def reveal(self, r, c):
        cell = self.button_refs[r][c]
        if cell['revealed'] or cell['flagged']:
            return
        
        cell['revealed'] = True
        count = self.get_neighbors(r, c)
        
        self.canvas.itemconfig(cell['shadow'], fill="#0f3460")
        self.canvas.itemconfig(cell['btn'], fill="#000000", outline="#5dade2")
        
        if count > 0:
            colors = {1: "#85c1e9", 2: "#5dade2", 3: "#3498db", 
                     4: "#2e86c1", 5: "#2874a6"}
            self.canvas.itemconfig(cell['txt'], text=str(count), 
                                 fill=colors.get(count, "#ffffff"))
        else:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        self.canvas.after(50, lambda nr=nr, nc=nc: self.reveal(nr, nc))
        
        revealed = sum(1 for row in self.button_refs for cell in row if cell['revealed'])
        if revealed == self.rows*self.cols - self.mines:
            self.canvas.create_text(500, 400, text="VICTORY!", 
                                   font=("Helvetica", 64, "bold"), fill="#5dade2")
    
    def right_click(self, r, c):
        cell = self.button_refs[r][c]
        if self.game_over or cell['revealed']:
            return
        
        cell['flagged'] = not cell['flagged']
        if cell['flagged']:
            self.canvas.itemconfig(cell['txt'], text="⚑", fill="#e74c3c")
            self.canvas.itemconfig(cell['btn'], fill="#16213e")
        else:
            self.canvas.itemconfig(cell['txt'], text="")
            self.canvas.itemconfig(cell['btn'], fill="#0a0a0f")
        
        flags = sum(1 for row in self.button_refs for cell in row if cell['flagged'])
        self.canvas.itemconfig(self.counter, text=f"MINES: {self.mines - flags}")
    
    def reveal_all(self):
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.button_refs[r][c]
                if cell['mine'] and not cell['flagged']:
                    self.canvas.itemconfig(cell['txt'], text="💣")
    
    def cleanup(self):
        self.game_over = True


class RPSExtendedGame:
    def __init__(self, canvas, particles):
        self.canvas = canvas
        self.particles = particles
        self.animating = False
        
        # Центрированный заголовок
        canvas.create_text(500, 80, text="🖖 RPSLS", 
                          font=("Helvetica", 36, "bold"), fill="#3498db")
        
        # Центрированный результат (крупный)
        self.result_emoji = canvas.create_text(500, 280, text="?", 
                                              font=("Helvetica", 80), fill="#ffffff")
        
        # Текст результата под эмодзи
        self.result_text = canvas.create_text(500, 380, text="Выберите знак", 
                                             font=("Helvetica", 20, "bold"), fill="#85c1e9")
        
        # Центрированные кнопки (строго по центру, симметрично)
        # Ширина кнопки 100, отступ 20 между ними
        # Всего 5 кнопок: занимают 5*100 + 4*20 = 580px
        # Центр экрана 500, начало: 500 - 290 = 210
        start_x = 210
        y_pos = 500
        spacing = 120
        
        buttons = ["rock", "paper", "scissors", "lizard", "spock"]
        
        for i, choice in enumerate(buttons):
            x = start_x + i * spacing
            NeonButton(canvas, x, y_pos, 100, 60, 
                      self.get_emoji(choice), 
                      lambda c=choice: self.play(c))
    
    def get_emoji(self, choice):
        emojis = {"rock": "✊", "paper": "✋", "scissors": "✌️", 
                 "lizard": "🦎", "spock": "🖖"}
        return emojis.get(choice, "?")
    
    def play(self, player):
        if self.animating:
            return
        
        self.animating = True
        choices = ["rock", "paper", "scissors", "lizard", "spock"]
        cpu = random.choice(choices)
        
        # Анимация рулетки
        frames = choices * 4
        for i, f in enumerate(frames):
            self.canvas.after(i*50, lambda f=f: 
                self.canvas.itemconfig(self.result_emoji, text=self.get_emoji(f)))
        
        self.canvas.after(len(frames)*50, lambda: self.show_result(player, cpu))
    
    def show_result(self, player, cpu):
        self.canvas.itemconfig(self.result_emoji, 
                              text=f"{self.get_emoji(player)} vs {self.get_emoji(cpu)}")
        
        rules = {
            "rock": ["scissors", "lizard"],
            "paper": ["rock", "spock"],
            "scissors": ["paper", "lizard"],
            "lizard": ["spock", "paper"],
            "spock": ["scissors", "rock"]
        }
        
        if player == cpu:
            result = "НИЧЬЯ"
            color = "#f39c12"
        elif cpu in rules[player]:
            result = "ПОБЕДА"
            color = "#5dade2"
            self.particles.emit(500, 280, count=20, color="#5dade2", speed=8)
        else:
            result = "ПОРАЖЕНИЕ"
            color = "#e74c3c"
        
        self.canvas.itemconfig(self.result_text, text=result, fill=color)
        self.animating = False


class TargetGame:
    def __init__(self, canvas, particles):
        self.canvas = canvas
        self.particles = particles
        self.active = False
        self.cleanup_flag = False
        self.after_ids = []
        
        self.laser_line = None
        self.crosshair_v = None
        self.aim_circle = None
        
        # УБРАН СЧЕТЧИК ОЧКОВ И ВРЕМЕНИ
        
        canvas.create_text(500, 80, text="🎯 TARGET PRACTICE", 
                          font=("Helvetica", 32, "bold"), fill="#3498db")
        
        # Игровая зона
        self.game_area = canvas.create_rectangle(150, 160, 850, 660, 
                                                fill="#050510", outline="#0066cc", width=3)
        
        self.targets = []
        
        self.start_btn = NeonButton(canvas, 430, 700, 140, 50, "START", self.start)
        
        self.bind_move = canvas.bind("<Motion>", self.update_aim)
        self.bind_click = canvas.bind("<Button-1>", self.shoot)
    
    def update_aim(self, event):
        if not self.active or self.cleanup_flag:
            return
        
        x, y = event.x, event.y
        
        if not (150 < x < 850 and 160 < y < 660):
            if self.laser_line:
                self.canvas.itemconfig(self.laser_line, state="hidden")
            if self.crosshair_v:
                self.canvas.itemconfig(self.crosshair_v, state="hidden")
            if self.aim_circle:
                self.canvas.itemconfig(self.aim_circle, state="hidden")
            return
        
        if not self.laser_line:
            self.laser_line = self.canvas.create_line(
                150, y, 850, y,
                fill="#0066cc", width=1, stipple="gray50"
            )
            self.crosshair_v = self.canvas.create_line(
                x, 160, x, 660,
                fill="#3498db", width=2
            )
            self.aim_circle = self.canvas.create_oval(
                x-20, y-20, x+20, y+20,
                outline="#5dade2", width=2
            )
        else:
            self.canvas.itemconfig(self.laser_line, state="normal")
            self.canvas.itemconfig(self.crosshair_v, state="normal")
            if self.aim_circle:
                self.canvas.itemconfig(self.aim_circle, state="normal")
            self.canvas.coords(self.laser_line, 150, y, 850, y)
            self.canvas.coords(self.crosshair_v, x, 160, x, 660)
            if self.aim_circle:
                self.canvas.coords(self.aim_circle, x-20, y-20, x+20, y+20)
    
    def start(self):
        self.active = True
        self.start_btn.delete()
        self.spawn_target()
        self.game_timer()
    
    def game_timer(self):
        # УБРАН ТАЙМЕР НА ЭКРАНЕ, игра бесконечная до выхода
        if not self.active or self.cleanup_flag:
            return
        self.spawn_target()
        aid = self.canvas.after(1000, self.game_timer)
        self.after_ids.append(aid)
    
    def spawn_target(self):
        if not self.active or self.cleanup_flag:
            return
        
        x = random.randint(200, 800)
        y = random.randint(200, 620)
        size = random.choice([25, 35, 45])
        
        target = {
            'x': x, 'y': y, 'size': size,
            'glow': self.canvas.create_oval(
                x-size-5, y-size-5, x+size+5, y+size+5,
                fill="", outline="#0066cc", width=3, stipple="gray50"
            ),
            'core': self.canvas.create_oval(
                x-size, y-size, x+size, y+size,
                fill="#0f3460", outline="#3498db", width=2
            ),
        }
        self.targets.append(target)
        
        # Убираем старые мишени, если их слишком много
        if len(self.targets) > 5:
            old = self.targets.pop(0)
            self.canvas.delete(old['glow'])
            self.canvas.delete(old['core'])
    
    def shoot(self, event):
        if not self.active or self.cleanup_flag:
            return
        
        x, y = event.x, event.y
        hit = False
        
        for target in self.targets[:]:
            dist = ((x - target['x'])**2 + (y - target['y'])**2)**0.5
            if dist < target['size']:
                self.particles.emit(target['x'], target['y'], 
                                   count=15, color="#5dade2", speed=7)
                self.canvas.delete(target['glow'])
                self.canvas.delete(target['core'])
                self.targets.remove(target)
                hit = True
                break
        
        if not hit and (150 < x < 850 and 160 < y < 660):
            self.particles.emit(x, y, count=5, color="#0f3460", speed=3)
    
    def cleanup(self):
        self.cleanup_flag = True
        self.active = False
        
        for aid in self.after_ids:
            try:
                self.canvas.after_cancel(aid)
            except:
                pass
        
        self.canvas.unbind("<Motion>", self.bind_move)
        self.canvas.unbind("<Button-1>", self.bind_click)
        
        for item in [self.laser_line, self.crosshair_v, self.aim_circle]:
            if item:
                try:
                    self.canvas.delete(item)
                except:
                    pass


class BallCatcherGame:
    def __init__(self, canvas, particles):
        self.canvas = canvas
        self.particles = particles
        self.active = False
        self.cleanup_flag = False
        self.after_ids = []
        
        canvas.create_text(500, 60, text="🏐 BALL CATCHER", 
                          font=("Helvetica", 32, "bold"), fill="#3498db")
        
        # УБРАНЫ СЧЕТЧИКИ ЖИЗНЕЙ И ОЧКОВ
        
        # Игровая зона (градиент)
        for i in range(20):
            shade = int(10 + i*2)
            color = f"#{shade:02x}{shade:02x}{shade+10:02x}"
            canvas.create_rectangle(150, 160+i*25, 850, 185+i*25, 
                                   fill=color, outline="")
        
        canvas.create_rectangle(150, 160, 850, 660, outline="#0066cc", width=3)
        
        self.basket_x = 500
        self.basket = canvas.create_rectangle(
            450, 620, 550, 650,
            fill="#0f3460", outline="#5dade2", width=3
        )
        
        self.balls = []
        
        self.start_btn = NeonButton(canvas, 430, 700, 140, 50, "START", self.start)
        
        self.bind_move = canvas.bind("<Motion>", self.move_basket)
    
    def move_basket(self, event):
        if not self.active or self.cleanup_flag:
            return
        self.basket_x = max(200, min(800, event.x))
        self.canvas.coords(
            self.basket, 
            self.basket_x-50, 620, self.basket_x+50, 650
        )
    
    def start(self):
        self.active = True
        self.start_btn.delete()
        self.spawn_ball()
        self.update()
    
    def spawn_ball(self):
        if not self.active or self.cleanup_flag:
            return
        
        x = random.randint(200, 800)
        ball_type = random.choices(['normal', 'fast', 'bonus'], weights=[60, 30, 10])[0]
        
        speed = {'normal': 4, 'fast': 7, 'bonus': 5}[ball_type]
        size = {'normal': 15, 'fast': 12, 'bonus': 10}[ball_type]
        color = {'normal': '#5dade2', 'fast': '#3498db', 'bonus': '#85c1e9'}[ball_type]
        
        ball = {
            'x': x, 'y': 170, 'speed': speed,
            'size': size, 'color': color,
            'id': self.canvas.create_oval(
                x-size, 170-size, x+size, 170+size,
                fill=color, outline="#ffffff", width=2
            ),
            'glow': self.canvas.create_oval(
                x-size-5, 170-size-5, x+size+5, 170+size+5,
                fill="", outline=color, width=2, stipple="gray50"
            )
        }
        self.balls.append(ball)
        
        aid = self.canvas.after(random.randint(1000, 2500), self.spawn_ball)
        self.after_ids.append(aid)
    
    def update(self):
        if not self.active or self.cleanup_flag:
            return
        
        for ball in self.balls[:]:
            ball['y'] += ball['speed']
            self.canvas.move(ball['id'], 0, ball['speed'])
            self.canvas.move(ball['glow'], 0, ball['speed'])
            
            if 620 <= ball['y'] <= 650:
                if abs(ball['x'] - self.basket_x) < 55:
                    self.particles.emit(ball['x'], 640, count=12, 
                                       color=ball['color'], speed=6)
                    self.canvas.delete(ball['id'])
                    self.canvas.delete(ball['glow'])
                    self.balls.remove(ball)
                    continue
            
            if ball['y'] > 660:
                self.canvas.delete(ball['id'])
                self.canvas.delete(ball['glow'])
                self.balls.remove(ball)
        
        aid = self.canvas.after(16, self.update)
        self.after_ids.append(aid)
    
    def cleanup(self):
        self.cleanup_flag = True
        self.active = False
        
        for aid in self.after_ids:
            try:
                self.canvas.after_cancel(aid)
            except:
                pass
        
        self.canvas.unbind("<Motion>", self.bind_move)


if __name__ == "__main__":
    root = tk.Tk()
    app = GameCollection(root)
    root.mainloop()