import numpy as np
import os
from utils import compress_wafer_map, generate_heatmap_image

def verify():
    # 1. Check Data Existence
    files = os.listdir("data")
    npy_files = [f for f in files if f.endswith(".npy")]
    print(f"Found {len(npy_files)} .npy files.")
    assert len(npy_files) == 20, "Should have 20 mock files."
    
    # 2. Check Compression Logic
    sample_path = os.path.join("data", npy_files[0])
    raw_data = np.load(sample_path)
    print(f"Raw shape: {raw_data.shape}")
    
    compressed = compress_wafer_map(raw_data)
    print(f"Compressed shape: {compressed.shape}")
    
    # User requested 130x28 (or 28x130). Our utils uses (28, 130).
    assert compressed.shape == (28, 130), f"Expected (28, 130), got {compressed.shape}"
    
    # 3. Check Heatmap Generation
    img = generate_heatmap_image(compressed)
    print(f"Heatmap image size: {img.size}")
    assert img.size == (130, 28), f"Expected image size (130, 28), got {img.size}"
    
    print("ALL VERIFICATION CHECKS PASSED.")

if __name__ == "__main__":
    verify()
