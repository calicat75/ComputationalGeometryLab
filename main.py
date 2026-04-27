import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

X_LINE = 10
Y_LINE = 15
RECTANGLE_LIMIT = 20


class ConicDesigner:
    def __init__(self):
        self.x_min, self.x_max = -RECTANGLE_LIMIT, RECTANGLE_LIMIT
        self.y_min, self.y_max = -RECTANGLE_LIMIT, RECTANGLE_LIMIT

        self.P0 = (0, Y_LINE)
        self.P4 = (0, -Y_LINE)
        self.P2 = (-X_LINE, 0)

        self.P1 = None
        self.P3 = None
        self.dragging = False
        self.stage = 0

        self.coeff1 = None
        self.coeff2 = None

        self.setup_plot()

        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        plt.show()

    def setup_plot(self):
        self.fig = plt.figure(figsize=(15, 9))
        self.fig.canvas.manager.set_window_title('Построение симметричного составного конического сечения')

        gs = self.fig.add_gridspec(1, 2, width_ratios=[2.5, 1])
        self.ax = self.fig.add_subplot(gs[0])
        self.ax_info = self.fig.add_subplot(gs[1])

        self.ax.set_xlim(self.x_min, self.x_max)
        self.ax.set_ylim(self.y_min, self.y_max)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_aspect('equal')
        self.ax.set_title(
            "Симметричное составное коническое сечение\nКасательные: P0, P4 - горизонтальные, P2 - вертикальная")

        self.ax.axhline(y=0, color='black', linewidth=0.5, alpha=0.5)
        self.ax.axvline(x=0, color='black', linewidth=0.5, alpha=0.5)
        self.ax.axhline(y=Y_LINE, color='red', linestyle='--', alpha=0.3, linewidth=1)
        self.ax.axhline(y=-Y_LINE, color='red', linestyle='--', alpha=0.3, linewidth=1)
        self.ax.axvline(x=-X_LINE, color='red', linestyle='--', alpha=0.3, linewidth=1)

        self.draw_fixed_points()
        self.draw_valid_zones()

        self.ax_info.axis('off')
        self.ax_info.set_xlim(0, 1)
        self.ax_info.set_ylim(0, 1)

        ax_btn_clear = plt.axes([0.4, 0.02, 0.2, 0.05])
        self.btn_clear = Button(ax_btn_clear, 'ОЧИСТИТЬ')
        self.btn_clear.on_clicked(self.clear_plot)

        self.update_info_panel()

    def draw_fixed_points(self):
        self.ax.plot(self.P0[0], self.P0[1], 'gs', markersize=12, markeredgewidth=2)
        self.ax.plot([self.P0[0] - 2, self.P0[0] + 2], [self.P0[1], self.P0[1]], 'r-', linewidth=2, alpha=0.7)
        self.ax.text(self.P0[0] + 0.5, self.P0[1] + 0.5, 'P0', fontsize=12, fontweight='bold')

        self.ax.plot(self.P4[0], self.P4[1], 'gs', markersize=12, markeredgewidth=2)
        self.ax.plot([self.P4[0] - 2, self.P4[0] + 2], [self.P4[1], self.P4[1]], 'r-', linewidth=2, alpha=0.7)
        self.ax.text(self.P4[0] + 0.5, self.P4[1] - 1, 'P4', fontsize=12, fontweight='bold')

        self.ax.plot(self.P2[0], self.P2[1], 'bs', markersize=12, markeredgewidth=2)
        self.ax.plot([self.P2[0], self.P2[0]], [self.P2[1] - 2, self.P2[1] + 2], 'r-', linewidth=2, alpha=0.7)
        self.ax.text(self.P2[0] - 2, self.P2[1], 'P2', fontsize=12, fontweight='bold', color='blue')

        if self.P1:
            self.ax.plot(self.P1[0], self.P1[1], 'ro', markersize=10)
            self.ax.text(self.P1[0] + 0.5, self.P1[1] + 0.5, 'P1', color='red', fontsize=11, fontweight='bold')
        if self.P3:
            self.ax.plot(self.P3[0], self.P3[1], 'ro', markersize=10)
            self.ax.text(self.P3[0] + 0.5, self.P3[1] + 0.5, 'P3', color='red', fontsize=11, fontweight='bold')

    def draw_valid_zones(self):
        """Рисуем полупрозрачные зоны, где разрешено ставить P1 и P3"""
        # Удаляем старые зоны
        for patch in self.ax.patches:
            if hasattr(patch, 'get_label') and patch.get_label() == 'valid_zone':
                patch.remove()

        # Зона для P1 (верхняя)
        rect1 = plt.Rectangle((-X_LINE, self.P2[1]), X_LINE, Y_LINE - self.P2[1],
                              facecolor='yellow', alpha=0.15, edgecolor='orange', linestyle='--', label='valid_zone')
        self.ax.add_patch(rect1)
        self.ax.text(-X_LINE / 2, (self.P2[1] + Y_LINE) / 2, 'Зона для P1', ha='center', color='orange', alpha=0.6)

        # Зона для P3 (нижняя)
        rect2 = plt.Rectangle((-X_LINE, -Y_LINE), X_LINE, self.P2[1] - (-Y_LINE),
                              facecolor='cyan', alpha=0.15, edgecolor='blue', linestyle='--', label='valid_zone')
        self.ax.add_patch(rect2)
        self.ax.text(-X_LINE / 2, (-Y_LINE + self.P2[1]) / 2, 'Зона для P3', ha='center', color='blue', alpha=0.6)

    def is_valid_click(self, x, y, target):
        """Проверяет, находится ли клик в допустимой прямоугольной области"""
        if x is None or y is None:
            return False
        # Базовые границы прямоугольника
        if not (-X_LINE <= x <= 0 and -Y_LINE <= y <= Y_LINE):
            return False
        # Уточнение по сегментам
        if target == 'P1':
            return self.P2[1] <= y <= Y_LINE
        elif target == 'P3':
            return -Y_LINE <= y <= self.P2[1]
        return False

    def reflect_point_across_line(self, point, line_point, is_horizontal=True):
        x, y = point
        if is_horizontal:
            return (x, 2 * line_point[1] - y)
        else:
            return (2 * line_point[0] - x, y)

    def fit_conic_liming(self, p_tangent1, p_tangent2, point_on_conic,
                         tangent1_horizontal=True, tangent2_vertical=True):
        mirrored1 = self.reflect_point_across_line(point_on_conic, p_tangent1, tangent1_horizontal)
        mirrored2 = self.reflect_point_across_line(mirrored1, p_tangent2, not tangent2_vertical)
        pts = np.array([p_tangent1, p_tangent2, point_on_conic, mirrored2])

        x = pts[:, 0]
        y = pts[:, 1]
        M = np.column_stack([x * x, x * y, y * y, x, y, np.ones_like(x)])
        _, _, Vt = np.linalg.svd(M)
        coeff = Vt[-1]
        norm = np.linalg.norm(coeff)
        if norm > 1e-10:
            coeff = coeff / norm
        return coeff

    def classify_conic(self, coeff):
        A, B, C, _, _, _ = coeff
        delta = B ** 2 - 4 * A * C
        if abs(delta) < 1e-4:
            return "Парабола"
        elif delta < 0:
            return "Эллипс"
        else:
            return "Гипербола"

    def evaluate_conic(self, coeff, x, y):
        if coeff is None: return 0
        A, B, C, D, E, F = coeff
        return A * x * x + B * x * y + C * y * y + D * x + E * y + F

    def get_derivatives(self, coeff, x, y):
        A, B, C, D, E, F = coeff
        dx = 2 * A * x + B * y + D
        dy = B * x + 2 * C * y + E
        return dx, dy

    def check_continuity(self, coeff1, coeff2, point):
        x0, y0 = point
        if coeff1 is None or coeff2 is None: return None
        val1 = self.evaluate_conic(coeff1, x0, y0)
        val2 = self.evaluate_conic(coeff2, x0, y0)
        c0_continuous = abs(val1 - val2) < 1e-6
        result = {'point': point, 'c0_continuous': c0_continuous, 'left_value': val1, 'right_value': val2,
                  'jump': abs(val1 - val2)}
        if not c0_continuous:
            result['discontinuity_type'] = 'Разрыв C0 (скачок функции)'
            return result

        dx1, dy1 = self.get_derivatives(coeff1, x0, y0)
        dx2, dy2 = self.get_derivatives(coeff2, x0, y0)
        tangent1 = np.array([-dy1, dx1])
        tangent2 = np.array([-dy2, dx2])
        norm1, norm2 = np.linalg.norm(tangent1), np.linalg.norm(tangent2)

        if norm1 > 1e-6 and norm2 > 1e-6:
            tangent1, tangent2 = tangent1 / norm1, tangent2 / norm2
            dot_product = np.clip(np.dot(tangent1, tangent2), -1, 1)
            angle = np.arccos(dot_product) * 180 / np.pi
            c1_continuous = angle < 1e-6
            result.update({'c1_continuous': c1_continuous, 'angle': angle, 'tangent1': tangent1, 'tangent2': tangent2})
            result[
                'discontinuity_type'] = 'Гладкое соединение' if c1_continuous else f'Разрыв C1 (излом, угол {angle:.2f}°)'
        else:
            result.update({'c1_continuous': False, 'discontinuity_type': 'Неопределенная касательная'})
        return result

    def draw_conic(self, coeff, ax, color='blue'):
        if coeff is None: return
        A, B, C, D, E, F = coeff
        x = np.linspace(self.x_min, self.x_max, 400)
        y = np.linspace(self.y_min, self.y_max, 400)
        X, Y = np.meshgrid(x, y)
        Z = A * X ** 2 + B * X * Y + C * Y ** 2 + D * X + E * Y + F
        ax.contour(X, Y, Z, levels=[0], colors=color, linewidths=2.5, alpha=0.8)

    def calculate_and_draw(self):
        if self.P1 is None or self.P3 is None: return
        for coll in self.ax.collections[:]:
            if hasattr(coll, 'get_color') and coll.get_color() in ['blue', 'green']:
                coll.remove()
        self.redraw_base()

        self.coeff1 = self.fit_conic_liming(self.P0, self.P2, self.P1, True, False)
        self.draw_conic(self.coeff1, self.ax, 'blue')

        self.coeff2 = self.fit_conic_liming(self.P2, self.P4, self.P3, False, True)
        self.draw_conic(self.coeff2, self.ax, 'green')

        self.visualize_continuity()
        self.analyze_conics(self.coeff1, self.coeff2)
        self.fig.canvas.draw_idle()

    def visualize_continuity(self):
        if self.coeff1 is None or self.coeff2 is None: return
        continuity = self.check_continuity(self.coeff1, self.coeff2, self.P2)
        if continuity:
            if not continuity['c0_continuous']:
                self.ax.plot(self.P2[0], self.P2[1], 'rx', markersize=15, markeredgewidth=3, label='Разрыв C0')
            elif not continuity.get('c1_continuous', False):
                self.ax.plot(self.P2[0], self.P2[1], 'rd', markersize=12, markeredgewidth=2, label='Излом (C1 разрыв)')
            else:
                self.ax.plot(self.P2[0], self.P2[1], 'go', markersize=12, markeredgewidth=2, label='Гладкое соединение')

    def analyze_conics(self, coeff1, coeff2):
        type1 = self.classify_conic(coeff1)
        type2 = self.classify_conic(coeff2)
        continuity = self.check_continuity(coeff1, coeff2, self.P2)
        self.update_info_panel(type1, type2, coeff1, coeff2, continuity)

    def update_info_panel(self, type1=None, type2=None, coeff1=None, coeff2=None, continuity=None):
        """Обновление информационной панели с анализом непрерывности"""
        self.ax_info.clear()
        self.ax_info.axis('off')

        text = "СИММЕТРИЧНОЕ СОСТАВНОЕ КОНИЧЕСКОЕ СЕЧЕНИЕ\n"
        text += "=" * 40 + "\n\n"

        text += "КАСАТЕЛЬНЫЕ:\n"
        text += f"  P0 ({self.P0[0]}, {self.P0[1]}) → горизонтальная\n"
        text += f"  P2 ({self.P2[0]:.1f}, {self.P2[1]:.2f}) → вертикальная\n"
        text += f"  P4 ({self.P4[0]}, {self.P4[1]}) → горизонтальная\n\n"

        if self.P1:
            text += "ТОЧКИ НА КОНИКЕ:\n"
            text += f"  P1: ({self.P1[0]:.2f}, {self.P1[1]:.2f})\n"
        if self.P3:
            text += f"  P3: ({self.P3[0]:.2f}, {self.P3[1]:.2f})\n\n"

        if type1 and type2 and coeff1 is not None and coeff2 is not None:
            text += "─" * 40 + "\n"
            text += "СЕГМЕНТ 1: P0 → P1 → P2\n"
            text += f"  Тип: {type1}\n"
            A, B, C, D, E, F = coeff1
            text += f"  {A:+.6f}x² {B:+.6f}xy {C:+.6f}y²\n"
            text += f"  {D:+.6f}x {E:+.6f}y {F:+.6f} = 0\n"
            text += "\n"

            text += "СЕГМЕНТ 2: P2 → P3 → P4\n"
            text += f"  Тип: {type2}\n"
            A, B, C, D, E, F = coeff2
            text += f"  {A:+.6f}x² {B:+.6f}xy {C:+.6f}y²\n"
            text += f"  {D:+.6f}x {E:+.6f}y {F:+.6f} = 0\n"
            text += "\n"

            text += "═" * 40 + "\n"
            text += "АНАЛИЗ НЕПРЕРЫВНОСТИ В ТОЧКЕ P2\n"
            text += "═" * 40 + "\n"

            if continuity:
                x0, y0 = continuity['point']
                text += f"\nКоординаты стыка: ({x0:.2f}, {y0:.2f})\n\n"

                # Проверка C0
                if continuity['c0_continuous']:
                    text += "C0 - НЕПРЕРЫВНОСТЬ ВЫПОЛНЕНА\n"
                    text += f"  F1({x0:.2f},{y0:.2f}) = {continuity['left_value']:.6f}\n"
                    text += f"  F2({x0:.2f},{y0:.2f}) = {continuity['right_value']:.6f}\n\n"
                else:
                    text += "C0 - НЕПРЕРЫВНОСТЬ НАРУШЕНА\n"
                    text += f"  Левое значение: {continuity['left_value']:.6f}\n"
                    text += f"  Правое значение: {continuity['right_value']:.6f}\n"
                    text += f"  Величина скачка: {continuity['jump']:.6f}\n\n"

                # Проверка C1 (только если C0 выполнена)
                if continuity['c0_continuous']:
                    if 'c1_continuous' in continuity:
                        if continuity['c1_continuous']:
                            text += "C1 - ГЛАДКОЕ СОЕДИНЕНИЕ\n"
                            text += "  Касательные совпадают по направлению\n"
                        else:
                            text += "C1 - НЕПРЕРЫВНОСТЬ НАРУШЕНА (излом)\n"
                            if 'angle' in continuity and continuity['angle'] is not None:
                                text += f"  Угол между касательными: {continuity['angle']:.2f}°\n"
                            if 'tangent1' in continuity and continuity['tangent1'] is not None:
                                text += f"  Касательная слева: ({continuity['tangent1'][0]:.4f}, {continuity['tangent1'][1]:.4f})\n"
                            if 'tangent2' in continuity and continuity['tangent2'] is not None:
                                text += f"  Касательная справа: ({continuity['tangent2'][0]:.4f}, {continuity['tangent2'][1]:.4f})\n"
                    else:
                        text += "? C1 - не удалось определить\n"

                text += f"\nТИП СОЕДИНЕНИЯ: {continuity['discontinuity_type']}\n"
            else:
                text += "\nНевозможно определить непрерывность\n"

        self.ax_info.text(0.05, 0.95, text, fontsize=8, family='monospace',
                          va='top', transform=self.ax_info.transAxes,
                          bbox=dict(boxstyle='round', facecolor='lightyellow',
                                    edgecolor='gray', alpha=0.9))

        self.fig.canvas.draw_idle()

    def on_click(self, event):
        if event.inaxes != self.ax or self.dragging: return
        x, y = event.xdata, event.ydata

        if self.stage == 0 and self.P1 is None:
            if not self.is_valid_click(x, y, 'P1'): return
            self.P1 = (x, y)
            self.ax.plot(x, y, 'ro', markersize=10)
            self.ax.text(x + 0.5, y + 0.5, 'P1', color='red', fontsize=11, fontweight='bold')
            self.stage = 1
            self.update_info_panel()
            self.fig.canvas.draw_idle()

        elif self.stage == 1 and self.P3 is None:
            if not self.is_valid_click(x, y, 'P3'): return
            self.P3 = (x, y)
            self.ax.plot(x, y, 'ro', markersize=10)
            self.ax.text(x + 0.5, y + 0.5, 'P3', color='red', fontsize=11, fontweight='bold')
            self.update_info_panel()
            self.fig.canvas.draw_idle()
            self.calculate_and_draw()

    def on_press(self, event):
        if event.inaxes != self.ax: return
        if self.is_near_point(event.xdata, event.ydata, self.P2):
            self.dragging = True
            self.current_drag_point = 'P2'

    def on_motion(self, event):
        if not self.dragging or event.inaxes != self.ax: return
        if self.current_drag_point == 'P2':
            # Ограничиваем движение P2 пределами прямоугольника
            new_y = max(-Y_LINE, min(event.ydata, Y_LINE))
            # Защита: не даем P2 пересечь уже установленные P1/P3
            if self.P1: new_y = min(new_y, self.P1[1] - 0.5)
            if self.P3: new_y = max(new_y, self.P3[1] + 0.5)

            self.P2 = (-X_LINE, new_y)
            if self.P1 and self.P3:
                self.calculate_and_draw()
            else:
                self.redraw_base()

    def on_release(self, event):
        self.dragging = False
        self.current_drag_point = None

    def redraw_base(self):
        self.ax.clear()
        self.ax.set_xlim(self.x_min, self.x_max)
        self.ax.set_ylim(self.y_min, self.y_max)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_aspect('equal')
        self.ax.set_title("Симметричное составное коническое сечение")
        self.ax.axhline(y=0, color='black', linewidth=0.5, alpha=0.5)
        self.ax.axvline(x=0, color='black', linewidth=0.5, alpha=0.5)
        self.ax.axhline(y=Y_LINE, color='red', linestyle='--', alpha=0.3, linewidth=1)
        self.ax.axhline(y=-Y_LINE, color='red', linestyle='--', alpha=0.3, linewidth=1)
        self.ax.axvline(x=-X_LINE, color='red', linestyle='--', alpha=0.3, linewidth=1)
        self.draw_fixed_points()
        self.draw_valid_zones()
        self.fig.canvas.draw_idle()

    def clear_plot(self, event):
        self.P1 = None
        self.P3 = None
        self.coeff1 = None
        self.coeff2 = None
        self.stage = 0
        self.redraw_base()
        self.update_info_panel()

    def is_near_point(self, x, y, point, tolerance=0.7):
        if x is None or y is None: return False
        return np.sqrt((x - point[0]) ** 2 + (y - point[1]) ** 2) < tolerance


if __name__ == "__main__":
    designer = ConicDesigner()