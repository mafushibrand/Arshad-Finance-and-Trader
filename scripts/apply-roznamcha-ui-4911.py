from pathlib import Path
import base64, gzip, subprocess, sys
root=Path(sys.argv[1]).resolve()
encoded=Path(__file__).with_name('roznamcha-ui-4911.patch').read_text().strip()
patch=gzip.decompress(base64.b64decode(encoded))
subprocess.run(['git','apply','--check','-'],cwd=root,input=patch,check=True)
subprocess.run(['git','apply','-'],cwd=root,input=patch,check=True)
print('Applied redesigned two-tab Roznamcha home and dedicated party ledger UI.')
