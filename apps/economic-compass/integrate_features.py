#!/usr/bin/env python3
"""
Economic Compass - Interactive Features Integration Script
This script automatically integrates the interactive features into your index.html safely.
"""

import os
import re

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_HTML_PATH = os.path.join(SCRIPT_DIR, 'app', 'templates', 'index.html')

def integrate_features():
    """Add interactive features to index.html"""
    
    print("🚀 Economic Compass - Interactive Features Integration")
    print("=" * 60)
    
    # Read the current index.html
    with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
   
    # Check if already integrated
    if 'interactive.css' in content:
        print("✅ Interactive features already integrated!")
        return True
    
    # Backup original file
    backup_path = INDEX_HTML_PATH + '.backup'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📦 Backup created: {backup_path}")
    
    # Step 1: Add interactive.css after style.css
    css_pattern = r'(<link rel="stylesheet" href="/EconomicCompass/static/style\.css">)'
    css_replacement = r'\1\n    <link rel="stylesheet" href="/EconomicCompass/static/interactive.css">'
    
    if re.search(css_pattern, content):
        content = re.sub(css_pattern, css_replacement, content)
        print("✅ Added interactive.css")
    else:
        print("❌ Could not find style.css link!")
        return False
    
    # Step 2: Add app.js before the language switching script
    js_pattern = r'(\s+<!-- Language Switching Script -->)'
    js_replacement = r'\n    <!-- Interactive Features -->\n    <script src="/EconomicCompass/static/app.js"></script>\n\1'
    
    if re.search(js_pattern, content):
        content = re.sub(js_pattern, js_replacement, content)
        print("✅ Added app.js")
    else:
        print("❌ Could not find Language Switching Script comment!")
        return False
    
    # Write the updated content
    with open(INDEX_HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "=" * 60)
    print("🎉 SUCCESS! Interactive features integrated!")
    print("=" * 60)
    print("\n📋 What was added:")
    print("   • /app/static/interactive.css - Visual styling")
    print("   • /app/static/app.js - Interactive functionality")
    print("\n🎯 Features now available:")
    print("   ✓ Educational tooltips (click ⓘ icons)")
    print("   ✓ Sparkline trend charts")
    print("   ✓ Interactive Fear & Greed gauge")
    print("   ✓ Community sentiment poll")
    print("   ✓ Trader vs Investor toggle")
    print("   ✓ Shareable snapshot button")
    print("   ✓ Event countdown badges")
    print("\n📱 All features are fully mobile-compatible!")
    print("\n🔄 Next steps:")
    print("   1. Clear your browser cache")
    print("   2. Reload the app")
    print("   3. Test on mobile device")
    print("   4. Check Arabic mode (RTL)")
    print(f"\n💡 To revert: cp {backup_path} {INDEX_HTML_PATH}")
    
    return True

if __name__ == '__main__':
    try:
        if not os.path.exists(INDEX_HTML_PATH):
            print(f"❌ Error: index.html not found at {INDEX_HTML_PATH}")
            print("   Make sure you're running this from the project root!")
            exit(1)
        
        integrate_features()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("   Please check the error and try again.")
        exit(1)
