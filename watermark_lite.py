#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轻量级图片水印GUI应用程序
专为小文件大小优化
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog
import os
import json
from pathlib import Path
from datetime import datetime
import threading

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont, ExifTags
except ImportError:
    messagebox.showerror("错误", "请安装Pillow库: pip install Pillow")
    exit(1)


class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片水印工具 v2.0")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 应用程序状态
        self.image_files = []
        self.current_image_index = 0
        self.original_image = None
        self.preview_image = None
        self.watermark_settings = {
            'text': '2024-01-01',
            'font_size': 36,
            'color': '#FFFFFF',
            'opacity': 128,
            'position': 'bottom-right',
            'shadow': True
        }
        
        self.create_widgets()
        self.load_settings()
        
    def create_widgets(self):
        """创建界面"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧文件操作面板
        left_panel = ttk.Frame(main_frame, width=280)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # 右侧面板（预览+设置）
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 右侧上部：预览区域
        preview_panel = ttk.Frame(right_panel)
        preview_panel.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 右侧下部：水印设置区域
        settings_panel = ttk.Frame(right_panel)
        settings_panel.pack(fill=tk.X)
        
        self.create_left_panel(left_panel)
        self.create_preview_panel(preview_panel)
        self.create_settings_panel(settings_panel)
        
    def create_left_panel(self, parent):
        """创建左侧文件操作面板"""
        # 文件操作
        file_frame = ttk.LabelFrame(parent, text="文件操作", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(file_frame, text="导入图片", command=self.import_images).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="导入文件夹", command=self.import_folder).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="清空列表", command=self.clear_images).pack(fill=tk.X, pady=2)
        
        # 文件列表
        list_frame = ttk.LabelFrame(parent, text="图片列表", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox.bind('<<ListboxSelect>>', self.on_image_select)
        
        # 模板管理
        template_frame = ttk.LabelFrame(parent, text="模板管理", padding=10)
        template_frame.pack(fill=tk.X, pady=(0, 10))
        
        template_btn_frame = ttk.Frame(template_frame)
        template_btn_frame.pack(fill=tk.X)
        ttk.Button(template_btn_frame, text="保存模板", command=self.save_template).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        ttk.Button(template_btn_frame, text="加载模板", command=self.load_template).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))
        
        # 导出设置
        export_frame = ttk.LabelFrame(parent, text="导出设置", padding=10)
        export_frame.pack(fill=tk.X)
        
        # 输出格式
        format_frame = ttk.Frame(export_frame)
        format_frame.pack(fill=tk.X, pady=(0, 5))
        self.output_format_var = tk.StringVar(value="PNG")
        ttk.Radiobutton(format_frame, text="PNG", variable=self.output_format_var, value="PNG").pack(side=tk.LEFT)
        ttk.Radiobutton(format_frame, text="JPEG", variable=self.output_format_var, value="JPEG").pack(side=tk.LEFT, padx=(20, 0))
        
        ttk.Button(export_frame, text="选择输出目录并导出", command=self.export_images).pack(fill=tk.X, pady=5)
        
    def create_preview_panel(self, parent):
        """创建预览面板"""
        preview_frame = ttk.LabelFrame(parent, text="预览", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(preview_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_var = tk.StringVar(value="请导入图片文件")
        ttk.Label(preview_frame, textvariable=self.status_var).pack(pady=(10, 0))
    
    def create_settings_panel(self, parent):
        """创建水印设置面板"""
        # 创建一个可滚动的框架来容纳所有设置
        canvas = tk.Canvas(parent, height=200)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 水印设置内容
        settings_frame = ttk.LabelFrame(scrollable_frame, text="水印设置", padding=10)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建三列布局
        col1 = ttk.Frame(settings_frame)
        col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        col2 = ttk.Frame(settings_frame)
        col2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        col3 = ttk.Frame(settings_frame)
        col3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 第一列：文本和字体
        ttk.Label(col1, text="水印文本:").pack(anchor=tk.W)
        self.text_var = tk.StringVar(value=self.watermark_settings['text'])
        text_entry = ttk.Entry(col1, textvariable=self.text_var)
        text_entry.pack(fill=tk.X, pady=(0, 10))
        text_entry.bind('<KeyRelease>', self.on_setting_change)
        
        # 字体大小
        size_frame = ttk.Frame(col1)
        size_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(size_frame, text="字体大小:").pack(anchor=tk.W)
        self.font_size_var = tk.IntVar(value=self.watermark_settings['font_size'])
        size_spin = ttk.Spinbox(size_frame, from_=12, to=100, width=8, textvariable=self.font_size_var)
        size_spin.pack(fill=tk.X, pady=2)
        size_spin.bind('<KeyRelease>', self.on_setting_change)
        
        # 第二列：颜色和透明度
        color_frame = ttk.Frame(col2)
        color_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(color_frame, text="颜色:").pack(anchor=tk.W)
        self.color_button = tk.Button(color_frame, text="选择颜色", bg=self.watermark_settings['color'], 
                                     command=self.choose_color)
        self.color_button.pack(fill=tk.X, pady=2)
        
        # 透明度
        opacity_frame = ttk.Frame(col2)
        opacity_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(opacity_frame, text="透明度:").pack(anchor=tk.W)
        self.opacity_var = tk.IntVar(value=self.watermark_settings['opacity'])
        opacity_scale = ttk.Scale(opacity_frame, from_=50, to=255, orient=tk.HORIZONTAL, 
                                 variable=self.opacity_var, command=self.on_setting_change)
        opacity_scale.pack(fill=tk.X, pady=2)
        
        # 第三列：位置和选项
        ttk.Label(col3, text="位置:").pack(anchor=tk.W)
        self.position_var = tk.StringVar(value=self.watermark_settings['position'])
        positions = [
            ('左上', 'top-left'), ('右上', 'top-right'),
            ('左下', 'bottom-left'), ('右下', 'bottom-right'),
            ('居中', 'center')
        ]
        
        for text, value in positions:
            ttk.Radiobutton(col3, text=text, variable=self.position_var, 
                           value=value, command=self.on_setting_change).pack(anchor=tk.W)
        
        # 阴影选项
        self.shadow_var = tk.BooleanVar(value=self.watermark_settings['shadow'])
        ttk.Checkbutton(col3, text="添加阴影", variable=self.shadow_var, 
                       command=self.on_setting_change).pack(anchor=tk.W, pady=(10, 0))
        
        # 打包滚动组件
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def import_images(self):
        """导入图片"""
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[('图片文件', '*.jpg *.jpeg *.png *.bmp'), ('所有文件', '*.*')]
        )
        if files:
            self.add_images(files)
    
    def import_folder(self):
        """导入文件夹"""
        folder = filedialog.askdirectory(title="选择图片文件夹")
        if folder:
            files = []
            for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                files.extend(Path(folder).glob(f'*{ext}'))
                files.extend(Path(folder).glob(f'*{ext.upper()}'))
            
            if files:
                self.add_images([str(f) for f in files])
            else:
                messagebox.showinfo("提示", "文件夹中没有找到图片文件")
    
    def add_images(self, files):
        """添加图片到列表"""
        for file in files:
            if file not in self.image_files:
                self.image_files.append(file)
                self.file_listbox.insert(tk.END, os.path.basename(file))
        
        if self.image_files and not self.original_image:
            self.file_listbox.selection_set(0)
            self.load_image(0)
        
        self.update_status()
    
    def clear_images(self):
        """清空列表"""
        self.image_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.original_image = None
        self.canvas.delete("all")
        self.update_status()
    
    def on_image_select(self, event):
        """图片选择事件"""
        selection = self.file_listbox.curselection()
        if selection:
            self.load_image(selection[0])
    
    def load_image(self, index):
        """加载图片"""
        if 0 <= index < len(self.image_files):
            self.current_image_index = index
            try:
                self.original_image = Image.open(self.image_files[index])
                # 提取日期
                date_text = self.extract_date(self.image_files[index])
                self.text_var.set(date_text)
                self.watermark_settings['text'] = date_text
                self.update_preview()
            except Exception as e:
                messagebox.showerror("错误", f"无法加载图片: {e}")
    
    def extract_date(self, image_path):
        """提取日期"""
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
                            except:
                                continue
        except:
            pass
        
        # 使用文件时间
        try:
            mtime = os.path.getmtime(image_path)
            return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        except:
            return "2024-01-01"
    
    def on_setting_change(self, event=None):
        """设置改变"""
        self.watermark_settings.update({
            'text': self.text_var.get(),
            'font_size': self.font_size_var.get(),
            'opacity': self.opacity_var.get(),
            'position': self.position_var.get(),
            'shadow': self.shadow_var.get()
        })
        self.update_preview()
    
    def choose_color(self):
        """选择颜色"""
        color = colorchooser.askcolor(initialcolor=self.watermark_settings['color'])
        if color[1]:
            self.watermark_settings['color'] = color[1]
            self.color_button.config(bg=color[1])
            self.update_preview()
    
    def update_preview(self):
        """更新预览"""
        if not self.original_image:
            return
        
        try:
            # 添加水印
            watermarked = self.add_watermark(self.original_image.copy())
            
            # 调整大小适应画布
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                img_w, img_h = watermarked.size
                scale = min(canvas_width / img_w, canvas_height / img_h, 1.0)
                
                if scale < 1.0:
                    new_w = int(img_w * scale)
                    new_h = int(img_h * scale)
                    watermarked = watermarked.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # 显示
            self.preview_image = ImageTk.PhotoImage(watermarked)
            self.canvas.delete("all")
            
            if canvas_width > 1:
                x = (canvas_width - watermarked.width) // 2
                y = (canvas_height - watermarked.height) // 2
                self.canvas.create_image(x, y, anchor=tk.NW, image=self.preview_image)
        except Exception as e:
            print(f"预览错误: {e}")
    
    def add_watermark(self, image):
        """添加水印"""
        draw = ImageDraw.Draw(image)
        
        # 使用默认字体
        try:
            font = ImageFont.truetype("arial.ttf", self.watermark_settings['font_size'])
        except:
            font = ImageFont.load_default()
        
        text = self.watermark_settings['text']
        
        # 计算位置
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        img_w, img_h = image.size
        margin = 20
        
        positions = {
            'top-left': (margin, margin),
            'top-right': (img_w - text_w - margin, margin),
            'bottom-left': (margin, img_h - text_h - margin),
            'bottom-right': (img_w - text_w - margin, img_h - text_h - margin),
            'center': ((img_w - text_w) // 2, (img_h - text_h) // 2)
        }
        
        x, y = positions.get(self.watermark_settings['position'], positions['bottom-right'])
        
        # 颜色
        color = self.watermark_settings['color']
        opacity = self.watermark_settings['opacity']
        
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            text_color = (r, g, b, opacity)
        else:
            text_color = (255, 255, 255, opacity)
        
        # 创建透明层
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # 阴影
        if self.watermark_settings['shadow']:
            shadow_color = (0, 0, 0, opacity // 2)
            overlay_draw.text((x + 2, y + 2), text, font=font, fill=shadow_color)
        
        # 主文本
        overlay_draw.text((x, y), text, font=font, fill=text_color)
        
        # 合并
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        result = Image.alpha_composite(image, overlay)
        return result.convert('RGB') if image.mode != 'RGBA' else result
    
    def save_template(self):
        """保存模板"""
        name = simpledialog.askstring("保存模板", "模板名称:")
        if name:
            try:
                templates_dir = Path("templates")
                templates_dir.mkdir(exist_ok=True)
                
                template_file = templates_dir / f"{name}.json"
                settings = self.watermark_settings.copy()
                settings['text'] = ''  # 不保存文本
                
                with open(template_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("成功", f"模板 '{name}' 已保存")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}")
    
    def load_template(self):
        """加载模板"""
        templates_dir = Path("templates")
        if not templates_dir.exists():
            messagebox.showinfo("提示", "没有找到模板文件")
            return
        
        template_files = list(templates_dir.glob("*.json"))
        if not template_files:
            messagebox.showinfo("提示", "没有找到模板文件")
            return
        
        # 简单的选择对话框
        template_names = [f.stem for f in template_files]
        
        # 创建选择窗口
        dialog = tk.Toplevel(self.root)
        dialog.title("选择模板")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="选择要加载的模板:").pack(pady=10)
        
        listbox = tk.Listbox(dialog)
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for name in template_names:
            listbox.insert(tk.END, name)
        
        def load_selected():
            selection = listbox.curselection()
            if selection:
                template_name = template_names[selection[0]]
                template_file = templates_dir / f"{template_name}.json"
                
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                    
                    current_text = self.watermark_settings['text']
                    self.watermark_settings.update(settings)
                    self.watermark_settings['text'] = current_text
                    
                    # 更新界面
                    self.text_var.set(self.watermark_settings['text'])
                    self.font_size_var.set(self.watermark_settings['font_size'])
                    self.opacity_var.set(self.watermark_settings['opacity'])
                    self.position_var.set(self.watermark_settings['position'])
                    self.shadow_var.set(self.watermark_settings['shadow'])
                    self.color_button.config(bg=self.watermark_settings['color'])
                    
                    self.update_preview()
                    dialog.destroy()
                    messagebox.showinfo("成功", f"已加载模板 '{template_name}'")
                    
                except Exception as e:
                    messagebox.showerror("错误", f"加载失败: {e}")
        
        ttk.Button(dialog, text="加载", command=load_selected).pack(pady=10)
    
    def export_images(self):
        """导出图片"""
        if not self.image_files:
            messagebox.showwarning("警告", "请先导入图片")
            return
        
        output_dir = filedialog.askdirectory(title="选择输出目录")
        if not output_dir:
            return
        
        # 进度窗口
        progress = tk.Toplevel(self.root)
        progress.title("导出进度")
        progress.geometry("400x100")
        progress.transient(self.root)
        progress.grab_set()
        
        ttk.Label(progress, text="正在导出...").pack(pady=10)
        progress_bar = ttk.Progressbar(progress, maximum=len(self.image_files))
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        
        def export_thread():
            success = 0
            for i, img_file in enumerate(self.image_files):
                try:
                    with Image.open(img_file) as img:
                        # 提取日期并添加水印
                        date_text = self.extract_date(img_file)
                        current_settings = self.watermark_settings.copy()
                        current_settings['text'] = date_text
                        
                        # 临时更新设置
                        original_settings = self.watermark_settings.copy()
                        self.watermark_settings = current_settings
                        
                        watermarked = self.add_watermark(img.copy())
                        
                        # 恢复设置
                        self.watermark_settings = original_settings
                        
                        # 保存
                        filename = os.path.basename(img_file)
                        name, ext = os.path.splitext(filename)
                        
                        if self.output_format_var.get() == 'JPEG':
                            output_path = os.path.join(output_dir, f"{name}_watermarked.jpg")
                            if watermarked.mode in ('RGBA', 'LA'):
                                watermarked = watermarked.convert('RGB')
                            watermarked.save(output_path, 'JPEG', quality=95)
                        else:
                            output_path = os.path.join(output_dir, f"{name}_watermarked.png")
                            watermarked.save(output_path, 'PNG')
                        
                        success += 1
                
                except Exception as e:
                    print(f"处理 {img_file} 失败: {e}")
                
                # 更新进度
                self.root.after(0, lambda i=i+1: progress_bar.config(value=i))
            
            # 完成
            self.root.after(0, lambda: self.export_complete(progress, success, len(self.image_files), output_dir))
        
        threading.Thread(target=export_thread, daemon=True).start()
    
    def export_complete(self, progress_window, success, total, output_dir):
        """导出完成"""
        progress_window.destroy()
        messagebox.showinfo("完成", f"成功导出 {success}/{total} 个文件\n输出目录: {output_dir}")
    
    def update_status(self):
        """更新状态"""
        if not self.image_files:
            self.status_var.set("请导入图片文件")
        else:
            current = self.current_image_index + 1
            total = len(self.image_files)
            self.status_var.set(f"图片 {current}/{total}")
    
    def load_settings(self):
        """加载设置"""
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self.watermark_settings.update(saved)
        except:
            pass
    
    def save_settings(self):
        """保存设置"""
        try:
            with open("settings.json", 'w', encoding='utf-8') as f:
                json.dump(self.watermark_settings, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def on_closing(self):
        """关闭处理"""
        self.save_settings()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = WatermarkApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()