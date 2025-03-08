import json
import os
import subprocess

from rich.console import Console

console = Console()
subset_ass_tag = "特效简中含字体"


def print_tracks(file_path):
    """打印 MKV 文件轨道"""
    cmd = ['mkvmerge', '-i', file_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        console.print(f"[red]无法读取文件轨道信息: {os.path.basename(file_path)}[/red]")
        return []
    for track in result.stdout.splitlines():
        if track.startswith("Track"):
            console.print(f"[green]{track}[/green]")


def extract_tracks(file_path):
    """提取 MKV 文件轨道信息到 Json"""
    cmd = ['mkvmerge', '-J', file_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        console.print(f"[red]无法读取文件轨道信息: {os.path.basename(file_path)}[/red]")
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        console.print(f"[red]解析轨道 JSON 数据失败: {os.path.basename(file_path)}[/red]")
        return None


def extract_ass(file_path, output_dir):
    """分离视频的 ASS 文件"""
    json_data = extract_tracks(file_path)
    tracks = json_data.get('tracks', [])
    ass_tracks = [
        track for track in tracks
        if track.get('type') == 'subtitles' and track['properties'].get('codec_id') == 'S_TEXT/ASS'
    ]
    if not ass_tracks:
        return None

    subset_ass_flag = None
    cmd = ['mkvextract', 'tracks', file_path]
    for track in ass_tracks:
        track_id = track['id']
        track_name = track['properties'].get('track_name', f"track_{track_id}")
        if track_name == subset_ass_tag:
            subset_ass_flag = track_id
        output_file = os.path.join(output_dir, f"{track_name}.ass")
        cmd.append(f"{track_id}:{output_file}")

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        console.print("[red]mkv 提取 ASS 失败[/red]")
    return subset_ass_flag
