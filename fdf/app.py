
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

        self.root.after(100, self.draw)

    def run(self) -> None:
        self.root.mainloop()

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

        camera = Camera.fit(self.height_map, width, height)

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
