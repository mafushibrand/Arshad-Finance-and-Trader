import sys
from pathlib import Path

p = Path(sys.argv[1]) / "app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt"
s = p.read_text()
old = '}.onFailure { archiveMessage=it.message ?: "Cannot open file" }) { Icon(Icons.Default.Visibility'
new = '}.onFailure { archiveMessage=it.message ?: "Cannot open file" } }) { Icon(Icons.Default.Visibility'
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit("Archive open callback anchor not found")
p.write_text(s)
print("Fixed archive open IconButton callback.")
