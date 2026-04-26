import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button


# 1. Отражение (ось x=0)
def reflect_vertical(point):
    x, y = point
    return (-x, y)


# 2. Подгонка коники
# Ax^2 + Cy^2 + Ey + F = 0
def fit_conic_exact_3points(points):
    # берём 3 точки
    p1, p2, p3 = points

    # формируем систему
    # A*x^2 + C*y^2 + E*y = 1   (F = -1)
    M = []
    b = []

    for x, y in [p1, p2, p3]:
        M.append([x*x, y*y, y])
        b.append(1)

    M = np.array(M)
    b = np.array(b)

    # строгое решение
    try:
        A, C, E = np.linalg.solve(M, b)
        F = -1
        return np.array([A, C, E, F]), True
    except np.linalg.LinAlgError:
        return None, False


# 3. Проверка прохождения
def check_all_points(coeff, points, tol=1e-4):
    A, C, E, F = coeff

    for x, y in points:
        val = A*x*x + C*y*y + E*y + F
        if abs(val) > tol:
            return False
    return True


# 4. Классификация
def classify_conic(coeff):
    A, C, _, _ = coeff

    if A * C > 0:
        return "Эллипс"
    elif A * C < 0:
        return "Гипербола"
    else:
        return "Парабола"


# 5. Производная
def derivative(coeff, x, y):
    A, C, E, F = coeff

    Fx = 2*A*x
    Fy = 2*C*y + E

    if abs(Fy) < 1e-6:
        return None

    return -Fx / Fy


def check_continuity(coeff, y0=0, eps=1e-3):
    # проверяем на оси x=0
    left = derivative(coeff, -eps, y0)
    right = derivative(coeff, eps, y0)

    if left is None or right is None:
        return True, "Вертикальная касательная"

    if abs(left - right) < 1e-2:
        return True, "G1 гладкость"
    else:
        return False, f"Разрыв: {left:.2f} vs {right:.2f}"


# 6. Отрисовка
def draw_conic(coeff, ax):
    x = np.linspace(-10, 10, 600)
    y = np.linspace(-10, 10, 600)
    X, Y = np.meshgrid(x, y)

    A, C, E, F = coeff
    Z = A*X**2 + C*Y**2 + E*Y + F

    for coll in ax.collections[:]:
        coll.remove()

    ax.contour(X, Y, Z, levels=[0], linewidths=2)


# 7. GUI
points_axis = []
points_curve = []
stage = 0

fig = plt.figure(figsize=(14, 7))
gs = fig.add_gridspec(1, 2, width_ratios=[3, 1])

ax = fig.add_subplot(gs[0])
ax_info = fig.add_subplot(gs[1])

ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)
ax.grid(True)
ax.set_aspect('equal')
ax.set_title("Кликните верхнюю точку оси (x=0)")
ax.axhline(0, color='black', linewidth=0.5)
ax.axvline(0, color='black', linewidth=0.5)

ax_info.axis('off')


# 8. Кнопка очистки
ax_btn_clear = plt.axes([0.4, 0.02, 0.2, 0.05])
btn_clear = Button(ax_btn_clear, 'ОЧИСТИТЬ')


def clear_plot(event):
    global stage, points_axis, points_curve

    stage = 0
    points_axis = []
    points_curve = []

    ax.clear()
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.grid(True)
    ax.set_aspect('equal')
    ax.set_title("Кликните верхнюю точку оси (x=0)")
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)

    ax_info.clear()
    ax_info.axis('off')

    fig.canvas.draw_idle()


btn_clear.on_clicked(clear_plot)


# 9. Клики
def onclick(event):
    global stage, points_axis, points_curve

    if event.xdata is None:
        return

    x, y = event.xdata, event.ydata

    # ось фиксируем
    if stage < 2:
        x = 0

    p = (x, y)

    if stage == 0:
        points_axis.append(p)
        ax.plot(x, y, 'kx')
        ax.text(x, y-0.5, 'P0')
        stage = 1
        ax.set_title("Кликните нижнюю точку оси")

    elif stage == 1:
        points_axis.append(p)
        ax.plot(x, y, 'kx')
        ax.text(x, y-0.5, 'P1')

        ax.plot([0, 0], [points_axis[0][1], points_axis[1][1]], 'g--')

        stage = 2
        ax.set_title("Кликните 3 точки кривой")

    elif stage == 2:
        points_curve.append(p)
        ax.plot(x, y, 'ro')

        if len(points_curve) == 3:
            process_result()
            stage = 3

    fig.canvas.draw_idle()


# 10. Основная логика
def process_result():
    coeff, ok = fit_conic_exact_3points(points_curve)

    if not ok:
        show_error("Система вырождена")
        return

    # проверяем все 6 точек
    mirrored = [reflect_vertical(p) for p in points_curve]
    all_points = points_curve + mirrored

    exact = check_all_points(coeff, all_points)

    draw_conic(coeff, ax)

    update_info(coeff, exact)


# 11. Инфо
def show_error(msg):
    ax_info.clear()
    ax_info.axis('off')
    ax_info.text(0.1, 0.5, msg, color='red', fontsize=12)


def update_info(coeff, exact):
    ax_info.clear()
    ax_info.axis('off')

    A, C, E, F = coeff
    c_type = classify_conic(coeff)
    cont, msg = check_continuity(coeff)

    text = f"""
ТИП: {c_type}

A = {A:.3f}
C = {C:.3f}
E = {E:.3f}
F = {F:.3f}

------------------
ПРОХОДИТ ЧЕРЕЗ ВСЕ ТОЧКИ:
{'ДА' if exact else 'НЕТ'}

------------------
ГЛАДКОСТЬ:
{'ДА' if cont else 'НЕТ'}
{msg}
"""

    ax_info.text(0.05, 0.95, text,
                 fontsize=10,
                 family='monospace',
                 va='top')


# Запуск
fig.canvas.mpl_connect('button_press_event', onclick)
plt.show()