def check_obj_bounds(path):
    min_x = min_y = min_z = float('inf')
    max_x = max_y = max_z = float('-inf')
    num_v = 0
    with open(path) as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)
                min_z = min(min_z, z)
                max_z = max(max_z, z)
                num_v += 1
    
    print(f"=== {path} ===")
    print(f"  Verts: {num_v}")
    print(f"  X: [{min_x:.2f}, {max_x:.2f}] span={max_x - min_x:.2f} center={(min_x + max_x)/2:.2f}")
    print(f"  Y: [{min_y:.2f}, {max_y:.2f}] span={max_y - min_y:.2f} center={(min_y + max_y)/2:.2f}")
    print(f"  Z: [{min_z:.2f}, {max_z:.2f}] span={max_z - min_z:.2f} base={min_z:.2f}")

check_obj_bounds(r"D:\Game\FishGame\Saved\DownloadedAssets\SM_FluidTank.obj")
check_obj_bounds(r"D:\Game\FishGame\Saved\DownloadedAssets\SM_PipeStraight.obj")
