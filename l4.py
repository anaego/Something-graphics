import math
import json
import numpy as np
import sdl2
import sdl2.ext as sdl2e


WIDTH = 800
HEIGHT = 600


def zoom(points, z):
    m = np.array([[z, 0, 0, 0],
                  [0, z, 0, 0],
                  [0, 0, z, 0],
                  [0, 0, 0, 1]])
    return np.dot(points, m)


# FIXME: replace w/ proper projection
def project(points, rho, phi, theta, d):
    z = rho * math.cos(phi)
    cp = math.cos(phi)
    sp = math.sin(phi)
    ct = math.cos(theta)
    st = math.sin(theta)
    m = np.array([[cp, sp * st,  0, (sp * ct) / z],
                  [0,  ct,       0, -st / z],
                  [sp, -cp * st, 0, -(cp * ct) / z],
                  [0,  0,        0, 1]])
    points = np.dot(points, m)
    points = points / points[:, -1].reshape((points.shape[0], 1))
    points += [WIDTH / 2, HEIGHT / 2, 0, 0]
    return points


def transform(world, points):
    points = zoom(points, 50) # FIXME: temporary, before proper proj is ready
    points = project(points, world["camera"]["rho"], world["camera"]["phi"], world["camera"]["theta"], world["d"])
    return points


def draw(window, points, polygons):
    surface = window.get_surface()
    sdl2e.fill(surface, sdl2e.string_to_color("#ffffff"))

    for polygon in polygons:
        n = len(polygon["points"])
        ppoints = list(map(lambda p: points[p], polygon["points"]))
        edges = map(lambda pi: (ppoints[pi], ppoints[(pi + 1) % n]), range(n))
        for edge, m in zip(edges, polygon["mask"]):
            if m == 0:
                continue
            try:
                # FIXME: fails on out-of-view lines, should do custom z-order canvas draws anyway
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
        return False

    return True


world = {
    "d": 100.0,
    "camera": {
        "rho": 400.0,
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
draw(window, transform(world, figure["points"]), figure["polygons"])

running = True
while running:
    events = sdl2e.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            running = False
            break
        if event.type == sdl2.SDL_KEYDOWN:
            if handle_key(window, event.key.keysym.sym):
                draw(window, transform(world, figure["points"]), figure["polygons"])

sdl2e.quit()
