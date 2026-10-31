"""Run a Blender script headless, one Blender at a time, with a RAM check and a timeout.

Usage (from the project root):
    python Tools/Art/run_blender.py Tools/Art/assets/<id>.py -- ArtSource/<id>/card.json [more args]
    python Tools/Art/run_blender.py --which          # print the blender.exe in use

Everything after `--` is passed to the script (read it with `bslib.args()`).
`Tools/Art/lib` is put on Blender's sys.path, so scripts can `import bslib`.

Why: this machine has 16 GB RAM and usually < 2 GB free with the editor open, so parallel Blender runs
swap or crash (Production/AgentRules.md §2). A lock file serialises runs across agents; a stale lock (dead
PID) is taken over. Logs go to ArtSource/_work/logs/.
"""
import ctypes
import glob
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LIB = os.path.join(ROOT, "Tools", "Art", "lib")
WORK = os.path.join(ROOT, "ArtSource", "_work")
LOCK = os.path.join(WORK, "blender.lock")
LOGS = os.path.join(WORK, "logs")

MIN_FREE_GB = 1.2        # below this, wait for memory before starting
WAIT_LOCK_S = 1800       # how long to queue behind another run
TIMEOUT_S = int(os.environ.get("BS_BLENDER_TIMEOUT", "1200"))


def find_blender():
    env = os.environ.get("BLENDER")
    if env and os.path.isfile(env):
        return env
    hits = sorted(glob.glob(r"C:\Program Files\Blender Foundation\Blender *\blender.exe"))
    if hits:
        return hits[-1]
    for d in os.environ.get("PATH", "").split(os.pathsep):
        p = os.path.join(d, "blender.exe")
        if os.path.isfile(p):
            return p
    sys.exit("blender.exe not found: install it (winget install BlenderFoundation.Blender) or set BLENDER")


class _MemStatus(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def free_gb():
    m = _MemStatus()
    m.dwLength = ctypes.sizeof(_MemStatus)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / 1024 ** 3


def pid_alive(pid):
    h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return False
    code = ctypes.c_ulong()
    ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
    ctypes.windll.kernel32.CloseHandle(h)
    return code.value == 259  # STILL_ACTIVE


def take_lock(label):
    os.makedirs(WORK, exist_ok=True)
    t0 = time.time()
    while True:
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f"{os.getpid()} {time.strftime('%Y-%m-%dT%H:%M:%S')} {label}\n".encode())
            os.close(fd)
            return
        except FileExistsError:
            try:
                pid = int(open(LOCK).read().split()[0])
            except (OSError, ValueError, IndexError):
                pid = -1
            if pid <= 0 or not pid_alive(pid):
                print(f"[run_blender] taking over stale lock (pid {pid})")
                try:
                    os.remove(LOCK)
                except OSError:
                    pass
                continue
            if time.time() - t0 > WAIT_LOCK_S:
                sys.exit(f"[run_blender] gave up: Blender busy for {WAIT_LOCK_S}s ({open(LOCK).read().strip()})")
            time.sleep(5)


def drop_lock():
    try:
        if open(LOCK).read().split()[0] == str(os.getpid()):
            os.remove(LOCK)
    except (OSError, IndexError):
        pass


def main():
    argv = sys.argv[1:]
    if argv[:1] == ["--which"]:
        print(find_blender())
        return 0
    if not argv:
        sys.exit(__doc__)
    script, rest = argv[0], argv[1:]
    if rest[:1] == ["--"]:
        rest = rest[1:]
    script = os.path.abspath(script)
    blender = find_blender()

    label = os.path.relpath(script, ROOT)
    take_lock(label)
    try:
        t0 = time.time()
        while free_gb() < MIN_FREE_GB and time.time() - t0 < 300:
            print(f"[run_blender] waiting for RAM: {free_gb():.1f} GB free < {MIN_FREE_GB}")
            time.sleep(10)
        os.makedirs(LOGS, exist_ok=True)
        log_path = os.path.join(LOGS, f"{os.path.splitext(os.path.basename(script))[0]}_{time.strftime('%Y%m%d_%H%M%S')}.log")
        boot = f"import sys; sys.path.insert(0, r'{LIB}'); import os; os.environ['BS_ROOT'] = r'{ROOT}'"
        cmd = [blender, "-b", "--factory-startup", "-noaudio", "--python-exit-code", "3",
               "--python-expr", boot, "-P", script, "--"] + rest
        print(f"[run_blender] {os.path.basename(blender)} :: {label} {' '.join(rest)}  (free RAM {free_gb():.1f} GB)")
        with open(log_path, "w", encoding="utf-8", errors="replace") as log:
            proc = subprocess.Popen(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            try:
                code = proc.wait(timeout=TIMEOUT_S)
            except subprocess.TimeoutExpired:
                proc.kill()
                code = -9
                log.write(f"\n[run_blender] KILLED after {TIMEOUT_S}s\n")
        with open(log_path, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
        keep = [l for l in lines if l.startswith(("[bs]", "Error", "Traceback", "  File", "[run_blender]"))
                or "Error" in l or "error:" in l]
        print("\n".join(keep[-60:]))
        print(f"[run_blender] exit {code} in {time.time() - t0:.0f}s; full log: {os.path.relpath(log_path, ROOT)}")
        return code
    finally:
        drop_lock()


if __name__ == "__main__":
    sys.exit(main())
