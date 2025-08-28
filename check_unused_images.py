#!/usr/bin/env python3
import os
import re
from pathlib import Path

def find_image_files(assets_dir):
    """找到assets目錄中的所有圖片文件"""
    image_extensions = {'.jpeg', '.jpg', '.png', '.JPG', '.JPEG', '.PNG'}
    image_files = set()
    
    for file_path in Path(assets_dir).rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.add(file_path.name)
    
    return image_files

def find_used_images(content_dir):
    """在markdown文件中找到所有被引用的圖片"""
    used_images = set()
    
    # 搜索所有markdown文件
    for file_path in Path(content_dir).rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 查找圖片引用模式
                patterns = [
                    r'src="([^"]+\.(?:jpeg|jpg|png|JPG|JPEG|PNG))"',
                    r'!\[.*?\]\(([^)]+\.(?:jpeg|jpg|png|JPG|JPEG|PNG))\)',
                    r'{% include custom-nav-links\.html src="([^"]+\.(?:jpeg|jpg|png|JPG|JPEG|PNG))"',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # 提取文件名
                        filename = os.path.basename(match)
                        used_images.add(filename)
                        
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return used_images

def main():
    assets_dir = 'assets'
    content_dir = '.'
    
    print("正在掃描圖片文件...")
    all_images = find_image_files(assets_dir)
    print(f"找到 {len(all_images)} 個圖片文件")
    
    print("正在檢查使用情況...")
    used_images = find_used_images(content_dir)
    print(f"找到 {len(used_images)} 個被使用的圖片")
    
    unused_images = all_images - used_images
    
    print(f"\n未使用的圖片文件 ({len(unused_images)} 個):")
    print("=" * 50)
    
    if unused_images:
        for img in sorted(unused_images):
            print(f"- {img}")
    else:
        print("所有圖片都被使用了！")
    
    print(f"\n使用統計:")
    print(f"總圖片數: {len(all_images)}")
    print(f"已使用: {len(used_images)}")
    print(f"未使用: {len(unused_images)}")
    print(f"使用率: {len(used_images)/len(all_images)*100:.1f}%" if all_images else "0%")

if __name__ == "__main__":
    main()
