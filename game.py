import os
import sys
import uuid
import pygame


def load_image(image):
    filepath = os.path.join(os.path.dirname(__file__), image)
    return pygame.image.load(filepath)


class GameStage:
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.moveableObjCollection = []
        self.background = None
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.explosibleObjCollection = []
        self.font = pygame.font.Font(None, 36)
        self.text = None

    def set_background(self, background):
        self.background = background

    def open(self):
        self.display_text("0:0")
        self.screen.blit(self.background, (0, 0))
        for item in self.moveableObjCollection:
            self.screen.blit(item.player, item.pos)
        pygame.display.update()

    def display_text(self, text):
        self.screen.blit(self.background, (0, 0))
        self.text = self.font.render(text, 1, (255, 255, 255))
        self.screen.blit(self.text, (self.width / 2, 0))

    def size(self):
        return self.width, self.height

    def get_pos(self, obj):
        assert (isinstance(obj, GameMoveableObj))
        return obj.pos.top

    def get_pos_by_id(self, objId):
        for item in self.moveableObjCollection:
            if item.id == objId:
                return self.get_pos(item)
        return 0

    def addMovableObj(self, obj):
        assert (isinstance(obj, GameMoveableObj))
        obj.stage = self
        self.moveableObjCollection.append(obj)
        if obj.is_explosible():
            self.explosibleObjCollection.append(obj)

    def move(self):
        for item in self.moveableObjCollection:
            item.move()

    def earse(self, obj):
        assert (isinstance(obj, GameMoveableObj))
        self.screen.blit(self.background, obj.pos, obj.pos)

    def destroy(self, obj):
        assert (isinstance(obj, GameMoveableObj))
        self.earse(obj)
        if obj in self.moveableObjCollection:
            self.moveableObjCollection.remove(obj)
        if obj in self.explosibleObjCollection:
            self.explosibleObjCollection.remove(obj)

    def raise_event(self, event):
        if event.type == pygame.KEYDOWN:
            for item in self.moveableObjCollection:
                item.on_key_down(event.key)

    def nextframe(self):
        for item in self.moveableObjCollection:
            self.screen.blit(self.background, item.pos, item.pos)
        self.move()
        for item in self.moveableObjCollection:
            self.screen.blit(item.player, item.pos)
            if isinstance(item, Bullet) or isinstance(item, MissileLeft):
                if item.is_missed():
                    self.destroy(item)
                else:
                    for explosibleObj in self.explosibleObjCollection:
                        if item.is_hit_target(explosibleObj):
                            self.exploseObj(item, explosibleObj)
                            self.display_text('{}:{}'.format(self._score_left, self._score_right))

        pygame.display.update()

    def on_command(self, command):
        objid, command = command.split('#')
        result = [
            objid,
        ]
        for item in self.moveableObjCollection:
            print(item.id)
            print(objid)
            if objid == 'ALL' or objid == item.id:
                cmdResult = item.on_command(command)
                if cmdResult:
                    result.append(cmdResult)
        return '#'.join(result)

    def exploseObj(self, bulletObj, exploreObj, destroyExploreObj=False):
        assert (isinstance(bulletObj, Bullet) or isinstance(bulletObj, MissileLeft))
        assert (isinstance(exploreObj, GameMoveableObj))
        self.destroy(bulletObj)
        exploreObj.on_explosed()
        # self.addMovableObj(Explose([1, 0], (exploreObj.pos[0], exploreObj.pos[1])))
        if (destroyExploreObj):
            self.destroy(exploreObj)

    _score_left = 0
    _score_right = 0


class GameMoveableObj:
    def __init__(self, player, speed, inipos):
        self.player = player
        self.speed = speed
        self.pos = player.get_rect()
        self.pos.move_ip(inipos)
        self.stage = None
        self.id = uuid.uuid4()

    def move(self):
        self.pos = self.pos.move(self.speed)

    def on_key_down(self, key):
        pass

    def on_command(self, command):
        pass

    def on_explosed(self):
        pass

    def is_explosible(self):
        return False


class PingBall(GameMoveableObj):
    def move(self):
        self.pos = self.pos.move(self.speed)
        if self.pos.left < 0 or self.pos.right > self.stage.width:
            self.speed[0] = -self.speed[0]
        if self.pos.top < 0 or self.pos.bottom > self.stage.height:
            self.speed[1] = -self.speed[1]


class Role(GameMoveableObj):
    def move_left(self):
        if self.pos.left > 0:
            self.stage.earse(self)
            self.pos = self.pos.move([-10, 0])

    def move_right(self):
        if self.pos.right < self.stage.width:
            self.stage.earse(self)
            self.pos = self.pos.move([10, 0])

    def on_key_down(self, key):
        if key == pygame.K_LEFT:
            self.move_left()
        elif key == pygame.K_RIGHT:
            self.move_right()


class ship(GameMoveableObj):
    def __init__(self, imagePath, initPos):
        filepath = os.path.join(os.path.dirname(__file__), imagePath)
        player = pygame.image.load(filepath)
        super(ship, self).__init__(player, [0, 0], initPos)

    def move_up(self):
        if self.pos.top > 0:
            self.stage.earse(self)
            self.pos = self.pos.move([0, -10])

    def move_down(self):
        if self.pos.bottom < self.stage.height:
            self.stage.earse(self)
            self.pos = self.pos.move([0, 10])

    def move_left(self):
        if self.pos.left > 0:
            self.stage.earse(self)
            self.pos = self.pos.move([-10, 0])

    def move_right(self):
        if self.pos.right < self.stage.width:
            self.stage.earse(self)
            self.pos = self.pos.move([10, 0])

    def on_key_down(self, key):
        if key == pygame.K_DOWN:
            self.move_up()
        elif key == pygame.K_UP:
            self.move_down()
        elif key == pygame.K_LEFT:
            self.fire()

    def fire(self):
        pass

    def fire_missile(self):
        pass

    def on_command(self, command):
        if command == 'UP':
            self.move_up()
        elif command == 'DOWN':
            self.move_down()
        elif command == 'FIRE':
            self.fire()
        elif command == 'LEFT':
            self.move_left()
        elif command == 'RIGHT':
            self.move_right()
        elif command == 'FIRE-MISSILE':
            self.fire_missile()

    def is_explosible(self):
        return True


class ShipLeft(ship):
    def __init__(self):
        super(ShipLeft, self).__init__('resource/shipl.png', (0, 200))
        self.id = 'LEFT'

    def fire(self):
        self.stage.addMovableObj(Bullet((self.pos[0] + self.pos.width, self.pos[1] + 50), [1, 0]))

    def fire_missile(self):
        self.stage.addMovableObj(MissileLeft((self.pos[0] + self.pos.width, self.pos[1] + 50), [20, 0]))

    def on_explosed(self):
        self.stage._score_right = self.stage._score_right + 1


class ShipRight(ship):
    def __init__(self):
        super(ShipRight, self).__init__('resource/shipr.png', (1000, 200))
        self.id = 'RIGHT'

    def fire(self):
        self.stage.addMovableObj(Bullet((self.pos[0] - 100, self.pos[1] + 50), [-1, 0]))

    def on_explosed(self):
        self.stage._score_left = self.stage._score_left + 1


class Bullet(GameMoveableObj):
    def __init__(self, inipos, speed):
        filepath = os.path.join(os.path.dirname(__file__), 'resource/bullet.gif')
        player = pygame.image.load(filepath)
        super(Bullet, self).__init__(player, speed, inipos)

    def is_missed(self):
        return self.pos.left > self.stage.width or self.pos.right < 0

    def is_hit_target(self, obj):
        assert isinstance(obj, GameMoveableObj)
        return self.pos.colliderect(obj.pos)


class MissileLeft(GameMoveableObj):
    def __init__(self, inipos, speed):
        filepath = os.path.join(os.path.dirname(__file__), 'resource/missile.png')
        player = pygame.image.load(filepath)
        super(MissileLeft, self).__init__(player, speed, inipos)
        self.id = "MISSILE-LEFT"

    def is_missed(self):
        return self.pos.left > self.stage.width or self.pos.right < 0

    def is_hit_target(self, obj):
        assert isinstance(obj, GameMoveableObj)
        return self.pos.colliderect(obj.pos)

    def move_up(self):
        if self.pos.top > 0:
            self.stage.earse(self)
            self.pos = self.pos.move([0, -10])

    def move_down(self):
        if self.pos.bottom < self.stage.height:
            self.stage.earse(self)
            self.pos = self.pos.move([0, 10])

    def on_command(self, command):
        if command == 'UP':
            self.move_up()
        elif command == 'DOWN':
            self.move_down()

        return '#'.join([str(self.pos.top), str(self.stage.get_pos_by_id("RIGHT"))])


class Explose(GameMoveableObj):
    def __init__(self, speed, initPos):
        filepath = os.path.join(os.path.dirname(__file__), 'resource/exploise.gif')
        player = pygame.image.load(filepath)
        super(Explose, self).__init__(player, speed, initPos)
        self.time = 0

    def move(self):
        super(Explose, self).move()
        self.time = self.time + 1
        if self.time > 3:
            self.stage.destroy(self)
