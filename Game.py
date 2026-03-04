from symtable import Class

import arcade
import random

from PIL.ImageOps import scale
from arcade.examples.view_instructions_and_game_over import GameOverView
from pyglet.graphics import Batch

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1200
SPEED = 6
from pyglet.graphics import Batch

class WinMenu(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLUE_GREEN  # Фон для меню

        self.batch = Batch()
        self.main_text = arcade.Text("You win!!!", SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2 + 150,
                                     arcade.color.WHITE, font_size=40, anchor_x="center", batch=self.batch)
        self.space_text = arcade.Text("Нажми SPACE, чтобы начать занова!", SCREEN_WIDTH / 2 - 200,
                                      SCREEN_HEIGHT / 2 + 50,
                                      arcade.color.WHITE, font_size=20, anchor_x="center", batch=self.batch)
        self.camera = arcade.camera.Camera2D()
        self.camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 75)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.batch.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            game_view = Super_Mario_baros_game()  # Создаём игровой вид
            self.window.show_view(game_view)  # Переключаем
class MenuGameOver(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.RED  # Фон для меню

        self.batch = Batch()
        self.main_text = arcade.Text("Game Over", SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2 + 150,
                                     arcade.color.WHITE, font_size=40, anchor_x="center", batch=self.batch)
        self.space_text = arcade.Text("Нажми SPACE, чтобы начать занова!", SCREEN_WIDTH / 2 - 200,
                                      SCREEN_HEIGHT / 2 + 50,
                                      arcade.color.WHITE, font_size=20, anchor_x="center", batch=self.batch)
        self.camera = arcade.camera.Camera2D()
        self.camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 75)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.batch.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            game_view = Super_Mario_baros_game()  # Создаём игровой вид
            self.window.show_view(game_view)  # Переключаем


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.BLUE_GRAY  # Фон для меню

        self.batch = Batch()
        self.main_text = arcade.Text("Главное Меню", SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2 + 150,
                                     arcade.color.WHITE, font_size=40, anchor_x="center", batch=self.batch)
        self.space_text = arcade.Text("Нажми SPACE, чтобы начать!", SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2 + 50,
                                      arcade.color.WHITE, font_size=20, anchor_x="center", batch=self.batch)
        self.camera = arcade.camera.Camera2D()
        self.camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 75)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.batch.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            game_view = Super_Mario_baros_game()  # Создаём игровой вид
            self.window.show_view(game_view)  # Переключаем


class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view  # Сохраняем, чтобы вернуться
        self.batch = Batch()
        self.pause_text = arcade.Text("Пауза", self.window.width / 2 - 325, self.window.height / 2 + 100,
                                      arcade.color.WHITE, font_size=40, anchor_x="center", batch=self.batch)
        self.space_text = arcade.Text("Нажми SPACE, чтобы продолжить", self.window.width / 2 - 300,
                                      self.window.height / 2 + 50,
                                      arcade.color.WHITE, font_size=20, anchor_x="center", batch=self.batch)
        self.camera = arcade.camera.Camera2D()
        self.camera.position = (self.window.width / 2 - 100, self.window.height / 2)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.batch.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.window.show_view(self.game_view)


class Super_Mario_baros_game(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.PASTEL_BLUE)
        self.now_texture = "assets/Characters/Big Mario/big_mario_idle.png"
        self.moving_right_list = []
        self.moving_left_list = []
        self.jumping_right_list = []
        self.jumping_left_list = []
        self.mushroom_list = arcade.SpriteList()
        for i in range(3):
            self.moving_right_list.append(arcade.load_texture(f"assets/Characters/Big Mario/big_mario_move{i + 1}.png"))
        for i in range(3):
            texture = arcade.load_texture(f"assets/Characters/Big Mario/big_mario_move{i + 1}.png").flip_left_right()
            self.moving_left_list.append(texture)
            self.number_coins = 0
        self.now_number = 0
        self.time = 120
        self.number_points = 0
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
        self.tile_map = arcade.load_tilemap(r"assets/Stages/Mario_World.tmx", scaling=3)
        self.coin_texture = arcade.load_texture("assets/coin.png")
        self.coins_list = arcade.SpriteList()

        self.Mario = arcade.Sprite(r"assets/Characters/Big Mario/big_mario_idle.png", scale=2)

        if self.tile_map:
            self.Mario.center_x = 200  # Начальная позиция
            self.Mario.center_y = 200

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.Mario)
        self.mushrooms()

        for lacky_box in self.tile_map.sprite_lists["Блоки"]:
            lacky_box.flag = True
            lacky_box.origibal_y = lacky_box.center_y
            lacky_box.first = True
            lacky_box.back = True
        #self.mushroom  = arcade.Sprite("assets/mushroom.png", scale=0.05)
        #self.player_list.append(self.mushroom)
        #self.mushroom.center_y = 200
        #self.mushroom.center_x = 230
        if self.tile_map:
            walls = []
            if "Блоки" in self.tile_map.sprite_lists:
                walls.append(self.tile_map.sprite_lists["Блоки"])
            if "Земля" in self.tile_map.sprite_lists:
                walls.append(self.tile_map.sprite_lists["Земля"])

            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.Mario,
                walls,
                gravity_constant=0.5
            )
            #self.mushroom_physics_engine = arcade.PhysicsEnginePlatformer(
            #    self.mushroom,
            #    walls,
            #    gravity_constant=0.5
            #)
            self.blocks = self.tile_map.sprite_lists["Блоки"]
    def dangerous(self):
        for mushroom in arcade.check_for_collision_with_list(self.Mario, self.mushroom_list):
            if mushroom.center_y + mushroom.height // 2 >= self.Mario.center_y - self.Mario.height // 2 >= mushroom.center_y + mushroom.height // 2 - 30:
                self.mushroom_list.remove(mushroom)
                self.number_points += 100
            else:
                game_over = MenuGameOver()
                self.window.show_view(game_over)
    def mushrooms(self):
        muchroom = Muchroom(1000)
        self.mushroom_list.append(muchroom)
        muchroom = Muchroom(1600)
        self.mushroom_list.append(muchroom)
        muchroom = Muchroom(2000)
        self.mushroom_list.append(muchroom)
        muchroom = Muchroom(2400)
        self.mushroom_list.append(muchroom)
        muchroom = Muchroom(2500)
        self.mushroom_list.append(muchroom)
        muchroom = Muchroom(3700)
        self.mushroom_list.append(muchroom)
        muchroom = Muchroom(3600)
        self.mushroom_list.append(muchroom)
        muchroom = Muchroom(4900)
        self.mushroom_list.append(muchroom)
        muchroom = Muchroom(4800)
        self.mushroom_list.append(muchroom)
        muchroom = Muchroom(4700)
        self.mushroom_list.append(muchroom)
        muchroom = Muchroom(4600)
        self.mushroom_list.append(muchroom)
        muchroom = Muchroom(7060)
        self.mushroom_list.append(muchroom)
        muchroom = Muchroom(7000)
        self.mushroom_list.append(muchroom)
        muchroom = Muchroom(8500)
        self.mushroom_list.append(muchroom)
        muchroom = Muchroom(8400)
        self.mushroom_list.append(muchroom)
        muchroom = Muchroom(9400)
        self.mushroom_list.append(muchroom)
        muchroom = Muchroom(9300)
        self.mushroom_list.append(muchroom)
    def on_draw(self):
        self.clear()
        self.text = arcade.Text(f"time: {str(int(self.time))}", self.world_camera.position[0] - 200,
                                self.world_camera.position[1] + self.world_camera.height // 2 - 80, arcade.color.BLACK,
                                30, 30)
        self.text_coins = arcade.Text(f"coins: {str(int(self.number_coins))}", self.world_camera.position[0] - 380,
                                      self.world_camera.position[1] + self.world_camera.height // 2 - 80,
                                      arcade.color.BLACK,
                                      30, 30)
        self.text_points = arcade.Text(f"points: {str(int(self.number_points))}", self.world_camera.position[0],
                                      self.world_camera.position[1] + self.world_camera.height // 2 - 80,
                                      arcade.color.BLACK,
                                      30, 30)
        self.world_camera.use()
        if self.tile_map:
            for key in self.tile_map.sprite_lists:
                self.tile_map.sprite_lists[key].draw()
        self.mushroom_list.draw()

        if self.player_list:
            self.player_list.draw()
        self.coins_list.draw()
        self.text.draw()
        self.text_coins.draw()
        self.text_points.draw()

    def on_update(self, delta_time: float):
        self.time -= delta_time
        if self.time <= 0 or self.Mario.center_y < -5:
            game_over = MenuGameOver()
            self.window.show_view(game_over)
        if arcade.check_for_collision_with_list(self.Mario, self.tile_map.sprite_lists["Столб"]):
            win = WinMenu()
            self.window.show_view(win)
        # for block in arcade.check_for_collision_with_list(self.Mario, self.blocks):
        # if block.bottom + block.center_y >= self.Mario.top + self.Mario.center_y:
        # self.coins.append(arcade.Sprite(""))
        self.animation_time += delta_time
        self.physics_engine.update()
        self.Mario.change_x = self.speed_right + self.speed_left
        position = (
            self.Mario.center_x + 175,
            self.Mario.center_y
        )
        self.world_camera.position = arcade.math.lerp_2d(
            self.world_camera.position,
            position,
            0.05,
        )
        self.mushroom_list.update()
        self.dangerous()
        if self.animation_time > 0.1:
            self.animation_time = 0
            if self.Mario.change_y < 0 and not self.is_moving_left:
                self.Mario.texture = arcade.load_texture("assets/Characters/Big Mario/big_mario_idle.png")
            elif self.Mario.change_y < 0 and self.is_moving_left:
                self.Mario.texture = arcade.load_texture(
                    "assets/Characters/Big Mario/big_mario_idle.png").flip_left_right()
            elif self.speed_left + self.speed_right == 0:
                self.Mario.texture = arcade.load_texture("assets/Characters/Big Mario/big_mario_idle.png")
                self.is_moving_Right = False
                self.is_moving_left = False
            elif self.speed_right > 0:
                if self.is_moving_Right:
                    self.now_number = (self.now_number + 1) % 3
                else:
                    self.is_moving_Right = True
            elif self.speed_left < 0:
                if self.is_moving_left:
                    self.now_number = (self.now_number + 1) % 3
                else:
                    self.is_moving_left = True
            else:
                self.now_number = 0
            if self.Mario.change_y > 0:
                if self.is_moving_Right:
                    self.Mario.texture = arcade.load_texture("assets/Characters/Big Mario/big_mario_jump.png")
                elif self.is_moving_left:
                    texture = arcade.load_texture("assets/Characters/Big Mario/big_mario_jump.png").flip_left_right()
                    self.Mario.texture = texture
                else:
                    self.Mario.texture = arcade.load_texture("assets/Characters/Big Mario/big_mario_jump.png")
            elif self.is_moving_Right and not self.is_moving_left:
                self.Mario.texture = self.moving_right_list[self.now_number]
            elif self.is_moving_left and not self.is_moving_Right:
                self.Mario.texture = self.moving_left_list[self.now_number]
        for lucky_box in self.tile_map.sprite_lists["Блоки"]:
            x = lucky_box.center_x
            box_widht = lucky_box.width
            if x + box_widht // 2 >= self.Mario.center_x >= x - box_widht // 2 and lucky_box.center_y - lucky_box.height // 2 >= self.Mario.center_y + self.Mario.height // 2 >= lucky_box.center_y - lucky_box.height // 2 - 5 and lucky_box.first:
                coin = arcade.Sprite(self.coin_texture)
                coin.center_y = lucky_box.center_y + 70
                coin.center_x = lucky_box.center_x
                self.coins_list.append(coin)
                lucky_box.first = False
        for coin in arcade.check_for_collision_with_list(self.Mario, self.coins_list):
            self.number_coins += 1
            self.coins_list.remove(coin)
        self.move_mushroom()
    def move_mushroom(self):
        for mushroom in self.mushroom_list:
            if arcade.check_for_collision_with_list(mushroom, self.tile_map.sprite_lists["Земля"]):
                mushroom.way = not mushroom.way


    def on_key_press(self, key: int, modifiers: int):
        if key in [arcade.key.D, arcade.key.RIGHT]:
            self.speed_right = SPEED
        if key in [arcade.key.A, arcade.key.LEFT]:
            self.speed_left = -SPEED
        if key in [arcade.key.W, arcade.key.UP, arcade.key.SPACE]:
            if self.physics_engine and self.physics_engine.can_jump():
                self.Mario.change_y = 15
        if key == arcade.key.ESCAPE:
            pause_view = PauseView(self)
            self.window.show_view(pause_view)

    def on_key_release(self, key: int, modifiers: int):
        if key in [arcade.key.D, arcade.key.RIGHT]:
            self.speed_right = 0
        if key in [arcade.key.A, arcade.key.LEFT]:
            self.speed_left = 0


class Muchroom(arcade.Sprite):
    def __init__(self, center_x):
        super().__init__(center_x)
        self.center_x = center_x
        self.center_y = 118.5
        self.texture = arcade.load_texture("assets/mushroom.png")
        self.scale = 0.05
        self.way = random.choice([True, False])

    def update(self, delta_time):
        if self.way:
            self.center_x += (SPEED * 18) * delta_time
        else:
            self.center_x -= (SPEED * 18) * delta_time


window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT)
menu_view = MenuView()
window.show_view(menu_view)
arcade.run()
