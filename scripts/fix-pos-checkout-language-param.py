from pathlib import Path
import sys
root = Path(sys.argv[1])
p = root / "app/src/main/java/com/example/ui/screens/PosCounterScreen.kt"
s = p.read_text()

def once(old, new):
    global s
    n = s.count(old)
    if n == 0 and new in s:
        return
    if n != 1:
        raise SystemExit(f"Unsafe PosCounterScreen language fix: expected one match, found {n}")
    s = s.replace(old, new, 1)

once("import com.example.data.model.Customer\n",
     "import com.example.data.model.AppLanguage\nimport com.example.data.model.Customer\n")
once('''      onDismiss = { showCheckoutDialog = false }
    )''',
     '''      onDismiss = { showCheckoutDialog = false },
      appLanguage = uiState.appLanguage
    )''')
once('''  onConfirmSale: (Invoice, List<InvoiceItemEntry>, Boolean) -> Unit,
  onDismiss: () -> Unit
) {''',
     '''  onConfirmSale: (Invoice, List<InvoiceItemEntry>, Boolean) -> Unit,
  onDismiss: () -> Unit,
  appLanguage: AppLanguage = AppLanguage.URDU
) {''')
once('''                itemName = uiState.word(item.name, org.json.JSONObject(item.detailsJson).optString("urduName", item.name).ifBlank { item.name }),''',
     '''                itemName = if (appLanguage == AppLanguage.URDU) org.json.JSONObject(item.detailsJson).optString("urduName", item.name).ifBlank { item.name } else item.name,''')
p.write_text(s)
print("POS checkout modal language parameter fixed.")
