#!/usr/bin/env python3
"""
修复版本的exe构建脚本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """安装PyInstaller"""
    try:
        import PyInstaller
        print("✓ PyInstaller已安装")
        return True
    except ImportError:
        print("正在安装PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller安装成功")
            return True
        except subprocess.CalledProcessError:
            print("✗ PyInstaller安装失败")
            return False

def create_minimal_app():
    """创建最小化版本的应用程序"""
    minimal_content = '''import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import json
from pathlib import Path

try:
    from version import __version__, __description__
except ImportError:
    __version__ = "1.0.0"
    __description__ = "图片水印工具"

class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"图片水印工具 v{__version__}")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # 应用程序状态
        self.images = []
        self.current_image_index = 0
        self.current_image = None
        self.preview_image = None
        self.watermark_settings = {
            'text': '水印文本',
            'font_size': 36,
            'font_family': 'Arial',
            'color': '#FFFFFF',
            'opacity': 128,
            'position': 'center',
            'x_offset': 0,
            'y_offset': 0,
            'rotation': 0
        }
        
        # 创建界面
        self.create_widgets()
        self.create_status_bar()
        self.load_default_settings()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建三栏布局
        self.create_left_panel(main_frame)
        self.create_center_panel(main_frame)
        self.create_right_panel(main_frame)
        
    def create_left_panel(self, parent):
        # 左栏 - 图片列表
        left_frame = ttk.LabelFrame(parent, text="图片列表", width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_frame.pack_propagate(False)
        
        # 导入按钮
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="导入图片", command=self.import_images).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="导入文件夹", command=self.import_folder).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="清空列表", command=self.clear_images).pack(fill=tk.X, pady=2)
        
        # 分隔线
        ttk.Separator(btn_frame, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # 输出设置
        output_label = ttk.Label(btn_frame, text="输出设置", font=("Arial", 10, "bold"))
        output_label.pack(pady=(5, 2))
        
        # 输出格式
        format_frame = ttk.Frame(btn_frame)
        format_frame.pack(fill=tk.X, pady=2)
        ttk.Label(format_frame, text="格式:").pack(side=tk.LEFT)
        self.output_format = tk.StringVar(value="PNG")
        format_combo = ttk.Combobox(format_frame, textvariable=self.output_format, 
                                   values=["PNG", "JPEG"], state="readonly", width=8)
        format_combo.pack(side=tk.RIGHT)
        
        # 文件命名
        naming_frame = ttk.Frame(btn_frame)
        naming_frame.pack(fill=tk.X, pady=2)
        ttk.Label(naming_frame, text="命名:").pack(anchor=tk.W)
        
        self.naming_option = tk.StringVar(value="suffix")
        ttk.Radiobutton(naming_frame, text="保留原名", variable=self.naming_option, 
                       value="original").pack(anchor=tk.W)
        ttk.Radiobutton(naming_frame, text="添加前缀", variable=self.naming_option, 
                       value="prefix").pack(anchor=tk.W)
        ttk.Radiobutton(naming_frame, text="添加后缀", variable=self.naming_option, 
                       value="suffix").pack(anchor=tk.W)
        
        self.naming_text = tk.StringVar(value="_watermarked")
        ttk.Entry(naming_frame, textvariable=self.naming_text, width=15).pack(fill=tk.X, pady=2)
        
        # 导出按钮
        ttk.Button(btn_frame, text="导出当前图片", command=self.export_current).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="批量导出", command=self.export_all).pack(fill=tk.X, pady=2)
        
        # 图片列表
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.image_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.image_listbox.bind('<<ListboxSelect>>', self.on_image_select)
        
        scrollbar.config(command=self.image_listbox.yview)
        
    def create_center_panel(self, parent):
        # 中栏 - 预览区域
        center_frame = ttk.LabelFrame(parent, text="预览")
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 预览画布
        self.canvas = tk.Canvas(center_frame, bg='white', cursor='hand2')
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 绑定鼠标事件用于拖拽水印
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        
        self.dragging = False
        self.preview_rect = None
        self.scale_factor = 1.0
        
    def create_right_panel(self, parent):
        # 右栏 - 设置面板
        right_frame = ttk.LabelFrame(parent, text="水印设置", width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_frame.pack_propagate(False)
        
        # 创建滚动区域
        canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 文本水印设置
        text_frame = ttk.LabelFrame(scrollable_frame, text="文本水印")
        text_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 水印文本
        ttk.Label(text_frame, text="水印文本:").pack(anchor=tk.W, padx=5, pady=2)
        self.text_var = tk.StringVar(value=self.watermark_settings['text'])
        text_entry = ttk.Entry(text_frame, textvariable=self.text_var)
        text_entry.pack(fill=tk.X, padx=5, pady=2)
        text_entry.bind('<KeyRelease>', self.on_text_change)
        
        # 字体大小
        ttk.Label(text_frame, text="字体大小:").pack(anchor=tk.W, padx=5, pady=2)
        self.font_size_var = tk.IntVar(value=self.watermark_settings['font_size'])
        font_size_scale = ttk.Scale(text_frame, from_=12, to=100, variable=self.font_size_var, 
                                   orient=tk.HORIZONTAL, command=self.on_setting_change)
        font_size_scale.pack(fill=tk.X, padx=5, pady=2)
        
        # 字体颜色
        color_frame = ttk.Frame(text_frame)
        color_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(color_frame, text="字体颜色:").pack(side=tk.LEFT)
        self.color_button = tk.Button(color_frame, text="选择颜色", bg=self.watermark_settings['color'],
                                     command=self.choose_color)
        self.color_button.pack(side=tk.RIGHT)
        
        # 透明度
        ttk.Label(text_frame, text="透明度:").pack(anchor=tk.W, padx=5, pady=2)
        self.opacity_var = tk.IntVar(value=self.watermark_settings['opacity'])
        opacity_scale = ttk.Scale(text_frame, from_=0, to=255, variable=self.opacity_var,
                                 orient=tk.HORIZONTAL, command=self.on_setting_change)
        opacity_scale.pack(fill=tk.X, padx=5, pady=2)
        
        # 位置设置
        position_frame = ttk.LabelFrame(scrollable_frame, text="位置设置")
        position_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 预设位置
        ttk.Label(position_frame, text="预设位置:").pack(anchor=tk.W, padx=5, pady=2)
        position_buttons_frame = ttk.Frame(position_frame)
        position_buttons_frame.pack(fill=tk.X, padx=5, pady=2)
        
        positions = [
            ('左上', 'top_left'), ('上中', 'top_center'), ('右上', 'top_right'),
            ('左中', 'middle_left'), ('中心', 'center'), ('右中', 'middle_right'),
            ('左下', 'bottom_left'), ('下中', 'bottom_center'), ('右下', 'bottom_right')
        ]
        
        for i, (text, pos) in enumerate(positions):
            row, col = divmod(i, 3)
            btn = ttk.Button(position_buttons_frame, text=text, width=6,
                           command=lambda p=pos: self.set_position(p))
            btn.grid(row=row, column=col, padx=1, pady=1)
        
        # 模板管理
        template_frame = ttk.LabelFrame(scrollable_frame, text="模板管理")
        template_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(template_frame, text="保存模板", command=self.save_template).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(template_frame, text="加载模板", command=self.load_template).pack(fill=tk.X, padx=5, pady=2)
        
        # 关于按钮
        ttk.Button(template_frame, text="关于程序", command=self.show_about).pack(fill=tk.X, padx=5, pady=2)
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="就绪")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # 图片信息标签
        self.image_info_label = ttk.Label(self.status_bar, text="")
        self.image_info_label.pack(side=tk.RIGHT, padx=5, pady=2)
        
    def update_status(self, message):
        """更新状态栏信息"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
        
    def update_image_info(self):
        """更新图片信息"""
        if self.current_image and self.images:
            current_name = self.images[self.current_image_index]['name']
            width, height = self.current_image.size
            info = f"{current_name} | {width}×{height} | {self.current_image_index + 1}/{len(self.images)}"
            self.image_info_label.config(text=info)
        else:
            self.image_info_label.config(text="")
    
    # 简化的方法实现
    def import_images(self):
        filetypes = [
            ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
            ("所有文件", "*.*")
        ]
        files = filedialog.askopenfilenames(title="选择图片文件", filetypes=filetypes)
        for file_path in files:
            self.add_image(file_path)
            
    def import_folder(self):
        folder_path = filedialog.askdirectory(title="选择图片文件夹")
        if not folder_path:
            return
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        for file_path in Path(folder_path).rglob('*'):
            if file_path.suffix.lower() in supported_formats:
                self.add_image(str(file_path))
                
    def add_image(self, file_path):
        try:
            with Image.open(file_path) as img:
                img.verify()
            image_info = {'path': file_path, 'name': os.path.basename(file_path)}
            if image_info not in self.images:
                self.images.append(image_info)
                self.image_listbox.insert(tk.END, image_info['name'])
                if len(self.images) == 1:
                    self.image_listbox.selection_set(0)
                    self.load_current_image()
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片 {file_path}: {str(e)}")
            
    def clear_images(self):
        self.images.clear()
        self.image_listbox.delete(0, tk.END)
        self.current_image = None
        self.canvas.delete("all")
        
    def on_image_select(self, event):
        selection = self.image_listbox.curselection()
        if selection:
            self.current_image_index = selection[0]
            self.load_current_image()
            
    def load_current_image(self):
        if not self.images or self.current_image_index >= len(self.images):
            return
        try:
            image_path = self.images[self.current_image_index]['path']
            self.update_status(f"正在加载图片...")
            self.current_image = Image.open(image_path)
            self.update_preview()
            self.update_image_info()
            self.update_status("就绪")
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片: {str(e)}")
            self.update_status("加载失败")
            
    def update_preview(self):
        if not self.current_image:
            self.canvas.delete("all")
            return
        try:
            watermarked_image = self.apply_watermark(self.current_image.copy())
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                self.root.after(100, self.update_preview)
                return
                
            img_width, img_height = watermarked_image.size
            scale_x = (canvas_width - 20) / img_width
            scale_y = (canvas_height - 20) / img_height
            scale = min(scale_x, scale_y, 1.0)
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            display_image = watermarked_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.preview_image = ImageTk.PhotoImage(display_image)
            
            self.canvas.delete("all")
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.preview_image)
            
            self.preview_rect = (x, y, x + new_width, y + new_height)
            self.scale_factor = scale
            
        except Exception as e:
            self.canvas.delete("all")
            
    def apply_watermark(self, image):
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
            
        watermark_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        text = self.text_var.get()
        font_size = int(self.font_size_var.get())
        color = self.watermark_settings['color']
        opacity = int(self.opacity_var.get())
        
        try:
            font_paths = [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/simhei.ttf",
                "C:/Windows/Fonts/simsun.ttc",
            ]
            font = None
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, font_size)
                        break
                except:
                    continue
            if font is None:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x, y = self.calculate_watermark_position(image.size, text_width, text_height)
        
        if color.startswith('#'):
            color = color[1:]
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        text_color = (r, g, b, opacity)
        
        draw.text((x, y), text, font=font, fill=text_color)
        result = Image.alpha_composite(image, watermark_layer)
        return result
        
    def calculate_watermark_position(self, image_size, text_width, text_height):
        img_width, img_height = image_size
        position = self.watermark_settings['position']
        
        if position == 'custom':
            x = img_width // 2 + self.watermark_settings['x_offset'] - text_width // 2
            y = img_height // 2 + self.watermark_settings['y_offset'] - text_height // 2
        else:
            positions = {
                'top_left': (10, 10),
                'top_center': ((img_width - text_width) // 2, 10),
                'top_right': (img_width - text_width - 10, 10),
                'middle_left': (10, (img_height - text_height) // 2),
                'center': ((img_width - text_width) // 2, (img_height - text_height) // 2),
                'middle_right': (img_width - text_width - 10, (img_height - text_height) // 2),
                'bottom_left': (10, img_height - text_height - 10),
                'bottom_center': ((img_width - text_width) // 2, img_height - text_height - 10),
                'bottom_right': (img_width - text_width - 10, img_height - text_height - 10)
            }
            base_x, base_y = positions.get(position, positions['center'])
            x = base_x + self.watermark_settings['x_offset']
            y = base_y + self.watermark_settings['y_offset']
        
        x = max(0, min(x, img_width - text_width))
        y = max(0, min(y, img_height - text_height))
        return x, y
        
    def on_text_change(self, event=None):
        self.watermark_settings['text'] = self.text_var.get()
        self.update_preview()
        
    def on_setting_change(self, event=None):
        self.watermark_settings['font_size'] = int(self.font_size_var.get())
        self.watermark_settings['opacity'] = int(self.opacity_var.get())
        self.update_preview()
        
    def choose_color(self):
        color = colorchooser.askcolor(color=self.watermark_settings['color'])
        if color[1]:
            self.watermark_settings['color'] = color[1]
            self.color_button.config(bg=color[1])
            self.update_preview()
            
    def set_position(self, position):
        self.watermark_settings['position'] = position
        self.update_preview()
        
    def on_canvas_click(self, event):
        self.dragging = True
        
    def on_canvas_drag(self, event):
        if self.dragging and self.current_image and hasattr(self, 'preview_rect'):
            x1, y1, x2, y2 = self.preview_rect
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                relative_x = (event.x - x1) / self.scale_factor
                relative_y = (event.y - y1) / self.scale_factor
                img_width, img_height = self.current_image.size
                self.watermark_settings['x_offset'] = int(relative_x - img_width // 2)
                self.watermark_settings['y_offset'] = int(relative_y - img_height // 2)
                self.watermark_settings['position'] = 'custom'
                self.update_preview()
    
    def export_current(self):
        if not self.current_image:
            messagebox.showwarning("警告", "请先选择一张图片")
            return
        output_dir = filedialog.askdirectory(title="选择输出文件夹")
        if not output_dir:
            return
        try:
            self.update_status("正在导出图片...")
            self.export_image(self.current_image_index, output_dir)
            self.update_status("导出成功")
            messagebox.showinfo("成功", "图片导出成功!")
        except Exception as e:
            self.update_status("导出失败")
            messagebox.showerror("错误", f"导出失败: {str(e)}")
            
    def export_all(self):
        if not self.images:
            messagebox.showwarning("警告", "请先导入图片")
            return
        output_dir = filedialog.askdirectory(title="选择输出文件夹")
        if not output_dir:
            return
        try:
            success_count = 0
            total_count = len(self.images)
            for i in range(total_count):
                try:
                    self.update_status(f"正在导出 {i+1}/{total_count}: {self.images[i]['name']}")
                    temp_image = Image.open(self.images[i]['path'])
                    self.export_image_with_data(temp_image, self.images[i], output_dir)
                    success_count += 1
                except Exception as e:
                    print(f"导出图片 {self.images[i]['name']} 失败: {str(e)}")
            self.update_status(f"批量导出完成: {success_count}/{total_count}")
            messagebox.showinfo("完成", f"成功导出 {success_count}/{total_count} 张图片")
        except Exception as e:
            self.update_status("批量导出失败")
            messagebox.showerror("错误", f"批量导出失败: {str(e)}")
            
    def export_image(self, image_index, output_dir):
        image_info = self.images[image_index]
        image = Image.open(image_info['path'])
        self.export_image_with_data(image, image_info, output_dir)
        
    def export_image_with_data(self, image, image_info, output_dir):
        watermarked_image = self.apply_watermark(image.copy())
        original_name = Path(image_info['name']).stem
        naming_option = self.naming_option.get()
        naming_text = self.naming_text.get()
        
        if naming_option == "original":
            new_name = original_name
        elif naming_option == "prefix":
            new_name = f"{naming_text}{original_name}"
        else:
            new_name = f"{original_name}{naming_text}"
            
        output_format = self.output_format.get()
        if output_format == "JPEG":
            output_ext = ".jpg"
            if watermarked_image.mode == 'RGBA':
                background = Image.new('RGB', watermarked_image.size, (255, 255, 255))
                background.paste(watermarked_image, mask=watermarked_image.split()[-1])
                watermarked_image = background
        else:
            output_ext = ".png"
            
        output_path = os.path.join(output_dir, f"{new_name}{output_ext}")
        
        if output_format == "JPEG":
            watermarked_image.save(output_path, "JPEG", quality=95)
        else:
            watermarked_image.save(output_path, "PNG")
    
    def save_template(self):
        template_name = simpledialog.askstring("保存模板", "请输入模板名称:")
        if not template_name:
            return
        templates_dir = Path("templates")
        templates_dir.mkdir(exist_ok=True)
        template_data = {
            'text': self.text_var.get(),
            'font_size': int(self.font_size_var.get()),
            'color': self.watermark_settings['color'],
            'opacity': int(self.opacity_var.get()),
            'position': self.watermark_settings['position'],
            'output_format': self.output_format.get(),
            'naming_option': self.naming_option.get(),
            'naming_text': self.naming_text.get()
        }
        template_path = templates_dir / f"{template_name}.json"
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("成功", f"模板 '{template_name}' 保存成功!")
        
    def load_template(self):
        templates_dir = Path("templates")
        if not templates_dir.exists():
            messagebox.showwarning("警告", "没有找到模板文件夹")
            return
        template_files = list(templates_dir.glob("*.json"))
        if not template_files:
            messagebox.showwarning("警告", "没有找到模板文件")
            return
        # 简化的模板选择
        messagebox.showinfo("提示", "模板功能已简化")
        
    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("关于")
        about_window.geometry("400x300")
        about_window.transient(self.root)
        about_window.grab_set()
        about_window.resizable(False, False)
        
        about_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        content_frame = ttk.Frame(about_window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = tk.Label(content_frame, text="图片水印工具", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        version_label = tk.Label(content_frame, text=f"版本: {__version__}")
        version_label.pack(pady=5)
        
        desc_label = tk.Label(content_frame, text=__description__, 
                             wraplength=350, justify=tk.CENTER)
        desc_label.pack(pady=10)
        
        features_text = """主要功能:
• 支持多种图片格式 (JPEG, PNG, BMP, TIFF)
• 文本水印自定义
• 实时预览效果
• 批量处理图片
• 九宫格位置预设
• 拖拽调整位置
• 透明度和颜色调节"""
        
        features_label = tk.Label(content_frame, text=features_text, 
                                 justify=tk.LEFT, font=("Arial", 9))
        features_label.pack(pady=10)
        
        ttk.Button(content_frame, text="确定", 
                  command=about_window.destroy).pack(pady=10)
    
    def load_default_settings(self):
        pass  # 简化实现
        
    def save_current_settings(self):
        pass  # 简化实现
        
    def on_closing(self):
        self.save_current_settings()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = WatermarkApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
'''
    
    with open('watermark_app_minimal.py', 'w', encoding='utf-8') as f:
        f.write(minimal_content)
    
    print("✓ 创建最小化版本应用程序")

def build_minimal_exe():
    """构建最小化exe"""
    print("开始构建最小化exe文件...")
    
    try:
        # 清理之前的构建
        if Path("build").exists():
            import shutil
            shutil.rmtree("build")
        if Path("dist").exists():
            import shutil
            shutil.rmtree("dist")
        
        # 使用更简单的命令构建
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed", 
            "--name=WatermarkTool",
            "--exclude-module=urllib",
            "--exclude-module=urllib3", 
            "--exclude-module=requests",
            "--exclude-module=certifi",
            "--exclude-module=charset_normalizer",
            "--exclude-module=idna",
            "watermark_app_minimal.py"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ 最小化exe构建成功")
            return True
        else:
            print(f"✗ 构建失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ 构建过程出错: {e}")
        return False

def main():
    """主函数"""
    print("=== 修复版 exe 构建脚本 ===\\n")
    
    # 安装PyInstaller
    if not install_pyinstaller():
        return False
    
    # 创建最小化应用
    create_minimal_app()
    
    # 构建exe
    if not build_minimal_exe():
        return False
    
    # 检查文件大小
    exe_path = Path("dist/WatermarkTool.exe")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"exe文件大小: {size_mb:.2f} MB")
        
        if size_mb < 50:
            print("✅ 文件大小符合要求")
        else:
            print("⚠️ 文件大小超过50MB")
    
    print("\\n=== 构建完成 ===")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\\n构建失败，请检查错误信息")
        sys.exit(1)
    else:
        print("\\n构建成功！")