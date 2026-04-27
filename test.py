import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

X_LINE = 20
Y_LINE = 30
RECTANGLE_LIMIT = 40


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
            "Симметричное составное коническое сечение\nКасательные: P0 и P4 - горизонтальные, P2 - вертикальная")

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
        self.ax.plot(self.P0[0], self.P0[1], 'gs', markersize=12, markeredgewidth=2, alpha=0.5, zorder=5)
        self.ax.plot([self.P0[0] - 2, self.P0[0] + 2], [self.P0[1], self.P0[1]],
                     'r-', linewidth=2, alpha=0.7, zorder=4)
        self.ax.text(self.P0[0] + 0.5, self.P0[1] + 0.5, 'P0', fontsize=12, fontweight='bold', zorder=6)

        self.ax.plot(self.P4[0], self.P4[1], 'gs', markersize=12, markeredgewidth=2, zorder=5, alpha=0.5)
        self.ax.plot([self.P4[0] - 2, self.P4[0] + 2], [self.P4[1], self.P4[1]],
                     'r-', linewidth=2, alpha=0.7, zorder=4)
        self.ax.text(self.P4[0] + 0.5, self.P4[1] - 1, 'P4', fontsize=12, fontweight='bold', zorder=6)

        self.ax.plot(self.P2[0], self.P2[1], 'bs', markersize=12, markeredgewidth=2, zorder=5, alpha=0.5)
        self.ax.plot([self.P2[0], self.P2[0]], [self.P2[1] - 2, self.P2[1] + 2],
                     'r-', linewidth=2, alpha=0.7, zorder=4)
        self.ax.text(self.P2[0] - 2, self.P2[1], 'P2', fontsize=12, fontweight='bold', zorder=6)

        if self.P1:
            self.ax.plot(self.P1[0], self.P1[1], 'ro', markersize=10, zorder=5, alpha=0.5)
            self.ax.text(self.P1[0] + 0.5, self.P1[1] + 0.5, 'P1', color='red', fontsize=11, fontweight='bold')
        
        if self.P3:
            self.ax.plot(self.P3[0], self.P3[1], 'ro', markersize=10, zorder=5, alpha=0.5)
            self.ax.text(self.P3[0] + 0.5, self.P3[1] + 0.5, 'P3', color='red', fontsize=11, fontweight='bold',
                         zorder=6)

    def draw_valid_zones(self):
        """Рисует полупрозрачные зоны, где разрешено ставить P1 и P3"""
        for patch in self.ax.patches:
            if hasattr(patch, 'get_label') and patch.get_label() == 'valid_zone':
                patch.remove()

        rect1 = plt.Rectangle((-X_LINE, self.P2[1]), X_LINE, Y_LINE - self.P2[1],
                              facecolor='yellow', alpha=0.15, edgecolor='orange', linestyle='--', label='valid_zone',
                              zorder=1)
        self.ax.add_patch(rect1)
        self.ax.text(-X_LINE / 2, (self.P2[1] + Y_LINE) / 2, 'Зона для P1', ha='center', color='orange', alpha=0.6,
                     zorder=2)

        rect2 = plt.Rectangle((-X_LINE, -Y_LINE), X_LINE, self.P2[1] - (-Y_LINE),
                              facecolor='cyan', alpha=0.15, edgecolor='blue', linestyle='--', label='valid_zone',
                              zorder=1)
        self.ax.add_patch(rect2)
        self.ax.text(-X_LINE / 2, (-Y_LINE + self.P2[1]) / 2, 'Зона для P3', ha='center', color='blue', alpha=0.6,
                     zorder=2)

    def is_valid_click(self, x, y, target):
        """Проверяет, находится ли клик в допустимой прямоугольной области"""
        if x is None or y is None:
            return False
        if not (-X_LINE <= x <= 0 and -Y_LINE <= y <= Y_LINE):
            return False
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
        pts = np.array([
            p_tangent1,
            p_tangent2,
            point_on_conic,
            mirrored2,
            self.P2  
        ])

        x = pts[:, 0]
        y = pts[:, 1]

        M = np.column_stack([
            x * x,
            x * y,
            y * y,
            x,
            y,
            np.ones_like(x)
        ])

        _, _, Vt = np.linalg.svd(M)
        coeff = Vt[-1]
        norm = np.linalg.norm(coeff)
        if norm > 1e-12:
            coeff /= norm

        return coeff

    def classify_conic(self, coeff):
        """Классификация конического сечения"""
        A, B, C, D, E, F = coeff

        norm = max(abs(A), abs(B), abs(C), abs(D), abs(E), abs(F))
        if norm < 1e-12:
            return "Вырожденная"

        A /= norm
        B /= norm
        C /= norm

        delta = B ** 2 - 4 * A * C

        if abs(delta) < 1e-10:
            return "Парабола"
        elif delta < 0:
            return "Эллипс"
        else:
            return "Гипербола"

    def evaluate_conic(self, coeff, x, y):
        if coeff is None:
            return 0
        A, B, C, D, E, F = coeff
        return A * x * x + B * x * y + C * y * y + D * x + E * y + F

    def get_derivatives(self, coeff, x, y):
        A, B, C, D, E, F = coeff
        dx = 2 * A * x + B * y + D
        dy = B * x + 2 * C * y + E
        return dx, dy

    def check_continuity(self, coeff1, coeff2, point):
        """Проверка непрерывности в точке стыка"""
        x0, y0 = point

        if coeff1 is None or coeff2 is None:
            return None

        val1 = self.evaluate_conic(coeff1, x0, y0)
        val2 = self.evaluate_conic(coeff2, x0, y0)
        c0_continuous = abs(val1 - val2) < 1e-6
        
        result = {
            'point': point,
            'c0_continuous': c0,
            'discontinuity_type': None,
            'left_value': val1,
            'right_value': val2,
            'jump': abs(val1 - val2)
        }

        if not c0:
            result['discontinuity_type'] = 'Разрыв C0 (скачок функции)'
            return result
        
        dx1, dy1 = self.get_derivatives(coeff1, x0, y0)
        dx2, dy2 = self.get_derivatives(coeff2, x0, y0)
        
        tangent1 = np.array([-dy1, dx1])
        tangent2 = np.array([-dy2, dx2])
        
        norm1 = np.linalg.norm(tangent1)
        norm2 = np.linalg.norm(tangent2)

        if norm1 > 1e-6 and norm2 > 1e-6:
            tangent1 = tangent1 / norm1
            tangent2 = tangent2 / norm2
            
            dot_product = np.clip(np.dot(tangent1, tangent2), -1, 1)
            angle = np.arccos(dot_product) * 180 / np.pi

            # G1: касательные коллинеарны (0° или 180°)
            is_collinear = abs(abs(dot_product) - 1.0) < 1e-3

            result['c1_continuous'] = is_collinear
            result['angle'] = angle
            result['tangent1'] = tangent1
            result['tangent2'] = tangent2

            if is_collinear:
                result['discontinuity_type'] = 'Гладкое соединение (G1)'
            else:
                result['discontinuity_type'] = f'Разрыв C1 (излом, угол {angle:.2f}°)'
        else:
            result['c1_continuous'] = False
            result['discontinuity_type'] = 'Неопределенная касательная'
            result['angle'] = None

        return result

    def draw_conic(self, coeff, ax, color='blue', linestyle='-', transparency=0.5):
        if coeff is None:
            return

        A, B, C, D, E, F = coeff

        x = np.linspace(self.x_min, self.x_max, 400)
        y = np.linspace(self.y_min, self.y_max, 400)
        X, Y = np.meshgrid(x, y)

        Z = A * X ** 2 + B * X * Y + C * Y ** 2 + D * X + E * Y + F

        ax.contour(X, Y, Z, levels=[0], colors=color, linestyles=linestyle, linewidths=1.5, alpha=transparency)

    def draw_composite_black(self):
        """Рисует чёрный контур составного сечения (P0-P2 и P2-P4) с симметрией"""
        if self.coeff1 is None or self.coeff2 is None:
            return

        def get_branch(coeff, x_range, branch='upper'):
            A, B, C, D, E, F = coeff
            xs = np.linspace(x_range[0], x_range[1], 400)
            ys = []
            for x in xs:
                a_q, b_q, c_q = C, B * x + E, A * x ** 2 + D * x + F
                if abs(a_q) < 1e-9:
                    ys.append(-c_q / b_q if abs(b_q) > 1e-9 else 0)
                else:
                    delta = b_q ** 2 - 4 * a_q * c_q
                    if delta >= 0:
                        sqrt_d = np.sqrt(delta)
                        y1 = (-b_q + sqrt_d) / (2 * a_q)
                        y2 = (-b_q - sqrt_d) / (2 * a_q)
                        ys.append(max(y1, y2) if branch == 'upper' else min(y1, y2))
                    else:
                        ys.append(np.nan)
            return xs, np.array(ys)

        # Верхняя дуга (P0 -> P2)
        xs_up, ys_up = get_branch(self.coeff1, [-X_LINE, 0], 'upper')
        self.ax.plot(xs_up, ys_up, 'k-', linewidth=2.5, zorder=3)
        self.ax.plot(-xs_up, ys_up, 'k-', linewidth=2.5, zorder=3)  # Симметрия

        # Нижняя дуга (P2 -> P4)
        xs_low, ys_low = get_branch(self.coeff2, [-X_LINE, 0], 'lower')
        self.ax.plot(xs_low, ys_low, 'k-', linewidth=2.5, zorder=3)
        self.ax.plot(-xs_low, ys_low, 'k-', linewidth=2.5, zorder=3)  # Симметрия

    def calculate_and_draw(self):
        if self.P1 is None or self.P3 is None:
            return
        
        # Очищаем старые кривые
        for coll in self.ax.collections[:]:
            if hasattr(coll, 'get_color') and coll.get_color() in ['blue', 'green']:
                coll.remove()
        
        self.redraw_base()

        self.coeff1 = self.fit_conic_liming(self.P0, self.P2, self.P1, True, False)
        self.draw_conic(self.coeff1, self.ax, 'blue', '--', 0.3)

        self.coeff2 = self.fit_conic_liming(self.P2, self.P4, self.P3, False, True)
        self.draw_conic(self.coeff2, self.ax, 'green', '--', 0.3)

        self.draw_composite_black()  # <-- ДОБАВЛЕНО: чёрное сечение поверх

        self.visualize_continuity()
        self.analyze_conics(self.coeff1, self.coeff2)
        self.fig.canvas.draw_idle()

    def visualize_continuity(self):
        if self.coeff1 is None or self.coeff2 is None:
            return

        continuity = self.check_continuity(self.coeff1, self.coeff2, self.P2)

        if continuity:
            if not continuity['c0_continuous']:
                # Разрыв C0 - красный крест
                self.ax.plot(self.P2[0], self.P2[1], 'rx', markersize=15, markeredgewidth=3, 
                           label='Разрыв C0', zorder=7)
            elif not continuity.get('c1_continuous', False):
                # Разрыв C1 (излом) - красный ромб
                self.ax.plot(self.P2[0], self.P2[1], 'rd', markersize=12, markeredgewidth=2,
                           label='Излом (C1 разрыв)', zorder=7)
            else:
                # Гладкое соединение - зеленый круг
                self.ax.plot(self.P2[0], self.P2[1], 'go', markersize=12, markeredgewidth=2, zorder=7)
    
    def analyze_conics(self, coeff1, coeff2):
        type1 = self.classify_conic(coeff1)
        type2 = self.classify_conic(coeff2)

        continuity = self.check_continuity(coeff1, coeff2, self.P2)

        self.update_info_panel(type1, type2, coeff1, coeff2, continuity)

    def update_info_panel(self, type1=None, type2=None, coeff1=None, coeff2=None, continuity=None):
        """Обновление информационной панели"""
        self.ax_info.clear()
        self.ax_info.axis('off')
        
        text = "СИММЕТРИЧНОЕ СОСТАВНОЕ КОНИЧЕСКОЕ СЕЧЕНИЕ\n"

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
                
                if continuity['c0_continuous']:
                    text += "C0 - НЕПРЕРЫВНОСТЬ ВЫПОЛНЕНА\n"
                    text += f"  F1({x0:.2f},{y0:.2f}) = {continuity['left_value']:.6e}\n"
                    text += f"  F2({x0:.2f},{y0:.2f}) = {continuity['right_value']:.6e}\n\n"
                else:
                    text += "C0 - НЕПРЕРЫВНОСТЬ НАРУШЕНА\n"
                    text += f"  Левое значение: {continuity['left_value']:.6f}\n"
                    text += f"  Правое значение: {continuity['right_value']:.6f}\n"
                    text += f"  Величина скачка: {continuity['jump']:.6f}\n\n"
                
                if continuity['c0_continuous']:
                    if 'c1_continuous' in continuity:
                        if continuity['c1_continuous']:
                            text += "C1 - ГЛАДКОЕ СОЕДИНЕНИЕ (G1)\n"
                            text += "  Касательные коллинеарны (совпадает касательная прямая)\n"
                        else:
                            text += "C1 - НЕПРЕРЫВНОСТЬ НАРУШЕНА (излом)\n"
                            if 'angle' in continuity and continuity['angle'] is not None:
                                text += f"  Угол между касательными: {continuity['angle']:.2f}°\n"
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
        if event.inaxes != self.ax or self.dragging:
            return

        if self.is_near_point(event.xdata, event.ydata, self.P2):
            return

        x, y = event.xdata, event.ydata

        if self.stage == 0 and self.P1 is None:
            if not self.is_valid_click(x, y, 'P1'):
                return
            self.P1 = (x, y)
            self.ax.plot(self.P1[0], self.P1[1], 'ro', markersize=10, zorder=5)
            self.ax.text(self.P1[0] + 0.5, self.P1[1] + 0.5, 'P1', color='red', fontsize=11, fontweight='bold',
                         zorder=6)
            self.stage = 1
            self.update_info_panel()
            self.fig.canvas.draw_idle()

        elif self.stage == 1 and self.P3 is None:
            if not self.is_valid_click(x, y, 'P3'):
                return
            self.P3 = (x, y)
            self.ax.plot(self.P3[0], self.P3[1], 'ro', markersize=10, zorder=5)
            self.ax.text(self.P3[0] + 0.5, self.P3[1] + 0.5, 'P3', color='red', fontsize=11, fontweight='bold',
                         zorder=6)
            self.update_info_panel()
            self.fig.canvas.draw_idle()
            self.calculate_and_draw()

    def is_near_point(self, x, y, point, tolerance=1.5):
        if x is None or y is None:
            return False
        return np.sqrt((x - point[0]) ** 2 + (y - point[1]) ** 2) < tolerance

    def on_press(self, event):
        if event.inaxes != self.ax:
            return

        if self.is_near_point(event.xdata, event.ydata, self.P2):
            self.dragging = True
            self.current_drag_point = 'P2'

    def on_motion(self, event):
        if not self.dragging or event.inaxes != self.ax:
            return

        if self.current_drag_point == 'P2':
            new_y = max(-Y_LINE, min(event.ydata, Y_LINE))
            # Не даём P2 пересечь установленные точки
            if self.P1:
                new_y = min(new_y, self.P1[1] - 1.0)
            if self.P3:
                new_y = max(new_y, self.P3[1] + 1.0)

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


if __name__ == "__main__":
    designer = ConicDesigner()