#!/usr/bin/env python3

import pygame
import os
import random
from libs.Vectors import Vector2D


def mod(x):
    return x if x >= 0 else -1 * x


def getRandomBoost():
    chancesOfCoin = 6
    chancesOfLife = 1
    randIndex = random.randint(1, 10)
    if randIndex <= chancesOfCoin:
        return 'coin'
    elif randIndex <= chancesOfCoin + chancesOfLife:
        return 'life'
    else:
        return 'none'


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.scoreFont = pygame.font.SysFont('Comic Sans MS', 20)
        pygame.display.set_caption('Brick Breaker')
        self.icon = pygame.image.load('sprites/Icons/Icon.png')
        self.icon = pygame.transform.scale(self.icon, (32, 32))
        self.heart = pygame.image.load('sprites/Icons/Heart.png')
        self.heart = pygame.transform.scale(self.heart, (30, 30))
        pygame.display.set_icon(self.icon)
        self.lives = 3
        self.devMode = False
        if self.devMode:
            self.arrow = pygame.image.load('sprites/Icons/Arrow.png')
            aspectRatio = self.arrow.get_width() / self.arrow.get_height()
            self.arrow = pygame.transform.scale(self.arrow, (int(aspectRatio * 30), 30))
        self.width = 720
        self.height = 720
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.ballSprite = pygame.image.load('sprites/Bullets/ball.png')
        self.ballSprite = pygame.transform.scale(self.ballSprite, (30, 30))
        self.playerSprite = pygame.image.load('sprites/Player/main_player.png')
        self.playerSprite = pygame.transform.scale(
            self.playerSprite, (114, 30))
        self.playerPosition = Vector2D(self.width / 2 - 57, self.height - 30)
        self.ballPosition = self.playerPosition + Vector2D(42, -30)
        self.ballLaunched = False
        self.ballVelocity = Vector2D(0, -1 * self.height / 60)
        self.playerVelocity = Vector2D(self.width / 60, 0)
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.screen.blit(self.playerSprite, self.playerPosition.toTuple)
        self.screen.blit(self.ballSprite, self.ballPosition.toTuple)
        self.loadText(text='Press SPACE to start', coordinates=(
            self.width / 3 - 10, self.height / 2))
        self.brickWidth = 0
        self.brickHeight = 0
        self.running = True
        self.won = False
        self.bricks = []
        self.boosts = ['coin', 'life']
        self.drops = []
        self.score = 0
        self.displayLives()
        self.displayScore()
        self.generateBricks()
        while True:
            self.eventLoop()
            if self.won:
                keepRunning = True
                while keepRunning:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                self.won = False
                                keepRunning = False
                                break
            self.startNewSession()

    def spawnNewDrop(self, brick: dict):
        if brick['boost'] == 'none':
            return

        dropVelocity = Vector2D(0, self.height / 120)
        drop = brick['boost']
        sprite = pygame.image.load(f'sprites/Drops/{drop}.png')
        sprite = pygame.transform.scale(sprite, (30, 30))
        dropPos = (brick['position'][0] + self.brickWidth/2, brick['position'][1] + self.brickHeight/2)
        dropInstance = {
            'type': drop,
            'velocity': dropVelocity,
            'position': dropPos,
            'sprite': sprite
        }
        self.drops.append(dropInstance)

    def generateBricks(self):
        sprites = os.listdir('sprites/Bricks/Mint')
        currentSprite = random.choice(sprites)
        brickSprite = pygame.image.load(f'sprites/Bricks/Mint/{currentSprite}')
        brokenSprite = pygame.image.load(
            f'sprites/Bricks/Broken/{currentSprite}')
        brickAspectRatio = brickSprite.get_height() / brickSprite.get_width()
        bricksPerLine = 7
        self.brickWidth, self.brickHeight = int(
            self.width / bricksPerLine), int(self.width * brickAspectRatio / bricksPerLine)
        brickSprite = pygame.transform.scale(
            brickSprite, (self.brickWidth, self.brickHeight))
        brokenSprite = pygame.transform.scale(
            brokenSprite, (self.brickWidth, self.brickHeight))
        current_width, current_height = 0, 40
        for i in range(3):
            current_width = 0
            for j in range(bricksPerLine):
                self.screen.blit(brickSprite, (current_width, current_height))
                brick = {
                    'position': (current_width, current_height),
                    'sprite': brickSprite,
                    'broken': False,
                    'brokenSprite': brokenSprite,
                    'boost': getRandomBoost()
                }
                self.bricks.append(brick)
                current_width += self.brickWidth
                currentSprite = random.choice(sprites)
                brickSprite = pygame.image.load(
                    f'sprites/Bricks/Mint/{currentSprite}')
                brokenSprite = pygame.image.load(
                    f'sprites/Bricks/Broken/{currentSprite}')
                brickSprite = pygame.transform.scale(
                    brickSprite, (self.brickWidth, self.brickHeight))
                brokenSprite = pygame.transform.scale(
                    brokenSprite, (self.brickWidth, self.brickHeight))
            current_height += self.brickHeight
        pygame.display.update()

    def displayLives(self):
        curr_width = 0
        for i in range(self.lives):
            self.screen.blit(self.heart, (curr_width, 5))
            curr_width += 35

    def displayScore(self):
        text = self.scoreFont.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(text, (self.width - 130, 2))

    def refresh(self):
        self.screen.fill((0, 0, 0))
        self.displayLives()
        self.displayScore()
        for brick in self.bricks:
            if not brick['broken']:
                self.screen.blit(brick['sprite'], brick['position'])
            else:
                self.screen.blit(brick['brokenSprite'], brick['position'])

        if not self.ballLaunched:
            self.loadText(text='Press SPACE to start',
                          coordinates=(self.width / 3 - 10, self.height / 2))

        if len(self.bricks) == 0:
            self.loadText(text='You Won!',
                          coordinates=(self.width / 3 + 40, self.height / 2 - 20))
            self.loadText('Press SPACE to start new game',
                          coordinates=(self.width / 4 - 30, self.height / 2 + 30))
            self.running = False
            self.won = True

        if len(self.drops) > 0:
            for drop in self.drops:
                self.screen.blit(drop['sprite'], drop['position'])

        self.screen.blit(self.playerSprite, self.playerPosition.toTuple)
        self.screen.blit(self.ballSprite, self.ballPosition.toTuple)
        if self.devMode:
            arr = pygame.transform.rotate(
                self.arrow, self.ballVelocity.angle)
            self.screen.blit(
                arr, (self.ballPosition.x, self.ballPosition.y))
        pygame.display.update()

    def startNewSession(self):
        self.bricks = []
        self.playerPosition = Vector2D(self.width / 2 - 57, self.height - 30)
        self.ballPosition = self.playerPosition + Vector2D(42, -30)
        self.ballLaunched = False
        self.ballVelocity = Vector2D(0, -1 * self.height / 60)
        self.running = True
        self.lives = 3
        self.score = 0
        self.drops = []
        self.generateBricks()
        self.refresh()

    def newLife(self):
        self.playerPosition = Vector2D(self.width / 2 - 57, self.height - 30)
        self.ballPosition = self.playerPosition + Vector2D(42, -30)
        self.ballLaunched = False
        self.ballVelocity = Vector2D(0, -1 * self.height / 60)
        self.running = True
        self.refresh()

    def loadText(self, text: str, coordinates: tuple = None):
        if coordinates is None:
            coordinates = (self.width / 2, self.height / 2)
        Text = self.font.render(text, False, (255, 255, 255))
        self.screen.blit(Text, coordinates)

    def eventLoop(self):
        keep_updating = False
        update_vel = Vector2D(0, 0)
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        update_vel = self.playerVelocity
                        keep_updating = True
                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        update_vel = self.playerVelocity * -1
                        keep_updating = True
                    elif event.key == pygame.K_SPACE:
                        if not self.ballLaunched:
                            self.ballVelocity += update_vel
                            self.ballLaunched = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        update_vel = Vector2D(0, 0)
                        keep_updating = False
                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        update_vel = Vector2D(0, 0)
                        keep_updating = False

            if keep_updating or self.ballLaunched:
                if keep_updating:
                    self.playerPosition += update_vel
                    if self.playerPosition.x >= self.width - 114:
                        self.playerPosition.x = self.width - 114
                    if self.playerPosition.x <= 0:
                        self.playerPosition.x = 0
                if not self.ballLaunched:
                    self.ballPosition = Vector2D(
                        self.playerPosition.x + 42, self.playerPosition.y - 30)
                else:
                    if mod(self.ballVelocity.x) >= self.width / 60:
                        self.ballVelocity.x = self.width / \
                                              60 if self.ballVelocity.x > 0 else -1 * self.width / 60
                    self.ballPosition += self.ballVelocity
                    if self.ballPosition.x >= self.width - 30 or self.ballPosition.x <= 0:
                        self.ballVelocity.x *= -1
                        if self.ballPosition.x >= self.width - 30:
                            self.ballPosition.x = self.width - 30
                        else:
                            self.ballPosition.x = 0
                    if self.height >= self.ballPosition.y >= self.height - 60 and \
                            self.playerPosition.x <= self.ballPosition.x + 15 <= self.playerPosition.x + 114:
                        self.ballVelocity.y *= -1
                        self.ballVelocity.x += update_vel.x
                    if self.ballPosition.y <= 40:
                        self.ballVelocity.y *= -1
                    else:
                        for i in range(len(self.bricks)):
                            brickPos = self.bricks[i]['position']
                            if brickPos[0] <= self.ballPosition.x + 15 <= brickPos[0] + self.brickWidth and \
                                    brickPos[1] <= self.ballPosition.y <= brickPos[1] + self.brickHeight:
                                self.ballVelocity.y *= -1
                                if self.bricks[i]['broken']:
                                    self.spawnNewDrop(self.bricks[i])
                                    self.bricks.pop(i)
                                else:
                                    self.bricks[i]['broken'] = True

                                break
                if len(self.drops) > 0 and self.ballLaunched:
                    for drop in self.drops:
                        drop['position'] = (drop['position'][0] + drop['velocity'].x,
                                            drop['position'][1] + drop['velocity'].y)

                    for i in range(len(self.drops)):
                        drop = self.drops[i]
                        if self.playerPosition.x <= drop['position'][0] <= self.playerPosition.x + 114 and \
                                self.playerPosition.y <= drop['position'][1] <= self.playerPosition.y + 30:
                            if drop['type'] == 'life':
                                self.lives += 1 if self.lives < 16 else 0
                            elif drop['type'] == 'coin':
                                self.score += 30
                            else:
                                pass

                            self.drops.pop(i)
                            break

                    for i in range(len(self.drops)):
                        drop = self.drops[i]
                        if drop['position'][1] >= self.height:
                            self.drops.pop(i)
                            break

                self.refresh()

            if self.ballPosition.y >= self.height - 15:
                if self.lives > 0:
                    self.lives -= not self.devMode
                    update_vel = Vector2D(0, 0)
                    self.newLife()
                else:
                    self.running = False

            if self.lives > 16:
                self.lives = 16
            self.clock.tick(self.fps)


game = Game()
