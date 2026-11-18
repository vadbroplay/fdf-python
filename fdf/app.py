
import tkinter as tk

from fdf.model import Map
from fdf.projection import Camera


class FdfApp:
    """Графическое приложение для просмотра карты высот."""

    def __init__(self, height_map: Map) -> None:
        self.height_map = height_map
        self.root = tk.Tk()
        self.root.title("FdF — карта высот")
        self.root.geometry("1000x700")
        self.root.minsize(500, 400)

        self.canvas = tk.Canvas(
            self.root,
            background="#20242B",
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.z_scale = 1.0
        self.angle_degrees = 0.0
        self.top_view = False

        self._drag_start_x = 0
        self._drag_start_y = 0
        self._draw_pending = False

        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)

        self.root.bind("<Escape>", lambda _event: self.root.destroy())
        self.root.bind("<Configure>", self._on_resize)

        self.root.bind_all("<Left>", self._on_left)
        self.root.bind_all("<Right>", self._on_right)
        self.root.bind_all("<Up>", self._on_up)
        self.root.bind_all("<Down>", self._on_down)
        self.root.bind_all("<plus>", self._on_height_up)
        self.root.bind_all("<minus>", self._on_height_down)
        self.root.bind_all("<KP_Add>", self._on_height_up)
        self.root.bind_all("<KP_Subtract>", self._on_height_down)
        self.root.bind_all("<KeyPress>", self._on_letter_key)

        self.root.after(100, self.draw)

    def run(self) -> None:
        """Запускает главный цикл приложения."""
        self.root.mainloop()


    def _on_mouse_wheel(self, event: tk.Event[tk.Misc]) -> None:
        """Масштабирует карту относительно положения курсора."""
        if event.delta > 0:
            factor = 1.1
        else:
            factor = 1 / 1.1

        self._set_zoom(
            self.zoom * factor,
            event.x,
            event.y,
        )

    def _set_zoom(
            self,
            value: float,
            cursor_x: float | None = None,
            cursor_y: float | None = None,
    ) -> None:
        """Меняет масштаб относительно положения курсора."""
        new_zoom = max(0.1, min(value, 10.0))

        if new_zoom == self.zoom:
            return

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        center_x = width / 2
        center_y = height / 2

        if cursor_x is None:
            cursor_x = center_x
        if cursor_y is None:
            cursor_y = center_y

        factor = new_zoom / self.zoom

        # Компенсируем смещение, чтобы выбранная точка оставалась на месте.
        self.pan_x = (
                             self.pan_x + center_x - cursor_x
                     ) * factor - center_x + cursor_x

        self.pan_y = (
                             self.pan_y + center_y - cursor_y
                     ) * factor - center_y + cursor_y

        self.zoom = new_zoom
        self.draw()

    def _on_drag_start(self, event: tk.Event[tk.Misc]) -> None:
        """Запоминает начальную позицию перетаскивания."""
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _on_drag_motion(self, event: tk.Event[tk.Misc]) -> None:
        """Перемещает карту вслед за мышью."""
        self.pan_x += event.x - self._drag_start_x
        self.pan_y += event.y - self._drag_start_y

        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self.draw()

    def _move(self, dx: float, dy: float) -> None:
        """Сдвигает карту на заданное количество пикселей."""
        self.pan_x += dx
        self.pan_y += dy
        self.draw()

    def _on_left(self, _event: tk.Event[tk.Misc]) -> None:
        self._move(-20, 0)

    def _on_right(self, _event: tk.Event[tk.Misc]) -> None:
        self._move(20, 0)

    def _on_up(self, _event: tk.Event[tk.Misc]) -> None:
        self._move(0, -20)

    def _on_down(self, _event: tk.Event[tk.Misc]) -> None:
        self._move(0, 20)

    def _on_height_up(self, _event: tk.Event[tk.Misc]) -> None:
        """Увеличивает вертикальный масштаб рельефа."""
        self.z_scale = min(self.z_scale + 0.2, 10.0)
        self.draw()

    def _on_height_down(self, _event: tk.Event[tk.Misc]) -> None:
        """Уменьшает вертикальный масштаб рельефа."""
        self.z_scale = max(self.z_scale - 0.2, 0.0)
        self.draw()

    def _on_toggle_view(self, _event: tk.Event[tk.Misc]) -> None:
        """Переключает изометрию и вид сверху."""
        self.top_view = not self.top_view
        self.draw()

    def _on_rotate_left(self, _event: tk.Event[tk.Misc]) -> None:
        """Поворачивает карту против часовой стрелки."""
        self.angle_degrees = (self.angle_degrees - 10) % 360
        self.draw()

    def _on_rotate_right(self, _event: tk.Event[tk.Misc]) -> None:
        """Поворачивает карту по часовой стрелке."""
        self.angle_degrees = (self.angle_degrees + 10) % 360
        self.draw()

    def _on_letter_key(self, event: tk.Event[tk.Misc]) -> None:
        """Обрабатывает клавиши независимо от раскладки Windows."""
        if event.keycode == 65:  # A
            self._on_rotate_left(event)
        elif event.keycode == 68:  # D
            self._on_rotate_right(event)
        elif event.keycode == 86:  # V
            self._on_toggle_view(event)

    def _on_resize(self, event: tk.Event[tk.Misc]) -> None:
        """Перерисовывает карту при изменении размера окна."""
        if event.widget is self.root and not self._draw_pending:
            self._draw_pending = True
            self.root.after_idle(self._redraw_after_resize)

    def _redraw_after_resize(self) -> None:
        """Выполняет отложенную перерисовку."""
        self._draw_pending = False
        self.draw()

    def _color_for_height(self, z: float) -> str:
        """Возвращает цвет точки в зависимости от высоты."""
        heights = [point.z for point in self.height_map]
        min_z = min(heights)
        max_z = max(heights)

        if min_z == max_z:
            return "#00BFFF"

        ratio = (z - min_z) / (max_z - min_z)

        if ratio < 0.25:
            return "#0066FF"
        if ratio < 0.5:
            return "#00CC66"
        if ratio < 0.75:
            return "#FFFF00"
        return "#FF3333"

    def draw(self) -> None:
        """Рисует каркас карты высот."""
        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        base_camera = Camera.fit(
            self.height_map,
            width,
            height,
            z_scale=self.z_scale,
            angle_degrees=self.angle_degrees,
            top_view=self.top_view,
        )

        center_x = width / 2
        center_y = height / 2

        camera = Camera(
            scale=base_camera.scale * self.zoom,
            offset_x=(
                center_x
                + (base_camera.offset_x - center_x) * self.zoom
                + self.pan_x
            ),
            offset_y=(
                center_y
                + (base_camera.offset_y - center_y) * self.zoom
                + self.pan_y
            ),
            z_scale=self.z_scale,
            angle_degrees=self.angle_degrees,
            top_view=self.top_view,
        )

        for point in self.height_map:
            start = camera.project(point)
            point_color = point.color or self._color_for_height(point.z)

            self.canvas.create_oval(
                start.x - 3,
                start.y - 3,
                start.x + 3,
                start.y + 3,
                fill=point_color,
                outline="",
            )

            if point.x + 1 < self.height_map.width:
                right = self.height_map.rows[point.y][point.x + 1]
                end = camera.project(right)
                edge_color = (
                    point.color
                    or right.color
                    or self._color_for_height((point.z + right.z) / 2)
                )
                self._draw_edge(
                    start.x, start.y, end.x, end.y, edge_color
                )

            if point.y + 1 < self.height_map.height:
                down = self.height_map.rows[point.y + 1][point.x]
                end = camera.project(down)
                edge_color = (
                    point.color
                    or down.color
                    or self._color_for_height((point.z + down.z) / 2)
                )
                self._draw_edge(
                    start.x, start.y, end.x, end.y, edge_color
                )

    def _draw_edge(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: str | None,
    ) -> None:
        """Рисует одно ребро каркасной модели."""
        self.canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            fill=color or "#E8EDF2",
            width=2,
        )
