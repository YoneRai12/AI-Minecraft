import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import os

def visualize():
    file_path = "latest_voxel.json"
    
    if not os.path.exists(file_path):
        print("Waiting for data...")
        return

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Read error: {e}")
        return

    grid_flat = data["grid"]
    width = data["width"]
    height = data["height"]
    radius = data["radius"]
    
    # Reshape to 3D (Y, Z, X) - Note order depends on JS loop
    # JS loop: dy(-h..h), dz(-r..r), dx(-r..r)
    # So index is dy * (W*W) + dz * W + dx ? No, JS is:
    # for dy... for dz... for dx...
    # So Y is outer, Z is middle, X is inner.
    
    # Numpy reshape: (H, W, W)
    grid = np.array(grid_flat).reshape((height, width, width))
    
    # Coordinates
    x, y, z = np.indices((width, height, width))
    
    # Mapping back to relative coordinates
    # But for visualization, just plotting the indices is fine, or shift them
    
    # Filter for Solid (1) and Liquid (2)
    # Note: reshape order in numpy vs JS might need checking. 
    # If JS fills x then z then y, then reshape(height, width, width) works if formatted right.
    # Actually JS loop: dy (outer), dz, dx (inner).
    # So the flat array is [y0z0x0, y0z0x1... y0z0xN, y0z1x0...]
    # This corresponds to C-order reshape(height, width, width).
    
    # Let's verify axis:
    # Axis 0: Y (Height)
    # Axis 1: Z (Depth)
    # Axis 2: X (Width)
    
    # Get coordinates of blocks
    # We want to plot X, Z, Y in 3D space
    
    xs = []
    ys = []
    zs = []
    colors = []
    
    for iy in range(height):
        for iz in range(width):
            for ix in range(width):
                val = grid[iy, iz, ix]
                if val != 0:
                    xs.append(ix - radius)
                    zs.append(iz - radius)
                    ys.append(iy - data["halfHeight"])
                    
                    if val == 1:
                        colors.append('green') # Solid
                    elif val == 2:
                        colors.append('blue')  # Liquid (Water/Lava)
                    else:
                        colors.append('red')   # Unknown?

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    if xs:
        ax.scatter(xs, zs, ys, c=colors, marker='s', s=10)
    
    # Player position (always 0,0,0 relative to center, but feet are at 0?)
    # snapshot origin is player's floor.
    ax.scatter([0], [0], [0], c='red', marker='^', s=50, label='Bot Head/Body')
    
    ax.set_xlabel('X Relative')
    ax.set_ylabel('Z Relative')
    ax.set_zlabel('Y Relative')
    ax.set_title(f"Bot Vision: {data['player']['name']}")
    
    # Set fixed limits to stop jitter
    R = radius
    H = data["halfHeight"]
    ax.set_xlim(-R, R)
    ax.set_ylim(-R, R)
    ax.set_zlim(-H, H)
    
    plt.legend()
    plt.show()

if __name__ == "__main__":
    visualize()
