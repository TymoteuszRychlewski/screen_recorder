import subprocess
import re

def get_available_screens():
    try:
        output = subprocess.check_output(["xrandr", "--query"]).decode("utf-8")
        lines = output.strip().split("\n")
        screens = []

        for line in lines:
            if " connected" in line:
                parts = line.split()
                name = parts[0]
                for part in parts:
                    if "+" in part and "x" in part:
                        res_and_pos = part.split("+")
                        if len(res_and_pos) == 3:
                            size = res_and_pos[0]
                            pos = f"{res_and_pos[1]},{res_and_pos[2]}"
                            screens.append({
                                "name": name,
                                "pos": pos,
                                "size": size
                            })
        return screens
    except Exception as e:
        return [{"name": "default", "pos": "0,0", "size": "1920x1080"}]
    
def get_window_list():
    try:
        output = subprocess.check_output(["wmctrl", "-l"]).decode("utf-8")
        windows = [line.strip().split(None, 3)[-1] for line in output.strip().split("\n") if len(line.strip().split(None, 3)) == 4]
        return windows
    except Exception:
        return ["no windows available"]

def get_mouse_selected_area():
    try:
        result = subprocess.check_output(["slop", "--format", "%x,%y %wx%h"]).decode("utf-8").strip()
        return result
    except Exception:
        return ""
    
def get_window_geometry(title):
    try:
        win_list = subprocess.check_output(["wmctrl", "-l"]).decode("utf-8").splitlines()
        window_id = None
        for line in win_list:
            if title.lower() in line.lower():
                window_id = line.split()[0]
                break

        if not window_id:
            return ""

        output = subprocess.check_output(["xwininfo", "-id", window_id]).decode("utf-8")
        x = y = w = h = None
        for line in output.splitlines():
            if "Absolute upper-left X:" in line:
                x = int(line.split(":")[1].strip())
            elif "Absolute upper-left Y:" in line:
                y = int(line.split(":")[1].strip())
            elif "Width:" in line:
                w = int(line.split(":")[1].strip())
            elif "Height:" in line:
                h = int(line.split(":")[1].strip())

        if None in (x, y, w, h):
            return ""

        return f"{x},{y} {w}x{h}"
    except Exception as e:
        print(f"Error getting window geometry: {e}")
        return ""    
    
def get_screen_bounds():
    try:
        output = subprocess.check_output(["xrandr", "--query"]).decode("utf-8")
        max_width = 0
        max_height = 0
        for line in output.splitlines():
            match = re.search(r"(\d+)x(\d+)\+(\d+)\+(\d+)", line)
            if match:
                w = int(match.group(1))
                h = int(match.group(2))
                x = int(match.group(3))
                y = int(match.group(4))
                max_width = max(max_width, x + w)
                max_height = max(max_height, y + h)
        if max_width == 0 or max_height == 0:
            raise RuntimeError("Could not parse screen layout from xrandr.")
        return max_width, max_height
    except Exception as e:
        raise RuntimeError(f"Failed to determine screen bounds: {e}")

def get_default_monitor_source():
    try:
        output = subprocess.check_output(["pactl", "list", "sources"]).decode("utf-8")
        blocks = output.split("Source #")

        for block in blocks:
            if "monitor" in block and ("State: RUNNING" in block or "State: IDLE" in block):
                for line in block.splitlines():
                    if line.strip().startswith("Name:"):
                        return line.strip().split("Name:")[1].strip()
        return None
    except Exception:
        return None
