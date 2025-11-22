import tkinter as tk
from tkinter import messagebox
import ast

DEBOUNCE_MS = 250  # 编辑防抖

def parse_literal(s):
    if s is None:
        return None
    s = str(s).strip()
    if s == "":
        return ""
    try:
        return ast.literal_eval(s)
    except Exception:
        return s

class MapGridApp:
    def __init__(self, root):
        self.root = root
        root.title("Simple LookUp Table Editor v1.0")

        self.rendered = False
        self.X = []
        self.Y = []
        self.Z = []
        self.header_x_entries = []
        self.header_y_entries = []
        self.cell_entries = []
        self._debounce_id = None

        # --- Inputs ---
        frm_inputs = tk.Frame(root)
        frm_inputs.pack(padx=10, pady=10, anchor="nw", fill="x")
        tk.Label(frm_inputs, text="X (left→right)").grid(row=0, column=0, sticky="w")
        self.entry_X = tk.Entry(frm_inputs, width=80)
        self.entry_X.grid(row=0, column=1, padx=5, pady=2)
        tk.Label(frm_inputs, text="Y (top→down)").grid(row=1, column=0, sticky="w")
        self.entry_Y = tk.Entry(frm_inputs, width=80)
        self.entry_Y.grid(row=1, column=1, padx=5, pady=2)
        tk.Label(frm_inputs, text="Z (2D list)").grid(row=2, column=0, sticky="w")
        self.entry_Z = tk.Entry(frm_inputs, width=80)
        self.entry_Z.grid(row=2, column=1, padx=5, pady=2)

        # --- Buttons ---
        btn_frame = tk.Frame(root)
        btn_frame.pack(padx=10, pady=5, anchor="nw", fill="x")
        self.btn_render = tk.Button(btn_frame, text="生成查表", command=self.on_render)
        self.btn_render.pack(side="left", padx=3)
        self.btn_example = tk.Button(btn_frame, text="加载示例数据", command=self.load_example)
        self.btn_example.pack(side="left", padx=3)
        self.btn_clear = tk.Button(btn_frame, text="清空所有", command=self.clear_all)
        self.btn_clear.pack(side="left", padx=3)
        self.btn_update = tk.Button(btn_frame, text="更新输出", command=self.update_outputs)
        self.btn_update.pack(side="left", padx=3)

        # --- Outputs ---
        out_frame = tk.Frame(root)
        out_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(out_frame, text="out_X:").grid(row=0, column=0, sticky="w")
        self.out_X = tk.Entry(out_frame, width=70, state="readonly")
        self.out_X.grid(row=0, column=1, padx=5, pady=2)
        tk.Button(out_frame, text="复制", command=lambda:self.copy_to_clipboard(self.out_X)).grid(row=0,column=2)
        tk.Label(out_frame, text="out_Y:").grid(row=1, column=0, sticky="w")
        self.out_Y = tk.Entry(out_frame, width=70, state="readonly")
        self.out_Y.grid(row=1, column=1, padx=5, pady=2)
        tk.Button(out_frame, text="复制", command=lambda:self.copy_to_clipboard(self.out_Y)).grid(row=1,column=2)
        tk.Label(out_frame, text="out_Z:").grid(row=2, column=0, sticky="w")
        self.out_Z = tk.Entry(out_frame, width=70, state="readonly")
        self.out_Z.grid(row=2, column=1, padx=5, pady=2)
        tk.Button(out_frame, text="复制", command=lambda:self.copy_to_clipboard(self.out_Z)).grid(row=2,column=2)

        # --- Scrollable Canvas ---
        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.scroll_y = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side="right", fill="y")
        self.scroll_x = tk.Scrollbar(root, orient="horizontal", command=self.canvas.xview)
        self.scroll_x.pack(side="bottom", fill="x")
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        # --- 内部 Frame ---
        self.grid_inner_frame = tk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0,0), window=self.grid_inner_frame, anchor="nw")
        # 保持 scrollregion
        self.grid_inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.load_example()

    # --- 功能 ---
    def copy_to_clipboard(self, entry):
        self.root.clipboard_clear()
        self.root.clipboard_append(entry.get())

    def load_example(self):
        self.entry_X.delete(0, tk.END)
        self.entry_Y.delete(0, tk.END)
        self.entry_Z.delete(0, tk.END)
        LENX = 6  # 测试多列
        LENY = 5
        self.entry_X.insert(0, str([i for i in range(1,LENX+1)]))
        self.entry_Y.insert(0, str([i for i in range(1,LENY+1)]))
        Z=[[i+j for j in range(1,LENX+1)] for i in range(LENY)]
        self.entry_Z.insert(0,str(Z))

    # --- 渲染 ---
    def on_render(self):
        if self.rendered:
            messagebox.showinfo("提示","已渲染，清空后可重新生成")
            return
        X=parse_literal(self.entry_X.get())
        Y=parse_literal(self.entry_Y.get())
        Z=parse_literal(self.entry_Z.get())
        X=X if isinstance(X,list) else []
        Y=Y if isinstance(Y,list) else []
        Z=Z if isinstance(Z,list) else []
        if Z and not X and not Y:
            rows=len(Z)
            cols=len(Z[0])
            X=[f"X{i}" for i in range(cols)]
            Y=[f"Y{i}" for i in range(rows)]
        elif Z and X and not Y:
            rows=len(Z)
            cols=len(Z[0])
            if len(X)!=cols: messagebox.showerror("错误",f"X/Z[0]长度不匹配{len(X)}/{cols}"); return
            Y=[f"Y{i}" for i in range(rows)]
        elif Z and Y and not X:
            rows=len(Z)
            cols=len(Z[0])
            if len(Y)!=rows: messagebox.showerror("错误",f"Y/Z长度不匹配{len(Y)}/{rows}"); return
            X=[f"X{i}" for i in range(cols)]
        elif Z and X and Y:
            rows=len(Z)
            cols=len(Z[0])
            if len(Y)!=rows or len(X)!=cols: messagebox.showerror("错误",f"X/Y长度与Z不匹配{len(X)}/{len(Y)},{cols}/{rows}"); return
        elif X and not Y and not Z: Y=["Y0"]; Z=[[0]*len(X)]
        elif Y and not X and not Z: X=["X0"]; Z=[[0] for _ in range(len(Y))]
        elif X and Y and not Z: Z=[[0]*len(X) for _ in range(len(Y))]
        else: X=["X0"]; Y=["Y0"]; Z=[[0]]
        self.X=X; self.Y=Y; self.Z=Z
        self._build_grid()
        self.entry_X.config(state="disabled")
        self.entry_Y.config(state="disabled")
        self.entry_Z.config(state="disabled")
        self.btn_render.config(state="disabled")
        self.rendered=True

    def _build_grid(self):
        for w in self.grid_inner_frame.winfo_children(): 
            w.destroy()
        self.header_x_entries=[]; self.header_y_entries=[]; self.cell_entries=[]
        cell_w=8

        # corner
        tk.Entry(self.grid_inner_frame,width=cell_w,state="readonly", 
                readonlybackground="#cccccc").grid(row=0,column=0)

        # X header
        for j,xv in enumerate(self.X):
            e=tk.Entry(self.grid_inner_frame,width=cell_w)
            e.insert(0,str(xv))
            e.grid(row=0,column=1+j,padx=1,pady=1)
            e.bind("<FocusOut>",self._on_edit)
            e.bind("<KeyRelease>",self._on_edit)
            # 设置 header 背景
            e.config(state="readonly", readonlybackground="#cccccc")  
            self.header_x_entries.append(e)

        # Y header + 数据单元格
        for i,yv in enumerate(self.Y):
            # Y header
            ey=tk.Entry(self.grid_inner_frame,width=cell_w)
            ey.insert(0,str(yv))
            ey.grid(row=1+i,column=0,padx=1,pady=1)
            ey.bind("<FocusOut>",self._on_edit)
            ey.bind("<KeyRelease>",self._on_edit)
            ey.config(state="readonly", readonlybackground="#cccccc")  # 与 X header 同色
            self.header_y_entries.append(ey)

            # 数据单元格
            row_entries=[]
            for j in range(len(self.X)):
                ec=tk.Entry(self.grid_inner_frame,width=cell_w)
                ec.insert(0,str(self.Z[i][j]))
                ec.grid(row=1+i,column=1+j,padx=1,pady=1)
                ec.bind("<FocusOut>",self._on_edit)
                ec.bind("<KeyRelease>",self._on_edit)
                row_entries.append(ec)
            self.cell_entries.append(row_entries)

        # 更新 scrollregion
        self.grid_inner_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_edit(self,event=None):
        if self._debounce_id:
            self.root.after_cancel(self._debounce_id)
        self._debounce_id=self.root.after(DEBOUNCE_MS,self._apply_edit)

    def _apply_edit(self):
        self._debounce_id=None
        newX=[parse_literal(e.get()) for e in self.header_x_entries]
        newY=[parse_literal(e.get()) for e in self.header_y_entries]
        newZ=[]
        for row in self.cell_entries: newZ.append([parse_literal(c.get()) for c in row])
        if len(newX)!=len(self.X) or len(newY)!=len(self.Y) or len(newZ)!=len(self.Z) or any(len(r)!=len(self.X) for r in newZ):
            self._restore_entries(); return
        self.X=newX; self.Y=newY; self.Z=newZ

    def _restore_entries(self):
        for j,e in enumerate(self.header_x_entries): e.delete(0,tk.END); e.insert(0,str(self.X[j]))
        for i,e in enumerate(self.header_y_entries): e.delete(0,tk.END); e.insert(0,str(self.Y[i]))
        for i,row in enumerate(self.cell_entries):
            for j,c in enumerate(row): c.delete(0,tk.END); c.insert(0,str(self.Z[i][j]))

    def update_outputs(self):
        def set_entry(e,text): e.config(state="normal"); e.delete(0,tk.END); e.insert(0,text); e.config(state="readonly")
        set_entry(self.out_X,repr(self.X))
        set_entry(self.out_Y,repr(self.Y))
        set_entry(self.out_Z,repr(self.Z))

    def clear_all(self):
        self.entry_X.config(state="normal"); self.entry_Y.config(state="normal"); self.entry_Z.config(state="normal")
        self.btn_render.config(state="normal")
        self.entry_X.delete(0,tk.END); self.entry_Y.delete(0,tk.END); self.entry_Z.delete(0,tk.END)
        for out in (self.out_X,self.out_Y,self.out_Z): out.config(state="normal"); out.delete(0,tk.END); out.config(state="readonly")
        for w in self.grid_inner_frame.winfo_children(): w.destroy()
        self.X=[]; self.Y=[]; self.Z=[]; self.header_x_entries=[]; self.header_y_entries=[]; self.cell_entries=[]; self.rendered=False

import sys, os
def resource_path(relative_path):
    """获取资源文件路径，适用于 PyInstaller 打包后"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

if __name__=="__main__":
    root=tk.Tk()
    root.geometry("1000x700")
    root.iconbitmap(resource_path("map-tool.ico"))
    app=MapGridApp(root)
    root.mainloop()
