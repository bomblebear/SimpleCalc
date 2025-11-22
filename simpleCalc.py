import tkinter as tk
from tkinter import messagebox
import ast
from tksheet import Sheet
import sys, os

DEBOUNCE_MS = 250  # 防抖

def parse_literal(s):
    if s is None:
        return None
    s = str(s).strip()
    if s == "":
        return ""
    try:
        return ast.literal_eval(s)
    except Exception:
        messagebox.showerror("错误",f"原数据格式无法转换为数组: {s}")

def resource_path(relative_path):
    """获取资源文件路径，适用于 PyInstaller 打包后"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

import webbrowser
class MapGridApp:
    def __init__(self, root):
        self.root = root
        root.title("Simple LookUp Table Editor v1.0")

        self.X = []
        self.Y = []
        self.Z = []

        smallSize = 9
        middleSize = 10
        link_conf = {"font": ('Microsoft YaHei', smallSize, "bold"), "fg": "blue"}
        input_conf = {"font": ('Microsoft YaHei', middleSize), "fg": "black"}
        button_conf = {"font": ('Microsoft YaHei', middleSize, "bold")}
        output_conf = {"font": ('Microsoft YaHei', middleSize), "fg": "black"}
        tip_conf = {"font": (None, smallSize, "bold"), "fg": "red"}

        def open_link(event):
            webbrowser.open("https://github.com/bomblebear")  # 点击后打开百度
        lbl_disclaimer = tk.Label(root, text="本工具由AI生成 > <, 本人概不负责", cursor="hand2", **link_conf)
        lbl_disclaimer.pack(anchor="nw", padx=10, pady=2)
        lbl_disclaimer.bind("<Button-1>", open_link)

        # --- Inputs ---
        frm_inputs = tk.Frame(root)
        frm_inputs.pack(padx=10, pady=10, anchor="nw", fill="x")
        tk.Label(frm_inputs, text="X (left→right)", **input_conf).grid(row=0, column=0, sticky="w")
        self.entry_X = tk.Entry(frm_inputs, width=80, **input_conf)
        self.entry_X.grid(row=0, column=1, padx=5, pady=2)
        tk.Label(frm_inputs, text="Y (top→down)", **input_conf).grid(row=1, column=0, sticky="w")
        self.entry_Y = tk.Entry(frm_inputs, width=80, **input_conf)
        self.entry_Y.grid(row=1, column=1, padx=5, pady=2)
        tk.Label(frm_inputs, text="Z (2D list)", **input_conf).grid(row=2, column=0, sticky="w")
        self.entry_Z = tk.Entry(frm_inputs, width=80, **input_conf)
        self.entry_Z.grid(row=2, column=1, padx=5, pady=2)

        # --- Buttons ---
        btn_frame = tk.Frame(root)
        btn_frame.pack(padx=10, pady=5, anchor="nw", fill="x")
        self.btn_render = tk.Button(btn_frame, text="生成查表", **button_conf, command=self.on_render)
        self.btn_render.pack(side="left", padx=3)
        self.btn_example = tk.Button(btn_frame, text="加载示例数据", **button_conf, command=self.load_example)
        self.btn_example.pack(side="left", padx=3)
        self.btn_clear = tk.Button(btn_frame, text="清空所有", **button_conf, command=self.clear_all)
        self.btn_clear.pack(side="left", padx=3)
        self.btn_update = tk.Button(btn_frame, text="更新输出", **button_conf, command=self.update_outputs)
        self.btn_update.pack(side="left", padx=3)

        # --- Outputs ---
        out_frame = tk.Frame(root)
        out_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(out_frame, text="out_X:", **output_conf).grid(row=0, column=0, sticky="w")
        self.out_X = tk.Entry(out_frame, width=70, state="readonly", **output_conf)
        self.out_X.grid(row=0, column=1, padx=5, pady=2)
        tk.Button(out_frame, text="复制", **output_conf, command=lambda:self.copy_to_clipboard(self.out_X)).grid(row=0,column=2)

        tk.Label(out_frame, text="out_Y:", **output_conf).grid(row=1, column=0, sticky="w")
        self.out_Y = tk.Entry(out_frame, width=70, state="readonly", **output_conf)
        self.out_Y.grid(row=1, column=1, padx=5, pady=2)
        tk.Button(out_frame, text="复制", **output_conf, command=lambda:self.copy_to_clipboard(self.out_Y)).grid(row=1,column=2)

        tk.Label(out_frame, text="out_Z:", **output_conf).grid(row=2, column=0, sticky="w")
        self.out_Z = tk.Entry(out_frame, width=70, state="readonly", **output_conf)
        self.out_Z.grid(row=2, column=1, padx=5, pady=2)
        tk.Button(out_frame, text="复制", **output_conf, command=lambda:self.copy_to_clipboard(self.out_Z)).grid(row=2,column=2)

        tk.Label(root, text="输入数据后请按回车保存", **tip_conf).pack(anchor="nw", padx=10, pady=2)

        # --- tksheet ---
        self.sheet = Sheet(
            root,
            data=[],
            headers=[],
            show_row_index=True,
            font=('Microsoft YaHei', middleSize, "normal"),
            header_font=('Microsoft YaHei', middleSize, "normal"),
            index_font=('Microsoft YaHei', middleSize, "normal"),
        )
        self.sheet.enable_bindings((
            "all",           # 包含 edit_cell, edit_header, edit_index, copy, paste 等
        ))
        self.sheet.pack(fill="both", expand=True, padx=10, pady=10)
        self.load_example()

    def copy_to_clipboard(self, entry):
        self.root.clipboard_clear()
        self.root.clipboard_append(entry.get())

    def load_example(self):
        LENX = 6
        LENY = 5
        X = [i for i in range(1,LENX+1)]
        Y = [i for i in range(1,LENY+1)]
        Z = [[i+j for j in range(1,LENX+1)] for i in range(LENY)]
        # 只填文本输入框，不刷新表格
        self.entry_X.delete(0, tk.END)
        self.entry_X.insert(0, str(X))
        self.entry_Y.delete(0, tk.END)
        self.entry_Y.insert(0, str(Y))
        self.entry_Z.delete(0, tk.END)
        self.entry_Z.insert(0, str(Z))

    def on_render(self):
        X = parse_literal(self.entry_X.get())
        Y = parse_literal(self.entry_Y.get())
        Z = parse_literal(self.entry_Z.get())

        X = X if isinstance(X,list) else []
        Y = Y if isinstance(Y,list) else []
        Z = Z if isinstance(Z,list) else []

        # 原有逻辑
        if Z and not X and not Y:
            rows = len(Z)
            cols = len(Z[0])
            X = [f"X{i}" for i in range(cols)]
            Y = [f"Y{i}" for i in range(rows)]
        elif Z and X and not Y:
            rows = len(Z)
            cols = len(Z[0])
            if len(X)!=cols:
                messagebox.showerror("错误",f"X/Z[0]长度不匹配 {len(X)}/{cols}")
                return
            Y = [f"Y{i}" for i in range(rows)]
        elif Z and Y and not X:
            rows = len(Z)
            cols = len(Z[0])
            if len(Y)!=rows:
                messagebox.showerror("错误",f"Y/Z长度不匹配 {len(Y)}/{rows}")
                return
            X = [f"X{i}" for i in range(cols)]
        elif Z and X and Y:
            rows = len(Z)
            cols = len(Z[0])
            if len(Y)!=rows or len(X)!=cols:
                messagebox.showerror("错误",f"X/Y长度与Z不匹配 {len(X)}/{len(Y)},{cols}/{rows}")
                return
        elif X and not Y and not Z:
            Z = [[0]*len(X)]
        elif Y and not X and not Z:
            Z = [[0] for _ in range(len(Y))]
        elif X and Y and not Z:
            Z = [[0]*len(X) for _ in range(len(Y))]
        else:
            X = ["X0"]; Y = ["Y0"]; Z = [[0]]

        self.X = X
        self.Y = Y
        self.Z = Z

        self._refresh_sheet()

    def _refresh_sheet(self):
        self.sheet.set_sheet_data(self.Z, reset_col_positions=True, reset_row_positions=True)
        self.sheet.headers(self.X)
        self.sheet.row_index(self.Y)
        self.sheet.redraw()

    def update_outputs(self):
        raw_Z = self.sheet.get_sheet_data()

        isErr = False
        isEmptyX = all([str(h).startswith('X') for h in self.sheet.headers()])
        isEmptyY = all([str(r).startswith('Y') for r in self.sheet.row_index()])

        if isEmptyX:
            self.X = []
        else:
            try:
                self.X = [float(h) for h in self.sheet.headers()]
            except Exception as e:
                isErr = True
                messagebox.showerror("错误",f"X轴存在无法解析的变量")               
        if isEmptyY:
            self.Y = []
        else:
            try:
                self.Y = [float(r) for r in self.sheet.row_index()]
            except Exception as e:
                isErr = True
                messagebox.showerror("错误",f"Y轴存在无法解析的变量")               
        try:
            self.Z = [[float(c) for c in row] for row in raw_Z]
        except Exception as e:
            isErr = True
            messagebox.showerror("错误",f"Map中存在无法解析的变量")

        def set_entry(e, text):
            e.config(state="normal")
            e.delete(0, tk.END)
            e.insert(0, text)
            e.config(state="readonly")
        if not isErr:
            set_entry(self.out_X, repr(self.X))
            set_entry(self.out_Y, repr(self.Y))
            set_entry(self.out_Z, repr(self.Z))

    def clear_all(self):
        self.entry_X.config(state="normal"); self.entry_Y.config(state="normal"); self.entry_Z.config(state="normal")
        self.entry_X.delete(0, tk.END); self.entry_Y.delete(0, tk.END); self.entry_Z.delete(0, tk.END)
        self.X = []; self.Y = []; self.Z = []
        self._refresh_sheet()
        for out in (self.out_X,self.out_Y,self.out_Z):
            out.config(state="normal"); out.delete(0, tk.END); out.config(state="readonly")

if __name__=="__main__":
    root = tk.Tk()
    root.geometry("1000x700")
    root.iconbitmap(resource_path("map-tool.ico"))
    app = MapGridApp(root)
    root.mainloop()
