from pathlib import Path
import sys
root = Path(sys.argv[1])
p = root / "app/src/main/java/com/example/ui/dialogs/ThermalSlipDialog.kt"
s = p.read_text()
d = chr(36)

def once(old, new):
    global s
    n = s.count(old)
    if n == 0 and new in s:
        return
    if n != 1:
        raise SystemExit(f"Unsafe thermal preview localization: expected one match, got {n}: {old[:70]}")
    s = s.replace(old, new, 1)

once("import androidx.compose.runtime.Composable\n",
     "import androidx.compose.runtime.Composable\nimport androidx.compose.runtime.remember\n")
once("import com.example.data.model.Invoice\n",
     "import com.example.data.model.Invoice\nimport com.example.data.model.AppLanguage\nimport com.example.data.local.BusinessPreferences\n")
once("""  val context = LocalContext.current
  val saveBillImage""",
     """  val context = LocalContext.current
  val isUrdu = remember { BusinessPreferences(context).read("language", AppLanguage.URDU) == AppLanguage.URDU }
  fun t(en: String, ur: String) = if (isUrdu) ur else en
  val paymentMethodLabel = if (isUrdu) when (invoice.paymentMethod.substringBefore(" (")) {
    "Cash" -> "نقد"
    "Udhar" -> "ادھار"
    "JazzCash" -> "جاز کیش"
    "EasyPaisa" -> "ایزی پیسہ"
    "Bank" -> "بینک"
    "Split" -> "تقسیم شدہ"
    else -> invoice.paymentMethod
  } else invoice.paymentMethod
  val saveBillImage""")
once("""  val dateFormat = SimpleDateFormat("yyyy-MM-dd | hh:mm a", Locale.getDefault())""",
     """  val dateFormat = SimpleDateFormat("yyyy-MM-dd | hh:mm a", if (isUrdu) Locale("ur", "PK") else Locale.ENGLISH)""")
for old,new in [
('''text = "🖨️ Thermal Receipt / بل کی پرچی",''','''text = "🖨️ " + t("Thermal Receipt", "تھرمل رسید"),'''),
('''contentDescription = "Close"''','''contentDescription = t("Close", "بند کریں")'''),
('''text = "INVOICE DETAILS",''','''text = t("INVOICE DETAILS", "بل کی تفصیل"),'''),
('''ThermalRow("Subtotal:",''','''ThermalRow(t("Subtotal:", "ذیلی رقم:"),'''),
('''ThermalRow("Discount:",''','''ThermalRow(t("Discount:", "رعایت:"),'''),
('''ThermalRow("Delivery/Labour:",''','''ThermalRow(t("Delivery/Labour:", "ترسیل / مزدوری:"),'''),
('''text = "TOTAL BILL:",''','''text = t("TOTAL BILL:", "کل بل:"),'''),
('''text = if (isPaid) "[ PAID ✅ وصول شدہ ]" else "[ UNPAID / CREDIT ⚠️ ادھار ]",''','''text = if (isPaid) t("[ PAID ✅ ]", "[ مکمل وصول ✅ ]") else t("[ UNPAID / CREDIT ⚠️ ]", "[ ادھار باقی ⚠️ ]"),'''),
('''text = "Shukriya! Phir zaroor aayein.\\nشکریہ! آپ کے تعاون کا شکریہ۔",''','''text = t("Thank you for your business.", "آپ کے کاروبار کا شکریہ۔"),'''),
('''Text("Save bill image / بل کی تصویر محفوظ کریں")''','''Text(t("Save bill image", "بل کی تصویر محفوظ کریں"))'''),
('''Text("📸 WhatsApp Slip (تصویر)",''','''Text("📸 " + t("WhatsApp Slip", "واٹس ایپ رسید"),'''),
('''Text("📱 Keypad Mobile (مختصر)",''','''Text("📱 " + t("Compact Mobile", "مختصر موبائل رسید"),'''),
('''Text("💬 WhatsApp Text",''','''Text("💬 " + t("WhatsApp Text", "واٹس ایپ پیغام"),'''),
('''Text("Print / PDF",''','''Text(t("Print / PDF", "پرنٹ / پی ڈی ایف"),'''),
('''contentDescription = "Print"''','''contentDescription = t("Print", "پرنٹ")''')]:
    once(old,new)
once('text = "Inv No: ' + d + '{invoice.invoiceNumber}",',
     'text = "' + d + '{t("Invoice No", "بل نمبر")}: ' + d + '{invoice.invoiceNumber}",')
once('text = "Date: ' + d + 'dateFormatted",',
     'text = "' + d + '{t("Date", "تاریخ")}: ' + d + '{dateFormatted}",')
once('text = "Customer: ' + d + '{invoice.customerName}' + d + '{custContact}",',
     'text = "' + d + '{t("Customer", "گاہک")}: ' + d + '{invoice.customerName}' + d + '{custContact}",')
old = 'val statusStr = if (isPaid) "Full Paid (' + d + '{invoice.paymentMethod})" else "Udhar: ' + d + '{currencySymbol} ' + d + '{"%,.0f".format(invoice.remainingBalance)}"\n            ThermalRow("Status:", statusStr)'
new = 'val statusStr = if (isPaid) t("Fully paid", "مکمل وصول") + " (' + d + '{paymentMethodLabel})" else t("Due", "بقایا") + ": ' + d + '{currencySymbol} ' + d + '{"%,.0f".format(invoice.remainingBalance)}"\n            ThermalRow(t("Status:", "حیثیت:"), statusStr)'
once(old,new)
old = 'text = "🏛️ FBR POS Tax: ' + d + '{currencySymbol} ' + d + '{"%,.0f".format(invoice.taxAmount)}",'
new = 'text = "🏛️ " + t("FBR POS Tax", "ایف بی آر ٹیکس") + ": ' + d + '{currencySymbol} ' + d + '{"%,.0f".format(invoice.taxAmount)}",'
once(old,new)
old = 'text = "Powered by ' + d + '{businessProfile.businessName}",'
new = 'text = t("Powered by", "بذریعہ") + " ' + d + '{businessProfile.businessName}",'
once(old,new)
p.write_text(s)
print("Thermal receipt preview now follows selected Urdu/English language.")
