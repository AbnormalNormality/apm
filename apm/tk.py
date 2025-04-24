from tkinter import Tk, Frame, Misc, Canvas, Scrollbar, Event, Misc
from typing import Callable, Optional, Any
from sys import platform


class APMMisc(Misc):
    def set_rows(self, *row_weights: int):
        if len(row_weights) == 1:
            row_weights = (1, ) * row_weights[0]

        _, r = self.grid_size()
        m = max(r, len(row_weights))

        for i in range(m):
            if i < r and i >= len(row_weights):
                self.grid_rowconfigure(i, weight=0)

            elif i < len(row_weights):
                self.grid_rowconfigure(i, weight=row_weights[i])

    def set_columns(self, *column_weights: int):
        if len(column_weights) == 1:
            column_weights = (1, ) * column_weights[0]

        c, _ = self.grid_size()
        m = max(c, len(column_weights))

        for i in range(m):
            if i < c and i >= len(column_weights):
                self.grid_columnconfigure(i, weight=0)

            elif i < len(column_weights):
                self.grid_columnconfigure(i, weight=column_weights[i])

    def set_rows_columns(self, row_weights: tuple[int, ...] | int, column_weights: tuple[int, ...] | int):
        if isinstance(row_weights, int):
            row_weights = (1, ) * row_weights

        if isinstance(column_weights, int):
            column_weights = (1, ) * column_weights

        self.set_rows(*row_weights)
        self.set_columns(*column_weights)

    def rows(self) -> int:
        return self.grid_size()[1]

    def columns(self) -> int:
        return self.grid_size()[0]


class APMTk(Tk, APMMisc):
    def __init__(self, title: Optional[str] = None, resize: tuple[int | float, int | float] | None = (1/2, 1/2), center: bool = True, *args, **kwargs):
        # AI generated
        if platform == "win32":
            try:
                from ctypes import windll  # type: ignore
                windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                try:
                    windll.user32.SetProcessDPIAware()
                except Exception:
                    pass
        #

        super().__init__(*args, **kwargs)

        if title is not None:
            self.title(title)

        if center:
            self.center()

        if resize is not None:
            self.resize(*resize)

        self.rows: Callable[[], int] = lambda: self.grid_size()[1]
        self.columns: Callable[[], int] = lambda: self.grid_size()[0]

    def resize(self, newWidth: int | float, newHeight: int | float):
        # self.update_idletasks()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        if isinstance(newWidth, float):
            newWidth = int(screen_width * newWidth)

        if isinstance(newHeight, float):
            newHeight = int(screen_height * newHeight)

        newX = (screen_width - newWidth) // 2
        newY = (screen_height - newHeight) // 2

        self.geometry(f"{newWidth}x{newHeight}+{newX}+{newY}")

    def center(self):
        # self.update_idletasks()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        width = self.winfo_width()
        height = self.winfo_height()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.geometry(f"+{x}+{y}")


class APMFrame(Frame, APMMisc):
    ...


class ScrollingFrame(APMFrame):
    def __init__(self, master: Misc | None = None, cnf: dict[str, Any] | None = None, **kwargs):
        self.frame = APMFrame(master)
        self.frame.grid_propagate(False)
        self.frame.set_rows_columns((1,), (1,))

        self.canvas = Canvas(self.frame)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = Scrollbar(self.frame, command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        super().__init__(self.canvas, **kwargs)
        self.id = self.canvas.create_window((0, 0), window=self, anchor="nw")

        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.bind("<Configure>", self.on_frame_configure)

        self.canvas.bind("<Enter>", lambda _: self._bind_mousewheel())
        self.canvas.bind("<Leave>", lambda _: self._unbind_mousewheel())

    def on_canvas_configure(self, event: Event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.id, width=event.width)
        self.canvas.configure(background=self.cget("background"))

    def on_frame_configure(self, event: Event):
        self.on_canvas_configure(event)
        self.canvas.bind_all("<MouseWheel>", self.mouse_scroll)

    def _bind_mousewheel(self):
        if platform.startswith("win"):
            self.canvas.bind_all("<MouseWheel>", self.mouse_scroll)
        elif platform == "darwin":
            self.canvas.bind_all("<MouseWheel>", self.mouse_scroll)
        else:
            self.canvas.bind_all("<Button-4>", self.mouse_scroll)
            self.canvas.bind_all("<Button-5>", self.mouse_scroll)

    def _unbind_mousewheel(self):
        if platform.startswith("win") or platform == "darwin":
            self.canvas.unbind_all("<MouseWheel>")
        else:
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")

    def mouse_scroll(self, event: Event):
        from tkinter import TclError
        try:
            if platform.startswith("win") or platform == "darwin":
                move = -1 if event.delta > 0 else 1
            else:
                move = -1 if event.num == 4 else 1

            self.canvas.yview_scroll(move, "units")

        except TclError:
            self._unbind_mousewheel()

    def grid(self, **kwargs): self.frame.grid(**kwargs)
    def pack(self, **kwargs): self.frame.pack(**kwargs)


__all__ = ["APMTk", "ScrollingFrame", "APMFrame"]

if __name__ == '__main__':
    from tkinter import Label

    root = APMTk("Test Window")

    root.set_rows(1)
    root.set_columns(1)

    scrolling_frame = ScrollingFrame()
    scrolling_frame.frame.grid(row=0, column=0, sticky="nsew")

    for i in range(1, 100):
        Label(scrolling_frame, text=f"Label {i}").pack()

    root.mainloop()
