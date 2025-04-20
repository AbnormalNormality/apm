from tkinter import Tk
from typing import Callable, Optional
from sys import platform


class Window(Tk):
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

        if resize is not None:
            self.resize(*resize)

        if center:
            self.center()

        self.rows: Callable[[], int] = lambda: self.grid_size()[1]
        self.columns: Callable[[], int] = lambda: self.grid_size()[0]

    def resize(self, newWidth: int | float, newHeight: int | float):
        self.update_idletasks()

        if isinstance(newWidth, float):
            newWidth = int(self.winfo_screenwidth() * newWidth)

        if isinstance(newHeight, float):
            newHeight = int(self.winfo_screenheight() * newHeight)

        newX = self.winfo_x() - (newWidth - self.winfo_width()) // 2
        newY = self.winfo_y() - (newHeight - self.winfo_height()) // 2

        self.geometry(f"{newWidth}x{newHeight}+{newX}+{newY}")

    def center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

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


__all__ = ["Window"]

if __name__ == '__main__':
    root = Window("Test Window")
    root.resize(1/2, 1/2)
    root.center()

    root.set_rows(1)
    root.set_columns(1, 2)

    from tkinter import Label
    Label(root, text="Row 1", bg="#f00").grid(row=0, column=0, sticky="nsew")

    root.mainloop()
