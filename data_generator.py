import numpy as np
import os
import random

# Configuration
DATA_DIR = "data"
NUM_SAMPLES = 20
# Original High-Res Dimensions (before compression)
# Assuming each "pixel" in the 28x130 map represents a block of cells.
# Let's say each block is 100x100 cells for simulation purposes.
ORIGINAL_H = 28 * 20
ORIGINAL_W = 130 * 20

def generate_mock_data(idx):
    # Initialize empty wafer (0 = pass, 1 = fail)
    # Using int8 to save space, though these are mock files
    wafer = np.zeros((ORIGINAL_H, ORIGINAL_W), dtype=np.int8)
    
    # 1. Random background noise (scattered fails)
    noise_level = random.uniform(0.0001, 0.001)
    mask = np.random.rand(ORIGINAL_H, ORIGINAL_W) < noise_level
    wafer[mask] = 1
    
    # Decisions for defects
    defect_type = random.choice(['normal', 'row_fail', 'col_fail', 'cluster_fail', 'edge_fail'])
    
    if defect_type == 'row_fail':
        # Add random horizontal lines
        for _ in range(random.randint(1, 4)):
            y = random.randint(0, ORIGINAL_H - 1)
            wafer[y, :] = 1
            
    elif defect_type == 'col_fail':
        # Add random vertical lines
        for _ in range(random.randint(1, 5)):
            x = random.randint(0, ORIGINAL_W - 1)
            wafer[:, x] = 1
            
    elif defect_type == 'cluster_fail':
        # Add blob defects
        for _ in range(random.randint(2, 6)):
            cy = random.randint(0, ORIGINAL_H - 1)
            cx = random.randint(0, ORIGINAL_W - 1)
            radius = random.randint(20, 100)
            y, x = np.ogrid[-radius:radius, -radius:radius]
            mask = x**2 + y**2 <= radius**2
            # Handle boundary checks simply by slicing
            # (Simplification: just placing scattered fails in a square region for performance)
            y_start = max(0, cy - radius)
            y_end = min(ORIGINAL_H, cy + radius)
            x_start = max(0, cx - radius)
            x_end = min(ORIGINAL_W, cx + radius)
            
            # Make the cluster dense but not solid
            region_h = y_end - y_start
            region_w = x_end - x_start
            if region_h > 0 and region_w > 0:
                cluster_mask = np.random.rand(region_h, region_w) < 0.6
                current_region = wafer[y_start:y_end, x_start:x_end]
                # Logical OR to combine
                wafer[y_start:y_end, x_start:x_end] = np.maximum(current_region, cluster_mask.astype(np.int8))

    elif defect_type == 'edge_fail':
         # Fails around the border
         border = random.randint(10, 50)
         wafer[:border, :] = 1
         wafer[-border:, :] = 1
         wafer[:, :border] = 1
         wafer[:, -border:] = 1

    return wafer, defect_type

def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created directory: {DATA_DIR}")
        
    print(f"Generating {NUM_SAMPLES} samples...")
    labels = []
    
    for i in range(NUM_SAMPLES):
        data, true_label = generate_mock_data(i)
        filename = f"sample_wafer_{i:02d}.npy"
        filepath = os.path.join(DATA_DIR, filename)
        np.save(filepath, data)
        print(f"Saved {filepath} (Simulated: {true_label})")
        
    print("Done!")

if __name__ == "__main__":
    main()
