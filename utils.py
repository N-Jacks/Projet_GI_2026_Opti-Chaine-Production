import math

def distance(p1, p2):
    x1, y1 = p1[:2]
    x2, y2 = p2[:2]
    return math.hypot(x2-x1,y2-y1)

def two_opt(path, distance_func):
    """
    path : liste de points [(x, y, poly), ...]
    distance_func : fonction distance(p1, p2)
    """
    improved = True
    while improved:
        improved = False
        n = len(path)
        for i in range(n - 1):
            for j in range(i + 2, n):
                # ne pas inverser les arêtes adjacentes
                a, b = path[i], path[i + 1]
                c, d = path[j], path[(j + 1) % n]

                # distance avant et après échange
                d0 = distance_func(a, b) + distance_func(c, d)
                d1 = distance_func(a, c) + distance_func(b, d)

                if d1 < d0:
                    # inversion
                    path[i + 1:j + 1] = reversed(path[i + 1:j + 1])
                    improved = True
    return path