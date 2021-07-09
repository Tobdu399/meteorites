# Import ONLY the items needed for slightly better performance
from pygame.display   import set_mode, set_caption, set_icon, flip
from pygame.font      import init, Font
from pygame           import Surface, SRCALPHA, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_RETURN, K_SPACE, quit, QUIT
from pygame.draw      import polygon, circle
from pygame.transform import rotate, scale
from pygame.time      import Clock
from pygame.image     import load
from pygame.key       import get_pressed
from pygame.event     import get

from math import sqrt, sin, cos, radians
from random import randint, uniform


class Meteorite:
    def __init__(self, surface: Surface, size=140):
        self.surface            = surface
        self.points             = []
        self.points_location    = []    # 'self.points' contains the points' positions on the surface, but...
        self.meteorite_rotation = uniform(-1, 1)          # ...not their actual location on the screen
        self.rotation_speed     = uniform(-1, 1)
        self.direction          = randint(0, 360)
        self.meteorite_size     = self.avg_size = size

        # Randomize the meteorite's spawning point
        side = randint(1, 4)  # 1 up, 2 right, 3 down, 4 left
        if side == 1:
            self.x, self.y = randint(0, self.surface.get_width()), -self.meteorite_size
        elif side == 2:
            self.x, self.y = self.surface.get_width()+self.meteorite_size, randint(0, self.surface.get_height())
        elif side == 3:
            self.x, self.y = randint(0, self.surface.get_width()), self.surface.get_height()+self.meteorite_size
        elif side == 4:
            self.x, self.y = -self.meteorite_size, randint(0, self.surface.get_height())

        # Generate the meteorite
        verts = 20
        vert_sizes = []
        for i in range(verts):
            radius = randint(int(self.meteorite_size/3), int(self.meteorite_size/2))
            vert_sizes.append(radius)

            rotation = (360 / verts) * i
            self.points.append((
                int(self.meteorite_size / 2) + sin(radians(rotation)) * (radius * -1),
                int(self.meteorite_size / 2) + cos(radians(rotation)) * (radius * -1),
            ))

        # Get the average size of the meteorites verts for a more accurate hit box
        self.avg_size = sum(vert_sizes) / len(vert_sizes)

    def show(self, surface: Surface, elapsed_time: float):
        self.move(surface, elapsed_time)

        # Show the meteorite
        meteorite_container = Surface((self.meteorite_size, self.meteorite_size), SRCALPHA)  # -> pygame.Surface()
        polygon(meteorite_container, (255, 255, 0), self.points, 3)                          # -> pygame.draw.polygon()
        meteorite_container = rotate(meteorite_container, self.meteorite_rotation)
        meteorite_container_rect = meteorite_container.get_rect(center=(self.x, self.y))

        self.surface.blit(meteorite_container, meteorite_container_rect)

    def move(self, surface: Surface, elapsed_time: float):
        # Move and rotate the meteorite
        self.x += sin(radians(self.direction)) * (0.5 * elapsed_time)
        self.y += cos(radians(self.direction)) * (0.5 * elapsed_time)
        self.meteorite_rotation += self.rotation_speed * elapsed_time
        self.meteorite_rotation = self.meteorite_rotation % 359

        # Check if the meteorite is in the screen. If it's not, move it to the other side
        display_dimensions = surface.get_size()
        if self.x > display_dimensions[0] + (self.meteorite_size / 2):
            self.x = -self.meteorite_size
        elif self.x < -self.meteorite_size:
            self.x = display_dimensions[0] + (self.meteorite_size / 2)
        if self.y > display_dimensions[1] + (self.meteorite_size / 2):
            self.y = -self.meteorite_size
        elif self.y < -self.meteorite_size:
            self.y = display_dimensions[1] + (self.meteorite_size / 2)

        # 'self.points' contains the points' positions on the surface, but not their actual location on the screen'
        # Updating the list containing the actual coordinates here
        self.points_location = []
        for point in self.points:
            self.points_location.append((point[0] + self.x, point[1] + self.y))

    # Check if given coordinates are inside the meteorite
    def collide(self, obj_pos: tuple):
        obj_x, obj_y = obj_pos

        dist = sqrt((self.x - obj_x) ** 2 + (self.y - obj_y) ** 2)
        if dist < self.avg_size:
            return True


def game():
    init()

    display             = set_mode((800, 800))     # -> pygame.display.set_mode()
    clock               = Clock()                  # -> pygame.time.Clock()
    process_interrupted, game_over = False, False
    elapsed_time        = 0

    # Effects -------------------------------------------------------

    # Fade the game in on start
    fade_in, fade_out, fade_alpha = True, False, 255

    # Stop displaying the game after the game has ended and the fade has faded out
    hide_game = False

    # Images --------------------------------------------------------

    # Icon and background image
    set_icon(load("lib/images/meteorite.png").convert())         # -> pygame.image.load()
    background_image = scale(                                    # -> pygame.transform.scale()
        load("lib/images/background.jpg").convert(), (800, 800)  # -> pygame.image.load()
    )

    # Explosion images
    explosion_images, explosion_frame = [
        scale(                                                                           # -> pygame.transform.scale()
            load(f"lib/images/explosion/frame_{frame}.png").convert_alpha(), (200, 200)  # -> pygame.image.load()
        ) for frame in range(1, 28)
    ], 0

    # Heart image
    heart_image = scale(                                        # -> pygame.transform.scale()
        load("lib/images/heart.png").convert_alpha(), (40, 40)  # -> pygame.image.load()
    )

    # Game properties -----------------------------------------------

    spaceship_location, spaceship_speed, spaceship_rotation = (display.get_width()/2, display.get_height()/2), 0, 0
    bullets             = []
    spaceship_destroyed = False

    meteorites = [Meteorite(display) for _ in range(3)]

    wave            = 1
    score           = 0
    lives_remaining = 3

    while not process_interrupted:
        set_caption(f"Meteorites!    FPS {int(clock.get_fps())}")   # -> pygame.display.set_caption()
        display.fill((0, 0, 0))

        display.blit(background_image, (0, 0))

        if not hide_game:
            # Meteorites ------------------------------------------------

            if len(meteorites) == 0:
                wave       += 1
                meteorites = [Meteorite(display) for _ in range(3 + wave)]

            for meteorite in meteorites:
                meteorite.show(display, elapsed_time)

                # Check if the spaceship collides with a meteorite
                if not spaceship_destroyed:
                    if meteorite.collide(spaceship_location):
                        lives_remaining     -= 1
                        spaceship_destroyed = True

            # Spaceship -------------------------------------------------

            if not spaceship_destroyed:
                spaceship_container = Surface((30, 35), SRCALPHA)   # -> pygame.Surface()
                container_dimensions = spaceship_container.get_size()
                polygon(spaceship_container, (255, 255, 255), (     # -> pygame.draw.polygon()
                    (container_dimensions[0] / 2, (container_dimensions[1] / 2) - 15),
                    ((container_dimensions[0] / 2) + 10, (container_dimensions[1] / 2) + 10),
                    ((container_dimensions[0] / 2) - 10, (container_dimensions[1] / 2) + 10)
                ), 2)

                spaceship_container = rotate(spaceship_container, spaceship_rotation)
                spaceship_container_rect = spaceship_container.get_rect(center=spaceship_location)
                display.blit(spaceship_container, spaceship_container_rect)

            if spaceship_destroyed:
                if explosion_frame < len(explosion_images):
                    image = explosion_images[int(explosion_frame)]
                    image_rect = image.get_rect(center=spaceship_location)
                    display.blit(image, image_rect)
                explosion_frame += 0.2*elapsed_time

            # Wait until the frame is 40 to add a little delay for the respawn
            if spaceship_destroyed and explosion_frame > 40:
                # Respawn the spaceship if it has lives remaining
                if lives_remaining > 0:
                    explosion_frame                        = 0
                    spaceship_location, spaceship_rotation = (display.get_width()/2, display.get_height()/2), 0
                    spaceship_destroyed                    = False
                else:
                    if not game_over:
                        game_over = True

                        # Fade the game out
                        fade_out, fade_alpha = True, 0

            # Spaceship Bullets -----------------------------------------

            for bullet in range(len(bullets)):
                if len(bullets) > bullet:
                    bullet_x, bullet_y = bullets[bullet][0]

                    # Check if the bullet is in the screen, otherwise remove it
                    display_dimensions = display.get_size()
                    if display_dimensions[0] > bullet_x > 0 and display_dimensions[1] > bullet_y > 0:
                        direction    = bullets[bullet][1]
                        bullet_speed = 8

                        circle(display, (255, 255, 255), (bullet_x, bullet_y), 3)   # -> pygame.draw.circle()

                        # Move the bullet in given angle
                        bullets[bullet] = (
                            (
                                (bullet_x + sin(radians(direction)) * ((bullet_speed * -1) * elapsed_time)),
                                (bullet_y + cos(radians(direction)) * ((bullet_speed * -1) * elapsed_time)),
                            ),
                            direction
                        )

                        for meteorite in range(len(meteorites)):
                            if meteorites[meteorite].collide((bullet_x, bullet_y)):
                                # If a bullet hits a meteorite, remove the bullet
                                bullets.pop(bullet)

                                # When the meteorite is destroyed, create two smaller ones to the same location,
                                # but in other directions
                                for child in range(2):
                                    size = meteorites[meteorite].meteorite_size
                                    if meteorites[meteorite].meteorite_size/2 >= 35:
                                        # If the meteorite has been divided multiple times, just remove it,
                                        # to avoid creating meteorites the size of an atom

                                        smaller_meteorite = Meteorite(display, size=int(size/2))
                                        smaller_meteorite.x, smaller_meteorite.y = meteorites[meteorite].x, meteorites[meteorite].y
                                        smaller_meteorite.direction = meteorites[meteorite].direction-90 if child == 1 else meteorites[meteorite].direction+90

                                        meteorites.append(smaller_meteorite)

                                # Remove the destroyed meteorite and increase the score
                                score += meteorites[meteorite].meteorite_size * wave
                                meteorites.pop(meteorite)
                                break

                    else:
                        bullets.pop(bullet)

            # Miscellaneous ---------------------------------------------

            for heart in range(0, lives_remaining):
                display.blit(heart_image, (heart_image.get_width()*heart, display.get_height()-heart_image.get_height()))

            font = Font("lib/fonts/fr73pixel.ttf", 22)

            score_text = font.render(f"score: {score}", True, (255, 255, 255))
            wave_text  = font.render(f"wave: {wave}", True, (255, 255, 255))

            display.blit(score_text, (10, 0))
            display.blit(wave_text, (10, 25))

            # Spaceship Movement-----------------------------------------

            if not game_over:
                keys = get_pressed()    # -> pygame.key.get_pressed()

                if not spaceship_destroyed:
                    # Add acceleration effect to the spaceship movement
                    if keys[K_UP]:
                        if spaceship_speed < 5:
                            spaceship_speed += 0.05 * elapsed_time
                    elif keys[K_DOWN]:
                        if spaceship_speed > -5:
                            spaceship_speed -= 0.05 * elapsed_time

                    # Add sliding effect to the spaceship movement
                    else:
                        if spaceship_speed >= 0.2:
                            spaceship_speed -= 0.02 * elapsed_time
                        elif spaceship_speed <= -0.02:
                            spaceship_speed += 0.02 * elapsed_time
                        else:
                            spaceship_speed = 0
                else:
                    spaceship_speed = 0

                # Rotate the spaceship
                if keys[K_LEFT]:
                    spaceship_rotation += 3 * elapsed_time
                elif keys[K_RIGHT]:
                    spaceship_rotation -= 3 * elapsed_time
                spaceship_rotation = spaceship_rotation % 359

                # Move the spaceship in the current angle
                spaceship_location = (
                    (spaceship_location[0] + sin(radians(spaceship_rotation)) * ((spaceship_speed*-1) * elapsed_time)),
                    (spaceship_location[1] + cos(radians(spaceship_rotation)) * ((spaceship_speed*-1) * elapsed_time)),
                )

                # Keep the rotation in the range of 360 to avoid possible overflow
                spaceship_location = (spaceship_location[0] % display.get_width(), spaceship_location[1] % display.get_height())

        else:
            # Game over screen --------------------------------------

            title_font  = Font("lib/fonts/fr73pixel.ttf", 50)   # -> pygame.font.Font()
            score_font  = Font("lib/fonts/fr73pixel.ttf", 30)   # -> pygame.font.Font()
            replay_font = Font("lib/fonts/fr73pixel.ttf", 20)   # -> pygame.font.Font()

            game_over_text = title_font.render("Game Over", True, (255, 0, 0))
            game_over_text_rect = game_over_text.get_rect(center=(display.get_width()/2, display.get_height()/3))

            score_text = score_font.render(f"score {score}", True, (255, 255, 255))
            score_text_rect = score_text.get_rect(center=(display.get_width()/2, (display.get_height()/3) + 60))

            replay_text = replay_font.render("Press ENTER to play again", True, (255, 255, 0))
            replay_text_rect = replay_text.get_rect(center=(display.get_width()/2, display.get_height()/2))

            display.blit(game_over_text, game_over_text_rect)
            display.blit(score_text, score_text_rect)
            display.blit(replay_text, replay_text_rect)

        # Other Keyboard Events -------------------------------------

        for event in get():  # -> pygame.event.get()
            if event.type == QUIT:  # -> pygame.QUIT
                process_interrupted = True

            if event.type == KEYDOWN:

                # Shoot ---------------------------------------------

                if not spaceship_destroyed and not game_over:
                    if event.key == K_SPACE:
                        bullets.append((spaceship_location, spaceship_rotation))

                # Replay --------------------------------------------

                if event.key == K_RETURN:
                    if hide_game and game_over:
                        fade_in, fade_out, fade_alpha = True, False, 255

                        game_over = hide_game = spaceship_destroyed = False

                        spaceship_location, spaceship_speed, spaceship_rotation = (display.get_width() / 2, display.get_height() / 2), 0, 0
                        bullets = []

                        meteorites = [Meteorite(display) for _ in range(3)]

                        explosion_frame, wave, score, lives_remaining = 0, 1, 0, 3

        # Effects ---------------------------------------------------

        if fade_in or fade_out:
            fade_effect = Surface(display.get_size(), SRCALPHA)  # -> pygame.Surface()
            fade_effect.fill((0, 0, 0, fade_alpha))
            display.blit(fade_effect, (0, 0))

        if fade_in:
            if fade_alpha > 0.0:
                fade_alpha -= 2.5 * elapsed_time
            else:
                fade_in = False
        elif fade_out:
            if fade_alpha < 255.0:
                fade_alpha += 2.5 * elapsed_time
            else:
                fade_out = False
                if game_over:
                    hide_game = True
                    fade_in, fade_alpha = True, 255

        # Get elapsed time since the last frame
        elapsed_time = clock.tick(0) / 10
        flip()  # -> pygame.display.flip()

    quit()  # -> pygame.quit()


if __name__ == "__main__":
    game()
