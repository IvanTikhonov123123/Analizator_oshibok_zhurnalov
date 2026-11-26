import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import os


class LogAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор журналов ошибок — Версия 0.2 (День 2-3)")
        self.root.geometry("950x600")
        self.root.minsize(750, 450)

        self.log_lines = []
        self.current_file = ""

        self.setup_ui()

    def setup_ui(self):
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        btn_open = ttk.Button(
            top_frame, text="📂 Открыть файл (.log / .txt)", command=self.load_file
        )
        btn_open.pack(side=tk.LEFT, padx=(0, 10))

        self.lbl_filename = ttk.Label(
            top_frame, text="Файл не выбран", foreground="gray"
        )
        self.lbl_filename.pack(side=tk.LEFT, fill=tk.X, expand=True)

        filter_frame = ttk.LabelFrame(
            self.root, text="Фильтрация и поиск", padding="10"
        )
        filter_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Label(filter_frame, text="Уровень:").pack(side=tk.LEFT, padx=(0, 5))
        self.level_var = tk.StringVar(value="ALL")
        levels = ["ALL", "ERROR", "WARNING", "INFO"]
        self.combo_level = ttk.Combobox(
            filter_frame,
            textvariable=self.level_var,
            values=levels,
            state="readonly",
            width=12,
        )
        self.combo_level.pack(side=tk.LEFT, padx=(0, 15))
        self.combo_level.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # Поле текстового поиска
        ttk.Label(filter_frame, text="Поиск (текст или время):").pack(
            side=tk.LEFT, padx=(0, 5)
        )
        self.search_var = tk.StringVar()
        self.entry_search = ttk.Entry(
            filter_frame, textvariable=self.search_var, width=30
        )
        self.entry_search.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_search.bind("<Return>", lambda e: self.apply_filters())

        btn_search = ttk.Button(
            filter_frame, text="🔍 Найти / Применить", command=self.apply_filters
        )
        btn_search.pack(side=tk.LEFT, padx=(0, 5))

        btn_reset = ttk.Button(
            filter_frame, text="Сбросить", command=self.reset_filters
        )
        btn_reset.pack(side=tk.LEFT)

        text_frame = ttk.Frame(self.root, padding="10 0 10 10")
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        scrollbar_x = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL)

        self.text_area = tk.Text(
            text_frame,
            wrap=tk.NONE,
            font=("Consolas", 10),
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            state=tk.DISABLED,
        )

        scrollbar_y.config(command=self.text_area.yview)
        scrollbar_x.config(command=self.text_area.xview)

        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.text_area.tag_configure("ERROR", foreground="#b30000", background="#ffe6e6")
        self.text_area.tag_configure("WARNING", foreground="#995c00", background="#fff5cc")
        self.text_area.tag_configure("INFO", foreground="#004d00")

        self.status_var = tk.StringVar(
            value="Готов к работе. Загрузите лог-файл для анализа."
        )
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding="5",
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл журнала",
            filetypes=[("Лог-файлы", "*.log *.txt"), ("Все файлы", "*.*")],
        )
        if not file_path:
            return

        try:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.log_lines = f.readlines()
            except UnicodeDecodeError:
                with open(file_path, "r", encoding="cp1251") as f:
                    self.log_lines = f.readlines()

            self.current_file = os.path.basename(file_path)
            self.lbl_filename.config(
                text=f"Загружен: {self.current_file} ({len(self.log_lines)} строк)",
                foreground="black",
            )
            self.reset_filters()

        except Exception as e:
            messagebox.showerror(
                "Ошибка чтения", f"Не удалось открыть файл:\n{str(e)}"
            )

    def apply_filters(self):
        if not self.log_lines:
            messagebox.showwarning("Внимание", "Сначала загрузите файл журнала!")
            return

        selected_level = self.level_var.get()
        keyword = self.search_var.get().strip()

        level_pattern = (
            re.compile(rf"\b{selected_level}\b", re.IGNORECASE)
            if selected_level != "ALL"
            else None
        )

        filtered_lines = []
        error_count = 0
        warning_count = 0

        for line in self.log_lines:
            if re.search(r"\bERROR\b", line, re.IGNORECASE):
                error_count += 1
            elif re.search(r"\bWARNING\b", line, re.IGNORECASE):
                warning_count += 1

            if level_pattern and not level_pattern.search(line):
                continue

            if keyword and keyword.lower() not in line.lower():
                continue

            filtered_lines.append(line)

        self.display_lines(filtered_lines)
        self.status_var.set(
            f"Показано строк: {len(filtered_lines)} из {len(self.log_lines)}  |  "
            f"Всего в файле — ERROR: {error_count}, WARNING: {warning_count}"
        )

    def display_lines(self, lines):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)

        if not lines:
            self.text_area.insert(tk.END, "Записей по заданным условиям не найдено.")
        else:
            for line in lines:
                tag = None
                if re.search(r"\bERROR\b", line, re.IGNORECASE):
                    tag = "ERROR"
                elif re.search(r"\bWARNING\b", line, re.IGNORECASE):
                    tag = "WARNING"
                elif re.search(r"\bINFO\b", line, re.IGNORECASE):
                    tag = "INFO"

                if tag:
                    self.text_area.insert(tk.END, line, tag)
                else:
                    self.text_area.insert(tk.END, line)

        self.text_area.config(state=tk.DISABLED)

    def reset_filters(self):
        self.level_var.set("ALL")
        self.search_var.set("")
        if self.log_lines:
            self.apply_filters()


if __name__ == "__main__":
    root = tk.Tk()
    app = LogAnalyzerApp(root)
    root.mainloop()
