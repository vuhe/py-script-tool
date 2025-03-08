import os
import shutil

from InquirerPy import prompt
from rich.console import Console

from ass_subset import ass_subset
from mkv_ass_subset.mkv_nix import print_tracks, extract_ass

console = Console()


def copy_extra_ass(pure_file_name, output_dir):
    """拷贝工作目录下同名的 ASS 文件"""
    handled = False
    cwd = os.getcwd()
    for file in os.listdir(cwd):
        if file.startswith(pure_file_name) and file.lower().endswith(".ass"):
            if ".assfonts." in file:
                handled = True
            file_path = os.path.join(cwd, file)
            dest_file_path = os.path.join(output_dir, file)
            try:
                shutil.copyfile(file_path, dest_file_path)
            except Exception as e:
                console.print(f"[red]复制 {file} 失败: {e}[/red]")
    return handled


def remove_temp_dir(output_dir):
    """删除临时文件夹"""
    # noinspection PyBroadException
    try:
        shutil.rmtree(output_dir)
    except Exception:
        pass


def continue_handle(hint: str, default=True):
    """确认继续处理"""
    questions = [{
        "type": "confirm",
        "message": hint,
        "name": "proceed",
        "default": default,
    }]
    answers = prompt(questions)
    return answers["proceed"]


def process_file(file_path):
    """处理单个文件"""
    file_name = os.path.basename(file_path)
    console.print(f"[blue]正在处理文件: {file_name}[/blue]")
    print_tracks(file_path)

    # 拷贝需要处理的 ass 文件到临时文件夹
    pure_file_name, _ = os.path.splitext(file_name)
    output_dir = os.path.join(os.getcwd(), pure_file_name)
    os.makedirs(output_dir, exist_ok=True)
    extract_ass(file_path, output_dir)
    subset_ass_exist = copy_extra_ass(pure_file_name, output_dir)
    if subset_ass_exist:
        console.print(f"[yellow]文件有已经处理过的 ASS[/yellow]")
        if not continue_handle(hint="是否覆盖处理？不覆盖将跳过此文件", default=False):
            remove_temp_dir(output_dir)
            return

    # 筛选出 ASS 格式的字幕轨道
    ass_tracks = [t for t in os.listdir(output_dir) if t.lower().endswith(".ass")]

    if not ass_tracks:
        console.print(f"[yellow]{file_name} 不含 ASS 字幕[/yellow]")
        remove_temp_dir(output_dir)
        if not continue_handle(hint="是否继续处理其他文件"):
            exit(0)
        return

    if len(ass_tracks) == 1:
        console.print(f"[blue]只有一个字幕文件，直接生成[/blue]")
        generated_ass = ass_subset(ass_tracks, ass_tracks[0], output_dir)
    else:
        # 选择要子集化的字幕文件，执行子集化
        questions = [
            {
                "type": "checkbox",
                "name": "分析字体",
                "message": "选择需要分析字体的 ASS 文件:",
                "choices": ass_tracks,
            },
            {
                "type": "list",
                "name": "写入文件",
                "message": "选择需要处理的 ASS 文件:",
                "choices": ass_tracks,
            },
        ]
        answers = prompt(questions)
        generated_ass = ass_subset(answers['分析字体'], answers['写入文件'], output_dir)

    if not generated_ass:
        remove_temp_dir(output_dir)
        if not continue_handle(hint="是否继续处理其他文件"):
            exit(0)
        return

    # 生成新的 ass 文件
    console.print(f"[green]ASS 生成完成[/green]")
    if not continue_handle(hint="是否移动文件"):
        remove_temp_dir(output_dir)
        exit(0)
    output_name = f"{pure_file_name}.assfonts.zh.default.ass"
    output_path = os.path.join(os.getcwd(), output_name)
    if os.path.isfile(output_path):
        os.remove(output_path)
    os.rename(generated_ass, output_path)
    console.print(f"[green]文件移动完成[/green]")

    remove_temp_dir(output_dir)
    if not continue_handle(hint="是否继续处理其他文件"):
        exit(0)


