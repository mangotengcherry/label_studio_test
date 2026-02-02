import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import io
from PIL import Image

# Target Dimensions
TARGET_H = 28
TARGET_W = 130

def compress_wafer_map(high_res_data, target_h=TARGET_H, target_w=TARGET_W):
    """
    Compresses a high-resolution binary wafer map into a density map.
    Each pixel in the output represents the sum of fails in a corresponding block.
    """
    h, w = high_res_data.shape
    
    # Calculate block sizes
    # Note: If dimensions aren't perfectly divisible, the last block will take the remainder
    # For simplicity in this mock, we assume the generator made them divisible or we define fixed blocks.
    # Our generator uses 20x scaling, so simple block reduce is fine.
    
    # Reshape and Sum approach for perfect multiples
    if h % target_h == 0 and w % target_w == 0:
        block_h = h // target_h
        block_w = w // target_w
        
        # Reshape to (TARGET_H, block_h, TARGET_W, block_w)
        # Then sum over the block dimensions (axis 1 and 3)
        reshaped = high_res_data.reshape(target_h, block_h, target_w, block_w)
        compressed = reshaped.sum(axis=(1, 3))
        return compressed
    
    # Fallback for non-perfect multiples (not needed for current generator but good for robustness)
    # Using simple binning
    y_bins = np.linspace(0, h, target_h + 1).astype(int)
    x_bins = np.linspace(0, w, target_w + 1).astype(int)
    
    compressed = np.zeros((target_h, target_w), dtype=np.int32)
    
    for i in range(target_h):
        for j in range(target_w):
            block = high_res_data[y_bins[i]:y_bins[i+1], x_bins[j]:x_bins[j+1]]
            compressed[i, j] = np.sum(block)
            
    return compressed

def generate_heatmap_image(density_map):
    """
    Converts a 2D density map into a PIL image using a Gray->Red colormap.
    """
    # Normalize data for visualization
    # We want 0 fails to be gray (or white-ish) and high fails to be red.
    max_val = np.max(density_map)
    if max_val == 0:
        norm_data = density_map.astype(float)
    else:
        norm_data = density_map / max_val
        
    # Create Custom Colormap: Light Gray -> Red
    # Colors: (R, G, B)
    # 0.0: (0.9, 0.9, 0.9) # Light Gray
    # 1.0: (1.0, 0.0, 0.0) # Red
    colors = [(0.85, 0.85, 0.85), (1, 0, 0)] 
    cmap = LinearSegmentedColormap.from_list("custom_grey_red", colors, N=256)
    
    # Apply colormap
    colored_map = cmap(norm_data) # Returns RGBA float array
    
    # Convert to PIL Image (remove Alpha channel if needed, or keep it)
    # Matplotlib returns 0-1 float, convert to 0-255 uint8
    img_uint8 = (colored_map[:, :, :3] * 255).astype(np.uint8)
    
    return Image.fromarray(img_uint8)
