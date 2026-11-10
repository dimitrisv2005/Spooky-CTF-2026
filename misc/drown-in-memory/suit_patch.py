"""
Drown in Memory - suit calibration patcher (Windows, Python 3, no extra packages).

The client keeps a calibration struct on the heap:
    +0x08 float  capacity   (stock 1.0, server accepts 0.5 .. 3.0)
    +0x0C uint32 guard      = float_bits(capacity) ^ cookie ^ 0xA731CF29
    +0x10 uint32 cookie     (sent by the server in /v1/session)
The final stretch to the submarine needs capacity > 1.01.
This script finds the struct and sets capacity = 3.0 with a matching guard.

Usage: start the game, press Enter to start a dive, then run:
    python suit_patch.py
Leave it running; it re-applies the patch after every restart/reset.
"""
import ctypes, ctypes.wintypes as wt, struct, time, sys

TARGET_EXE = "Abyss-Win64-Shipping.exe"
NEW_CAP = 3.0
MAGIC_PATCH = 0xA731CF29

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
PROCESS_ALL = 0x0438  # VM_READ | VM_WRITE | VM_OPERATION | QUERY_INFORMATION
MEM_COMMIT, MEM_PRIVATE, PAGE_READWRITE = 0x1000, 0x20000, 0x04

class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p), ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", wt.DWORD), ("PartitionId", wt.WORD),
                ("RegionSize", ctypes.c_size_t), ("State", wt.DWORD),
                ("Protect", wt.DWORD), ("Type", wt.DWORD)]

class PE32(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ProcessID", wt.DWORD),
                ("th32DefaultHeapID", ctypes.c_void_p), ("th32ModuleID", wt.DWORD),
                ("cntThreads", wt.DWORD), ("th32ParentProcessID", wt.DWORD),
                ("pcPriClassBase", ctypes.c_long), ("dwFlags", wt.DWORD),
                ("szExeFile", ctypes.c_char * 260)]

def find_pid():
    snap = k32.CreateToolhelp32Snapshot(2, 0)
    e = PE32(); e.dwSize = ctypes.sizeof(e)
    ok = k32.Process32First(snap, ctypes.byref(e))
    while ok:
        if e.szExeFile.decode(errors="ignore").lower() == TARGET_EXE.lower():
            k32.CloseHandle(snap); return e.th32ProcessID
        ok = k32.Process32Next(snap, ctypes.byref(e))
    k32.CloseHandle(snap); return None

def read(h, addr, n):
    buf = ctypes.create_string_buffer(n); got = ctypes.c_size_t()
    if k32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, n, ctypes.byref(got)):
        return buf.raw[:got.value]
    return b""

def write(h, addr, data):
    got = ctypes.c_size_t()
    return k32.WriteProcessMemory(h, ctypes.c_void_p(addr), data, len(data), ctypes.byref(got))

def scan(h):
    hits, addr, mbi = [], 0, MBI()
    while k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
        base, size = mbi.BaseAddress or 0, mbi.RegionSize
        if mbi.State == MEM_COMMIT and mbi.Type == MEM_PRIVATE and mbi.Protect == PAGE_READWRITE and size < 1 << 30:
            data = read(h, base, size)
            i = data.find(b"\x00\x00\x80\x3f")              # capacity == 1.0 (stock)
            while i != -1:
                s = i - 8
                if s >= 0 and s % 4 == 0 and s + 0x14 <= len(data):
                    cap_bits, guard, cookie = struct.unpack_from("<III", data, s + 8)
                    if guard == cap_bits ^ cookie ^ MAGIC_PATCH and cookie != 0:
                        hits.append((base + s, cookie))
                i = data.find(b"\x00\x00\x80\x3f", i + 1)
        addr = base + size
    return hits

def main():
    pid = find_pid()
    if not pid: sys.exit(f"{TARGET_EXE} is not running. Start the game first.")
    h = k32.OpenProcess(PROCESS_ALL, False, pid)
    if not h: sys.exit("OpenProcess failed - try running the terminal as Administrator.")
    new_bits = struct.unpack("<I", struct.pack("<f", NEW_CAP))[0]
    print(f"Attached to PID {pid}. Watching for the stock suit calibration (Ctrl+C to stop)...")
    while True:
        for addr, cookie in scan(h):
            guard = new_bits ^ cookie ^ MAGIC_PATCH
            write(h, addr + 8, struct.pack("<fI", NEW_CAP, guard))
            print(f"[+] {addr:#x}: cookie={cookie:#010x} -> capacity={NEW_CAP}, guard={guard:#010x}")
        time.sleep(2)

if __name__ == "__main__":
    main()
