import sdl2
import sdl2.ext as sdl2e


ROTATE_STEP = 0.1


class World(object):
    def __init__(self):
        self.camera_rho = 10
        self.camera_theta = 0
        self.camera_phi = 0
        self.x_a = 0
        self.y_a = 0
        self.z_a = 0

    def handle_key(self, ks):
        if ks == sdl2.SDLK_m:
            print(self)
        elif ks == sdl2.SDLK_a:
            self.x_a -= ROTATE_STEP
        elif ks == sdl2.SDLK_d:
            self.y_a += ROTATE_STEP

    def __str__(self):
        return ("CAMERA\t\t𝛒: {0}, Θ: {1}, 𝜑: {2}\n"
                "ROTATE\t\tx: {3}, y: {4}, z: {5}\n").format(
                    self.camera_rho, self.camera_theta, self.camera_phi,
                    self.x_a, self.y_a, self.z_a)


world = World()

sdl2e.init()
window = sdl2e.Window("Anal Penetration", size=(800, 600))
window.show()

running = True
while running:
    events = sdl2e.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            running = False
            break
        if event.type == sdl2.SDL_KEYDOWN:
            world.handle_key(event.key.keysym.sym)
    window.refresh()

sdl2e.quit()
