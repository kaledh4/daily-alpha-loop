import os
from PIL import Image
try:
    from cairosvg import svg2png
    CAIRO_AVAILABLE = True
except ImportError:
    CAIRO_AVAILABLE = False
    print("CairoSVG not available, using basic conversion")

def convert_svg_to_png(svg_path, png_path, size):
    """Convert SVG to PNG using CairoSVG if available, otherwise create a simple placeholder"""
    if CAIRO_AVAILABLE:
        # Use CairoSVG for better quality conversion
        svg2png(url=svg_path, write_to=png_path, output_width=size, output_height=size)
    else:
        # Create a simple placeholder image
        img = Image.new('RGB', (size, size), color='#0f0f13')
        # Draw a simple circle and cross
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        # Circle
        draw.ellipse((size//4, size//4, 3*size//4, 3*size//4), fill='#3b82f6')
        # Cross
        draw.line((size//2, size//3, size//2, 2*size//3), fill='white', width=size//20)
        draw.line((size//3, size//2, 2*size//3, size//2), fill='white', width=size//20)
        # Text
        try:
            draw.text((size//2, 5*size//6), "EC", fill="white", anchor="mm")
        except:
            pass  # Font might not be available
        img.save(png_path, 'PNG')

def main():
    # Define icon sizes
    sizes = [192, 256, 384, 512]
    
    # Convert each SVG to PNG
    for size in sizes:
        svg_path = f"app/static/icons/icon-{size}x{size}.svg"
        png_path = f"app/static/icons/icon-{size}x{size}.png"
        
        if os.path.exists(svg_path):
            print(f"Converting {svg_path} to {png_path}...")
            convert_svg_to_png(svg_path, png_path, size)
            print(f"Created {png_path}")
        else:
            print(f"SVG file not found: {svg_path}")

if __name__ == "__main__":
    main()