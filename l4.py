import math
import json
import numpy as np
import sdl2
import sdl2.ext as sdl2e

WIDTH = 800
HEIGHT = 600


def rotate_x(points, angle):
    c = math.cos(angle)
    s = math.sin(angle)
    m = np.array([[1, 0, 0, 0],
                  [0, c, -s, 0],
                  [0, s, c, 0],
                  [0, 0, 0, 1]])
    return np.dot(m, points.T).T


def rotate_y(points, angle):
    c = math.cos(angle)
    s = math.sin(angle)
    m = np.array([[c, 0, -s, 0],
                  [0, 1, 0, 0],
                  [s, 0, c, 0],
                  [0, 0, 0, 1]])
    return np.dot(m, points.T).T


def rotate_z(points, angle):
    c = math.cos(angle)
    s = math.sin(angle)
    m = np.array([[c, -s, 0, 0],
                  [s, c, 0, 0],
                  [0, 0, 1, 0],
                  [0, 0, 0, 1]])
    return np.dot(m, points.T).T


def move(points, point):
    m = np.array([[1, 0, 0, point[0]],
                  [0, 1, 0, point[1]],
                  [0, 0, 1, point[2]],
                  [0, 0, 0, 1]])
    return np.dot(m, points.T).T


def axis_rotate(points, axis, angle):
    S = (axis[1] - axis[0]).T
    W = S / np.linalg.norm(S)
    a = np.cross(W, [0, 0, 1])
    V = a / np.linalg.norm(a)
    U = np.cross(V, W)
    m = np.array([[U[0], U[1], U[2], 0],
                  [V[0], V[1], V[2], 0],
                  [W[0], W[1], W[2], 0],
                  [0, 0, 0, 1]])
    # step 1
    points = move(points, -axis[0])
    # step 2
    points = np.dot(m, points.T).T
    # step 3
    points = rotate_z(points, angle)
    # step 4
    points = np.dot(m.T, points.T).T
    # step 5
    points = move(points, axis[0])
    return points


def zoom(points, z):
    m = np.array([[z, 0, 0, 0],
                  [0, z, 0, 0],
                  [0, 0, z, 0],
                  [0, 0, 0, 1]])
    return np.dot(m, points.T).T


# FIXME: replace w/ proper projection
def project(points, rho, phi, theta, d):
    z = rho * math.cos(phi)
    cp = math.cos(phi)
    sp = math.sin(phi)
    ct = math.cos(theta)
    st = math.sin(theta)
    m = np.array([[cp, sp * st, 0, (sp * ct) / z],
                  [0, ct, 0, -st / z],
                  [sp, -cp * st, 0, -(cp * ct) / z],
                  [0, 0, 0, 1]])
    points = np.dot(m, points.T).T
    points = points / points[:, -1].reshape((points.shape[0], 1))
    #points += [WIDTH / 2, HEIGHT / 2, 0, 0]
    return points


def true_project(points, rho, phi, theta, d):
    n = 1
    f = 100
    aspect = WIDTH / HEIGHT
    fov = 0.02
    # helpers
    ctg = 1 / math.tan(fov / 2)
    nct = ctg / aspect
    fpn = (f + n) / (f - n)
    nfn = -2 * f * n / (f - n)
    # The Matrix
    m = np.array([[ctg, 0, 0, 0],
                  [0, nct, 0, 0],
                  [0, 0, fpn, 1],
                  [0, 0, nfn, 0]])
    return np.dot(m, points.T).T


def transform(world, points):
    #points = zoom(points, 50)  # FIXME: temporary, before proper proj is ready
    points = rotate_x(points, world["rotate"]["x"])
    points = rotate_y(points, world["rotate"]["y"])
    points = rotate_z(points, world["rotate"]["z"])
    points = axis_rotate(points, figure["AB"], world["rotate"]["AB"])
    #points = project(points, world["camera"]["rho"], world["camera"]["phi"], world["camera"]["theta"], world["d"])
    points = true_project(points, world["camera"]["rho"], world["camera"]["phi"], world["camera"]["theta"], world["d"])
    points += [WIDTH / 2, HEIGHT / 2, 0, 0]
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
    elif ks == sdl2.SDLK_s:
        world["rotate"]["x"] -= 0.05
    elif ks == sdl2.SDLK_w:
        world["rotate"]["x"] += 0.05
    elif ks == sdl2.SDLK_a:
        world["rotate"]["y"] -= 0.05
    elif ks == sdl2.SDLK_d:
        world["rotate"]["y"] += 0.05
    elif ks == sdl2.SDLK_q:
        world["rotate"]["z"] -= 0.05
    elif ks == sdl2.SDLK_e:
        world["rotate"]["z"] += 0.05
    elif ks == sdl2.SDLK_r:
        world["rotate"]["AB"] += 0.05
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
        "z": 0.0,
        "AB": 0.0
    },
    "m": [0, 0, 0]
}

with open("figure.json", "r") as ff:
    figure = json.loads(ff.read())

figure["points"] = np.array(figure["points"])
print(figure["points"])
figure["points"] -= np.mean(figure["points"], axis=0)
print(figure["points"])
figure["points"] = np.hstack((figure["points"], np.ones((figure["points"].shape[0], 1))))
print(figure["points"])
figure["AB"] = np.array(figure["AB"])

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
