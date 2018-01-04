import math
import json
import numpy as np
import sdl2
import sdl2.ext as sdl2e


WIDTH = 800
HEIGHT = 600


def zoom(z):
    return np.array([[z, 0, 0, 0],
                     [0, z, 0, 0],
                     [0, 0, z, 0],
                     [0, 0, 0, 1]])


def perspective_projection(rho, phi, theta):
    z = rho * math.cos(phi)
    cp = math.cos(phi)
    sp = math.sin(phi)
    ct = math.cos(theta)
    st = math.sin(theta)
    return np.array([[cp, sp * st,  0, (sp * ct) / z],
                     [0,  ct,       0, -st / z],
                     [sp, -cp * st, 0, -(cp * ct) / z],
                     [0,  0,        0, 1]])


def draw(window):
    surface = window.get_surface()
    sdl2e.fill(surface, sdl2e.string_to_color("#ffffff"))

    points = figure["points"]
    points = np.dot(points, zoom(20))
    points = np.dot(points, perspective_projection(world["camera"]["rho"], world["camera"]["phi"], world["camera"]["theta"]))
    points = points / points[:, -1].reshape((points.shape[0], 1))
    points += [WIDTH / 2, HEIGHT / 2, 0, 0]

    for polygon in figure["polygons"]:
        n = len(polygon["points"])
        ppoints = list(map(lambda p: points[p], polygon["points"]))
        edges = map(lambda pi: (ppoints[pi], ppoints[(pi + 1) % n]), range(n))
        for edge, m in zip(edges, polygon["mask"]):
            if m == 0:
                continue
            try:
                # fails on out-of-view lines
                sdl2e.line(surface, sdl2e.string_to_color("#000000"), (edge[0][0], edge[0][1], edge[1][0], edge[1][1]))
            except:
                pass

    window.refresh()


def handle_key(window, ks):
    if ks == sdl2.SDLK_m:
        print(json.dumps(world, indent=2))
    elif ks == sdl2.SDLK_UP:
        world["camera"]["theta"] -= 0.05
    elif ks == sdl2.SDLK_DOWN:
        world["camera"]["theta"] += 0.05
    elif ks == sdl2.SDLK_LEFT:
        world["camera"]["phi"] -= 0.05
    elif ks == sdl2.SDLK_RIGHT:
        world["camera"]["phi"] += 0.05
    else:
        return
    draw(window)


world = {
    "camera": {
        "rho": 450.0,
        "phi": 0.0,
        "theta": 0.0
    },
    "rotate": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
    }
}

with open("figure.json", "r") as ff:
    figure = json.loads(ff.read())

figure["points"] = np.array(figure["points"])
figure["points"] -= np.mean(figure["points"], axis=0)
figure["points"] = np.hstack((figure["points"], np.ones((figure["points"].shape[0], 1))))

sdl2e.init()
window = sdl2e.Window("...", size=(WIDTH, HEIGHT))
window.show()
draw(window)

running = True
while running:
    events = sdl2e.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            running = False
            break
        if event.type == sdl2.SDL_KEYDOWN:
            handle_key(window, event.key.keysym.sym)

sdl2e.quit()
