#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


def process_pdf_with_mineru(input_path: str, output_dir: str) -> None:
    """调用MinerU处理单个PDF文件，输出Markdown"""
    try:
        # 构建输出路径（保持原目录结构）
        rel_path = os.path.relpath(os.path.dirname(input_path), os.path.dirname(input_path))
        output_subdir = os.path.join(output_dir, rel_path)
        os.makedirs(output_subdir, exist_ok=True)

        # 生成输出文件名（同名的.md文件）
        output_file = os.path.join(output_subdir, f"{Path(input_path).stem}.md")

        # 调用MinerU命令（示例：转换为Markdown）
        cmd = [
            "mineru", "convert",
            "--input", input_path,
            "--output", output_file,
            "--format", "markdown"
        ]

        # 执行命令并捕获错误
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=300  # 设置5分钟超时
        )
        print(f"✅ 成功处理: {input_path} -> {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"❌ 处理失败（命令错误）: {input_path}\n错误详情: {e.stderr}")
    except subprocess.TimeoutExpired:
        print(f"⏱️ 处理超时: {input_path}")
    except Exception as e:
        print(f"⚠️ 未知错误: {input_path}\n错误类型: {type(e).__name__}, 详情: {str(e)}")


def find_pdfs(root_dir: str) -> list:
    """递归查找所有PDF文件"""
    pdf_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files


def main():
    # 配置路径
    input_dir = "/path/to/your/pdf/folder"  # 替换为PDF文件夹路径
    output_dir = "/path/to/output/markdown"  # 替换为输出目录

    # 查找所有PDF文件
    pdf_files = find_pdfs(input_dir)
    if not pdf_files:
        print("⚠️ 未找到PDF文件，请检查输入路径")
        return

    print(f"🔍 找到 {len(pdf_files)} 个PDF文件，开始处理...")

    # 使用线程池并行处理（默认4线程）
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(lambda f: process_pdf_with_mineru(f, output_dir), pdf_files)

    print("🎉 所有文件处理完成！")


if __name__ == "__main__":
    main()