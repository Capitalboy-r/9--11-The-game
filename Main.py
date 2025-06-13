import pygame
import random
from PIL import Image  # pip install pillow

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600
GROUND_HEIGHT = 50
FPS = 60
pygame.display.set_caption("9/11 the game: OG Version")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)

# Mute state
is_muted = False

def toggle_mute():
    global is_muted
    is_muted = not is_muted
    volume = 0 if is_muted else 0.5
    pygame.mixer.music.set_volume(volume)
    introSong.set_volume(0 if is_muted else 1)
    explosion_sound.set_volume(0 if is_muted else 1)

# Load and resize images
plane_img = pygame.image.load("assets/plane.png")
plane_img = pygame.transform.scale(plane_img, (50, 35))
bg_img = pygame.image.load("assets/background.png")
bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
sky_scrapper_img = pygame.image.load("assets/Skyscraper.png")
enemy_img = pygame.image.load("assets/enemy.png")
enemy_img = pygame.transform.scale(enemy_img, (50, 50))
ground_texture = pygame.image.load("assets/Ground.png")
ground_texture = pygame.transform.scale(ground_texture, (500, GROUND_HEIGHT))
ground_texture_width = ground_texture.get_width()

# Load sounds
introSong = pygame.mixer.Sound("sounds/Intro.mp3")
pygame.mixer.music.load("sounds/Improvised_Explosive_Device.mp3")
pygame.mixer.music.set_volume(0.5)
explosion_sound = pygame.mixer.Sound("sounds/explosion_sound.wav")

# Load explosion GIF
explosion_gif = Image.open("assets/explosion.gif")
explosion_frames = []
for frame in range(explosion_gif.n_frames):
    explosion_gif.seek(frame)
    frame_surface = pygame.image.fromstring(explosion_gif.tobytes(), explosion_gif.size, explosion_gif.mode)
    frame_surface = pygame.transform.scale(frame_surface, (120, 120))
    explosion_frames.append(frame_surface)

# Game Variables
gravity = 0.5
plane_speed = 0
building_gap = 150
building_width = 80
building_speed = 3
enemy_speed = 4
bullet_speed = 10
min_building_height = 100
max_building_height = 450
score = 0
top_score = 0
building_spawn_rate = 90
enemy_spawn_rate = 120
spawn_rate = 0

# Classes
class Plane:
    def __init__(self, x, y):
        self.image = plane_img
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        self.rect.y += plane_speed

class Building:
    def __init__(self, x, y, width, height, image):
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.passed = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        self.rect.x -= building_speed

class Enemy:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        self.rect.x -= enemy_speed

class Bullet:
    def __init__(self, x, y):
        self.image = pygame.Surface((10, 5))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        self.rect.x += bullet_speed

class Explosion:
    def __init__(self, x, y):
        self.frames = explosion_frames
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.index += 1
            if self.index >= len(self.frames):
                return False
            self.image = self.frames[self.index]
        return True

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# Utility functions
def create_buildings():
    height = random.randint(min_building_height, max_building_height)
    return Building(SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT - height, building_width, height, sky_scrapper_img)

def create_enemy():
    x = SCREEN_WIDTH
    y = random.randint(50, SCREEN_HEIGHT - GROUND_HEIGHT - 50)
    return Enemy(x, y, enemy_img)

def show_instructions():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.SysFont(None, 35)
    instructions = [
        "Instructions:",
        "Press SPACE to fly up",
        "Press S to shoot",
        "Avoid buildings/enemies",
        "Press any key to return",
        "M to mute/unmute song"
    ]
    waiting = True
    while waiting:
        screen.fill(WHITE)
        screen.blit(bg_img, (0, 0))
        for i, line in enumerate(instructions):
            text = font.render(line, True, BLACK)
            screen.blit(text, (50, 100 + i * 40))

        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def defeat_screen(final_score):
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.SysFont(None, 55)
    small_font = pygame.font.SysFont(None, 35)
    title_text = font.render("Game Over", True, RED)
    score_text = small_font.render(f"Your Score: {final_score}", True, BLACK)
    retry_text = small_font.render("Press R to Retry or Q to Quit", True, BLACK)

    while True:
        screen.fill(WHITE)
        screen.blit(bg_img, (0, 0))
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)))
        screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
        screen.blit(retry_text, retry_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)))

        mute_icon = pygame.font.SysFont(None, 40).render("M to unmute" if is_muted else "M to mute", True, BLACK)
        mute_rect = pygame.Rect(SCREEN_WIDTH - 120, 20, 40, 40)
        screen.blit(mute_icon, mute_icon.get_rect(center=mute_rect.center))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main(); return
                if event.key == pygame.K_q:
                    pygame.quit(); exit()
                if event.key == pygame.K_m:
                    toggle_mute()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if mute_rect.collidepoint(event.pos):
                    toggle_mute()

def start_menu():
    global building_speed, enemy_speed, gravity, building_spawn_rate, enemy_spawn_rate, spawn_rate, max_building_height
    pygame.mixer.music.stop()
    introSong.play()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.SysFont(None, 55)
    small_font = pygame.font.SysFont(None, 35)

    while True:
        screen.fill(WHITE)
        screen.blit(bg_img, (0, 0))
        title = font.render("9/11 THE GAME", True, RED)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 100)))

        buttons = {
            "Easy": pygame.Rect(70, 250, 100, 50),
            "Medium": pygame.Rect(200, 250, 100, 50),
            "Hard": pygame.Rect(330, 250, 100, 50),
            "How to play": pygame.Rect(150, 330, 200, 50)
        }

        for text, rect in buttons.items():
            pygame.draw.rect(screen, BROWN if text == "How to play" else RED if text == "Hard" else BLUE if text == "Medium" else GREEN, rect)
            label = small_font.render(text, True, WHITE)
            screen.blit(label, label.get_rect(center=rect.center))

        mute_icon = pygame.font.SysFont(None, 40).render("M to Unmute" if is_muted else "M to Mute", True, BLACK)
        mute_rect = pygame.Rect(SCREEN_WIDTH - 120, 20, 40, 40)
        screen.blit(mute_icon, mute_icon.get_rect(center=mute_rect.center))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if mute_rect.collidepoint(pos):
                    toggle_mute()
                elif buttons["Easy"].collidepoint(pos):
                    building_speed = 3
                    enemy_speed = 4
                    gravity = 0.5
                    building_spawn_rate = 120
                    enemy_spawn_rate = 180
                    max_building_height = SCREEN_HEIGHT - SCREEN_HEIGHT/2
                    introSong.stop(); main(); return
                elif buttons["Medium"].collidepoint(pos):
                    building_speed = 4
                    enemy_speed = 5
                    gravity = 0.6
                    building_spawn_rate = 100
                    enemy_spawn_rate = 160
                    max_building_height = SCREEN_HEIGHT - 350
                    introSong.stop(); main(); return
                elif buttons["Hard"].collidepoint(pos):
                    building_speed = 5
                    enemy_speed = 6
                    gravity = 0.7
                    building_spawn_rate = 80
                    enemy_spawn_rate = 140
                    max_building_height = SCREEN_HEIGHT - 160
                    introSong.stop(); main(); return
                elif buttons["How to play"].collidepoint(pos):
                    show_instructions()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                toggle_mute()

def main():
    global plane_speed, score, top_score, spawn_rate
    pygame.mixer.music.play(-1)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    plane = Plane(100, SCREEN_HEIGHT // 2)
    buildings, enemies, bullets, explosions = [], [], [], []
    running = True
    score = 0
    spawn_rate = 0

    while running:
        screen.fill(WHITE)
        screen.blit(bg_img, (0, 0))
        plane_speed += gravity
        plane.update()
        plane.draw(screen)

        if spawn_rate % building_spawn_rate == 0:
            buildings.append(create_buildings())

        for building in buildings[:]:
            building.update()
            building.draw(screen)
            if building.rect.right < 0:
                buildings.remove(building)
            if building.rect.colliderect(plane.rect):
                explosion_sound.play()
                explosions.append(Explosion(plane.rect.centerx, plane.rect.centery))
                running = False
            if not building.passed and building.rect.right < plane.rect.left:
                score += 1
                building.passed = True

        if spawn_rate % enemy_spawn_rate == 0:
            enemies.append(create_enemy())

        for enemy in enemies[:]:
            enemy.update()
            enemy.draw(screen)
            if enemy.rect.right < 0:
                enemies.remove(enemy)
            if enemy.rect.colliderect(plane.rect):
                explosion_sound.play()
                explosions.append(Explosion(plane.rect.centerx, plane.rect.centery))
                running = False

        for bullet in bullets[:]:
            bullet.update()
            bullet.draw(screen)
            for enemy in enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
                    enemies.remove(enemy)
                    if bullet in bullets:
                        bullets.remove(bullet)
                    explosion_sound.play()
                    score += 2

        for explosion in explosions[:]:
            if not explosion.update():
                explosions.remove(explosion)
            explosion.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    plane_speed = -10
                if event.key == pygame.K_s:
                    bullets.append(Bullet(plane.rect.right, plane.rect.centery))
                if event.key == pygame.K_m:
                    toggle_mute()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mute_rect = pygame.Rect(SCREEN_WIDTH - 60, 10, 40, 40)
                if mute_rect.collidepoint(event.pos):
                    toggle_mute()

        if plane.rect.top <= 0 or plane.rect.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT:
            explosion_sound.play()
            explosions.append(Explosion(plane.rect.centerx, plane.rect.centery))
            running = False

        score_font = pygame.font.SysFont(None, 35)
        screen.blit(score_font.render(f'Score: {score}', True, BLACK), (10, 10))
        if score > top_score:
            top_score = score
        screen.blit(score_font.render(f'Top Score: {top_score}', True, BLACK), (10, 40))

        for i in range(0, SCREEN_WIDTH, ground_texture_width):
            screen.blit(ground_texture, (i, SCREEN_HEIGHT - GROUND_HEIGHT))

        # Draw mute icon
        mute_icon = pygame.font.SysFont(None, 40).render("M to Unmute" if is_muted else "M to Mute", True, BLACK)
        mute_rect = pygame.Rect(SCREEN_WIDTH - 120, 10, 40, 40)
        screen.blit(mute_icon, mute_icon.get_rect(center=mute_rect.center))

        pygame.display.flip()
        clock.tick(FPS)
        spawn_rate += 1

    pygame.mixer.music.stop()
    defeat_screen(score)

# Launch the game
start_menu()
