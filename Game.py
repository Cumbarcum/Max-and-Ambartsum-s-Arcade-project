import arcade
from pyglet.graphics import Batch
import os


def get_best_time():
    """Читает лучший результат из файла. Если файла нет, возвращает 999.9"""
    if os.path.exists("best_time.txt"):
        with open("best_time.txt", "r") as f:
            try:
                return float(f.read())
            except ValueError:
                return 999.9
    return 999.9


def save_best_time(time_val):
    """Сохраняет новый рекорд в файл"""
    with open("best_time.txt", "w") as f:
        f.write(f"{time_val:.2f}")


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 625
SPEED = 7

# Размеры мёртвой зоны камеры
DEAD_ZONE_W = int(SCREEN_WIDTH * 0.35)
DEAD_ZONE_H = int(SCREEN_HEIGHT * 0.45)
# Плавность слежения камеры
CAMERA_LERP = 0.18


class Goomba(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("assets/Characters/Enemies/Goomba/goomba1.png", scale=2)
        self.center_x = x
        self.center_y = y
        self.change_x = 0  # Изначально стоит на месте!
        self.moving_right = False

        # --- НОВОЕ: Флаг активации ---
        self.is_active = False

        self.walk_textures = [
            arcade.load_texture("assets/Characters/Enemies/Goomba/goomba1.png"),
            arcade.load_texture("assets/Characters/Enemies/Goomba/goomba2.png")
        ]
        self.die_texture = arcade.load_texture("assets/Characters/Enemies/Goomba/goomba_die.png")

        self.cur_texture = 0
        self.anim_timer = 0
        self.is_dead = False
        self.death_timer = 0

    def update_animation(self, delta_time: float = 1 / 60):
        if self.is_dead or not self.is_active:
            return

        self.anim_timer += delta_time
        if self.anim_timer > 0.5:
            self.anim_timer = 0
            self.cur_texture = (self.cur_texture + 1) % len(self.walk_textures)
            self.texture = self.walk_textures[self.cur_texture]


class FinishView(arcade.View):
    """Экран окончания игры (Победа или Поражение) с таймером"""

    def __init__(self, result_text, current_time=0.0):
        super().__init__()
        self.result_text = result_text
        self.current_time = current_time

        # Логика рекордов
        self.best_time = get_best_time()
        self.is_new_record = False

        if "ПОБЕДА" in self.result_text and self.current_time < self.best_time:
            save_best_time(self.current_time)
            self.best_time = self.current_time
            self.is_new_record = True

        self.ui_camera = arcade.camera.Camera2D()
        self.text_elements = []

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        color = arcade.color.GREEN if "ПОБЕДА" in self.result_text else arcade.color.RED

        # Главный текст
        self.text_elements.append(arcade.Text(
            self.result_text, self.window.width / 2, self.window.height / 2 + 100,
            color, font_size=50, anchor_x="center"
        ))

        # Текст времени (только при победе)
        if "ПОБЕДА" in self.result_text:
            time_str = f"Ваше время: {self.current_time:.2f} сек"
            if self.is_new_record:
                time_str += " (НОВЫЙ РЕКОРД!)"

            self.text_elements.append(arcade.Text(
                time_str, self.window.width / 2, self.window.height / 2 + 20,
                arcade.color.LIGHT_GRAY, font_size=25, anchor_x="center"
            ))
            self.text_elements.append(arcade.Text(
                f"Лучшее время: {self.best_time:.2f} сек", self.window.width / 2, self.window.height / 2 - 20,
                arcade.color.GOLD, font_size=20, anchor_x="center"
            ))

        # Инструкция выхода
        self.text_elements.append(arcade.Text(
            "Нажми SPACE, чтобы выйти в меню", self.window.width / 2, self.window.height / 2 - 100,
            arcade.color.WHITE, font_size=20, anchor_x="center"
        ))

    def on_draw(self):
        self.clear()
        self.ui_camera.use()
        for text in self.text_elements:
            text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.window.lives = 3
            self.window.show_view(MenuView())


class LivesView(arcade.View):
    """Промежуточный экран, который сам запускает игру через 2 секунды"""

    def __init__(self):
        super().__init__()
        self.timer = 0.0
        self.ui_camera = arcade.camera.Camera2D()
        self.text = None

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        # Подготавливаем текст заранее
        self.text = arcade.Text(
            f"Жизней осталось: {self.window.lives}",
            self.window.width / 2, self.window.height / 2,
            arcade.color.WHITE, font_size=30, anchor_x="center"
        )

    def on_draw(self):
        self.clear()
        self.ui_camera.use()  # Используем UI камеру, чтобы текст был в центре
        if self.text:
            self.text.draw()

    def on_update(self, delta_time: float):
        self.timer += delta_time
        # Через 2 секунды автоматически переключаем на игру
        if self.timer > 2.0:
            game_view = Super_Mario_Bros_Game()
            self.window.show_view(game_view)


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.main_text = None
        self.lives_text = None
        self.space_text = None

        # --- НОВОЕ: Создаем статичную камеру для UI ---
        self.ui_camera = arcade.camera.Camera2D()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

        self.main_text = arcade.Text(
            "Главное Меню", self.window.width / 2, self.window.height / 2 + 50,
            arcade.color.WHITE, font_size=40, anchor_x="center", anchor_y="center"
        )

        self.lives_text = arcade.Text(
            f"Жизни: {self.window.lives}", self.window.width / 2, self.window.height / 2 - 7,
            arcade.color.RED_DEVIL, font_size=30, anchor_x="center", anchor_y="center"
        )

        self.space_text = arcade.Text(
            "Нажми SPACE, чтобы начать!", self.window.width / 2, self.window.height / 2 - 60,
            arcade.color.WHITE, font_size=20, anchor_x="center", anchor_y="center"
        )

    def on_draw(self):
        self.clear()

        # --- НОВОЕ: Применяем UI камеру перед отрисовкой текста ---
        self.ui_camera.use()

        if self.main_text:
            self.main_text.draw()
            self.lives_text.draw()
            self.space_text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            game_view = Super_Mario_Bros_Game()
            self.window.show_view(game_view)


class Super_Mario_Bros_Game(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.PASTEL_BLUE)

        # --- Состояния игрока ---
        self.is_dead = False
        self.death_phase = 0  # 0: зависание, 1: падение, 2: ожидание рестарта
        self.death_timer = 0.0

        self.is_winning = False
        self.win_phase = 0
        self.win_timer = 0.0

        self.time_elapsed = 0.0  # Таймер прохождения уровня

        # --- Состояния размера Марио (Новое) ---
        self.is_big = True
        self.is_shrinking = False
        self.shrink_timer = 0.0
        self.shrink_frame = 0
        # Заданная вами последовательность анимации:
        self.shrink_sequence = [
            "medium", "big", "medium", "big", "medium", "small",
            "big", "medium", "small", "big", "small"
        ]

        # Заглушки текстур для уменьшения (замените пути на свои)
        self.shrink_textures = {
            "big": arcade.load_texture("assets/Characters/Big Mario/big_mario_idle.png"),
            "medium": arcade.load_texture("assets/Characters/big_mario_turn_into_small1.png"),  # <- Ваш средний спрайт
            "small": arcade.load_texture("assets/Characters/big_mario_turn_into_small2.png")
            # <- Ваш маленький спрайт
        }

        self.now_texture = "assets/Characters/Big Mario/big_mario_idle.png"
        self.moving_right_list = []
        self.moving_left_list = []
        for i in range(3):
            self.moving_right_list.append(arcade.load_texture(f"assets/Characters/Big Mario/big_mario_move{i + 1}.png"))
            texture = arcade.load_texture(f"assets/Characters/Big Mario/big_mario_move{i + 1}.png").flip_left_right()
            self.moving_left_list.append(texture)

        # Наборы для Маленького Марио
        self.small_moving_right = []
        self.small_moving_left = []
        for i in range(3):
            # Укажи правильные пути к своим спрайтам маленького Марио
            tex = arcade.load_texture(f"assets/Characters/Small Mario/small_mario_move{i + 1}.png")
            self.small_moving_right.append(tex)
            self.small_moving_left.append(tex.flip_left_right())

        self.small_idle_right = arcade.load_texture("assets/Characters/Small Mario/small_mario_idle.png")
        self.small_idle_left = self.small_idle_right.flip_left_right()
        self.small_jump = arcade.load_texture("assets/Characters/Small Mario/small_mario_jump.png")

        # Текстуры для спуска
        self.big_flag_slide_textures = [
            arcade.load_texture("assets/Characters/Big Mario/big_mario_slide_down_the_pole1.png"),
            arcade.load_texture("assets/Characters/Big Mario/big_mario_slide_down_the_pole2.png")
        ]
        self.small_flag_slide_textures = [
            arcade.load_texture("assets/Characters/Small Mario/small_mario_slide_down_the_pole1.png"),
            arcade.load_texture("assets/Characters/Small Mario/small_mario_slide_down_the_pole2.png")
        ]
        self.slide_anim_timer = 0

        self.now_number = 0
        self.is_moving_left = False
        self.is_moving_Right = False
        self.speed_left = 0
        self.speed_right = 0
        self.animation_time = 0

        self.world_camera = arcade.camera.Camera2D()

        self.tile_map = arcade.load_tilemap(r"assets/Stages/World 1-1 (с включенными тайлсетами).tmx", scaling=3)
        self.map_width = self.tile_map.width * self.tile_map.tile_width * 3
        self.map_height = self.tile_map.height * self.tile_map.tile_height * 3

        self.Mario = arcade.Sprite(r"assets/Characters/Big Mario/big_mario_idle.png", scale=2)
        self.Mario.center_x = 200  # 8800
        self.Mario.center_y = 200  # 1000

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.Mario)

        self.enemy_list = arcade.SpriteList()
        self.moving_blocks = []

        # --- Механика неуязвимости ---
        self.is_invincible = False
        self.invincible_timer = 0.0
        self.invincible_duration = 2.0  # Длительность в секундах
        self.blink_timer = 0.0  # Таймер для эффекта мигания

        # --- ЗАГРУЗКА ЗВУКОВ ---
        self.bg_music = arcade.load_sound("assets/Soundtrack/01. Ground Theme.flac", streaming=True)
        self.music_player = arcade.play_sound(self.bg_music, volume=0.5, loop=True)
        self.jump_sound = arcade.load_sound(
            "assets/Soundtrack/NES - Super Mario Bros. - Miscellaneous - Sound Effects/jump.wav")
        self.small_jump_sound = arcade.load_sound(
            "assets/Soundtrack/NES - Super Mario Bros. - Miscellaneous - Sound Effects/jumpsmall.wav")
        self.stomp_sound = arcade.load_sound(
            "assets/Soundtrack/NES - Super Mario Bros. - Miscellaneous - Sound Effects/stompswim.wav")
        self.hit_block_sound = arcade.load_sound(
            "assets/Soundtrack/NES - Super Mario Bros. - Miscellaneous - Sound Effects/bump.wav")
        self.shrink_sound = arcade.load_sound(
            "assets/Soundtrack/NES - Super Mario Bros. - Miscellaneous - Sound Effects/pipepowerdown.wav")
        self.death_sound = arcade.load_sound(
            "assets/Soundtrack/NES - Super Mario Bros. - Miscellaneous - Sound Effects/death.wav")
        self.flagpole_sound = arcade.load_sound(
            "assets/Soundtrack/NES - Super Mario Bros. - Miscellaneous - Sound Effects/flagpole.wav")
        self.win_music = arcade.load_sound("assets/Soundtrack/06. Level Complete Theme.flac")

        self.physics_engine = None
        self.enemy_physics_engines = []  # Список движков для врагов
        self.blocks = arcade.SpriteList()
        self.ground = arcade.SpriteList()
        self.flagpoles = arcade.SpriteList()
        self.castles = arcade.SpriteList()

        walls = []
        if self.tile_map:
            if "Блоки" in self.tile_map.sprite_lists:
                self.blocks = self.tile_map.sprite_lists["Блоки"]
                walls.append(self.blocks)
            if "Земля" in self.tile_map.sprite_lists:
                self.ground = self.tile_map.sprite_lists["Земля"]
                walls.append(self.ground)
            if "Столб" in self.tile_map.sprite_lists:
                self.flagpoles = self.tile_map.sprite_lists["Столб"]
            if "Замок" in self.tile_map.sprite_lists:
                self.castles = self.tile_map.sprite_lists["Замок"]

            self.physics_engine = arcade.PhysicsEnginePlatformer(self.Mario, walls, gravity_constant=0.55)

            # --- Генерация нескольких врагов с физикой ---
            enemy_positions = [(800, 200), (1200, 200), (1500, 200)]
            for ex, ey in enemy_positions:
                goomba = Goomba(ex, ey)
                self.enemy_list.append(goomba)
                # Каждый враг получает свой физический движок для гравитации и коллизий
                engine = arcade.PhysicsEnginePlatformer(goomba, walls, gravity_constant=0.55)
                self.enemy_physics_engines.append(engine)

    def mario_die(self):
        """Логика смерти Марио"""
        if self.is_dead or self.is_winning or self.is_shrinking:
            return

        self.is_dead = True
        self.death_phase = 0
        self.death_timer = 0.0
        self.physics_engine = None  # Отключаем физику коллизий

        arcade.stop_sound(self.music_player)
        arcade.play_sound(self.death_sound)

        self.Mario.texture = arcade.load_texture("assets/Characters/Small Mario/small_mario_die.png")
        self.Mario.change_x = 0
        self.Mario.change_y = 0  # Зависаем в воздухе

    def mario_win(self, flagpole_sprite):
        """Инициализация логики победы при касании флага"""
        if self.is_dead or self.is_winning:
            return

        self.is_winning = True
        self.music_player.pause()
        arcade.play_sound(self.flagpole_sound)

        # Отключаем физику для скриптовой сценки
        self.physics_engine = None
        self.Mario.change_x = 0
        self.Mario.change_y = 0
        self.Mario.right = flagpole_sprite.left + 10

    def update_mario_animation(self, delta_time):
        if not self.physics_engine or self.is_shrinking or self.is_winning:
            return

        # 1. ОБНОВЛЯЕМ НАПРАВЛЕНИЕ ВЗГЛЯДА КАЖДЫЙ КАДР
        if self.speed_left < 0:
            self.is_moving_left = True
        elif self.speed_right > 0:
            self.is_moving_left = False

        # 2. ВЫБИРАЕМ ТЕКУЩИЙ НАБОР ТЕКСТУР В ЗАВИСИМОСТИ ОТ РАЗМЕРА
        if self.is_big:
            idle = arcade.load_texture("assets/Characters/Big Mario/big_mario_idle.png")
            jump = arcade.load_texture("assets/Characters/Big Mario/big_mario_jump.png")
            walk_list = self.moving_left_list if self.is_moving_left else self.moving_right_list
        else:
            idle = self.small_idle_left if self.is_moving_left else self.small_idle_right
            jump = self.small_jump
            walk_list = self.small_moving_left if self.is_moving_left else self.small_moving_right

        # 3. ПРИМЕНЯЕМ ТЕКСТУРУ МГНОВЕННО (для прыжка и состояния покоя)
        if not self.physics_engine.can_jump():
            # В воздухе (прыжок или падение)
            self.Mario.texture = jump.flip_left_right() if self.is_moving_left else jump
            return  # Прерываем выполнение, анимация ходьбы в воздухе не нужна

        if self.speed_left == 0 and self.speed_right == 0:
            # Стояние на месте с учетом последнего направления
            if self.is_big:
                self.Mario.texture = idle.flip_left_right() if self.is_moving_left else idle
            else:
                self.Mario.texture = idle  # У малого Марио мы уже выбрали нужный idle выше
            return  # Прерываем выполнение, анимация ходьбы при стоянии не нужна

        # 4. АНИМАЦИЯ ХОДЬБЫ (срабатывает только если мы на земле и двигаемся)
        self.animation_time += delta_time
        if self.animation_time > 0.08:  # Скорость смены ног (чем меньше, тем быстрее перебирает ногами)
            self.animation_time = 0
            self.now_number = (self.now_number + 1) % 3
            self.Mario.texture = walk_list[self.now_number]

    def update_camera(self):
        if not self.Mario or self.is_dead:
            return

            # Центр экрана
        half_w = self.window.width / 2
        half_h = self.window.height / 2

        # Целевая позиция - это Марио, но с ограничениями
        target_x = self.Mario.center_x
        target_y = self.Mario.center_y

        # Ограничение по горизонтали (чтобы не видели край карты)
        target_x = max(half_w, min(self.map_width - half_w, target_x))

        # Не даем камере подняться выше, чем (высота карты - половина экрана - 100)
        target_y = max(half_h, min(self.map_height - half_h - 100, target_y))

        # Текущая позиция камеры
        cur_x, cur_y = self.world_camera.position

        # Применяем плавное следование
        new_x = arcade.math.lerp(cur_x, target_x, CAMERA_LERP)
        new_y = arcade.math.lerp(cur_y, target_y, CAMERA_LERP)

        self.world_camera.position = (new_x, new_y)

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        if self.tile_map:
            for key in self.tile_map.sprite_lists:
                self.tile_map.sprite_lists[key].draw()

        self.enemy_list.draw()

        if self.player_list:
            self.player_list.draw()

    def on_update(self, delta_time: float):
        # Обновляем таймер, если игра активна
        if not self.is_dead and not self.is_winning:
            self.time_elapsed += delta_time

        # 1. Логика смерти (Машина состояний)
        if self.is_dead:
            self.death_timer += delta_time

            if self.death_phase == 0:
                # Фаза 0: Зависание на 0.5 секунды
                if self.death_timer > 0.5:
                    self.death_phase = 1
                    self.Mario.change_y = 10  # Подскок

            elif self.death_phase == 1:
                # Фаза 1: Подскок и падение
                self.Mario.center_y += self.Mario.change_y
                self.Mario.change_y -= 0.3  # Гравитация
                if self.Mario.top < -50:
                    self.death_phase = 2
                    self.death_timer = 0.0  # Сбрасываем таймер для следующей фазы

            elif self.death_phase == 2:
                if self.death_timer > 1.5:
                    self.window.lives -= 1
                    if self.window.lives > 0:
                        # Теперь вызываем экран с авто-стартом
                        self.window.show_view(LivesView())
                    else:
                        # Если жизней 0, выводим финальный экран (там всё еще нужен пробел)
                        self.window.show_view(FinishView("ИГРА ОКОНЧЕНА", self.time_elapsed))
            return

            # 2. Логика уменьшения (Shrinking)
        if self.is_shrinking:

            self.shrink_timer += delta_time
            if self.shrink_timer > 0.05:  # Скорость смены кадров (80мс)
                self.shrink_timer = 0.0
                self.shrink_frame += 1

                # Если анимация завершена:
                if self.shrink_frame >= len(self.shrink_sequence):
                    self.is_shrinking = False
                    self.is_big = False
                    old_bottom = self.Mario.bottom
                    self.Mario.texture = self.shrink_textures["small"]
                    self.Mario.hit_box = arcade.hitbox.HitBox(self.Mario.texture.hit_box_points)
                    # Возвращаем ноги точно на землю
                    self.Mario.bottom = old_bottom + 2
                    # --- НОВОЕ: Включаем неуязвимость сразу после превращения ---
                    self.is_invincible = True
                    self.invincible_timer = self.invincible_duration
                else:
                    # Берем кадр из последовательности и устанавливаем текстуру
                    current_state = self.shrink_sequence[self.shrink_frame]
                    self.Mario.texture = self.shrink_textures[current_state]

            # В процессе уменьшения игра стоит на паузе (возвращаемся из update)
            return

        # --- Обработка неуязвимости (мигание) ---
        if self.is_invincible:
            self.invincible_timer -= delta_time
            self.blink_timer += delta_time

            # Каждые 0.1 сек меняем прозрачность (255 - виден, 100 - полупрозрачен)
            if self.blink_timer > 0.1:
                self.blink_timer = 0
                if self.Mario.alpha == 255:
                    self.Mario.alpha = 100
                else:
                    self.Mario.alpha = 255

            # Когда время вышло
            if self.invincible_timer <= 0:
                self.is_invincible = False
                self.Mario.alpha = 255  # Возвращаем полную видимость

        # Проверка флага
        if not self.is_winning:
            flag_hit = arcade.check_for_collision_with_list(self.Mario, self.flagpoles)
            if flag_hit:
                self.is_winning = True
                self.win_phase = 0
                self.physics_engine = None
                self.Mario.change_x = 0
                self.Mario.change_y = 0
                arcade.stop_sound(self.music_player)
                arcade.play_sound(self.flagpole_sound)
                self.Mario.center_x = flag_hit[0].center_x - 15

        # 3. ОБРАБОТКА ПОБЕДЫ
        if self.is_winning:
            if self.win_phase == 0:
                self.slide_anim_timer += delta_time
                if self.slide_anim_timer > 0.15:
                    self.slide_anim_timer = 0
                    self.now_number = (self.now_number + 1) % len(self.big_flag_slide_textures)
                    self.Mario.texture = self.big_flag_slide_textures[self.now_number] if self.is_big else \
                        self.small_flag_slide_textures[self.now_number]

                self.Mario.center_y -= 4

                if arcade.check_for_collision_with_list(self.Mario, self.blocks) or \
                        arcade.check_for_collision_with_list(self.Mario, self.ground):
                    self.win_phase = 1
                    self.Mario.change_x = 3
                    self.Mario.change_y = 5
                    arcade.play_sound(self.win_music)

            elif self.win_phase == 1:
                self.Mario.center_x += self.Mario.change_x
                self.Mario.center_y += self.Mario.change_y
                self.Mario.change_y -= 0.5
                self.Mario.texture = self.moving_right_list[0] if self.is_big else self.small_moving_right[0]

                hit_ground = arcade.check_for_collision_with_list(self.Mario, self.ground)
                if hit_ground and self.Mario.change_y < 0:
                    self.Mario.bottom = hit_ground[0].top
                    self.Mario.change_y = 0
                    self.win_phase = 2

            elif self.win_phase == 2:
                self.Mario.center_x += 3
                self.animation_time += delta_time
                if self.animation_time > 0.1:
                    self.animation_time = 0
                    self.now_number = (self.now_number + 1) % 3
                    self.Mario.texture = self.moving_right_list[self.now_number] if self.is_big else \
                        self.small_moving_right[self.now_number]

                on_ground = arcade.check_for_collision_with_list(self.Mario, self.ground)
                if not on_ground:
                    self.Mario.center_y -= 5

                if self.Mario.center_x > self.castles[0].center_x:
                    self.win_phase = 3
                    self.Mario.alpha = 0

            elif self.win_phase == 3:
                self.win_timer += delta_time
                if self.win_timer > 4:
                    # Победа: отправляем на экран FinishView с соответствующим текстом
                    self.window.show_view(FinishView("ПОБЕДА!", self.time_elapsed))

            return

            # --- ОБЫЧНЫЙ ИГРОВОЙ ЦИКЛ ---
        if self.physics_engine:
            self.physics_engine.update()

            if self.Mario.left < 0:
                self.Mario.left = 0

        # Обновление физики для врагов
        for engine in self.enemy_physics_engines:
            engine.update()

        # Проверка падения в пропасть
        if self.Mario.bottom < 0:
            self.mario_die()

        # Логика коллизий с врагами
        enemy_hit_list = arcade.check_for_collision_with_list(self.Mario, self.enemy_list)
        for enemy in enemy_hit_list:
            if enemy.is_dead:
                continue

            # Прыжок сверху (успешная атака)
            if self.Mario.change_y < 0 and self.Mario.bottom > enemy.center_y:
                enemy.is_dead = True
                enemy.change_x = 0
                enemy.texture = enemy.die_texture
                self.Mario.change_y = 10
                arcade.play_sound(self.stomp_sound)
            else:
                # Если Марио неуязвим — просто игнорируем контакт
                if self.is_invincible:
                    continue
                # Столкновение (урон)
                if self.is_big:
                    # Если Большой: запуск анимации уменьшения
                    self.shrink_sound.play()
                    self.is_shrinking = True
                    self.shrink_frame = 0
                    self.shrink_timer = 0.0
                    self.Mario.change_x = 0
                    self.Mario.change_y = 0
                else:
                    # Если Маленький: смерть
                    self.mario_die()

        self.Mario.change_x = self.speed_right + self.speed_left
        self.update_mario_animation(delta_time)
        self.update_camera()

        # Обработка врагов (обновленная с ленивой активацией)
        for enemy in self.enemy_list:
            if enemy.is_dead:
                enemy.death_timer += delta_time
                if enemy.death_timer > 0.5:
                    enemy.remove_from_sprite_lists()
            else:
                # --- Активация врага при приближении Марио ---
                if not enemy.is_active:
                    distance = abs(enemy.center_x - self.Mario.center_x)
                    if distance < 800:  # Радиус активации (примерно ширина экрана)
                        enemy.is_active = True
                        enemy.change_x = 2 if enemy.moving_right else -2

                enemy.update_animation(delta_time)

                # Разворот при столкновении со стеной
                if enemy.is_active and enemy.change_x == 0:
                    enemy.moving_right = not enemy.moving_right
                    enemy.change_x = 2 if enemy.moving_right else -2

    def on_key_press(self, key: int, modifiers: int):
        if self.is_dead or self.is_winning or self.is_shrinking or self.is_winning:
            return

        if key in [arcade.key.D, arcade.key.RIGHT]:
            self.speed_right = SPEED
        if key in [arcade.key.A, arcade.key.LEFT]:
            self.speed_left = -SPEED
        if key in [arcade.key.W, arcade.key.UP, arcade.key.SPACE]:
            if self.physics_engine and self.physics_engine.can_jump():
                self.Mario.change_y = 15
                arcade.play_sound(self.jump_sound, volume=0.5) if self.is_big else arcade.play_sound(
                    self.small_jump_sound, volume=0.5)

    def on_key_release(self, key: int, modifiers: int):
        if self.is_dead or self.is_winning:
            return

        if key in [arcade.key.D, arcade.key.RIGHT]:
            self.speed_right = 0
        if key in [arcade.key.A, arcade.key.LEFT]:
            self.speed_left = 0


# Запуск
if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Super Mario Bros")
    # Глобальная переменная окна для хранения жизней (доступна из любого View)
    window.lives = 3
    window.show_view(MenuView())
    arcade.run()
