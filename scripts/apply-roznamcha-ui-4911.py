from pathlib import Path
import subprocess, sys
root=Path(sys.argv[1]).resolve()
patch=Path(__file__).with_name('roznamcha-ui-4911.patch')
if not patch.is_file(): raise SystemExit('Roznamcha UI patch is missing')
subprocess.run(['git','apply','--check',str(patch)],cwd=root,check=True)
subprocess.run(['git','apply',str(patch)],cwd=root,check=True)
print('Applied two-tab Roznamcha home and dedicated party ledger UI patch.')
