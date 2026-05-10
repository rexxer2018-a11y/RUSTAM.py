# -*- coding: utf-8 -*-  --- Последние правки  произведены сегодня 10_05_2026 ---
import pygame
import sqlite3
import random

# --- Константы ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)     # Цвет монеток
RED = (200, 0, 0)        # Цвет врагов
BLUE = (0, 128, 255)     # Цвет игрока
GRAY = (200, 200, 200)

# --- Класс управления Базой Данных (SQLite3) ---
# --- Класс CoinCollectorGame (основной движок) взаимодействует с базой данных не напрямую,---
# ---- -  а через экземпляр LeaderboardDB:   --
class LeaderboardDB:
    def __init__(self, db_name="scores.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        # Создаем таблицу, если она еще не создана
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS leaderboard 
                             (name TEXT, score INTEGER)''')
        self.conn.commit()

    def save_result(self, name, score):
        """Сохранение ника и очков в БД"""
        self.cursor.execute("INSERT INTO leaderboard VALUES (?, ?)", (name, score))
        self.conn.commit()

    def fetch_top_5(self):
        """Получение 5 лучших результатов"""
        self.cursor.execute("SELECT name, score FROM leaderboard ORDER BY score DESC LIMIT 5")
        return self.cursor.fetchall()

# --- Класс Игрока (ООП: Главный персонаж) ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = 40
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BLUE, (size // 2, size // 2), size // 2)
        pygame.draw.circle(self.image, BLACK, (size // 2, size // 2), size // 2, 2)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.speed = 5

    def update(self):
        """Управление стрелками (Пункт 1 задания)"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed

# --- Класс Монетки ---
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = 20
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GOLD, (size // 2, size // 2), size // 2)
        pygame.draw.circle(self.image, BLACK, (size // 2, size // 2), size // 2, 1)
        self.rect = self.image.get_rect(
            center=(random.randint(50, 750), random.randint(50, 550))
        )

# --- Класс Врага ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = 30
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (size // 2, size // 2), size // 2)
        pygame.draw.circle(self.image, BLACK, (size // 2, size // 2), size // 2, 2)
        self.rect = self.image.get_rect(
            center=(random.randint(50, 750), random.randint(50, 550))
        )

# --- Основной класс Игры ---
class CoinCollectorGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Coin Collector - Практическая работа")
        self.clock = pygame.time.Clock()
        self.db = LeaderboardDB()
        self.font = pygame.font.SysFont("Arial", 24)
        self.player_name = ""
        self.score = 0
        self.running = True

    def draw_text(self, text, x, y, color=BLACK):
        surface = self.font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def get_user_name_in_window(self):
        """Запрос имени пользователя в окне игры (Пункт 2 задания)"""
        input_text = ""
        done = False
        while not done:
            self.screen.fill(WHITE)
            self.draw_text("ВВЕДИТЕ ВАШ НИКНЕЙМ:", 280, 200, BLUE)
            
            # Поле ввода
            rect = pygame.Rect(250, 250, 300, 45)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            self.draw_text(input_text, 265, 260)
            
            self.draw_text("Нажмите ENTER для начала", 270, 320, (150, 150, 150))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.player_name = input_text if input_text.strip() else "Игрок"
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        if len(input_text) < 15:
                            input_text += event.unicode
            
            pygame.display.flip()
            self.clock.tick(30)

    def show_start_instructions(self):
        """Интуитивно понятные пояснения (Пункт 8 задания)"""
        self.screen.fill(WHITE)
        self.draw_text(f"Привет, {self.player_name}!", 330, 150, BLUE)
        self.draw_text("ПРАВИЛА ИГРЫ:", 330, 220)
        self.draw_text("- Собирай желтые монетки (нужно 10)", 220, 260)
        self.draw_text("- Избегай красных врагов", 220, 290)
        self.draw_text("- Управление: СТРЕЛКИ на клавиатуре", 220, 320)
        self.draw_text("Нажмите ЛЮБУЮ КЛАВИШУ для старта", 230, 450, (100, 100, 100))
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); exit()
                if event.type == pygame.KEYDOWN: waiting = False

    def run(self):
        self.get_user_name_in_window()
        self.show_start_instructions()

        all_sprites = pygame.sprite.Group()
        coins = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        
        player = Player()
        all_sprites.add(player)
        
        for _ in range(6):
            c = Coin(); coins.add(c); all_sprites.add(c)
        for _ in range(4):
            e = Enemy(); enemies.add(e); all_sprites.add(e)

        game_over = False
        won = False

        while self.running:
            self.screen.fill(WHITE)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False

            if not game_over:
                all_sprites.update()

                # Сбор монет (Пункт 3: Подсчет очков)
                if pygame.sprite.spritecollide(player, coins, True):
                    self.score += 1
                    if self.score < 10:
                        new_c = Coin(); coins.add(new_c); all_sprites.add(new_c)
                    else:
                        won = True; game_over = True # Возможность выиграть (Пункт 4)

                # Столкновение с врагом
                if pygame.sprite.spritecollide(player, enemies, False):
                    won = False; game_over = True # Возможность проиграть (Пункт 4)

                all_sprites.draw(self.screen)
                self.draw_text(f"Счёт: {self.score} / 10", 10, 10)
            else:
                self.db.save_result(self.player_name, self.score)
                self.show_final_screen(won)
                self.running = False

            pygame.display.flip()
            self.clock.tick(60)

    def show_final_screen(self, won):
        """Вывод Топ-5 игроков (Пункты 5 и 6 задания)"""
        self.screen.fill(WHITE)
        title = "ВЫ ПОБЕДИЛИ!" if won else "ИГРА ОКОНЧЕНА"
        color = (0, 150, 0) if won else RED
        
        self.draw_text(title, 310, 80, color)
        self.draw_text(f"Ваш результат: {self.score}", 315, 130)
        
        self.draw_text("--- ТОП-5 ЛУЧШИХ ---", 300, 220, BLUE)
        leaders = self.db.fetch_top_5()
        for i, (name, val) in enumerate(leaders):
            self.draw_text(f"{i+1}. {name}: {val}", 320, 260 + i*30)

        self.draw_text("Нажмите ESC для выхода", 290, 500, (150, 150, 150))
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: waiting = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    waiting = False
        pygame.quit()

if __name__ == "__main__":
    game = CoinCollectorGame()
    game.run()
