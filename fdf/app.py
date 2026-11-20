
import tkinter as tk

from fdf.model import Map, Point
from fdf.projection import Camera


class FdfApp:
    def __init__(self, height_map: Map) -> None:
        self.height_map = height_map
        self.root = tk.Tk()
        self.root.title("FdF — карта высот")
        self.root.geometry("1000x700")
        self.root.minsize(500, 400)

        self.top_view = False

        self.canvas = tk.Canvas(
            self.root,
            background="#20242B",
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0

        self._drag_start_x = 0
        self._drag_start_y = 0
        self._draw_pending = False

        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", self._on_mouse_wheel)
        self.canvas.bind("<Button-5>", self._on_mouse_wheel)
        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)

        self.root.bind("<Escape>", lambda _event: self.root.destroy())
        self.root.bind("<Configure>", self._on_resize)
        self.root.bind("<KeyPress>", self._on_key_press)

        self.root.bind_all("<Left>", self._on_left)
        self.root.bind_all("<Right>", self._on_right)
        self.root.bind_all("<Up>", self._on_up)
        self.root.bind_all("<Down>", self._on_down)

        self.root.after(100, self.draw)

    def _on_key_press(self, event: tk.Event[tk.Misc]) -> None:
        if event.keycode == 86:
            self._toggle_view(event)
    def run(self) -> None:
        self.root.mainloop()

    def _on_mouse_wheel(self, event: tk.Event[tk.Misc]) -> str:
        if getattr(event, "num", None) == 4:
            factor = 1.1
        elif getattr(event, "num", None) == 5:
            factor = 1 / 1.1
        else:
            factor = 1.1 if event.delta > 0 else 1 / 1.1

        self._set_zoom(
            self.zoom * factor,
            event.x,
            event.y,
        )
        return "break"

    def _set_zoom(
        self,
        value: float,
        cursor_x: float | None = None,
        cursor_y: float | None = None,
    ) -> None:
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

        self.pan_x = (
            self.pan_x + center_x - cursor_x
        ) * factor - center_x + cursor_x

        self.pan_y = (
            self.pan_y + center_y - cursor_y
        ) * factor - center_y + cursor_y

        self.zoom = new_zoom
        self.draw()

    def _on_drag_start(self, event: tk.Event[tk.Misc]) -> None:
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _on_drag_motion(self, event: tk.Event[tk.Misc]) -> None:
        self.pan_x += event.x - self._drag_start_x
        self.pan_y += event.y - self._drag_start_y

        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self.draw()

    def _move(self, dx: float, dy: float) -> None:
        self.pan_x += dx
        self.pan_y += dy
        self.draw()

    def _on_left(self, _event: tk.Event[tk.Misc]) -> str:
        self._move(-20, 0)
        return "break"

    def _on_right(self, _event: tk.Event[tk.Misc]) -> str:
        self._move(20, 0)
        return "break"

    def _on_up(self, _event: tk.Event[tk.Misc]) -> str:
        self._move(0, -20)
        return "break"

    def _on_down(self, _event: tk.Event[tk.Misc]) -> str:
        self._move(0, 20)
        return "break"

    def _on_resize(self, event: tk.Event[tk.Misc]) -> None:
        if event.widget is self.root and not self._draw_pending:
            self._draw_pending = True
            self.root.after_idle(self._redraw_after_resize)

    def _redraw_after_resize(self) -> None:
        self._draw_pending = False
        self.draw()

    def _point_color(self, point: Point) -> str:
        if point.color is not None:
            return point.color

        if self.max_z == self.min_z:
            ratio = 0.5
        else:
            ratio = (point.z - self.min_z) / (self.max_z - self.min_z)

        if ratio < 0.5:
            part = ratio * 2
            red = 0
            green = round(180 * part)
            blue = round(255 * (1 - part))
        else:
            part = (ratio - 0.5) * 2
            red = round(255 * part)
            green = round(180 * (1 - part))
            blue = 0

        return f"#{red:02x}{green:02x}{blue:02x}"

    def draw(self) -> None:
        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        base_camera = Camera.fit(self.height_map, width, height)

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
        )

        for point in self.height_map:
            start = camera.project(point)

            if point.x + 1 < self.height_map.width:
                right = self.height_map.rows[point.y][point.x + 1]
                end = camera.project(right)
                self._draw_edge(
                    start.x,
                    start.y,
                    end.x,
                    end.y,
                    self._point_color(point),
                    self._point_color(right),
                )

            if point.y + 1 < self.height_map.height:
                down = self.height_map.rows[point.y + 1][point.x]
                end = camera.project(down)
                self._draw_edge(
                    start.x,
                    start.y,
                    end.x,
                    end.y,
                    self._point_color(point),
                    self._point_color(down),
                )

            color = self._point_color(point)

            self.canvas.create_oval(
                start.x - 3,
                start.y - 3,
                start.x + 3,
                start.y + 3,
                fill=color,
                outline="",
            )
        self._draw_hud()


    def _draw_hud(self) -> None:
        self.canvas.create_text(
            16,
            self.canvas.winfo_height() - 16,
            anchor="sw",
            text=(
                "Колесо мыши - Масштабирование | Стрелки: Сдвиг | "
                "ЛКМ + перетаскивание: Перемещение | Esc - Выход"
            ),
            fill="#B8C0CC",
            font=("Segoe UI", 11),
        )

        self._draw_hud()

    def _draw_hud(self) -> None:
        self.canvas.create_text(
            15,
            self.canvas.winfo_height() - 27,
            anchor=tk.NW,
            text="V: сменить вид",
            fill="#B8C0CC",
            font=("Segoe UI", 11),
        )

    def _draw_edge(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color1: str,
        color2: str,
    ) -> None:
        steps = 16

        rgb1 = tuple(
            int(color1[index:index + 2], 16)
            for index in (1, 3, 5)
        )
        rgb2 = tuple(
            int(color2[index:index + 2], 16)
            for index in (1, 3, 5)
        )

        for step in range(steps):
            t1 = step / steps
            t2 = (step + 1) / steps

            color = "#" + "".join(
                f"{round(c1 + (c2 - c1) * t1):02x}"
                for c1, c2 in zip(rgb1, rgb2, strict=True)
            )

            self.canvas.create_line(
                x1 + (x2 - x1) * t1,
                y1 + (y2 - y1) * t1,
                x1 + (x2 - x1) * t2,
                y1 + (y2 - y1) * t2,
                fill=color,
                width=2,
            )
