import pygame
import math
import random


class Meteorite:
    def __init__(self, surface: pygame.Surface, size=140):
        self.surface            = surface
        self.points             = []
        self.points_location    = []
        self.meteorite_rotation = random.uniform(-1, 1)
        self.rotation_speed     = random.uniform(-1, 1)
        self.direction          = random.randint(0, 360)
        self.meteorite_size     = self.avg_size = size

        side = random.randint(1, 4)  # 1 up, 2 right, 3 down, 4 left
        if side == 1:
            self.x, self.y = random.randint(0, self.surface.get_width()), -self.meteorite_size
        elif side == 2:
            self.x, self.y = self.surface.get_width()+self.meteorite_size, random.randint(0, self.surface.get_height())
        elif side == 3:
            self.x, self.y = random.randint(0, self.surface.get_width()), self.surface.get_height()+self.meteorite_size
        elif side == 4:
            self.x, self.y = -self.meteorite_size, random.randint(0, self.surface.get_height())

        verts = 20
        vert_sizes = []
        for i in range(verts):
            radius = random.randint(int(self.meteorite_size/3), int(self.meteorite_size/2))
            vert_sizes.append(radius)

            rotation = (360 / verts) * i
            self.points.append((
                int(self.meteorite_size / 2) + math.sin(math.radians(rotation)) * (radius * -1),
                int(self.meteorite_size / 2) + math.cos(math.radians(rotation)) * (radius * -1),
            ))

        # Get the average size of the meteorite for a more accurate hit box
        self.avg_size = sum(vert_sizes) / len(vert_sizes)

    def show(self, surface: pygame.Surface, elapsed_time: float):
        self.move(surface, elapsed_time)

        # Show the meteorite
        meteorite_container = pygame.Surface((self.meteorite_size, self.meteorite_size), pygame.SRCALPHA)
        pygame.draw.polygon(meteorite_container, (255, 255, 0), self.points, 3)
        meteorite_container = pygame.transform.rotate(meteorite_container, self.meteorite_rotation)
        meteorite_container_rect = meteorite_container.get_rect(center=(self.x, self.y))

        self.surface.blit(meteorite_container, meteorite_container_rect)

    def move(self, surface: pygame.Surface, elapsed_time: float):
        # Move and rotate the meteorite
        self.x += math.sin(math.radians(self.direction)) * (0.5 * elapsed_time)
        self.y += math.cos(math.radians(self.direction)) * (0.5 * elapsed_time)
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

        # 'self.points' contains the points' positions on the surface, but not their actual location on the screen
        self.points_location = []
        for point in self.points:
            self.points_location.append((point[0] + self.x, point[1] + self.y))

    # Check if given coordinates are inside the meteorite
    def collide(self, obj_pos: tuple):
        obj_x, obj_y = obj_pos

        dist = math.sqrt((self.x - obj_x) ** 2 + (self.y - obj_y) ** 2)
        if dist < self.avg_size:
            return True


def game():
    pygame.init()

    pygame.display.set_caption("Meteorites!")

    display             = pygame.display.set_mode((800, 800))
    clock               = pygame.time.Clock()
    process_interrupted, game_over = False, False
    elapsed_time        = 0

    # Effects -------------------------------------------------------

    # Fade the game in on start
    fade_in, fade_out, fade_alpha = True, False, 255

    # Stop displaying the game after the game has ended and the fade has faded out
    hide_game = False

    # Images --------------------------------------------------------

    # Icon and background image
    pygame.display.set_icon(pygame.image.load("images/meteorite.png").convert())
    background_image = pygame.transform.scale(
        pygame.image.load("images/background.jpg").convert(), (800, 800)
    )

    # Explosion images
    explosion_images, explosion_frame = [
        pygame.transform.scale(
            pygame.image.load(f"images/explosion/frame_{frame}.png").convert_alpha(), (200, 200)
        ) for frame in range(1, 28)
    ], 0

    # Heart image
    heart_image = pygame.transform.scale(
        pygame.image.load("images/heart.png").convert_alpha(), (40, 40)
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
                spaceship_container = pygame.Surface((30, 35), pygame.SRCALPHA)
                container_dimensions = spaceship_container.get_size()
                pygame.draw.polygon(spaceship_container, (255, 255, 255), (
                    (container_dimensions[0] / 2, (container_dimensions[1] / 2) - 15),
                    ((container_dimensions[0] / 2) + 10, (container_dimensions[1] / 2) + 10),
                    ((container_dimensions[0] / 2) - 10, (container_dimensions[1] / 2) + 10)
                ), 2)

                spaceship_container = pygame.transform.rotate(spaceship_container, spaceship_rotation)
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

                        pygame.draw.circle(display, (255, 255, 255), (bullet_x, bullet_y), 3)

                        # Move the bullet in given angle
                        bullets[bullet] = (
                            (
                                (bullet_x + math.sin(math.radians(direction)) * ((bullet_speed * -1) * elapsed_time)),
                                (bullet_y + math.cos(math.radians(direction)) * ((bullet_speed * -1) * elapsed_time)),
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

            font = pygame.font.Font("fonts/fr73pixel.ttf", 22)

            score_text = font.render(f"score: {score}", True, (255, 255, 255))
            wave_text  = font.render(f"wave: {wave}", True, (255, 255, 255))

            display.blit(score_text, (10, 0))
            display.blit(wave_text, (10, 25))

            # Spaceship Movement-----------------------------------------

            if not game_over:
                keys = pygame.key.get_pressed()

                if not spaceship_destroyed:
                    # Add acceleration effect to the spaceship movement
                    if keys[pygame.K_UP]:
                        if spaceship_speed < 5:
                            spaceship_speed += 0.05 * elapsed_time
                    elif keys[pygame.K_DOWN]:
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
                if keys[pygame.K_LEFT]:
                    spaceship_rotation += 3 * elapsed_time
                elif keys[pygame.K_RIGHT]:
                    spaceship_rotation -= 3 * elapsed_time
                spaceship_rotation = spaceship_rotation % 359

                # Move the spaceship in the current angle
                spaceship_location = (
                    (spaceship_location[0] + math.sin(math.radians(spaceship_rotation)) * ((spaceship_speed*-1) * elapsed_time)),
                    (spaceship_location[1] + math.cos(math.radians(spaceship_rotation)) * ((spaceship_speed*-1) * elapsed_time)),
                )

                spaceship_location = (spaceship_location[0] % display.get_width(), spaceship_location[1] % display.get_height())

        else:
            # Game over screen --------------------------------------

            title_font  = pygame.font.Font("fonts/fr73pixel.ttf", 50)
            score_font  = pygame.font.Font("fonts/fr73pixel.ttf", 30)
            replay_font = pygame.font.Font("fonts/fr73pixel.ttf", 20)

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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                process_interrupted = True

            if event.type == pygame.KEYDOWN:

                # Shoot ---------------------------------------------

                if not spaceship_destroyed and not game_over:
                    if event.key == pygame.K_SPACE:
                        bullets.append((spaceship_location, spaceship_rotation))

                # Replay --------------------------------------------

                if hide_game and game_over:
                    fade_in, fade_out, fade_alpha = True, False, 255

                    game_over = hide_game = spaceship_destroyed = False

                    spaceship_location, spaceship_speed, spaceship_rotation = (display.get_width() / 2, display.get_height() / 2), 0, 0
                    bullets = []

                    meteorites = [Meteorite(display) for _ in range(3)]

                    explosion_frame, wave, score, lives_remaining = 0, 1, 0, 3

        # Effects ---------------------------------------------------

        fade_effect = pygame.Surface(display.get_size(), pygame.SRCALPHA)
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
        elapsed_time = clock.tick(1000) / 10
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    game()
