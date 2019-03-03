import pygame, pytmx
import pyscroll
import pyscroll.data
from pyscroll.group import PyscrollGroup

#Цвет Background
BACKGROUND = (20, 20, 20)

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 480

#Плиточный слой карты с плитками, с которыми вы сталкиваетесь
MAP_COLLISION_LAYER = 1

#Простая оболочка для изменения размера экрана
def init_screen(width, height):
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    return screen

class Game(object):
    def __init__(self):
        #Установите уровень для загрузки
        self.currentLevelNumber = 0
        self.levels = []
        self.levels.append(Level(fileName = "resources/level1.tmx"))
        self.currentLevel = self.levels[self.currentLevelNumber]

        #Создайте объект игрока и установите уровень, в котором он находится
        self.player = Player(x = 200, y = 100)
        self.player.currentLevel = self.currentLevel

        #Отрисовка эстетического наложения - градиент размером с экран
        self.overlay = pygame.image.load("resources/overlay.png")

    def processEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            #Получить ввод с клавиатуры для перемещения игрока
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.goLeft()
                elif event.key == pygame.K_RIGHT:
                    self.player.goRight()
                elif event.key == pygame.K_UP:
                    self.player.jump()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and self.player.changeX < 0:
                    self.player.stop()
                elif event.key == pygame.K_RIGHT and self.player.changeX > 0:
                    self.player.stop()

        return False

    def runLogic(self):
        #Обновить логику движения и столкновения игрока
        self.player.update()

    ####################Отрисовка уровня, игрока и наложения
    def draw(self, screen):
        #Центрируем карту/экран на нашем герое
        #self.group.center(self.hero.rect.center)
        #Отрисовка карты и спрайтов
        #self.group.draw(screen)
        screen.fill(BACKGROUND)
        self.currentLevel.draw(screen)
        self.player.draw(screen)
        screen.blit(self.overlay, [0, 0])
        pygame.display.flip()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        #Загрузка таблицы с кадрами анимации  для этого игрока
        self.sprites = SpriteSheet("resources/player.png")

        self.stillRight = self.sprites.image_at((0, 0, 30, 42))
        self.stillLeft = self.sprites.image_at((0, 42, 30, 42))

        #Список кадров для каждой анимации
        self.runningRight = (self.sprites.image_at((0, 84, 30, 42)),
                    self.sprites.image_at((30, 84, 30, 42)),
                    self.sprites.image_at((60, 84, 30, 42)),
                    self.sprites.image_at((90, 84, 30, 42)),
                    self.sprites.image_at((120, 84, 30, 42)))

        self.runningLeft = (self.sprites.image_at((0, 126, 30, 42)),
                    self.sprites.image_at((30, 126, 30, 42)),
                    self.sprites.image_at((60, 126, 30, 42)),
                    self.sprites.image_at((90, 126, 30, 42)),
                    self.sprites.image_at((120, 126, 30, 42)))

        self.jumpingRight = (self.sprites.image_at((30, 0, 30, 42)),
                    self.sprites.image_at((60, 0, 30, 42)),
                    self.sprites.image_at((90, 0, 30, 42)))

        self.jumpingLeft = (self.sprites.image_at((30, 42, 30, 42)),
                    self.sprites.image_at((60, 42, 30, 42)),
                    self.sprites.image_at((90, 42, 30, 42)))

        self.image = self.stillRight

        #Установить положение игрока
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        #Установите скорость и направление
        self.changeX = 0
        self.changeY = 0
        self.direction = "right"

        #Логическое значение, чтобы проверить, бежит ли игрок, текущий выполняемый кадр и время с момента последнего изменения кадра
        self.running = False
        self.runningFrame = 0
        self.runningTime = pygame.time.get_ticks()

        #Текущий уровень игроков, установленный после инициализации объекта в конструкторе игры
        self.currentLevel = None

    def update(self):
        #Обновить позицию игрока путем изменения
        self.rect.x += self.changeX

        #Получите плитки в слое столкновений, которых теперь касается игрок
        tileHitList = pygame.sprite.spritecollide(self, self.currentLevel.layers[MAP_COLLISION_LAYER].tiles, False)

        #Переместить игрока на правильную сторону этого блока
        for tile in tileHitList:
            if self.changeX > 0:
                self.rect.right = tile.rect.left
            else:
                self.rect.left = tile.rect.right

        #Переместить экран, если игрок достигает границ экрана
        if self.rect.right >= SCREEN_WIDTH - 200:
            difference = self.rect.right - (SCREEN_WIDTH - 200)
            self.rect.right = SCREEN_WIDTH - 200
            self.currentLevel.shiftLevel(-difference)

        #Переместить экран когда игрок достигает границ экрана
        if self.rect.left <= 200:
            difference = 200 - self.rect.left
            self.rect.left = 200
            self.currentLevel.shiftLevel(difference)

        #Обновить позицию игрока путем изменения
        self.rect.y += self.changeY

        #Получите плитки в слое столкновений, которых теперь касается игрок
        tileHitList = pygame.sprite.spritecollide(self, self.currentLevel.layers[MAP_COLLISION_LAYER].tiles, False)

        #Если в этом списке есть плитки
        if len(tileHitList) > 0:
            #Переместить игрока на правильную сторону этой плитки, обновить кадр игрока
            for tile in tileHitList:
                if self.changeY > 0:
                    self.rect.bottom = tile.rect.top
                    self.changeY = 1

                    if self.direction == "right":
                        self.image = self.stillRight
                    else:
                        self.image = self.stillLeft
                else:
                    self.rect.top = tile.rect.bottom
                    self.changeY = 0
        #Если в этом списке нет тайлов
        else:
            #Обновлена анимация игрока для прыжков/падений в кадре игрока
            self.changeY += 0.2
            if self.changeY > 0:
                if self.direction == "right":
                    self.image = self.jumpingRight[1]
                else:
                    self.image = self.jumpingLeft[1]

        #Если игрок на земле и бежит, обновить анимацию бега
        if self.running and self.changeY == 1:
            if self.direction == "right":
                self.image = self.runningRight[self.runningFrame]
            else:
                self.image = self.runningLeft[self.runningFrame]

        #Когда правильное количество времени прошло, переходите к следующему кадру
        if pygame.time.get_ticks() - self.runningTime > 50:
            self.runningTime = pygame.time.get_ticks()
            if self.runningFrame == 4:
                self.runningFrame = 0
            else:
                self.runningFrame += 1

    #Заставить игрока прыгнуть
    def jump(self):
        #Проверьте, находится ли игрок на земле
        self.rect.y += 2
        tileHitList = pygame.sprite.spritecollide(self, self.currentLevel.layers[MAP_COLLISION_LAYER].tiles, False)
        self.rect.y -= 2

        if len(tileHitList) > 0:
            if self.direction == "right":
                self.image = self.jumpingRight[0]
            else:
                self.image = self.jumpingLeft[0]
            #Высота прыжка
            self.changeY = -6

    #Двигаться вправо
    def goRight(self):
        self.direction = "right"
        self.running = True
        self.changeX = 3

    #Двигаться влево
    def goLeft(self):
        self.direction = "left"
        self.running = True
        self.changeX = -3

    #Прекратить движение
    def stop(self):
        self.running = False
        self.changeX = 0

    #Отрисовка игрока
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Level(object):
    def __init__(self, fileName):
        #Создать объект карты из PyTMX
        self.mapObject = pytmx.load_pygame(fileName)

        ##Настройка геометрии уровня с простыми pygame прямоугольниками, загруженными из pytmx
        self.walls = list()
        self.npcs = list()
        self.stairs = list()
        for map_object in self.mapObject.objects:
            if map_object.type == "wall":
                print("wall загрузка не удалась: переопределение wall")
                #self.walls.append(Wall(map_object))
            elif map_object.type == "stair":
                print("stair загрузка не удалась: переопределение stair")
                #self.stairs.append(Wall(map_object))
            elif map_object.type == "guard":
                print("npc загрузка не удалась: переопределение npc")
                #self.npcs.append(Npc(map_object))
            elif map_object.type == "hero":
                print("hero загрузка не удалась: переопределение hero")
                #self.hero = Hero(map_object)

        ##Создать новый источник данных для pyscroll
        map_data = pyscroll.data.TiledMapData(self.mapObject)

        ##Создать новый рендер (камера)
        screen = init_screen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.map_layer = pyscroll.BufferedRenderer(map_data, screen.get_size(), clamp_camera=True, tall_sprites=1)
        self.map_layer.zoom = 2

        ##pyscroll поддерживает многоуровневую визуализацию. наша карта имеет 3 нижних слоя
        ##Слои начинаются с 0, поэтому это 0, 1 и 2.
        ##Так как мы хотим, чтобы спрайт был на вершине слоя 1, мы устанавливаем значение по умолчанию
        ##слой для спрайтов как 2
        self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=3)

        ##Добавить нашего героя в группу объектов для рендеринга
        ##self.group.add(self.hero)
        ##for npc in self.npcs:
        ##    self.group.add(npc)

        #Создать список слоев для карты
        self.layers = []

        #Число сдвига уровня влево/вправо
        self.levelShift = 0

        #Создайте слои для каждого слоя на карте тайлов
        for layer in range(len(self.mapObject.layers)):
            self.layers.append(Layer(index = layer, mapObject = self.mapObject))

    #Переместить слой влево/вправо
    def shiftLevel(self, shiftX):
        self.levelShift += shiftX

        for layer in self.layers:
            for tile in layer.tiles:
                tile.rect.x += shiftX

    #Обновить слой
    def draw(self, screen):
        for layer in self.layers:
            layer.draw(screen)

class Layer(object):
    def __init__(self, index, mapObject):
        #Индекс слоя с тайловой карты
        self.index = index

        #Создать группу плиток для этого слоя
        self.tiles = pygame.sprite.Group()

        #Объект эталонной карты
        self.mapObject = mapObject

        #Создайте плитки в правильном положении для каждого слоя
        for x in range(self.mapObject.width):
            for y in range(self.mapObject.height):
                img = self.mapObject.get_tile_image(x, y, self.index)
                if img:
                    self.tiles.add(Tile(image = img, x = (x * self.mapObject.tilewidth), y = (y * self.mapObject.tileheight)))

    #Отрисовать слой
    def draw(self, screen):
        self.tiles.draw(screen)

#Плитка класс с изображением, х и у
class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

#Класс листов спрайтов для загрузки спрайтов из листов спрайтов игроков
class SpriteSheet(object):
    def __init__(self, fileName):
        self.sheet = pygame.image.load(fileName)

    def image_at(self, rectangle):
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size, pygame.SRCALPHA, 32).convert_alpha()
        image.blit(self.sheet, (0, 0), rect)
        return image

def main():
    pygame.init()
    screen = init_screen(SCREEN_WIDTH, SCREEN_HEIGHT)
    pygame.display.set_caption("Pygame Tiled Demo")
    clock = pygame.time.Clock()
    done = False
    game = Game()

    while not done:
        done = game.processEvents()
        game.runLogic()
        game.draw(screen)
        clock.tick(60)

    pygame.quit()

main()
