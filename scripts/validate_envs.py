import yaml
from pathlib import Path
import sys

files = [Path('environments/dev/values.yaml'), Path('environments/stage/values.yaml'), Path('environments/prod/values.yaml')]
errors = []
for f in files:
    if not f.exists():
        errors.append((str(f), 'file not found'))
        continue
    try:
        with f.open() as fh:
            data = yaml.safe_load(fh)
            # Basic sanity checks
            if 'replicaCount' not in data:
                errors.append((str(f), 'replicaCount missing'))
    except Exception as e:
        errors.append((str(f), str(e)))

if errors:
    print('Environment YAML validation errors:')
    for p, e in errors:
        print(f'- {p}: {e}')
    sys.exit(2)

print('All environment YAML files parsed successfully')
