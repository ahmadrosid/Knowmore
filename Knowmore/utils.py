import os
import re
from django.conf import settings

def get_vite_assets():
    """
    Parse the Vite-generated index.html to extract asset paths
    """
    try:
        vite_html_path = os.path.join(settings.BASE_DIR, 'static', 'dist', 'index.html')
        
        with open(vite_html_path, 'r') as f:
            content = f.read()
        
        # Extract CSS file
        css_match = re.search(r'href="([^"]*\.css)"', content)
        css_file = css_match.group(1) if css_match else None
        
        # Extract JS file  
        js_match = re.search(r'src="([^"]*\.js)"', content)
        js_file = js_match.group(1) if js_match else None
        
        return {
            'css': css_file.replace('/static/', '') if css_file else None,
            'js': js_file.replace('/static/', '') if js_file else None
        }
    except FileNotFoundError:
        return {'css': None, 'js': None}