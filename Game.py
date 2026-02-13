import arcade
import random

from pyglet.event import EVENT_HANDLE_STATE

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1200
SPEED = 10


class Super_Mario_baros_game(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.width = 700

    def setup(self):
        self.tile_map = arcade.load_tilemap("assets/Stages/World 1-1.tmx", scaling=16)
        self.height = self.tile_map.height
        self.tile_map.center_x = self.tile_map.width // 2
        self.tile_map.center_y = self.tile_map.height // 2
        self.world_camera = arcade.camera.Camera2D()
        self.Mario = arcade.Sprite("assets/Characters/Big Mario/big_mario_idle.png", scale=1)
        self.Mario.center_x = self.tile_map.width // 2
        self.Mario.center_y = self.tile_map.height // 2
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.Mario)
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.Mario, [self.tile_map.sprite_lists["Блоки"],
                                                                          self.tile_map.sprite_lists["Земля"]])
        self.speed_left = 0
        self.speed_right = 0

    def on_draw(self):
        self.world_camera.use()
        for key in self.tile_map.sprite_lists:
            self.tile_map.sprite_lists[key].draw()
        self.player_list.draw()

    def on_update(self, delta_time: float):
        self.physics_engine.update()
        self.Mario.change_x = self.speed_right + self.speed_left
        position = (
            self.Mario.center_x,
            self.Mario.center_y
        )
        self.world_camera.position = arcade.math.lerp_2d(  # Изменяем позицию камеры
            self.world_camera.position,
            position,
            1,  # Плавность следования камеры
        )

    def on_key_press(self, key: int, modifiers: int):
        if key == [arcade.key.D, arcade.key.RIGHT]:
            self.speed_right = -SPEED
        if key in [arcade.key.A, arcade.key.LEFT]:
            self.speed_left = SPEED
        if key in [arcade.key.W, arcade.key.UP]:
            self.Mario.change_y = SPEED

    def on_key_release(self, key: int, modifiers: int):
        if key == [arcade.key.D, arcade.key.RIGHT]:
            self.speed_right = 0
        if key in [arcade.key.A, arcade.key.LEFT]:
            self.speed_left = 0


def setup_game(width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
    game = Super_Mario_baros_game(width, height)
    game.setup()
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT)
    arcade.run()


main()
