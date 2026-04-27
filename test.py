import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

X_LINE = 10
Y_LINE = 15
RECTANGLE_LIMIT = 20

class ConicDesigner:
    def __init__(self):
        # Прямоугольная область
        self.x_min, self.x_max = -RECTANGLE_LIMIT, RECTANGLE_LIMIT
        self.y_min, self.y_max = -RECTANGLE_LIMIT, RECTANGLE_LIMIT
        
        # Фиксированные точки с касательными параллельными осям
        self.P0 = (0, Y_LINE)
        self.P4 = (0, -Y_LINE)  
        
        # Перетаскиваемая точка на левой вертикальной стороне
        self.P2 = (-X_LINE, 0)
        
        self.P1 = None   # Точка коники для сегмента P0-P2
        self.P3 = None   # Точка коники для сегмента P2-P4
        self.dragging = False
        self.stage = 0  # 0: ожидание P1, 1: ожидание P3
        
        self.setup_plot()
        
        # Подключение событий
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        plt.show()
    
    def setup_plot(self):
        """Настройка графического интерфейса"""
        self.fig = plt.figure(figsize=(15, 8))
        gs = self.fig.add_gridspec(1, 2, width_ratios=[2.5, 1])
        
        self.ax = self.fig.add_subplot(gs[0])
        self.ax_info = self.fig.add_subplot(gs[1])
        
        # Настройка области рисования
        self.ax.set_xlim(self.x_min, self.x_max)
        self.ax.set_ylim(self.y_min, self.y_max)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_aspect('equal')
        self.ax.set_title("Составное коническое сечение\nКасательные: P0 и P4 - горизонтальные, P2 - вертикальная")
        
        # оси координат
        self.ax.axhline(y=0, color='black', linewidth=0.5, alpha=0.5)
        self.ax.axvline(x=0, color='black', linewidth=0.5, alpha=0.5)
        
        # направляющие для касательных
        self.ax.axhline(y=Y_LINE, color='red', linestyle='--', alpha=0.3, linewidth=1)
        self.ax.axhline(y=-Y_LINE, color='red', linestyle='--', alpha=0.3, linewidth=1)
        self.ax.axvline(x=-X_LINE, color='red', linestyle='--', alpha=0.3, linewidth=1)
        
        # фиксированные точки
        self.draw_fixed_points()
        
        # Информационная панель
        self.ax_info.axis('off')
        self.ax_info.set_xlim(0, 1)
        self.ax_info.set_ylim(0, 1)
        
        # Кнопка очистки
        ax_btn_clear = plt.axes([0.4, 0.02, 0.2, 0.05])
        self.btn_clear = Button(ax_btn_clear, 'ОЧИСТИТЬ')
        self.btn_clear.on_clicked(self.clear_plot)
        
        self.update_info_panel()
    
    def draw_fixed_points(self):
        """Рисование фиксированных и перетаскиваемых точек"""
        # P0 с горизонтальной касательной
        self.ax.plot(self.P0[0], self.P0[1], 'gs', markersize=12, markeredgewidth=2)
        self.ax.plot([self.P0[0]-2, self.P0[0]+2], [self.P0[1], self.P0[1]], 
                    'r-', linewidth=2, alpha=0.7)
        self.ax.text(self.P0[0] + 0.5, self.P0[1] + 0.5, 'P0', fontsize=12, fontweight='bold')
        
        # P4 с горизонтальной касательной
        self.ax.plot(self.P4[0], self.P4[1], 'gs', markersize=12, markeredgewidth=2)
        self.ax.plot([self.P4[0]-2, self.P4[0]+2], [self.P4[1], self.P4[1]], 
                    'r-', linewidth=2, alpha=0.7)
        self.ax.text(self.P4[0] + 0.5, self.P4[1] - 1, 'P4', fontsize=12, fontweight='bold')
        
        # P2 с вертикальной касательной (перетаскиваемая)
        self.P2_marker = self.ax.plot(self.P2[0], self.P2[1], 'bs', markersize=12, markeredgewidth=2)[0]
        self.ax.plot([self.P2[0], self.P2[0]], [self.P2[1]-2, self.P2[1]+2], 
                    'r-', linewidth=2, alpha=0.7)
        self.ax.text(self.P2[0] - 2, self.P2[1], 'P2', fontsize=12, fontweight='bold', color='blue')
        
        # Точки пользователя
        if self.P1:
            self.ax.plot(self.P1[0], self.P1[1], 'ro', markersize=10)
            self.ax.text(self.P1[0] + 0.5, self.P1[1] + 0.5, 'P1', color='red', fontsize=11, fontweight='bold')
        
        if self.P3:
            self.ax.plot(self.P3[0], self.P3[1], 'mo', markersize=10)
            self.ax.text(self.P3[0] + 0.5, self.P3[1] + 0.5, 'P3', color='magenta', fontsize=11, fontweight='bold')
    
    def reflect_point_across_line(self, point, line_point, is_horizontal=True):
        """
        Отражение точки относительно прямой
        line_point - точка на прямой
        is_horizontal: True - горизонтальная прямая, False - вертикальная
        """
        x, y = point
        
        if is_horizontal:
            # Отражение относительно горизонтальной прямой y = line_point[1]
            return (x, 2 * line_point[1] - y)
        else:
            # Отражение относительно вертикальной прямой x = line_point[0]
            return (2 * line_point[0] - x, y)
    
    def determinant_4x4(self, matrix):
        """Вычисление определителя матрицы 4x4"""
        return np.linalg.det(matrix)
    
    def fit_conic_liming(self, p_tangent1, p_tangent2, point_on_conic, 
                        tangent1_horizontal=True, tangent2_vertical=True):
        """
        Построение конического сечения МЕТОДОМ ЛАЙМИНГА
        Используется зеркальное отражение и решение через определитель
        
        p_tangent1 - точка на первой касательной
        p_tangent2 - точка на второй касательной
        point_on_conic - точка на конике
        """
        # Шаг 1: Отражаем точку относительно первой касательной
        mirrored1 = self.reflect_point_across_line(point_on_conic, p_tangent1, tangent1_horizontal)
        
        # Шаг 2: Отражаем полученную точку относительно второй касательной
        mirrored2 = self.reflect_point_across_line(mirrored1, p_tangent2, not tangent2_vertical)
        
        # Шаг 3: Получаем 4 точки для построения коники
        # Точки: P_tangent1, P_tangent2, point_on_conic, mirrored2
        x1, y1 = p_tangent1
        x2, y2 = p_tangent2
        x3, y3 = point_on_conic
        x4, y4 = mirrored2
        
        # Шаг 4: Метод Лайминга - решение через определители
        # Уравнение коники: | x^2  xy  y^2  x  y  1 |
        #                   | x1^2 x1y1 y1^2 x1 y1 1 |
        #                   | x2^2 x2y2 y2^2 x2 y2 1 | = 0
        #                   | x3^2 x3y3 y3^2 x3 y3 1 |
        #                   | x4^2 x4y4 y4^2 x4 y4 1 |
        
        # Вычисляем коэффициенты через дополнительные определители
        # Формируем матрицу 5x5 для каждого коэффициента
        
        def conic_coefficient(x, y, idx):
            """Вычисление коэффициента через определитель"""
            # Матрица 5x5, где заменяем соответствующий столбец
            M = np.array([
                [x1*x1, x1*y1, y1*y1, x1, y1, 1],
                [x2*x2, x2*y2, y2*y2, x2, y2, 1],
                [x3*x3, x3*y3, y3*y3, x3, y3, 1],
                [x4*x4, x4*y4, y4*y4, x4, y4, 1],
                [x*x,   x*y,   y*y,   x,   y,   1]
            ])
            
            # Удаляем столбец idx и вычисляем определитель
            M_reduced = np.delete(M, idx, axis=1)
            return ((-1) ** idx) * np.linalg.det(M_reduced)
        
        # Вычисляем коэффициенты A, B, C, D, E, F
        A = conic_coefficient(0, 0, 0)
        B = conic_coefficient(0, 0, 1)
        C = conic_coefficient(0, 0, 2)
        D = conic_coefficient(0, 0, 3)
        E = conic_coefficient(0, 0, 4)
        F = conic_coefficient(0, 0, 5)
        
        coeff = np.array([A, B, C, D, E, F])
        
        # Нормализация
        norm = np.linalg.norm(coeff)
        if norm > 1e-10:
            coeff = coeff / norm
        
        return coeff
    
    def classify_conic(self, coeff):
        """Классификация типа конического сечения"""
        A, B, C, _, _, _ = coeff
        delta = B ** 2 - 4 * A * C
        
        if abs(delta) < 1e-4:
            return "Парабола"
        elif delta < 0:
            return "Эллипс"
        else:
            return "Гипербола"
    
    def draw_conic(self, coeff, ax, color='blue'):
        """Отрисовка конического сечения"""
        if coeff is None:
            return
        
        A, B, C, D, E, F = coeff
        
        x = np.linspace(self.x_min, self.x_max, 400)
        y = np.linspace(self.y_min, self.y_max, 400)
        X, Y = np.meshgrid(x, y)
        
        Z = A * X**2 + B * X * Y + C * Y**2 + D * X + E * Y + F
        
        # Удаляем старые контуры
        for coll in ax.collections[:]:
            if hasattr(coll, 'get_color') and coll.get_color() in [color, 'green']:
                coll.remove()
        
        ax.contour(X, Y, Z, levels=[0], colors=color, linewidths=2.5, alpha=0.8)
    
    def calculate_and_draw(self):
        """Расчет и отрисовка обоих конических сечений методом Лайминга"""
        if self.P1 is None or self.P3 is None:
            return
        
        # Очищаем старые кривые
        for coll in self.ax.collections[:]:
            if hasattr(coll, 'get_color') and coll.get_color() in ['blue', 'green']:
                coll.remove()
        
        # Перерисовываем базовые элементы
        self.redraw_base()
        
        # Расчет и отрисовка первого сечения (P0-P2) с точкой P1
        coeff1 = self.fit_conic_liming(self.P0, self.P2, self.P1, True, False)
        self.draw_conic(coeff1, self.ax, 'blue')
        
        # Расчет и отрисовка второго сечения (P2-P4) с точкой P3
        coeff2 = self.fit_conic_liming(self.P2, self.P4, self.P3, False, True)
        self.draw_conic(coeff2, self.ax, 'green')
        

        self.analyze_conics(coeff1, coeff2)
        self.fig.canvas.draw_idle()
    
    def analyze_conics(self, coeff1, coeff2):
        """Анализ обоих конических сечений"""
        type1 = self.classify_conic(coeff1)
        type2 = self.classify_conic(coeff2)
        
        self.update_info_panel(type1, type2, coeff1, coeff2)
    
    def update_info_panel(self, type1=None, type2=None, coeff1=None, coeff2=None):
        """Обновление информационной панели"""
        self.ax_info.clear()
        self.ax_info.axis('off')
        
        text = "СОСТАВНОЕ КОНИЧЕСКОЕ СЕЧЕНИЕ\n"
        text += "=" * 35 + "\n\n"
        
        text += "КАСАТЕЛЬНЫЕ:\n"
        text += f"P0 ({self.P0[0]}, {self.P0[1]}) → горизонтальная\n"
        text += f"P2 ({self.P2[0]:.1f}, {self.P2[1]:.2f}) → вертикальная\n"
        text += f"P4 ({self.P4[0]}, {self.P4[1]}) → горизонтальная\n\n"
        
        if self.P1:
            text += f"ТОЧКИ НА КОНИКЕ:\n"
            text += f"P1: ({self.P1[0]:.2f}, {self.P1[1]:.2f})\n"
        if self.P3:
            text += f"P3: ({self.P3[0]:.2f}, {self.P3[1]:.2f})\n\n"
        
        if type1 and type2:
            text += "─" * 35 + "\n"
            text += "СЕГМЕНТ 1: P0 → P1 → P2\n"
            text += f"Тип: {type1}\n"
            if coeff1 is not None:
                A, B, C, D, E, F = coeff1
                text += f"{A:.3f}x² + {B:.3f}xy + {C:.3f}y²\n"
                text += f"+ {D:.3f}x + {E:.3f}y + {F:.3f} = 0\n"
            text += "\n"
            
            text += "СЕГМЕНТ 2: P2 → P3 → P4\n"
            text += f"Тип: {type2}\n"
            if coeff2 is not None:
                A, B, C, D, E, F = coeff2
                text += f"\n{A:.3f}·x² + {B:.3f}·xy + {C:.3f}·y²\n"
                text += f"+ {D:.3f}·x + {E:.3f}·y + {F:.3f} = 0\n"
        
        self.ax_info.text(0.05, 0.95, text, fontsize=9, family='monospace',
                         va='top', transform=self.ax_info.transAxes,
                         bbox=dict(boxstyle='round', facecolor='lightyellow', 
                                  edgecolor='gray', alpha=0.9))
        
        self.fig.canvas.draw_idle()
    
    def on_click(self, event):
        """Обработка кликов для установки P1 и P3"""
        if event.inaxes != self.ax or self.dragging:
            return
        
        if self.is_near_point(event.xdata, event.ydata, self.P2):
            return
        
        if self.stage == 0 and self.P1 is None:
            self.P1 = (event.xdata, event.ydata)
            self.ax.plot(self.P1[0], self.P1[1], 'ro', markersize=10)
            self.ax.text(self.P1[0] + 0.5, self.P1[1] + 0.5, 'P1', color='red', fontsize=11, fontweight='bold')
            self.stage = 1
            self.update_info_panel()
            self.fig.canvas.draw_idle()
            
        elif self.stage == 1 and self.P3 is None:
            self.P3 = (event.xdata, event.ydata)
            self.ax.plot(self.P3[0], self.P3[1], 'mo', markersize=10)
            self.ax.text(self.P3[0] + 0.5, self.P3[1] + 0.5, 'P3', color='magenta', fontsize=11, fontweight='bold')
            self.update_info_panel()
            self.fig.canvas.draw_idle()
            self.calculate_and_draw()
    
    def is_near_point(self, x, y, point, tolerance=0.7):
        """Проверка, находится ли точка рядом с заданной"""
        if x is None or y is None:
            return False
        return np.sqrt((x - point[0])**2 + (y - point[1])**2) < tolerance
    
    def on_press(self, event):
        """Обработка нажатия для перетаскивания P2"""
        if event.inaxes != self.ax:
            return
        
        if self.is_near_point(event.xdata, event.ydata, self.P2):
            self.dragging = True
            self.current_drag_point = 'P2'
    
    def on_motion(self, event):
        """Обработка движения мыши для перетаскивания"""
        if not self.dragging or event.inaxes != self.ax:
            return
        
        if self.current_drag_point == 'P2':
            new_x = -10
            new_y = max(self.y_min + 1, min(event.ydata, self.y_max - 1))
            self.P2 = (new_x, new_y)
            
            if self.P1 and self.P3:
                self.calculate_and_draw()
            else:
                self.redraw_base()
    
    def on_release(self, event):
        """Обработка отпускания мыши"""
        self.dragging = False
        self.current_drag_point = None
    
    def redraw_base(self):
        """Перерисовка базовых элементов"""
        self.ax.clear()
        self.ax.set_xlim(self.x_min, self.x_max)
        self.ax.set_ylim(self.y_min, self.y_max)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_aspect('equal')
        self.ax.set_title("Составное коническое сечение")
        
        self.ax.axhline(y=0, color='black', linewidth=0.5, alpha=0.5)
        self.ax.axvline(x=0, color='black', linewidth=0.5, alpha=0.5)
        self.ax.axhline(y=Y_LINE, color='red', linestyle='--', alpha=0.3, linewidth=1)
        self.ax.axhline(y=-Y_LINE, color='red', linestyle='--', alpha=0.3, linewidth=1)
        self.ax.axvline(x=-X_LINE, color='red', linestyle='--', alpha=0.3, linewidth=1)
        
        self.draw_fixed_points()
        self.fig.canvas.draw_idle()
    
    def clear_plot(self, event):
        """Очистка пользовательских точек"""
        self.P1 = None
        self.P3 = None
        self.stage = 0
        self.redraw_base()
        self.update_info_panel()

if __name__ == "__main__":
    designer = ConicDesigner()