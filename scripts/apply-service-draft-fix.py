from pathlib import Path
import sys
p = Path(sys.argv[1]) / "app/src/main/java/com/example/ui/FinanceViewModel.kt"
s = p.read_text()
old = "require(db.financeDao().getInventoryItemById(id)!=null&&q.isFinite()&&q>0);cart[id]=q"
new = "val isSavedService = _services.value.any { -kotlin.math.abs(it.id) == id };require((db.financeDao().getInventoryItemById(id)!=null || isSavedService)&&q.isFinite()&&q>0);cart[id]=q"
if old in s:
    p.write_text(s.replace(old,new,1))
elif new in s:
    print("Service draft restore already patched")
else:
    raise SystemExit("POS draft restore source line not found; refusing unsafe edit")
print("Held POS carts can now restore saved service lines.")
