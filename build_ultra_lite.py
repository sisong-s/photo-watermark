#!/usr/bin/env python3
"""
超轻量版exe构建脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def create_ultra_lite_app():
    """创建超轻量版本的应用程序"""
    lite_content = '''import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import json

class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片水印工具 v1.0.0")
        self.root.geometry("1000x700")
        self.root.minsize(800, 500)
        
        self.images = []
        self.current_image_index = 0
        self.current_image = None
        self.preview_image = None
        self.watermark_settings = {
            'text': '水印文本',
            'font_size': 36,
            'color': '#FFFFFF',
            'opacity': 128,
            'position': 'center',
            'x_offset': 0,
            'y_offset': 0
        }
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左栏
        left_frame = ttk.LabelFrame(main_frame, text="图片列表", width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_frame.pack_propagate(False)
        
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="导入图片", command=self.import_images).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="清空列表", command=self.clear_images).pack(fill=tk.X, pady=2)
        
        # 输出设置
        ttk.Label(btn_frame, text="输出格式:").pack(anchor=tk.W, pady=(10,2))
        self.output_format = tk.StringVar(value="PNG")
        ttk.Combobox(btn_frame, textvariable=self.output_format, 
                    values=["PNG", "JPEG"], state="readonly").pack(fill=tk.X, pady=2)
        
        ttk.Label(btn_frame, text="文件命名:").pack(anchor=tk.W, pady=(5,2))
        self.naming_text = tk.StringVar(value="_watermarked")
        ttk.Entry(btn_frame, textvariable=self.naming_text).pack(fill=tk.X, pady=2)
        
        ttk.Button(btn_frame, text="导出当前图片", command=self.export_current).pack(fill=tk.X, pady=5)
        
        # 图片列表
        self.image_listbox = tk.Listbox(left_frame)
        self.image_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.image_listbox.bind('<<ListboxSelect>>', self.on_image_select)
        
        # 中栏 - 预览
        center_frame = ttk.LabelFrame(main_frame, text="预览")
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.canvas = tk.Canvas(center_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 右栏 - 设置
        right_frame = ttk.LabelFrame(main_frame, text="水印设置", width=250)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_frame.pack_propagate(False)
        
        # 文本设置
        ttk.Label(right_frame, text="水印文本:").pack(anchor=tk.W, padx=5, pady=2)
        self.text_var = tk.StringVar(value=self.watermark_settings['text'])
        text_entry = ttk.Entry(right_frame, textvariable=self.text_var)
        text_entry.pack(fill=tk.X, padx=5, pady=2)
        text_entry.bind('<KeyRelease>', self.on_text_change)
        
        # 字体大小
        ttk.Label(right_frame, text="字体大小:").pack(anchor=tk.W, padx=5, pady=2)
        self.font_size_var = tk.IntVar(value=self.watermark_settings['font_size'])
        ttk.Scale(right_frame, from_=12, to=100, variable=self.font_size_var, 
                 orient=tk.HORIZONTAL, command=self.on_setting_change).pack(fill=tk.X, padx=5, pady=2)
        
        # 颜色
        color_frame = ttk.Frame(right_frame)
        color_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(color_frame, text="颜色:").pack(side=tk.LEFT)
        self.color_button = tk.Button(color_frame, text="选择", bg=self.watermark_settings['color'],
                                     command=self.choose_color, width=8)
        self.color_button.pack(side=tk.RIGHT)
        
        # 透明度
        ttk.Label(right_frame, text="透明度:").pack(anchor=tk.W, padx=5, pady=2)
        self.opacity_var = tk.IntVar(value=self.watermark_settings['opacity'])
        ttk.Scale(right_frame, from_=0, to=255, variable=self.opacity_var,
                 orient=tk.HORIZONTAL, command=self.on_setting_change).pack(fill=tk.X, padx=5, pady=2)
        
        # 位置按钮
        ttk.Label(right_frame, text="位置:").pack(anchor=tk.W, padx=5, pady=(10,2))
        pos_frame = ttk.Frame(right_frame)
        pos_frame.pack(fill=tk.X, padx=5, pady=2)
        
        positions = [
            ('左上', 'top_left'), ('中上', 'top_center'), ('右上', 'top_right'),
            ('左中', 'middle_left'), ('中心', 'center'), ('右中', 'middle_right'),
            ('左下', 'bottom_left'), ('中下', 'bottom_center'), ('右下', 'bottom_right')
        ]
        
        for i, (text, pos) in enumerate(positions):
            row, col = divmod(i, 3)
            btn = ttk.Button(pos_frame, text=text, width=4,
                           command=lambda p=pos: self.set_position(p))
            btn.grid(row=row, column=col, padx=1, pady=1)
        
    def import_images(self):
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")]
        )
        for file_path in files:
            self.add_image(file_path)
            
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
            messagebox.showerror("错误", f"无法加载图片: {str(e)}")
            
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
            self.current_image = Image.open(image_path)
            self.update_preview()
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片: {str(e)}")
            
    def update_preview(self):
        if not self.current_image:
            return
        try:
            watermarked_image = self.apply_watermark(self.current_image.copy())
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                self.root.after(100, self.update_preview)
                return
                
            img_width, img_height = watermarked_image.size
            scale = min(canvas_width / img_width, canvas_height / img_height, 1.0)
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            display_image = watermarked_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.preview_image = ImageTk.PhotoImage(display_image)
            
            self.canvas.delete("all")
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.preview_image)
        except:
            pass
            
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
            font = ImageFont.load_default()
        except:
            font = None
        
        if font:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width = len(text) * font_size // 2
            text_height = font_size
        
        x, y = self.calculate_watermark_position(image.size, text_width, text_height)
        
        if color.startswith('#'):
            color = color[1:]
        try:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            text_color = (r, g, b, opacity)
        except:
            text_color = (255, 255, 255, opacity)
        
        draw.text((x, y), text, font=font, fill=text_color)
        result = Image.alpha_composite(image, watermark_layer)
        return result
        
    def calculate_watermark_position(self, image_size, text_width, text_height):
        img_width, img_height = image_size
        position = self.watermark_settings['position']
        
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
        
        x, y = positions.get(position, positions['center'])
        return max(0, min(x, img_width - text_width)), max(0, min(y, img_height - text_height))
        
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
    
    def export_current(self):
        if not self.current_image:
            messagebox.showwarning("警告", "请先选择一张图片")
            return
        output_dir = filedialog.askdirectory(title="选择输出文件夹")
        if not output_dir:
            return
        try:
            watermarked_image = self.apply_watermark(self.current_image.copy())
            original_name = os.path.splitext(self.images[self.current_image_index]['name'])[0]
            new_name = f"{original_name}{self.naming_text.get()}"
            
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
                
            messagebox.showinfo("成功", "图片导出成功!")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")

def main():
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
'''
    
    with open('watermark_lite.py', 'w', encoding='utf-8') as f:
        f.write(lite_content)
    
    print("✓ 创建超轻量版本应用程序")

def build_ultra_lite_exe():
    """构建超轻量exe"""
    print("开始构建超轻量exe文件...")
    
    try:
        # 清理之前的构建
        import shutil
        for dir_name in ["build", "dist"]:
            if Path(dir_name).exists():
                shutil.rmtree(dir_name)
        
        # 使用最精简的构建参数
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name=WatermarkLite",
            "--optimize=2",
            "--strip",
            # 排除大量不需要的模块
            "--exclude-module=urllib",
            "--exclude-module=urllib3", 
            "--exclude-module=requests",
            "--exclude-module=certifi",
            "--exclude-module=charset_normalizer",
            "--exclude-module=idna",
            "--exclude-module=email",
            "--exclude-module=html",
            "--exclude-module=http",
            "--exclude-module=xml",
            "--exclude-module=xmlrpc",
            "--exclude-module=unittest",
            "--exclude-module=test",
            "--exclude-module=tests",
            "--exclude-module=distutils",
            "--exclude-module=setuptools",
            "--exclude-module=pip",
            "--exclude-module=wheel",
            "--exclude-module=pkg_resources",
            "--exclude-module=multiprocessing",
            "--exclude-module=concurrent",
            "--exclude-module=asyncio",
            "--exclude-module=socket",
            "--exclude-module=ssl",
            "--exclude-module=hashlib",
            "--exclude-module=hmac",
            "--exclude-module=base64",
            "--exclude-module=binascii",
            "--exclude-module=sqlite3",
            "--exclude-module=csv",
            "--exclude-module=datetime",
            "--exclude-module=calendar",
            "--exclude-module=locale",
            "--exclude-module=gettext",
            "--exclude-module=doctest",
            "--exclude-module=pdb",
            "--exclude-module=profile",
            "--exclude-module=pstats",
            "--exclude-module=timeit",
            "--exclude-module=trace",
            "--exclude-module=traceback",
            "--exclude-module=warnings",
            "--exclude-module=weakref",
            "--exclude-module=gc",
            "--exclude-module=ctypes",
            "--exclude-module=struct",
            "--exclude-module=array",
            "--exclude-module=collections",
            "--exclude-module=heapq",
            "--exclude-module=bisect",
            "--exclude-module=random",
            "--exclude-module=statistics",
            "--exclude-module=decimal",
            "--exclude-module=fractions",
            "--exclude-module=math",
            "--exclude-module=cmath",
            "--exclude-module=numbers",
            "watermark_lite.py"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ 超轻量exe构建成功")
            return True
        else:
            print(f"✗ 构建失败: {result.stderr}")
            # 尝试更简单的构建方式
            print("尝试简化构建...")
            simple_cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--windowed",
                "--name=WatermarkLite",
                "watermark_lite.py"
            ]
            result2 = subprocess.run(simple_cmd, capture_output=True, text=True)
            if result2.returncode == 0:
                print("✓ 简化构建成功")
                return True
            else:
                print(f"✗ 简化构建也失败: {result2.stderr}")
                return False
            
    except Exception as e:
        print(f"✗ 构建过程出错: {e}")
        return False

def main():
    """主函数"""
    print("=== 超轻量版 exe 构建脚本 ===\n")
    
    # 创建超轻量应用
    create_ultra_lite_app()
    
    # 构建exe
    if not build_ultra_lite_exe():
        return False
    
    # 检查文件大小
    exe_path = Path("dist/WatermarkLite.exe")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"exe文件大小: {size_mb:.2f} MB")
        
        if size_mb < 50:
            print("✅ 文件大小符合要求")
        else:
            print("⚠️ 文件大小仍然超过50MB")
    
    print("\n=== 构建完成 ===")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n构建失败")
        sys.exit(1)
    else:
        print("\n构建成功！")