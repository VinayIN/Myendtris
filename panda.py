import random
import time
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Point3
from panda3d.core import TextNode
from panda3d.core import CollisionHandlerQueue
from panda3d.core import CollisionNode
from panda3d.core import CollisionRay
from panda3d.core import Camera
from panda3d.core import AmbientLight
from panda3d.core import DirectionalLight
from direct.gui.OnscreenText import OnscreenText

class F1SignalButtonGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        self.light_on = False
        self.start_time = 0

        self.create_light()
        self.create_text()
        self.create_button()
        self.schedule_light()

    def create_light(self):
        self.light = self.loader.loadModel("models/light")
        self.light.setPos(0, 0, 0)
        self.light.setColor((1, 0, 0, 1))
        self.light.reparentTo(self.render)

    def create_text(self):
        self.text_node = TextNode("reaction_time_text")
        self.text_node.setTextColor(1, 1, 1, 1)
        self.text_node.setText("Click the button when the light turns green")
        self.text_node.setAlign(TextNode.ACenter)
        self.text_np = self.aspect2d.attachNewNode(self.text_node)
        self.text_np.setScale(0.1)
        self.text_np.setPos(0, 0, -0.9)

    def create_button(self):
        self.button = self.loader.loadModel("models/button")
        self.button.setPos(0, 0, 0)
        self.button.setScale(0.1)
        self.button.reparentTo(self.render)
        self.button.setTransparency(True)

        self.button_handler = CollisionHandlerQueue()
        self.button_ray = CollisionRay()
        self.button_ray.setOrigin(0, 0, 2)
        self.button_ray.setDirection(0, 0, -1)
        self.button_collider = CollisionNode("button_collider")
        self.button_collider.addSolid(self.button_ray)
        self.button_collider_np = self.button.attachNewNode(self.button_collider)
        self.button_collider_np.setTag("action", "click")
        self.button_collider_np.setCollideMask(0x1)
        self.button_collider_np.setPythonTag("button", self.button)
        self.button_collider_np.setPythonTag("game", self)
        self.collision_traverser.addCollider(self.button_collider_np, self.button_handler)

        self.accept("click", self.on_button_click)

    def schedule_light(self):
        delay = random.uniform(1.0, 5.0)
        self.taskMgr.doMethodLater(delay, self.turn_on_light, "turn_on_light")

    def turn_on_light(self, task):
        self.light.setColor((0, 1, 0, 1))
        self.start_time = time.time()
        self.light_on = True
        return task.done

    def on_button_click(self, entry):
        if self.light_on:
            end_time = time.time()
            reaction_time = end_time - self.start_time
            self.display_reaction_time(reaction_time)
            self.light_on = False
            self.schedule_light()

    def display_reaction_time(self, reaction_time):
        self.text_node.setText(f"Your reaction time: {reaction_time:.3f} seconds")

game = F1SignalButtonGame()
game.run()
