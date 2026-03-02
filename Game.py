import arcade

from pyglet.graphics import Batch

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SPEED = 7


class Goomba(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("assets/Characters/Enemies/Goomba/goomba1.png", scale=2)
        self.center_x = x
        self.center_y = y
        self.change_x = -2

        # Загружаем текстуры
        self.walk_textures = [
            arcade.load_texture("assets/Characters/Enemies/Goomba/goomba1.png"),
            arcade.load_texture("assets/Characters/Enemies/Goomba/goomba2.png")
        ]
        self.die_texture = arcade.load_texture("assets/Characters/Enemies/Goomba/goomba_die.png")

        self.cur_texture = 0
        self.anim_timer = 0
        self.is_dead = False  # Флаг жизни
        self.death_timer = 0  # Таймер до полного исчезновения

    def update_animation(self, delta_time: float = 1 / 60):
        if self.is_dead:
            return  # Если мертв, обычную анимацию не крутим

        self.anim_timer += delta_time
        if self.anim_timer > 0.2:
            self.anim_timer = 0
            self.cur_texture = (self.cur_texture + 1) % len(self.walk_textures)
            self.texture = self.walk_textures[self.cur_texture]


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLUE_GRAY  # Фон для меню

        self.batch = Batch()
        self.main_text = arcade.Text("Главное Меню", self.window.width / 2, self.window.height / 2 + 50,
                                     arcade.color.WHITE, font_size=40, anchor_x="center", batch=self.batch)
        self.space_text = arcade.Text("Нажми SPACE, чтобы начать!", self.window.width / 2, self.window.height / 2 - 50,
                                      arcade.color.WHITE, font_size=20, anchor_x="center", batch=self.batch)

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            game_view = Super_Mario_Bros_game()  # Создаём игровой вид
            self.window.show_view(game_view)  # Переключаем


class Super_Mario_Bros_game(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.PASTEL_BLUE)
        self.now_texture = "assets/Characters/Big Mario/big_mario_idle.png"
        self.moving_right_list = []
        self.moving_left_list = []
        self.jumping_right_list = []
        self.jumping_left_list = []
        for i in range(3):
            self.moving_right_list.append(arcade.load_texture(f"assets/Characters/Big Mario/big_mario_move{i + 1}.png"))
        for i in range(3):
            texture = arcade.load_texture(f"assets/Characters/Big Mario/big_mario_move{i + 1}.png").flip_left_right()
            self.moving_left_list.append(texture)
        self.now_number = 0
        self.is_moving_left = False
        self.is_moving_Right = False
        self.tile_map = None
        self.Mario = None
        self.player_list = None
        self.physics_engine = None
        self.speed_left = 0
        self.speed_right = 0
        self.world_camera = arcade.camera.Camera2D()
        self.animation_time = 0
        self.tile_map = arcade.load_tilemap(r"assets/Stages/World 1-1 (с включенными тайлсетами).tmx", scaling=3)
        self.map_width = self.tile_map.width * self.tile_map.tile_width * 3  # 3 - это твой scaling
        self.map_height = self.tile_map.height * self.tile_map.tile_height * 3

        self.Mario = arcade.Sprite(r"assets/Characters/Big Mario/big_mario_idle.png", scale=2)

        # Загружаем музыку (укажи свой путь к файлу)
        self.bg_music = arcade.load_sound("assets/Soundtrack/01. Ground Theme.flac")
        # Запускаем музыку (loop=True для зацикливания, volume от 0.0 до 1.0)
        self.music_player = arcade.play_sound(self.bg_music, volume=0.5, loop=True)
        self.jump_sound = arcade.load_sound(
            "assets/Soundtrack/NES - Super Mario Bros. - Miscellaneous - Sound Effects/jump.wav")
        self.stomp_sound = arcade.load_sound(
            "assets/Soundtrack/NES - Super Mario Bros. - Miscellaneous - Sound Effects/stompswim.wav")
        self.hit_block_sound = arcade.load_sound(
            "assets/Soundtrack/NES - Super Mario Bros. - Miscellaneous - Sound Effects/bump.wav")

        if self.tile_map:
            self.Mario.center_x = 200  # Начальная позиция
            self.Mario.center_y = 200

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.Mario)

        self.enemy_list = arcade.SpriteList()
        self.enemy_list.append(Goomba(800, 200))  # Пример спавна

        if self.tile_map:
            walls = []
            if "Блоки" in self.tile_map.sprite_lists:
                walls.append(self.tile_map.sprite_lists["Блоки"])
            if "Земля" in self.tile_map.sprite_lists:
                walls.append(self.tile_map.sprite_lists["Земля"])

            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.Mario,
                walls,
                gravity_constant=0.55
            )
            self.blocks = self.tile_map.sprite_lists["Блоки"]
            self.coins = arcade.SpriteList()

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        if self.tile_map:
            for key in self.tile_map.sprite_lists:
                self.tile_map.sprite_lists[key].draw()

        if self.player_list:
            self.player_list.draw()

        self.enemy_list.draw()

    def on_update(self, delta_time: float):
        self.physics_engine.update()

        # Находим врагов, с которыми столкнулся Марио
        enemy_hit_list = arcade.check_for_collision_with_list(self.Mario, self.enemy_list)

        for enemy in enemy_hit_list:
            # Если враг уже мертв (в процессе исчезновения), игнорируем его
            if enemy.is_dead:
                continue

            # Прыжок сверху (проверяем, что Марио падает и он выше центра врага)
            if self.Mario.change_y < 0 and self.Mario.bottom > enemy.center_y:
                enemy.is_dead = True
                enemy.change_x = 0  # Останавливаем движение
                enemy.texture = enemy.die_texture  # Меняем спрайт на сплющенный
                self.Mario.change_y = 10  # Подскок Марио
                arcade.play_sound(self.stomp_sound)
            else:
                # Если коснулся живого врага не сверху — рестарт уровня
                self.music_player.pause()
                self.__init__()

        # Если Марио летит вверх (прыгает)
        if self.Mario.change_y > 0:
            # Проверяем коллизии с блоками
            hit_blocks = arcade.check_for_collision_with_list(self.Mario, self.blocks)
            for block in hit_blocks:
                # Убеждаемся, что Марио ударил блок ИМЕННО снизу
                if self.Mario.top >= block.bottom > self.Mario.bottom:
                    # Делаем простую анимацию: смещаем блок вверх
                    # В идеале здесь нужно запустить таймер, чтобы вернуть блок обратно
                    block.center_y += 5
                    # Добавь звук удара о блок
                    arcade.play_sound(self.hit_block_sound)

        self.animation_time += delta_time

        # 1. Обновление скорости
        self.Mario.change_x = self.speed_right + self.speed_left

        # 2. Логика камеры (Плавное следование без ухода под землю)
        target_x = self.Mario.center_x - (self.window.width / 2)
        target_y = self.Mario.center_y - (self.window.height / 2)

        # Ограничиваем, чтобы не видеть левый край (0) и правый край карты
        if target_x < 0:
            target_x = 0
        elif target_x > self.map_width - self.window.width:
            target_x = self.map_width - self.window.width

        # Ограничиваем по высоте (обычно в Марио камера не сильно прыгает вверх-вниз)
        if target_y < 0:
            target_y = 0
        elif target_y > self.map_height - self.window.height:
            target_y = self.map_height - self.window.height

        # Устанавливаем позицию мгновенно, чтобы Марио всегда был в центре
        self.world_camera.position = (int(target_x), int(target_y))

        for enemy in self.enemy_list:
            if enemy.is_dead:
                enemy.death_timer += delta_time
                if enemy.death_timer > 0.5:  # Исчезнет через полсекунды
                    enemy.remove_from_sprite_lists()
            else:
                # Обычное движение только для живых
                enemy.center_x += enemy.change_x
                enemy.update_animation(delta_time)

            # Простая проверка стен для врага (разворот)
            if arcade.check_for_collision_with_list(enemy, self.blocks):
                enemy.change_x *= -1

        # 3. Логика анимации
        if self.animation_time > 0.1:
            self.animation_time = 0

            # Если в воздухе (не можем прыгнуть)
            if not self.physics_engine.can_jump():
                jump_texture = arcade.load_texture("assets/Characters/Big Mario/big_mario_jump.png")
                if self.is_moving_left:
                    self.Mario.texture = jump_texture.flip_left_right()
                else:
                    self.Mario.texture = jump_texture

            # Если стоим на месте
            elif self.speed_left == 0 and self.speed_right == 0:
                self.Mario.texture = arcade.load_texture("assets/Characters/Big Mario/big_mario_idle.png")
                self.is_moving_Right = False
                self.is_moving_left = False

            # Если идем вправо
            elif self.speed_right > 0:
                self.is_moving_Right = True
                self.is_moving_left = False
                self.now_number = (self.now_number + 1) % 3
                self.Mario.texture = self.moving_right_list[self.now_number]

            # Если идем влево
            elif self.speed_left < 0:
                self.is_moving_left = True
                self.is_moving_Right = False
                self.now_number = (self.now_number + 1) % 3
                self.Mario.texture = self.moving_left_list[self.now_number]

    def on_key_press(self, key: int, modifiers: int):
        if key in [arcade.key.D, arcade.key.RIGHT]:
            self.speed_right = SPEED
        if key in [arcade.key.A, arcade.key.LEFT]:
            self.speed_left = -SPEED
        if key in [arcade.key.W, arcade.key.UP, arcade.key.SPACE]:
            if self.physics_engine and self.physics_engine.can_jump():
                self.Mario.change_y = 15
                arcade.play_sound(self.jump_sound, volume=0.5)

    def on_key_release(self, key: int, modifiers: int):
        if key in [arcade.key.D, arcade.key.RIGHT]:
            self.speed_right = 0
        if key in [arcade.key.A, arcade.key.LEFT]:
            self.speed_left = 0


window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, resizable=True, antialiasing=True)
menu_view = MenuView()
window.show_view(menu_view)
arcade.run()
