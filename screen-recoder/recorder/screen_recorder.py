import subprocess
import os
import time
import sys
from recorder.screen_utils import (
    get_screen_bounds,
    get_window_geometry,
    get_default_monitor_source
)

ffmpeg_process = None

def start_recording(settings):
    global ffmpeg_process

    mode = settings.get("mode", "screen")
    file_format = settings.get("format", "mp4")
    filename = settings.get("filename", "output").strip()
    path = settings.get("path", "recordings/").strip()
    delay = settings.get("delay", 0)
    duration = settings.get("duration", 0)
    display = settings.get("display", ":0.0").strip()
    screen = settings.get("screen", {"pos": "0,0", "size": "1920x1080"})
    area = settings.get("area", "0,0 1920x1080").strip()
    window_title = settings.get("window", "").strip()
    fps = settings.get("fps", 25)

    max_width, max_height = get_screen_bounds()
    print(f"Detected screen bounds: width={max_width}, height={max_height}")

    if not filename:
        raise ValueError("Filename cannot be empty.")
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)

    output_file = os.path.join(path, f"{filename}.{file_format}")

    if delay > 0:
        time.sleep(delay)

    if mode == "screen":
        pos = screen['pos']
        size = screen['size']
        video_input = f"{display}+{pos}"
        video_size = size

    elif mode == "section":
        geometry = get_window_geometry(window_title)
        if not geometry:
            raise ValueError(f"Could not locate geometry for window: '{window_title}'")

        try:
            pos, size = geometry.split()
            x, y = map(int, pos.split(","))
            w, h = map(int, size.split("x"))
        except ValueError:
            raise ValueError(f"Invalid geometry format for window: {geometry}")

        if x + w > max_width or y + h > max_height:
            raise ValueError("Selected window is outside screen bounds.")

        video_input = f"{display}+{pos}"
        video_size = size

    elif mode == "area":
        try:
            pos, size = area.split()
            x, y = map(int, pos.split(","))
            w, h = map(int, size.split("x"))
        except ValueError:
            raise ValueError("Invalid area format. Use format 'X,Y WxH' (e.g. 100,100 1280x720)")

        if x + w > max_width or y + h > max_height:
            raise ValueError("Selected area is outside screen bounds.")

        video_input = f"{display}+{pos}"
        video_size = size

    else:
        raise ValueError(f"Unknown capture mode: {mode}")

    if not video_input or not video_size:
        raise RuntimeError("Missing video input or size.")

    record_input = settings.get("record_input", False)
    record_output = settings.get("record_output", False)

    audio_inputs = []
    audio_maps = []
    filter_complex = []

    if record_input:
        print(f"[DEBUG] monitor_source = {monitor_source}")
        audio_inputs.extend(["-f", "pulse", "-i", "default"])
        audio_maps.append("1:a")

    if record_output:
        monitor_source = get_default_monitor_source()
        if not monitor_source:
            raise RuntimeError("No system audio (monitor) source found.")
        audio_inputs.extend(["-f", "pulse", "-i", monitor_source])
        audio_maps.append(f"{len(audio_maps)+1}:a")

    if record_input and record_output:
        filter_complex = [
            "-filter_complex", "[1:a][2:a]amix=inputs=2:duration=first[aout]",
            "-map", "0:v", "-map", "[aout]"
        ]
    elif record_input or record_output:
        filter_complex = ["-map", "0:v", "-map", audio_maps[0]]
    else:
        filter_complex = ["-map", "0:v"]

    cmd = [
        "ffmpeg",
        "-y",
        "-video_size", video_size,
        "-framerate", str(fps),
        "-f", "x11grab",
        "-i", video_input
    ]

    cmd.extend(audio_inputs)
    cmd.extend(filter_complex)

    if file_format == "mp4":
        cmd.extend(["-c:v", "libx264", "-preset", "ultrafast"])

    if duration > 0:
        cmd.extend(["-t", str(duration)])

    cmd.append(output_file)

    print("Running ffmpeg command:\n", " ".join(cmd))

    try:
        ffmpeg_process = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
    except FileNotFoundError:
        raise RuntimeError("ffmpeg is not installed or not found in PATH.")

def stop_recording(wait=False):
    global ffmpeg_process
    if ffmpeg_process:
        ffmpeg_process.terminate()
        if wait:
            ffmpeg_process.wait()
        ffmpeg_process = None
