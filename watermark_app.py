import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import json
from pathlib import Path
import shutil

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
        self.images = []  # 存储导入的图片信息
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
        
    def import_images(self):
        """导入图片文件"""
        filetypes = [
            ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
            ("JPEG", "*.jpg *.jpeg"),
            ("PNG", "*.png"),
            ("BMP", "*.bmp"),
            ("TIFF", "*.tiff *.tif"),
            ("所有文件", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=filetypes
        )
        
        for file_path in files:
            self.add_image(file_path)
            
    def import_folder(self):
        """导入文件夹中的所有图片"""
        folder_path = filedialog.askdirectory(title="选择图片文件夹")
        if not folder_path:
            return
            
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        
        for file_path in Path(folder_path).rglob('*'):
            if file_path.suffix.lower() in supported_formats:
                self.add_image(str(file_path))
                
    def add_image(self, file_path):
        """添加图片到列表"""
        try:
            # 验证图片文件
            with Image.open(file_path) as img:
                img.verify()
            
            # 添加到列表
            image_info = {
                'path': file_path,
                'name': os.path.basename(file_path)
            }
            
            if image_info not in self.images:
                self.images.append(image_info)
                self.image_listbox.insert(tk.END, image_info['name'])
                
                # 如果是第一张图片，自动选择
                if len(self.images) == 1:
                    self.image_listbox.selection_set(0)
                    self.load_current_image()
                    
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片 {file_path}: {str(e)}")
            
    def clear_images(self):
        """清空图片列表"""
        self.images.clear()
        self.image_listbox.delete(0, tk.END)
        self.current_image = None
        self.canvas.delete("all")
        
    def on_image_select(self, event):
        """图片选择事件"""
        selection = self.image_listbox.curselection()
        if selection:
            self.current_image_index = selection[0]
            self.load_current_image()
            
    def load_current_image(self):
        """加载当前选中的图片"""
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
        """更新预览"""
        if not self.current_image:
            self.canvas.delete("all")
            self.canvas.create_text(
                self.canvas.winfo_width()//2, 
                self.canvas.winfo_height()//2,
                text="请选择图片", 
                fill="gray", 
                font=("Arial", 16)
            )
            return
            
        try:
            # 创建水印图片
            watermarked_image = self.apply_watermark(self.current_image.copy())
            
            # 调整图片大小以适应画布
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                self.root.after(100, self.update_preview)
                return
                
            # 计算缩放比例
            img_width, img_height = watermarked_image.size
            scale_x = (canvas_width - 20) / img_width  # 留出边距
            scale_y = (canvas_height - 20) / img_height
            scale = min(scale_x, scale_y, 1.0)  # 不放大图片
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # 调整图片大小
            display_image = watermarked_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为 PhotoImage
            self.preview_image = ImageTk.PhotoImage(display_image)
            
            # 在画布中央显示图片
            self.canvas.delete("all")
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.preview_image)
            
            # 存储图片在画布中的位置和尺寸，用于拖拽计算
            self.preview_rect = (x, y, x + new_width, y + new_height)
            self.scale_factor = scale
            
        except Exception as e:
            self.canvas.delete("all")
            self.canvas.create_text(
                canvas_width//2, 
                canvas_height//2,
                text=f"预览错误: {str(e)}", 
                fill="red", 
                font=("Arial", 12)
            )
        
    def apply_watermark(self, image):
        """应用水印到图片"""
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
            
        # 创建透明图层用于水印
        watermark_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        # 获取水印设置
        text = self.text_var.get()
        font_size = int(self.font_size_var.get())
        color = self.watermark_settings['color']
        opacity = int(self.opacity_var.get())
        
        # 创建字体
        try:
            # Windows系统字体路径
            font_paths = [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/Arial.ttf", 
                "C:/Windows/Fonts/simhei.ttf",  # 黑体，支持中文
                "C:/Windows/Fonts/simsun.ttc",  # 宋体，支持中文
                "/System/Library/Fonts/Arial.ttf",  # macOS
                "/usr/share/fonts/truetype/arial.ttf",  # Linux
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
                
        except Exception as e:
            print(f"字体加载失败: {e}")
            font = ImageFont.load_default()
        
        # 获取文本尺寸
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 计算位置
        x, y = self.calculate_watermark_position(image.size, text_width, text_height)
        
        # 转换颜色并添加透明度
        if color.startswith('#'):
            color = color[1:]
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        text_color = (r, g, b, opacity)
        
        # 绘制文本
        draw.text((x, y), text, font=font, fill=text_color)
        
        # 合并图层
        result = Image.alpha_composite(image, watermark_layer)
        
        return result
        
    def calculate_watermark_position(self, image_size, text_width, text_height):
        """计算水印位置"""
        img_width, img_height = image_size
        position = self.watermark_settings['position']
        
        if position == 'custom':
            # 自定义位置，直接使用偏移值
            x = img_width // 2 + self.watermark_settings['x_offset'] - text_width // 2
            y = img_height // 2 + self.watermark_settings['y_offset'] - text_height // 2
        else:
            # 预设位置
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
            
            # 添加偏移
            x = base_x + self.watermark_settings['x_offset']
            y = base_y + self.watermark_settings['y_offset']
        
        # 确保水印不会超出图片边界
        x = max(0, min(x, img_width - text_width))
        y = max(0, min(y, img_height - text_height))
        
        return x, y
        
    def on_text_change(self, event=None):
        """文本变化事件"""
        self.watermark_settings['text'] = self.text_var.get()
        self.update_preview()
        
    def on_setting_change(self, event=None):
        """设置变化事件"""
        self.watermark_settings['font_size'] = int(self.font_size_var.get())
        self.watermark_settings['opacity'] = int(self.opacity_var.get())
        self.update_preview()
        
    def choose_color(self):
        """选择颜色"""
        color = colorchooser.askcolor(color=self.watermark_settings['color'])
        if color[1]:
            self.watermark_settings['color'] = color[1]
            self.color_button.config(bg=color[1])
            self.update_preview()
            
    def set_position(self, position):
        """设置水印位置"""
        self.watermark_settings['position'] = position
        self.update_preview()
        
    def on_canvas_click(self, event):
        """画布点击事件"""
        self.dragging = True
        
    def on_canvas_drag(self, event):
        """画布拖拽事件"""
        if self.dragging and self.current_image and hasattr(self, 'preview_rect'):
            # 检查鼠标是否在图片区域内
            x1, y1, x2, y2 = self.preview_rect
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                # 计算相对于图片的位置
                relative_x = (event.x - x1) / self.scale_factor
                relative_y = (event.y - y1) / self.scale_factor
                
                # 转换为水印偏移
                img_width, img_height = self.current_image.size
                self.watermark_settings['x_offset'] = int(relative_x - img_width // 2)
                self.watermark_settings['y_offset'] = int(relative_y - img_height // 2)
                
                # 设置为自定义位置
                self.watermark_settings['position'] = 'custom'
                self.update_preview()
            
    def export_current(self):
        """导出当前图片"""
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
        """批量导出所有图片"""
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
                    # 临时加载图片
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
        """导出指定索引的图片"""
        image_info = self.images[image_index]
        image = Image.open(image_info['path'])
        self.export_image_with_data(image, image_info, output_dir)
        
    def export_image_with_data(self, image, image_info, output_dir):
        """使用图片数据导出图片"""
        # 应用水印
        watermarked_image = self.apply_watermark(image.copy())
        
        # 生成输出文件名
        original_name = Path(image_info['name']).stem
        original_ext = Path(image_info['name']).suffix
        
        naming_option = self.naming_option.get()
        naming_text = self.naming_text.get()
        
        if naming_option == "original":
            new_name = original_name
        elif naming_option == "prefix":
            new_name = f"{naming_text}{original_name}"
        else:  # suffix
            new_name = f"{original_name}{naming_text}"
            
        # 确定输出格式和扩展名
        output_format = self.output_format.get()
        if output_format == "JPEG":
            output_ext = ".jpg"
            # 转换为RGB模式（JPEG不支持透明度）
            if watermarked_image.mode == 'RGBA':
                background = Image.new('RGB', watermarked_image.size, (255, 255, 255))
                background.paste(watermarked_image, mask=watermarked_image.split()[-1])
                watermarked_image = background
        else:
            output_ext = ".png"
            
        output_path = os.path.join(output_dir, f"{new_name}{output_ext}")
        
        # 保存图片
        if output_format == "JPEG":
            watermarked_image.save(output_path, "JPEG", quality=95)
        else:
            watermarked_image.save(output_path, "PNG")
            
    def save_template(self):
        """保存水印模板"""
        template_name = tk.simpledialog.askstring("保存模板", "请输入模板名称:")
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
            'x_offset': self.watermark_settings['x_offset'],
            'y_offset': self.watermark_settings['y_offset'],
            'output_format': self.output_format.get(),
            'naming_option': self.naming_option.get(),
            'naming_text': self.naming_text.get()
        }
        
        template_path = templates_dir / f"{template_name}.json"
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, ensure_ascii=False, indent=2)
            
        messagebox.showinfo("成功", f"模板 '{template_name}' 保存成功!")
        
    def load_template(self):
        """加载水印模板"""
        templates_dir = Path("templates")
        if not templates_dir.exists():
            messagebox.showwarning("警告", "没有找到模板文件夹")
            return
            
        template_files = list(templates_dir.glob("*.json"))
        if not template_files:
            messagebox.showwarning("警告", "没有找到模板文件")
            return
            
        # 创建模板选择对话框
        template_names = [f.stem for f in template_files]
        
        # 简单的选择对话框
        selection_window = tk.Toplevel(self.root)
        selection_window.title("选择模板")
        selection_window.geometry("300x200")
        selection_window.transient(self.root)
        selection_window.grab_set()
        
        tk.Label(selection_window, text="选择要加载的模板:").pack(pady=10)
        
        listbox = tk.Listbox(selection_window)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for name in template_names:
            listbox.insert(tk.END, name)
            
        def load_selected():
            selection = listbox.curselection()
            if selection:
                template_name = template_names[selection[0]]
                self.load_template_by_name(template_name)
                selection_window.destroy()
                
        ttk.Button(selection_window, text="加载", command=load_selected).pack(pady=5)
        
    def load_template_by_name(self, template_name):
        """根据名称加载模板"""
        try:
            template_path = Path("templates") / f"{template_name}.json"
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
                
            # 应用模板设置
            self.text_var.set(template_data.get('text', '水印文本'))
            self.font_size_var.set(template_data.get('font_size', 36))
            self.watermark_settings['color'] = template_data.get('color', '#FFFFFF')
            self.color_button.config(bg=self.watermark_settings['color'])
            self.opacity_var.set(template_data.get('opacity', 128))
            self.watermark_settings['position'] = template_data.get('position', 'center')
            self.watermark_settings['x_offset'] = template_data.get('x_offset', 0)
            self.watermark_settings['y_offset'] = template_data.get('y_offset', 0)
            self.output_format.set(template_data.get('output_format', 'PNG'))
            self.naming_option.set(template_data.get('naming_option', 'suffix'))
            self.naming_text.set(template_data.get('naming_text', '_watermarked'))
            
            # 更新预览
            self.update_preview()
            
            messagebox.showinfo("成功", f"模板 '{template_name}' 加载成功!")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载模板失败: {str(e)}")
            
    def load_default_settings(self):
        """加载默认设置"""
        # 尝试加载上次的设置
        settings_path = Path("last_settings.json")
        if settings_path.exists():
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                self.text_var.set(settings.get('text', '水印文本'))
                self.font_size_var.set(settings.get('font_size', 36))
                self.watermark_settings['color'] = settings.get('color', '#FFFFFF')
                self.color_button.config(bg=self.watermark_settings['color'])
                self.opacity_var.set(settings.get('opacity', 128))
                self.watermark_settings['position'] = settings.get('position', 'center')
                
            except Exception as e:
                print(f"加载上次设置失败: {str(e)}")
                
    def save_current_settings(self):
        """保存当前设置"""
        try:
            settings = {
                'text': self.text_var.get(),
                'font_size': int(self.font_size_var.get()),
                'color': self.watermark_settings['color'],
                'opacity': int(self.opacity_var.get()),
                'position': self.watermark_settings['position']
            }
            
            with open("last_settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存设置失败: {str(e)}")
            
    def show_about(self):
        """显示关于对话框"""
        about_window = tk.Toplevel(self.root)
        about_window.title("关于")
        about_window.geometry("400x300")
        about_window.transient(self.root)
        about_window.grab_set()
        about_window.resizable(False, False)
        
        # 居中显示
        about_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # 内容
        content_frame = ttk.Frame(about_window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(content_frame, text="图片水印工具", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 版本信息
        version_label = tk.Label(content_frame, text=f"版本: {__version__}")
        version_label.pack(pady=5)
        
        # 描述
        desc_label = tk.Label(content_frame, text=__description__, 
                             wraplength=350, justify=tk.CENTER)
        desc_label.pack(pady=10)
        
        # 功能列表
        features_text = """主要功能:
• 支持多种图片格式 (JPEG, PNG, BMP, TIFF)
• 文本水印自定义
• 实时预览效果
• 批量处理图片
• 九宫格位置预设
• 拖拽调整位置
• 模板保存和加载
• 透明度和颜色调节"""
        
        features_label = tk.Label(content_frame, text=features_text, 
                                 justify=tk.LEFT, font=("Arial", 9))
        features_label.pack(pady=10)
        
        # 关闭按钮
        ttk.Button(content_frame, text="确定", 
                  command=about_window.destroy).pack(pady=10)
    
    def on_closing(self):
        """程序关闭时的处理"""
        self.save_current_settings()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = WatermarkApp(root)
    
    # 绑定关闭事件
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()