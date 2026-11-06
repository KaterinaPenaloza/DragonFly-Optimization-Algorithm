# Restricciones unarias
# Cada variable está en un rango de 0 a valormaximo que puede tomar
domains = {
    'x1': list(range(16)),  # Rango de 0 a 15 tv tarde
    'x2': list(range(11)),  # Rango de 0 a 10 tv noche
    'x3': list(range(26)),  # Rango de 0 a 25 diario
    'x4': list(range(5)),   # Rango de 0 a 4  revista
    'x5': list(range(31))   # Rango de 0 a 30 radio
}

# Restricciones binarias
constraints = {
    # Presupuesto en tv
    ('x1', 'x2'): lambda x1, x2: 180 * x1 + 310 * x2 <= 3800,
    # Presupuesto en diario y revista
    ('x3', 'x4'): lambda x3, x4: 60 * x3 + 100 * x4 <= 2800,
    # Presupuesto en diario y radio
    ('x3', 'x5'): lambda x3, x5: 60 * x3 + 15 * x5 <= 3500,
}


def revise(x, y):
    revised = False
    x_domain = domains[x]
    y_domain = domains[y]

    for x_value in x_domain[:]:
        satisfies = False
        for y_value in y_domain:
            if (x, y) in constraints:
                ok = constraints[(x, y)](x_value, y_value)
            else:
                ok = constraints[(y, x)](y_value, x_value)
            if ok:
                satisfies = True
                break
        if not satisfies:
            x_domain.remove(x_value)
            revised = True
    return revised

def ac3(arcs):
    queue = arcs[:]
    while queue:
        (x, y) = queue.pop(0)
        if revise(x, y):
            if not domains[x]:
                return False
            neighbors = [(z, w) for (z, w) in arcs if w == x and z != y]
            queue.extend(neighbors)
    return True

arcs = [
    ('x1', 'x2'), ('x2', 'x1'),
    ('x3', 'x4'), ('x4', 'x3'),
    ('x3', 'x5'), ('x5', 'x3')
]

if __name__ == "__main__":
    consistent = ac3(arcs)
    print(consistent)
    print(domains)
