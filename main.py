import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import sys
import win32api
import win32con
import win32gui
import random
import time
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, QEvent

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 70, 70
DRAGGED_WINDOW_SIZE = 300
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
SCALE = 2
move_speed = 10

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Desktop Cat")

hwnd = pygame.display.get_wm_info()["window"]

extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extended_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)

style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style & ~win32con.WS_OVERLAPPEDWINDOW)

screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 
                      screen_width // 2 - SCREEN_WIDTH // 2, 
                      screen_height // 2 - SCREEN_HEIGHT // 2, 
                      SCREEN_WIDTH, SCREEN_HEIGHT, 
                      0)

class Pet:
    def __init__(self):
        self.current_frame = 0
        self.animation_speed = 0.1
        self.animation_time = 0
        self.state = "sitting"
        self.direction = 'r'
        self.frames = []
        self.image = None
        self.rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.target_x = None
        self.target_y = None
        self.next_action_time = time.time() + random.uniform(2, 5)
        self.last_interaction_time = time.time()
        self.is_dragging = False
        self.windows_to_draw = []
        self.drawing_windows = False
        self.sit()
    
    def load_frames(self, state, direction='r'):
        frames = []
        try:
            max_frames = {
                'lick': 15,
                'sit': 5,
                'play': 6,
                'walk': 8
            }.get(state, 0)
            for i in range(1, max_frames + 1):
                file_path = os.path.join("assets", state, f"{i}.png")
                if not os.path.exists(file_path):
                    continue
                frame = pygame.image.load(file_path).convert_alpha()
                frame = pygame.transform.scale(frame, (frame.get_width() * SCALE, frame.get_height() * SCALE))
                if direction == 'l':
                    frame = pygame.transform.flip(frame, True, False)
                frames.append(frame)
        except pygame.error as e:
            pass
        return frames

    def sit(self):
        self.state = "sitting"
        self.frames = self.load_frames('sit', self.direction)
        if not self.frames:
            default_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            default_surface.fill(RED)
            self.frames = [default_surface]
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
    def lick(self):
        self.state = "licking"
        self.frames = self.load_frames('lick', self.direction)
        if not self.frames:
            self.sit()

    def walk(self):
        self.state = "walking"
        self.frames = self.load_frames('walk', self.direction)
        if not self.frames:
            self.sit()

    def play(self):
        self.state = "playing"
        self.frames = self.load_frames('play', self.direction)
        if not self.frames:
            self.sit()

    def update(self, dt):
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            if self.frames:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]
            else:
                pass

        self.update_position()
        self.update_state()

    def update_position(self):
        if self.target_x is not None and self.target_y is not None:
            hwnd = pygame.display.get_wm_info()["window"]
            current_x, current_y = win32gui.GetWindowRect(hwnd)[:2]

            moved = False
            new_direction = self.direction

            if abs(current_x - self.target_x) <= move_speed:
                current_x = self.target_x
            elif current_x < self.target_x:
                current_x += move_speed
                moved = True
                new_direction = 'r'
            elif current_x > self.target_x:
                current_x -= move_speed
                moved = True
                new_direction = 'l'

            if abs(current_y - self.target_y) <= move_speed:
                current_y = self.target_y
            elif current_y < self.target_y:
                current_y += move_speed
                moved = True
            elif current_y > self.target_y:
                current_y -= move_speed
                moved = True

            if moved:
                if new_direction != self.direction or self.state != "walking":
                    self.direction = new_direction
                    self.walk()
            elif not moved and self.state == "walking":
                self.sit()

            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, current_x, current_y, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
            
            if current_x == self.target_x and current_y == self.target_y:
                self.target_x = None
                self.target_y = None
                self.sit()

    def update_state(self):
        current_time = time.time()
        if current_time >= self.next_action_time and not self.is_dragging and not self.drawing_windows:
            if self.state == "sitting":
                if random.random() < 0.7:
                    self.move_to_random_position()
                elif random.random() < 0.5:
                    self.play()
                else:
                    self.lick()
            elif self.state == "walking":
                if random.random() < 0.3:
                    self.sit()
            elif self.state == "playing" or self.state == "licking":
                if random.random() < 0.5:
                    self.sit()
            self.next_action_time = current_time + random.uniform(2, 5)

    def move_to_random_position(self):
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        self.move_to(random.randint(0, screen_width - SCREEN_WIDTH), 
                     random.randint(0, screen_height - SCREEN_HEIGHT))

    def move_to(self, x, y):
        self.target_x = x
        self.target_y = y
        self.direction = 'r' if x > self.rect.x else 'l'
        self.walk()

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, RED, self.rect)

    def interact(self):
        self.sit()
        self.last_interaction_time = time.time()
        pet.start_drawing_windows()

    def resume_random_behavior(self):
        self.is_dragging = False
        self.next_action_time = time.time() + random.uniform(1, 3)
        self.sit()

    def start_drawing_windows(self):
        self.windows_to_draw = []
        side = random.choice(['top', 'left', 'right', 'bottom'])
        
        if side == 'top':
            start_x = random.randint(0, screen_width - DRAGGED_WINDOW_SIZE)
            start_y = -DRAGGED_WINDOW_SIZE
        elif side == 'left':
            start_x = -DRAGGED_WINDOW_SIZE
            start_y = random.randint(0, screen_height - DRAGGED_WINDOW_SIZE)
        elif side == 'right':
            start_x = screen_width
            start_y = random.randint(0, screen_height - DRAGGED_WINDOW_SIZE)
        else:  # bottom
            start_x = random.randint(0, screen_width - DRAGGED_WINDOW_SIZE)
            start_y = screen_height

        target_x = max(0, min(start_x, screen_width - DRAGGED_WINDOW_SIZE))
        target_y = max(0, min(start_y, screen_height - DRAGGED_WINDOW_SIZE))
        self.windows_to_draw.append((start_x, start_y, target_x, target_y))

        self.drawing_windows = True
        self.move_to(start_x, start_y)

    def update_window_drawing(self, qt_app):
        if self.drawing_windows and self.windows_to_draw:
            if self.target_x is None and self.target_y is None:
                start_x, start_y, target_x, target_y = self.windows_to_draw.pop(0)
                new_window = create_window(self, qt_app, start_x, start_y, target_x, target_y)
                windows.append(new_window)
                if self.windows_to_draw:
                    next_window = self.windows_to_draw[0]
                    self.move_to(next_window[0], next_window[1])
                else:
                    self.drawing_windows = False
                    self.resume_random_behavior()

class QtWindow(QMainWindow):
    def __init__(self, start_x, start_y, target_x, target_y):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(DRAGGED_WINDOW_SIZE, DRAGGED_WINDOW_SIZE)
        self.setWindowTitle("meow")
        
        self.label = QLabel(self)
        random_number = random.randint(1, 7)
        image_path = f"assets/images/{random_number}.png"
        self.label.setPixmap(QPixmap(image_path).scaled(DRAGGED_WINDOW_SIZE, DRAGGED_WINDOW_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.label)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.move(start_x, start_y)
        self.show()

        self.target_x = target_x
        self.target_y = target_y
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate_movement)
        self.animation_timer.start(16)  # ~60 FPS

    def animate_movement(self):
        current_pos = self.pos()
        x, y = current_pos.x(), current_pos.y()
        
        if x != self.target_x:
            x += min(move_speed, abs(self.target_x - x)) * (1 if self.target_x > x else -1)
        if y != self.target_y:
            y += min(move_speed, abs(self.target_y - y)) * (1 if self.target_y > y else -1)
        
        self.move(x, y)
        
        if x == self.target_x and y == self.target_y:
            self.animation_timer.stop()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.close()

class QtApp(QApplication):
    def __init__(self, *args, **kwargs):
        super(QtApp, self).__init__(*args, **kwargs)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            self.quit()
        return super(QtApp, self).eventFilter(obj, event)

def create_window(pet, qt_app, start_x, start_y, target_x, target_y):
    qt_window = QtWindow(start_x, start_y, target_x, target_y)
    
    pet_x = target_x - SCREEN_WIDTH
    pet_y = target_y + DRAGGED_WINDOW_SIZE // 2 - SCREEN_HEIGHT // 2
    pet.move_to(pet_x, pet_y)

    return qt_window

pet = Pet()
qt_app = QtApp(sys.argv)
windows = []

clock = pygame.time.Clock()
running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not pet.drawing_windows:
                pet.interact()
                

    pet.update(dt)
    pet.update_window_drawing(qt_app)

    screen.fill((0, 0, 0, 0))
    pet.draw(screen)
    pygame.display.flip()

    qt_app.processEvents()

    # Remove closed windows from the list
    windows = [window for window in windows if window.isVisible()]

pygame.quit()
sys.exit()