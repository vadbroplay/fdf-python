
import tkinter as tk

from fdf.model import Map
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

        self.root.bind_all("<Left>", self._on_left)
        self.root.bind_all("<Right>", self._on_right)
        self.root.bind_all("<Up>", self._on_up)
        self.root.bind_all("<Down>", self._on_down)

        self.root.after(100, self.draw)

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
                self._draw_edge(start.x, start.y, end.x, end.y)

            if point.y + 1 < self.height_map.height:
                down = self.height_map.rows[point.y + 1][point.x]
                end = camera.project(down)
                self._draw_edge(start.x, start.y, end.x, end.y)

            self.canvas.create_oval(
                start.x - 3,
                start.y - 3,
                start.x + 3,
                start.y + 3,
                fill="#E8EDF2",
                outline="",
            )

    def _draw_edge(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
    ) -> None:
        self.canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            fill="#E8EDF2",
            width=2,
        )
