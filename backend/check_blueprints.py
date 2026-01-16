import sys
sys.path.insert(0, 'd:/hac2vento/HACK-VENTO-2K26/backend')

from app import app

print('Registered blueprints:')
for bp_name, bp in app.blueprints.items():
    print(f'  - {bp_name}: {bp.url_prefix}')
