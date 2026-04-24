import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import math


# 1. Математика: Отражение точки относительно прямой
def reflect_point_across_line(point, p1_line, p2_line):
    """
    Отражает точку point относительно прямой, заданной точками p1_line и p2_line.
    """
    x, y = point
    x1, y1 = p1_line
    x2, y2 = p2_line

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0: return point

    t = ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy

    return (2 * proj_x - x, 2 * proj_y - y)


# 2. Математика: Подгонка коники (SVD для 8 точек)
def fit_conic_symmetric(axis_p1, axis_p2, curve_points):
    # 1. Генерируем зеркальные точки
    mirrored_points = [reflect_point_across_line(p, axis_p1, axis_p2) for p in curve_points]

    # 2. Собираем все точки: 2 точки оси + 3 исходные + 3 зеркальные = 8 точек
    all_points = [axis_p1, axis_p2] + curve_points + mirrored_points

    M = []
    for x, y in all_points:
        # Уравнение: Ax^2 + Bxy + Cy^2 + Dx + Ey + F = 0
        M.append([x * x, x * y, y * y, x, y, 1])

    M = np.array(M)

    # SVD решение (находим вектор, минимизирующий ошибку для 8 точек)
    _, _, Vt = np.linalg.svd(M)
    coeff = Vt[-1, :]

    # Нормализация
    norm = np.linalg.norm(coeff)
    if norm > 1e-10:
        coeff = coeff / norm

    return coeff


# 3. Классификация
def classify_conic(coeff):
    A, B, C, _, _, _ = coeff
    delta = B ** 2 - 4 * A * C
    if abs(delta) < 1e-4:
        return "Парабола"
    elif delta < 0:
        return "Эллипс"
    else:
        return "Гипербола"


def check_continuity(coeff):
    A, B, C, D, E, F = coeff
    # Для симметричной коники B и D должны быть близки к 0
    is_symmetric = (abs(B) < 0.1) and (abs(D) < 0.1)
    if is_symmetric:
        return True, "Гладкое соединение (G1 непрерывность)"
    else:
        return False, "Возможен излом"


# 4. Отрисовка
def draw_conic(coeff, ax):
    x = np.linspace(-10, 10, 600)
    y = np.linspace(-10, 10, 600)
    X, Y = np.meshgrid(x, y)

    A, B, C, D, E, F = coeff
    Z = A * X ** 2 + B * X * Y + C * Y ** 2 + D * X + E * Y + F

    # Удаляем старые контуры
    for coll in ax.collections[:]:
        coll.remove()

    ax.contour(X, Y, Z, levels=[0], colors='blue', linewidths=2)


# 5. GUI Состояние
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
ax.set_title("Кликните 1-ю точку оси (P0)")
ax.axhline(0, color='black', linewidth=0.5)
ax.axvline(0, color='black', linewidth=0.5)

ax_info.axis('off')

# 6. Кнопка ОЧИСТИТЬ
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
    ax.set_title("Кликните 1-ю точку оси (P0)")
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)

    # Добавляем подсказку сразу после очистки
    ax.text(0, -9, "Совет: Для Гиперболы ставьте точки 'зигзагом' (W)",
            ha='center', fontsize=10, style='italic', color='gray')

    ax_info.clear()
    ax_info.axis('off')

    fig.canvas.draw_idle()


btn_clear.on_clicked(clear_plot)


# 7. Обработка кликов
def onclick(event):
    global stage, points_axis, points_curve

    if event.xdata is None or event.ydata is None:
        return

    p = (event.xdata, event.ydata)

    # Этап 1: Первая точка оси
    if stage == 0:
        points_axis.append(p)
        ax.plot(p[0], p[1], 'kx', markersize=15, markeredgewidth=2)
        ax.text(p[0], p[1] - 0.5, 'P0', color='black', fontsize=12)
        stage = 1
        ax.set_title("Кликните 2-ю точку оси (P1)")
        fig.canvas.draw_idle()

    # Этап 2: Вторая точка оси
    elif stage == 1:
        points_axis.append(p)
        ax.plot(p[0], p[1], 'kx', markersize=15, markeredgewidth=2)
        ax.text(p[0], p[1] - 0.5, 'P1', color='black', fontsize=12)

        ax.plot([points_axis[0][0], points_axis[1][0]],
                [points_axis[0][1], points_axis[1][1]],
                'g--', linewidth=1.5, alpha=0.7)

        stage = 2
        ax.set_title("Кликните 3 точки кривой")
        fig.canvas.draw_idle()

    # Этап 3: Точки кривой
    elif stage == 2:
        points_curve.append(p)
        ax.plot(p[0], p[1], 'ro', markersize=10)
        ax.text(p[0] + 0.2, p[1] + 0.2, f'P{len(points_curve) + 1}', color='red', fontweight='bold')

        if len(points_curve) == 3:
            process_result()
            stage = 3

        fig.canvas.draw_idle()


def process_result():
    # 1. Математика
    coeff = fit_conic_symmetric(points_axis[0], points_axis[1], points_curve)

    # 2. Рисуем сечение
    draw_conic(coeff, ax)
    ax.set_title("Симметричное составное коническое сечение")

    # 3. Обновляем информационную панель
    update_info_panel(coeff, points_axis, points_curve)


def update_info_panel(coeff, p_axis, p_curve):
    ax_info.clear()
    ax_info.axis('off')

    A, B, C, D, E, F = coeff
    c_type = classify_conic(coeff)
    is_cont, msg = check_continuity(coeff)

    text = f"""
ВХОДНЫЕ ДАННЫЕ:
P0 (Ось): ({p_axis[0][0]:.1f}, {p_axis[0][1]:.1f})
P1 (Ось): ({p_axis[1][0]:.1f}, {p_axis[1][1]:.1f})

P2 (Дуга): ({p_curve[0][0]:.1f}, {p_curve[0][1]:.1f})
P3 (Дуга): ({p_curve[1][0]:.1f}, {p_curve[1][1]:.1f})
P4 (Дуга): ({p_curve[2][0]:.1f}, {p_curve[2][1]:.1f})

--------------------------
ТИП СЕЧЕНИЯ: {c_type}
--------------------------
КОЭФФИЦИЕНТЫ:
A = {A:.3f}   B = {B:.3f}
C = {C:.3f}   D = {D:.3f}
E = {E:.3f}   F = {F:.3f}

--------------------------
АНАЛИЗ РАЗРЫВОВ:
{'НЕПРЕРЫВНО' if is_cont else 'РАЗРЫВ'}
{msg}
"""
    ax_info.text(0.05, 0.95, text, fontsize=10, family='monospace',
                 va='top',
                 bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='gray'))


# Запуск
fig.canvas.mpl_connect('button_press_event', onclick)
# Инициализация подсказки
#ax.text(0, -9, "Совет: Для Гиперболы ставьте точки 'зигзагом' (W)",
 #       ha='center', fontsize=10, style='italic', color='gray')
plt.show()