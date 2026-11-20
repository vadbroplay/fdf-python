
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

        self.z_scale = 1.0
        self._draw_pending = False

        self.root.bind("<Escape>", lambda _event: self.root.destroy())
        self.root.bind("<Configure>", self._on_resize)
        self.root.bind_all("<plus>", self._increase_height)
        self.root.bind_all("<equal>", self._increase_height)
        self.root.bind_all("<minus>", self._decrease_height)
        self.root.bind_all("<KP_Add>", self._increase_height)
        self.root.bind_all("<KP_Subtract>", self._decrease_height)

        self.root.after(100, self.draw)

    def run(self) -> None:
        self.root.mainloop()

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


    def _draw_hud(self) -> None:
        color = "#B8C0CC"
        font = ("Segoe UI", 10)

        # Информация о высоте — слева сверху.
        self.canvas.create_text(
            16,
            14,
            anchor="nw",
            text=f"Высота рельефа: {self.z_scale:.1f}×",
            fill=color,
            font=("Segoe UI", 11, "bold"),
        )

        # Подсказки — внизу экрана.
        height = self.canvas.winfo_height()
        bottom = height - 16

        self.canvas.create_text(
            16,
            bottom,
            anchor="sw",
            text="+  Увеличить высоту",
            fill=color,
            font=font,
        )

        self.canvas.create_text(
            165,
            bottom,
            anchor="sw",
            text="−  Уменьшить высоту",
            fill=color,
            font=font,
        )

        self.canvas.create_text(
            320,
            bottom,
            anchor="sw",
            text="Esc  Закрыть приложение",
            fill=color,
            font=font,
        )


    def draw(self) -> None:
        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        base_camera = Camera.fit(self.height_map, width, height)
        camera = Camera(
            scale=base_camera.scale,
            offset_x=base_camera.offset_x,
            offset_y=base_camera.offset_y,
            z_scale=self.z_scale,
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

        self._draw_hud()

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
