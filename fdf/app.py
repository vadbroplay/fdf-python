
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

        self.rotation = 0.0
        self.top_view = False
        self.z_scale = 1.0

        self.canvas = tk.Canvas(
            self.root,
            background="#20242B",
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        heights = [point.z for point in self.height_map]
        self.min_z = min(heights)
        self.max_z = max(heights)

        self._draw_pending = False

        self.root.bind("<Escape>", lambda _event: self.root.destroy())
        self.root.bind("<Configure>", self._on_resize)
        self.root.bind("<KeyPress>", self._on_key_press)

        self.root.bind_all("<plus>", self._increase_height)
        self.root.bind_all("<equal>", self._increase_height)
        self.root.bind_all("<minus>", self._decrease_height)
        self.root.bind_all("<KP_Add>", self._increase_height)
        self.root.bind_all("<KP_Subtract>", self._decrease_height)

        self.root.after(100, self.draw)

    def _on_key_press(self, event: tk.Event[tk.Misc]) -> None:
        if event.keycode == 65:
            self.rotation -= 10.0
        elif event.keycode == 68:
            self.rotation += 10.0
        elif event.keycode == 86:
            self._toggle_view(event)
        else:
            return

        self.draw()

    def run(self) -> None:
        self.root.mainloop()

    def _toggle_view(self, _event: tk.Event[tk.Misc]) -> None:
        self.top_view = not self.top_view
        self.draw()

    def _increase_height(self, _event: tk.Event[tk.Misc]) -> str:
        self.z_scale = min(round(self.z_scale + 0.1, 1), 5.0)
        self.draw()
        return "break"

    def _decrease_height(self, _event: tk.Event[tk.Misc]) -> str:
        self.z_scale = max(round(self.z_scale - 0.1, 1), 0.0)
        self.draw()
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

    def _draw_hud(self) -> None:
        self.canvas.create_text(
            15,
            self.canvas.winfo_height() - 12,
            anchor="sw",
            text=(
                "A/D — поворот | V — вид сверху\n"
                "+/- — масштаб высоты | Esc — выход"
            ),
            fill="#B8C0CC",
            font=("Segoe UI", 10),
        )

    def draw(self) -> None:
        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        camera = Camera.fit(
            self.height_map,
            width,
            height,
            rotation=self.rotation,
            top_view=self.top_view,
            z_scale=self.z_scale,
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
