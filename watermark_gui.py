#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片水印GUI应用程序
支持拖拽导入、实时预览、批量处理等功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog
from tkinter.font import Font
import tkinter.font as tkFont
from PIL import Image, ImageTk, ImageDraw, ImageFont, ExifTags
import os
import json
from pathlib import Path
from datetime import datetime
import threading
import queue


class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片水印工具 v2.0")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # 应用程序状态
        self.image_files = []  # 导入的图片文件列表
        self.current_image_index = 0  # 当前预览的图片索引
        self.original_image = None  # 原始图片
        self.preview_image = None  # 预览图片
        self.watermark_settings = self.get_default_settings()
        
        # 创建界面
        self.create_widgets()
        self.load_last_settings()
        
        # 绑定拖拽事件
        self.setup_drag_drop()
        
    def get_default_settings(self):
        """获取默认水印设置"""
        return {
            'text': '2024-01-01',
            'font_family': 'Arial',
            'font_size': 36,
            'font_bold': False,
            'font_italic': False,
            'color': '#FFFFFF',
            'opacity': 128,
            'position': 'bottom-right',
            'x_offset': 50,
            'y_offset': 50,
            'rotation': 0,
            'shadow': True,
            'shadow_color': '#000000',
            'shadow_offset': 2
        }
    
    def create_widgets(self):
        """创建主界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板 - 文件列表和设置
        left_panel = ttk.Frame(main_frame, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # 右侧面板 - 预览区域
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_left_panel(left_panel)
        self.create_right_panel(right_panel)
        
    def create_left_panel(self, parent):
        """创建左侧控制面板"""
        # 文件操作区域
        file_frame = ttk.LabelFrame(parent, text="文件操作", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 导入按钮
        ttk.Button(file_frame, text="导入图片", command=self.import_images).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="导入文件夹", command=self.import_folder).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="清空列表", command=self.clear_images).pack(fill=tk.X, pady=2)
        
        # 文件列表
        list_frame = ttk.LabelFrame(parent, text="图片列表", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建列表框和滚动条
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.file_listbox = tk.Listbox(list_container, selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox.bind('<<ListboxSelect>>', self.on_image_select)
        
        # 水印设置区域
        settings_frame = ttk.LabelFrame(parent, text="水印设置", padding=10)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_watermark_settings(settings_frame)
        
        # 模板管理
        template_frame = ttk.LabelFrame(parent, text="模板管理", padding=10)
        template_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_template_management(template_frame)
        
        # 导出设置
        export_frame = ttk.LabelFrame(parent, text="导出设置", padding=10)
        export_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_export_settings(export_frame)
        
    def create_watermark_settings(self, parent):
        """创建水印设置控件"""
        # 水印文本
        ttk.Label(parent, text="水印文本:").pack(anchor=tk.W)
        self.text_var = tk.StringVar(value=self.watermark_settings['text'])
        text_entry = ttk.Entry(parent, textvariable=self.text_var)
        text_entry.pack(fill=tk.X, pady=(0, 10))
        text_entry.bind('<KeyRelease>', self.on_setting_change)
        
        # 字体设置
        font_frame = ttk.Frame(parent)
        font_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(font_frame, text="字体:").pack(anchor=tk.W)
        
        # 字体选择
        font_select_frame = ttk.Frame(font_frame)
        font_select_frame.pack(fill=tk.X, pady=2)
        
        self.font_var = tk.StringVar(value=self.watermark_settings['font_family'])
        font_combo = ttk.Combobox(font_select_frame, textvariable=self.font_var, width=15)
        font_combo['values'] = self.get_system_fonts()
        font_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        font_combo.bind('<<ComboboxSelected>>', self.on_setting_change)
        
        # 字体大小
        ttk.Label(font_select_frame, text="大小:").pack(side=tk.LEFT, padx=(10, 2))
        self.font_size_var = tk.IntVar(value=self.watermark_settings['font_size'])
        size_spin = ttk.Spinbox(font_select_frame, from_=8, to=200, width=8, textvariable=self.font_size_var)
        size_spin.pack(side=tk.LEFT)
        size_spin.bind('<KeyRelease>', self.on_setting_change)
        size_spin.bind('<<Increment>>', self.on_setting_change)
        size_spin.bind('<<Decrement>>', self.on_setting_change)
        
        # 字体样式
        style_frame = ttk.Frame(font_frame)
        style_frame.pack(fill=tk.X, pady=2)
        
        self.bold_var = tk.BooleanVar(value=self.watermark_settings['font_bold'])
        self.italic_var = tk.BooleanVar(value=self.watermark_settings['font_italic'])
        
        ttk.Checkbutton(style_frame, text="粗体", variable=self.bold_var, command=self.on_setting_change).pack(side=tk.LEFT)
        ttk.Checkbutton(style_frame, text="斜体", variable=self.italic_var, command=self.on_setting_change).pack(side=tk.LEFT, padx=(10, 0))
        
        # 颜色设置
        color_frame = ttk.Frame(parent)
        color_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(color_frame, text="颜色:").pack(side=tk.LEFT)
        self.color_button = tk.Button(color_frame, text="选择颜色", bg=self.watermark_settings['color'], 
                                     command=self.choose_color, width=10)
        self.color_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # 透明度
        ttk.Label(parent, text="透明度:").pack(anchor=tk.W)
        self.opacity_var = tk.IntVar(value=self.watermark_settings['opacity'])
        opacity_scale = ttk.Scale(parent, from_=0, to=255, orient=tk.HORIZONTAL, 
                                 variable=self.opacity_var, command=self.on_setting_change)
        opacity_scale.pack(fill=tk.X, pady=(0, 5))
        
        opacity_label_frame = ttk.Frame(parent)
        opacity_label_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(opacity_label_frame, text="0").pack(side=tk.LEFT)
        ttk.Label(opacity_label_frame, text="255").pack(side=tk.RIGHT)
        
        # 位置设置
        ttk.Label(parent, text="位置:").pack(anchor=tk.W)
        position_frame = ttk.Frame(parent)
        position_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.position_var = tk.StringVar(value=self.watermark_settings['position'])
        positions = [
            ('左上', 'top-left'), ('上中', 'top-center'), ('右上', 'top-right'),
            ('左中', 'center-left'), ('居中', 'center'), ('右中', 'center-right'),
            ('左下', 'bottom-left'), ('下中', 'bottom-center'), ('右下', 'bottom-right')
        ]
        
        for i, (text, value) in enumerate(positions):
            row, col = divmod(i, 3)
            ttk.Radiobutton(position_frame, text=text, variable=self.position_var, 
                           value=value, command=self.on_setting_change).grid(row=row, column=col, sticky=tk.W)
        
        # 阴影效果
        self.shadow_var = tk.BooleanVar(value=self.watermark_settings['shadow'])
        ttk.Checkbutton(parent, text="添加阴影", variable=self.shadow_var, 
                       command=self.on_setting_change).pack(anchor=tk.W, pady=(0, 10))
    
    def create_template_management(self, parent):
        """创建模板管理控件"""
        # 模板选择
        template_select_frame = ttk.Frame(parent)
        template_select_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(template_select_frame, text="模板:").pack(side=tk.LEFT)
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(template_select_frame, textvariable=self.template_var, 
                                          state="readonly", width=15)
        self.template_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.template_combo.bind('<<ComboboxSelected>>', self.load_template)
        
        # 模板操作按钮
        template_btn_frame = ttk.Frame(parent)
        template_btn_frame.pack(fill=tk.X, pady=2)
        
        ttk.Button(template_btn_frame, text="保存模板", command=self.save_template, width=12).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(template_btn_frame, text="删除模板", command=self.delete_template, width=12).pack(side=tk.LEFT, padx=2)
        
        # 加载已保存的模板
        self.refresh_template_list()
        
    def create_export_settings(self, parent):
        """创建导出设置控件"""
        # 输出格式
        ttk.Label(parent, text="输出格式:").pack(anchor=tk.W)
        self.output_format_var = tk.StringVar(value="PNG")
        format_frame = ttk.Frame(parent)
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(format_frame, text="PNG", variable=self.output_format_var, value="PNG").pack(side=tk.LEFT)
        ttk.Radiobutton(format_frame, text="JPEG", variable=self.output_format_var, value="JPEG").pack(side=tk.LEFT, padx=(20, 0))
        
        # 文件命名
        ttk.Label(parent, text="文件命名:").pack(anchor=tk.W)
        self.naming_var = tk.StringVar(value="suffix")
        naming_frame = ttk.Frame(parent)
        naming_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Radiobutton(naming_frame, text="保留原名", variable=self.naming_var, value="original").pack(anchor=tk.W)
        ttk.Radiobutton(naming_frame, text="添加前缀", variable=self.naming_var, value="prefix").pack(anchor=tk.W)
        ttk.Radiobutton(naming_frame, text="添加后缀", variable=self.naming_var, value="suffix").pack(anchor=tk.W)
        
        # 自定义前缀/后缀
        self.custom_text_var = tk.StringVar(value="_watermarked")
        ttk.Entry(parent, textvariable=self.custom_text_var).pack(fill=tk.X, pady=(0, 10))
        
        # 导出按钮
        ttk.Button(parent, text="选择输出目录并导出", command=self.export_images).pack(fill=tk.X, pady=5)
        
    def create_right_panel(self, parent):
        """创建右侧预览面板"""
        # 预览区域
        preview_frame = ttk.LabelFrame(parent, text="预览", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建画布用于显示图片
        self.canvas = tk.Canvas(preview_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定画布点击事件用于拖拽水印
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        
        # 状态栏
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="请导入图片文件")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
    def get_system_fonts(self):
        """获取系统字体列表"""
        try:
            fonts = list(tkFont.families())
            # 添加一些常用字体
            common_fonts = ['Arial', 'Times New Roman', 'Courier New', 'Helvetica', 'Georgia']
            for font in common_fonts:
                if font not in fonts:
                    fonts.append(font)
            return sorted(fonts)
        except:
            return ['Arial', 'Times New Roman', 'Courier New', 'Helvetica']
    
    def setup_drag_drop(self):
        """设置拖拽功能"""
        # 注意：这里简化了拖拽实现，实际项目中可能需要使用tkinterdnd2库
        pass
    
    def import_images(self):
        """导入图片文件"""
        filetypes = [
            ('图片文件', '*.jpg *.jpeg *.png *.bmp *.tiff'),
            ('JPEG文件', '*.jpg *.jpeg'),
            ('PNG文件', '*.png'),
            ('所有文件', '*.*')
        ]
        
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=filetypes
        )
        
        if files:
            self.add_images(files)
    
    def import_folder(self):
        """导入文件夹中的所有图片"""
        folder = filedialog.askdirectory(title="选择图片文件夹")
        if folder:
            supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
            files = []
            for ext in supported_formats:
                files.extend(Path(folder).glob(f'*{ext}'))
                files.extend(Path(folder).glob(f'*{ext.upper()}'))
            
            if files:
                self.add_images([str(f) for f in files])
            else:
                messagebox.showinfo("提示", "所选文件夹中没有找到支持的图片文件")
    
    def add_images(self, files):
        """添加图片到列表"""
        for file in files:
            if file not in self.image_files:
                self.image_files.append(file)
                filename = os.path.basename(file)
                self.file_listbox.insert(tk.END, filename)
        
        if self.image_files and not self.original_image:
            self.file_listbox.selection_set(0)
            self.load_image(0)
        
        self.update_status()
    
    def clear_images(self):
        """清空图片列表"""
        self.image_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.original_image = None
        self.preview_image = None
        self.canvas.delete("all")
        self.update_status()
    
    def on_image_select(self, event):
        """图片列表选择事件"""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            self.load_image(index)
    
    def load_image(self, index):
        """加载指定索引的图片"""
        if 0 <= index < len(self.image_files):
            self.current_image_index = index
            image_path = self.image_files[index]
            
            try:
                self.original_image = Image.open(image_path)
                # 自动提取EXIF时间作为水印文本
                date_text = self.extract_date_from_exif(image_path)
                if date_text:
                    self.text_var.set(date_text)
                    self.watermark_settings['text'] = date_text
                
                self.update_preview()
                self.update_status()
            except Exception as e:
                messagebox.showerror("错误", f"无法加载图片: {e}")
    
    def extract_date_from_exif(self, image_path):
        """从EXIF信息中提取拍摄时间"""
        try:
            with Image.open(image_path) as img:
                exif = img._getexif()
                if exif:
                    for tag, value in exif.items():
                        tag_name = ExifTags.TAGS.get(tag, tag)
                        if tag_name in ['DateTime', 'DateTimeOriginal']:
                            try:
                                date_obj = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                                return date_obj.strftime("%Y-%m-%d")
                            except ValueError:
                                continue
        except:
            pass
        
        # 如果无法从EXIF获取，使用文件修改时间
        try:
            mtime = os.path.getmtime(image_path)
            date_obj = datetime.fromtimestamp(mtime)
            return date_obj.strftime("%Y-%m-%d")
        except:
            return "2024-01-01"
    
    def on_setting_change(self, event=None):
        """水印设置改变事件"""
        # 更新设置
        self.watermark_settings.update({
            'text': self.text_var.get(),
            'font_family': self.font_var.get(),
            'font_size': self.font_size_var.get(),
            'font_bold': self.bold_var.get(),
            'font_italic': self.italic_var.get(),
            'opacity': self.opacity_var.get(),
            'position': self.position_var.get(),
            'shadow': self.shadow_var.get()
        })
        
        # 更新预览
        self.update_preview()
    
    def choose_color(self):
        """选择颜色"""
        color = colorchooser.askcolor(initialcolor=self.watermark_settings['color'])
        if color[1]:  # color[1] 是十六进制颜色值
            self.watermark_settings['color'] = color[1]
            self.color_button.config(bg=color[1])
            self.update_preview()
    
    def update_preview(self):
        """更新预览图片"""
        if not self.original_image:
            return
        
        try:
            # 创建预览图片副本
            preview_img = self.original_image.copy()
            
            # 添加水印
            watermarked_img = self.add_watermark_to_image(preview_img)
            
            # 调整图片大小以适应画布
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:  # 确保画布已初始化
                img_width, img_height = watermarked_img.size
                
                # 计算缩放比例
                scale_w = canvas_width / img_width
                scale_h = canvas_height / img_height
                scale = min(scale_w, scale_h, 1.0)  # 不放大，只缩小
                
                if scale < 1.0:
                    new_width = int(img_width * scale)
                    new_height = int(img_height * scale)
                    watermarked_img = watermarked_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage并显示
            self.preview_image = ImageTk.PhotoImage(watermarked_img)
            
            self.canvas.delete("all")
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                x = (canvas_width - watermarked_img.width) // 2
                y = (canvas_height - watermarked_img.height) // 2
                self.canvas.create_image(x, y, anchor=tk.NW, image=self.preview_image)
            
        except Exception as e:
            print(f"预览更新错误: {e}")
    
    def add_watermark_to_image(self, image):
        """为图片添加水印"""
        # 创建图片副本
        img = image.copy()
        
        # 创建绘图对象
        draw = ImageDraw.Draw(img)
        
        # 获取字体
        try:
            font_path = self.get_font_path(self.watermark_settings['font_family'])
            font = ImageFont.truetype(font_path, self.watermark_settings['font_size'])
        except:
            font = ImageFont.load_default()
        
        # 获取文本尺寸
        text = self.watermark_settings['text']
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 计算位置
        img_width, img_height = img.size
        x, y = self.calculate_text_position(img_width, img_height, text_width, text_height)
        
        # 颜色和透明度
        color = self.watermark_settings['color']
        opacity = self.watermark_settings['opacity']
        
        # 转换颜色
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            text_color = (r, g, b, opacity)
        else:
            text_color = (255, 255, 255, opacity)
        
        # 创建透明图层
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # 添加阴影
        if self.watermark_settings['shadow']:
            shadow_offset = self.watermark_settings['shadow_offset']
            shadow_color = (0, 0, 0, opacity // 2)
            overlay_draw.text((x + shadow_offset, y + shadow_offset), text, 
                            font=font, fill=shadow_color)
        
        # 添加主文本
        overlay_draw.text((x, y), text, font=font, fill=text_color)
        
        # 合并图层
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        result = Image.alpha_composite(img, overlay)
        
        # 如果原图不是RGBA，转换回原格式
        if image.mode != 'RGBA':
            result = result.convert(image.mode)
        
        return result
    
    def get_font_path(self, font_family):
        """获取字体文件路径"""
        # 这里简化处理，实际应用中需要更复杂的字体查找逻辑
        import platform
        system = platform.system()
        
        if system == "Windows":
            font_dirs = [
                "C:/Windows/Fonts/",
                "C:/Windows/System32/Fonts/"
            ]
            font_files = {
                'Arial': 'arial.ttf',
                'Times New Roman': 'times.ttf',
                'Courier New': 'cour.ttf'
            }
        else:
            font_dirs = [
                "/System/Library/Fonts/",
                "/Library/Fonts/",
                "/usr/share/fonts/"
            ]
            font_files = {
                'Arial': 'Arial.ttf',
                'Times New Roman': 'Times New Roman.ttf',
                'Courier New': 'Courier New.ttf'
            }
        
        font_file = font_files.get(font_family, 'arial.ttf')
        
        for font_dir in font_dirs:
            font_path = os.path.join(font_dir, font_file)
            if os.path.exists(font_path):
                return font_path
        
        # 如果找不到，返回默认字体
        raise OSError("Font not found")
    
    def calculate_text_position(self, img_width, img_height, text_width, text_height):
        """计算文本位置"""
        position = self.watermark_settings['position']
        margin = 20  # 边距
        
        positions = {
            'top-left': (margin, margin),
            'top-center': ((img_width - text_width) // 2, margin),
            'top-right': (img_width - text_width - margin, margin),
            'center-left': (margin, (img_height - text_height) // 2),
            'center': ((img_width - text_width) // 2, (img_height - text_height) // 2),
            'center-right': (img_width - text_width - margin, (img_height - text_height) // 2),
            'bottom-left': (margin, img_height - text_height - margin),
            'bottom-center': ((img_width - text_width) // 2, img_height - text_height - margin),
            'bottom-right': (img_width - text_width - margin, img_height - text_height - margin)
        }
        
        return positions.get(position, positions['bottom-right'])
    
    def on_canvas_click(self, event):
        """画布点击事件"""
        # 这里可以实现拖拽水印位置的功能
        pass
    
    def on_canvas_drag(self, event):
        """画布拖拽事件"""
        # 这里可以实现拖拽水印位置的功能
        pass
    
    def export_images(self):
        """导出处理后的图片"""
        if not self.image_files:
            messagebox.showwarning("警告", "请先导入图片文件")
            return
        
        # 选择输出目录
        output_dir = filedialog.askdirectory(title="选择输出目录")
        if not output_dir:
            return
        
        # 检查是否选择了原目录
        for img_file in self.image_files:
            if os.path.dirname(img_file) == output_dir:
                if not messagebox.askyesno("警告", "输出目录与原图片目录相同，可能会覆盖原文件。是否继续？"):
                    return
                break
        
        # 创建进度窗口
        progress_window = tk.Toplevel(self.root)
        progress_window.title("导出进度")
        progress_window.geometry("400x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text="正在导出图片...").pack(pady=10)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=len(self.image_files))
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        
        status_label = ttk.Label(progress_window, text="")
        status_label.pack(pady=5)
        
        # 在后台线程中处理导出
        def export_thread():
            success_count = 0
            total_count = len(self.image_files)
            
            for i, img_file in enumerate(self.image_files):
                try:
                    # 更新进度
                    filename = os.path.basename(img_file)
                    self.root.after(0, lambda f=filename: status_label.config(text=f"处理: {f}"))
                    
                    # 加载和处理图片
                    with Image.open(img_file) as img:
                        # 提取日期并更新水印文本
                        date_text = self.extract_date_from_exif(img_file)
                        current_settings = self.watermark_settings.copy()
                        current_settings['text'] = date_text
                        
                        # 添加水印
                        watermarked_img = self.add_watermark_to_image_with_settings(img, current_settings)
                        
                        # 生成输出文件名
                        output_filename = self.generate_output_filename(filename)
                        output_path = os.path.join(output_dir, output_filename)
                        
                        # 保存图片
                        output_format = self.output_format_var.get()
                        if output_format == 'JPEG':
                            if watermarked_img.mode in ('RGBA', 'LA'):
                                watermarked_img = watermarked_img.convert('RGB')
                            watermarked_img.save(output_path, 'JPEG', quality=95)
                        else:
                            watermarked_img.save(output_path, 'PNG')
                        
                        success_count += 1
                    
                except Exception as e:
                    print(f"处理文件 {img_file} 时出错: {e}")
                
                # 更新进度条
                self.root.after(0, lambda i=i+1: progress_var.set(i))
            
            # 完成后关闭进度窗口并显示结果
            self.root.after(0, lambda: self.export_complete(progress_window, success_count, total_count, output_dir))
        
        # 启动导出线程
        threading.Thread(target=export_thread, daemon=True).start()
    
    def add_watermark_to_image_with_settings(self, image, settings):
        """使用指定设置为图片添加水印"""
        # 临时保存当前设置
        original_settings = self.watermark_settings.copy()
        
        # 应用新设置
        self.watermark_settings = settings
        
        # 添加水印
        result = self.add_watermark_to_image(image)
        
        # 恢复原设置
        self.watermark_settings = original_settings
        
        return result
    
    def generate_output_filename(self, original_filename):
        """生成输出文件名"""
        name, ext = os.path.splitext(original_filename)
        naming_rule = self.naming_var.get()
        custom_text = self.custom_text_var.get()
        output_format = self.output_format_var.get()
        
        # 确定输出扩展名
        if output_format == 'JPEG':
            new_ext = '.jpg'
        else:
            new_ext = '.png'
        
        if naming_rule == 'original':
            return name + new_ext
        elif naming_rule == 'prefix':
            return custom_text + name + new_ext
        else:  # suffix
            return name + custom_text + new_ext
    
    def export_complete(self, progress_window, success_count, total_count, output_dir):
        """导出完成处理"""
        progress_window.destroy()
        
        if success_count == total_count:
            messagebox.showinfo("完成", f"成功导出 {success_count} 个文件到:\n{output_dir}")
        else:
            messagebox.showwarning("完成", f"导出完成，成功 {success_count}/{total_count} 个文件\n输出目录: {output_dir}")
    
    def update_status(self):
        """更新状态栏"""
        if not self.image_files:
            self.status_var.set("请导入图片文件")
        else:
            current = self.current_image_index + 1 if self.image_files else 0
            total = len(self.image_files)
            self.status_var.set(f"图片 {current}/{total}")
    
    def load_last_settings(self):
        """加载上次的设置"""
        try:
            settings_file = "watermark_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    self.watermark_settings.update(saved_settings)
                    self.apply_loaded_settings()
        except Exception as e:
            print(f"加载设置失败: {e}")
    
    def save_settings(self):
        """保存当前设置"""
        try:
            settings_file = "watermark_settings.json"
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.watermark_settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def apply_loaded_settings(self):
        """应用加载的设置到界面"""
        self.text_var.set(self.watermark_settings['text'])
        self.font_var.set(self.watermark_settings['font_family'])
        self.font_size_var.set(self.watermark_settings['font_size'])
        self.bold_var.set(self.watermark_settings['font_bold'])
        self.italic_var.set(self.watermark_settings['font_italic'])
        self.opacity_var.set(self.watermark_settings['opacity'])
        self.position_var.set(self.watermark_settings['position'])
        self.shadow_var.set(self.watermark_settings['shadow'])
        
        # 更新颜色按钮
        self.color_button.config(bg=self.watermark_settings['color'])
    
    def refresh_template_list(self):
        """刷新模板列表"""
        templates_dir = Path("templates")
        if not templates_dir.exists():
            templates_dir.mkdir()
        
        template_files = list(templates_dir.glob("*.json"))
        template_names = [f.stem for f in template_files]
        
        self.template_combo['values'] = template_names
        if template_names and not self.template_var.get():
            self.template_var.set(template_names[0])
    
    def save_template(self):
        """保存当前设置为模板"""
        template_name = tk.simpledialog.askstring("保存模板", "请输入模板名称:")
        if not template_name:
            return
        
        # 清理文件名
        template_name = "".join(c for c in template_name if c.isalnum() or c in (' ', '-', '_')).strip()
        if not template_name:
            messagebox.showerror("错误", "模板名称无效")
            return
        
        templates_dir = Path("templates")
        if not templates_dir.exists():
            templates_dir.mkdir()
        
        template_file = templates_dir / f"{template_name}.json"
        
        try:
            # 保存当前设置（不包括文本内容）
            template_settings = self.watermark_settings.copy()
            template_settings['text'] = ''  # 不保存具体文本内容
            
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_settings, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("成功", f"模板 '{template_name}' 已保存")
            self.refresh_template_list()
            self.template_var.set(template_name)
            
        except Exception as e:
            messagebox.showerror("错误", f"保存模板失败: {e}")
    
    def load_template(self, event=None):
        """加载选中的模板"""
        template_name = self.template_var.get()
        if not template_name:
            return
        
        template_file = Path("templates") / f"{template_name}.json"
        if not template_file.exists():
            messagebox.showerror("错误", f"模板文件不存在: {template_name}")
            return
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_settings = json.load(f)
            
            # 保留当前的文本内容
            current_text = self.watermark_settings['text']
            
            # 应用模板设置
            self.watermark_settings.update(template_settings)
            self.watermark_settings['text'] = current_text  # 恢复文本内容
            
            # 更新界面
            self.apply_loaded_settings()
            self.update_preview()
            
            messagebox.showinfo("成功", f"已加载模板 '{template_name}'")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载模板失败: {e}")
    
    def delete_template(self):
        """删除选中的模板"""
        template_name = self.template_var.get()
        if not template_name:
            messagebox.showwarning("警告", "请先选择要删除的模板")
            return
        
        if not messagebox.askyesno("确认", f"确定要删除模板 '{template_name}' 吗？"):
            return
        
        template_file = Path("templates") / f"{template_name}.json"
        
        try:
            if template_file.exists():
                template_file.unlink()
                messagebox.showinfo("成功", f"模板 '{template_name}' 已删除")
                self.refresh_template_list()
                self.template_var.set('')
            else:
                messagebox.showerror("错误", "模板文件不存在")
                
        except Exception as e:
            messagebox.showerror("错误", f"删除模板失败: {e}")
    
    def on_closing(self):
        """程序关闭时的处理"""
        self.save_settings()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = WatermarkApp(root)
    
    # 绑定关闭事件
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()