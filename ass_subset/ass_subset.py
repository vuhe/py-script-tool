import os
import subprocess

from rich.console import Console

console = Console()


def otf_to_ttf(font_dir):
    """转换 otf 字体到 ttf 字体，可能抛出异常"""
    for root, _, files in os.walk(font_dir):
        for file in files:
            if file.lower().endswith(".otf"):
                otf_path = os.path.join(root, file)
                subprocess.run(["otf2ttf", otf_path], check=True)
                console.print(f"[blue]covert {file} to ttf[/blue]")
                os.remove(otf_path)


if __name__ == "__main__":
    # 测试或简单转换
    otf_to_ttf("")


def assfonts_process(cmd):
    """执行 assfonts，输出含有 [Error] 判定为失败"""
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    success = True
    for log in stdout.splitlines():
        if log.startswith("[WARN]"):
            console.print(f"[yellow]{log.removeprefix('[WARN] ')}[/yellow]")
            if "Missing the font" in log:
                success = False
        if log.startswith("[Error]"):
            console.print(f"[red]{log.removeprefix('[Error] ')}[/red]")
            success = False
    for log in stderr.splitlines():
        if log.startswith("[WARN]"):
            console.print(f"[yellow]{log.removeprefix('[WARN] ')}[/yellow]")
            if "Missing the font" in log:
                success = False
        if log.startswith("[Error]"):
            console.print(f"[red]{log.removeprefix('[Error] ')}[/red]")
            success = False
    return success


def ass_subset(parse_font_ass, append_font_ass, ass_dir):
    """执行 assfonts 子集化程序，返回生成的 ass 文件"""
    subset_font_dir = os.path.join(ass_dir, "subset_font")
    os.makedirs(subset_font_dir, exist_ok=True)

    # 对 ass 进行字体子集化，出现警告和错误默认终止程序
    input_ass = [os.path.join(ass_dir, it) for it in parse_font_ass]
    subset_cmd = ["assfonts", "-o", subset_font_dir, "-s", "-i"] + input_ass
    if not assfonts_process(subset_cmd):
        return None

    # 对生成的字体子集中的 otf 转换为 tff
    try:
        otf_to_ttf(subset_font_dir)
    except Exception as e:
        console.print(f"[red]oft 转换 tff 异常: {e}[/red]")
        return None

    # 将生成的子集化字体嵌入文件中
    ass_file_name, _ = os.path.splitext(append_font_ass)
    generated_output = f"{ass_file_name}.assfonts.ass"
    append_cmd = ["assfonts", "-f", subset_font_dir, "-e", "-i", os.path.join(ass_dir, append_font_ass)]
    if not assfonts_process(append_cmd):
        return None

    return os.path.join(ass_dir, generated_output)
