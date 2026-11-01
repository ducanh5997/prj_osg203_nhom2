
import os
import json

# 1. Cau hinh
DISK_SIZE = 10 * 1024 * 1024
CLUSTER_SIZE = 4096
BOOT = 512
FAT_SIZE = 5120
DATA = BOOT + FAT_SIZE
TOTAL = (DISK_SIZE - DATA) // CLUSTER_SIZE

FREE = 0
EOF = 65535

# 2. Tao o dia ao
if not os.path.exists("disk.bin"):
    with open("disk.bin", "wb") as f:
        f.write(b"\0" * DISK_SIZE)
        f.seek(0)
        f.write(b"OSG203 FAT FILE SYSTEM")

# 3. Doc va ghi FAT
def get_fat(block):
    with open("disk.bin", "rb") as f:
        f.seek(BOOT + block * 2)
        return int.from_bytes(f.read(2), "little")

def set_fat(block, value):
    with open("disk.bin", "r+b") as f:
        f.seek(BOOT + block * 2)
        f.write(value.to_bytes(2, "little"))

# 4. Doc va luu danh sach file
def get_files():
    with open("disk.bin", "rb") as f:
        f.seek(DATA)
        data = f.read(CLUSTER_SIZE).split(b"\0")[0]
    return json.loads(data) if data else {}

def save_files(files):
    data = json.dumps(files).encode()
    with open("disk.bin", "r+b") as f:
        f.seek(DATA)
        f.write(data.ljust(CLUSTER_SIZE, b"\0"))

# 5. Tim cluster trong
def allocate():
    for block in range(1, TOTAL):
        if get_fat(block) == FREE:
            set_fat(block, EOF)
            return block
    return None

# 6. Xoa chuoi cluster
def release(block):
    while block != EOF:
        next_block = get_fat(block)
        set_fat(block, FREE)
        block = next_block

# 7. Tao file
def create(name):
    files = get_files()
    if name in files:
        print("File da ton tai!")
    elif len(name.encode()) > 32:
        print("Ten file qua dai!")
    else:
        files[name] = [-1, 0]
        save_files(files)
        print("Tao file thanh cong!")

# 8. Ghi file
def write(name, content):
    files = get_files()
    if name not in files:
        print("Khong tim thay file!")
        return

    old_block = files[name][0]
    if old_block != -1:
        release(old_block)

    data = content.encode()
    blocks = []

    for i in range(0, len(data), CLUSTER_SIZE):
        block = allocate()
        if block is None:
            print("Khong du dung luong!")
            return

        with open("disk.bin", "r+b") as f:
            f.seek(DATA + block * CLUSTER_SIZE)
            f.write(data[i:i+CLUSTER_SIZE])

        if blocks:
            set_fat(blocks[-1], block)
        blocks.append(block)

    files[name] = [blocks[0] if blocks else -1, len(data)]
    save_files(files)
    print("Ghi file thanh cong!")

# 9. Doc file
def read(name):
    files = get_files()
    if name not in files:
        print("Khong tim thay file!")
        return

    block, size = files[name]
    data = b""

    while block != -1 and block != EOF:
        with open("disk.bin", "rb") as f:
            f.seek(DATA + block * CLUSTER_SIZE)
            data += f.read(CLUSTER_SIZE)
        block = get_fat(block)

    print(data[:size].decode())

# 10. Xoa file
def delete(name):
    files = get_files()
    if name not in files:
        print("Khong tim thay file!")
        return

    if files[name][0] != -1:
        release(files[name][0])

    del files[name]
    save_files(files)
    print("Xoa file thanh cong!")

print("Lenh: create, write, read, delete, exit")
# 11. CLI
while True:
    command = input("\nFAT> ").split(" ", 1)
    cmd = command[0]

    if cmd == "exit":
        break
    elif len(command) == 2:
        name = command[1].split(" ", 1)[0]
        content = command[1][len(name):].strip().strip('"')

        if cmd == "create":
            create(name)
        elif cmd == "write":
            write(name, content)
        elif cmd == "read":
            read(name)
        elif cmd == "delete":
            delete(name)
        else:
            print("Lenh khong hop le!")
    else:
        print("Lenh khong hop le!")
