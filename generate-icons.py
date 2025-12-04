"""
Generate PWA icons for all dashboards from the static icons
"""
from PIL import Image
import os
from pathlib import Path

# Base directories
static_icons_dir = Path(r"c:\Users\Administrator\Downloads\monorepo-master\static\icons")
apps_dir = Path(r"c:\Users\Administrator\Downloads\monorepo-master\apps")

# Icon mapping
icon_mapping = {
    'the-shield': 'icons8-shield-48.png',
    'the-coin': 'icons8-coin-64.png',
    'the-map': 'icons8-map-48.png',
    'the-frontier': 'icons8-ai-48.png',
    'the-strategy': 'icons8-strategy-48.png',
    'the-library': 'icons8-library-48.png',
    'the-commander': 'icons8-commander-of-the-canadian-navy-48.png'
}

# Required PWA sizes
pwa_sizes = [192, 512]

print("🎨 Generating PWA icons for all dashboards...\n")

for app_name, icon_file in icon_mapping.items():
    print(f"📱 Processing {app_name}...")
    
    # Source icon path
    source_icon = static_icons_dir / icon_file
    
    if not source_icon.exists():
        print(f"  ⚠️  Source icon not found: {icon_file}")
        continue
    
    # Create icons directory for this app
    app_icons_dir = apps_dir / app_name / "icons"
    app_icons_dir.mkdir(exist_ok=True, parents=True)
    
    # Open source image
    try:
        img = Image.open(source_icon)
        
        # Also check for static subdirs
        static_dir = apps_dir / app_name / "static" / "icons"
        static_dir.mkdir(exist_ok=True, parents=True)
        
        # Generate each size
        for size in pwa_sizes:
            # Resize image
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Save to both locations
            icon_path_1 = app_icons_dir / f"icon-{size}.png"
            icon_path_2 = static_dir / f"icon-{size}x{size}.png"
            
            resized.save(icon_path_1, "PNG")
            resized.save(icon_path_2, "PNG")
            
            print(f"  ✅ Created {size}x{size} icon")
        
        # Also create favicon.ico (16x16, 32x32, 48x48)
        favicon_sizes = [16, 32, 48]
        favicon_images = []
        
        for size in favicon_sizes:
            favicon_images.append(img.resize((size, size), Image.Resampling.LANCZOS))
        
        # Save favicon to root and static
        favicon_path_1 = apps_dir / app_name / "favicon.ico"
        favicon_path_2 = static_dir / "favicon.ico"
        
        favicon_images[0].save(favicon_path_1, format='ICO', sizes=[(16,16), (32,32), (48,48)])
        favicon_images[0].save(favicon_path_2, format='ICO', sizes=[(16,16), (32,32), (48,48)])
        
        print(f"  ✅ Created favicon.ico")
        print()
        
    except Exception as e:
        print(f"  ❌ Error: {e}\n")
        continue

print("✨ Icon generation complete!")
