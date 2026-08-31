import yaml
from pathlib import Path
import sys

files = [Path('k8s/deployment.yaml'), Path('k8s/service.yaml')]
errors = []
for f in files:
    if not f.exists():
        errors.append((str(f), 'file not found'))
        continue
    try:
        with f.open() as fh:
            # load_all to allow multiple docs
            list(yaml.safe_load_all(fh))
    except Exception as e:
        errors.append((str(f), str(e)))

if errors:
    print('YAML validation errors:')
    for p, e in errors:
        print(f'- {p}: {e}')
    sys.exit(2)

print('All k8s YAML files parsed successfully')
