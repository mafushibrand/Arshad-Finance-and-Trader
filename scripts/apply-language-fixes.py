from pathlib import Path
import sys
root = Path(sys.argv[1])

def replace_once(rel, old, new):
    p = root / rel
    s = p.read_text()
    n = s.count(old)
    if n == 0 and new in s:
        return
    if n != 1:
        raise SystemExit(f"Unsafe localization patch in {rel}: expected 1 match, found {n}")
    p.write_text(s.replace(old, new, 1))

card = "app/src/main/java/com/example/ui/components/TransactionItemCard.kt"
replace_once(card, "import com.example.data.model.Transaction\n",
             "import com.example.data.model.Transaction\nimport com.example.data.model.AppLanguage\n")
replace_once(card, """  modifier: Modifier = Modifier
) {
  val isIncome = transaction.type == TransactionType.INCOME""",
             """  modifier: Modifier = Modifier,
  appLanguage: AppLanguage = AppLanguage.ENGLISH
) {
  val isUrdu = appLanguage == AppLanguage.URDU
  val isIncome = transaction.type == TransactionType.INCOME""")
replace_once(card, "  val formattedTime = formatTransactionDate(transaction.dateMillis)\n",
             """  val formattedTime = formatTransactionDate(transaction.dateMillis, isUrdu)
  val localizedTitle = if (!isUrdu) transaction.title else when {
    transaction.title.startsWith("Customer Bill:", true) -> "گاہک کا بل:" + transaction.title.substringAfter("Customer Bill:")
    transaction.title.startsWith("Khata receipt:", true) -> "کھاتہ وصولی:" + transaction.title.substringAfter("Khata receipt:")
    transaction.title.startsWith("Stock Purchase:", true) -> "اسٹاک خریداری:" + transaction.title.substringAfter("Stock Purchase:")
    transaction.title.startsWith("Supplier payment:", true) -> "سپلائر ادائیگی:" + transaction.title.substringAfter("Supplier payment:")
    else -> transaction.title
  }
  val localizedAccount = if (isUrdu) transaction.accountName.replace("Cash", "کیش", true) else transaction.accountName
  val localizedPayment = if (isUrdu) when (transaction.paymentMethod.substringBefore(" (")) {
    "Cash" -> "نقد"
    "Udhar" -> "ادھار"
    "Split" -> "تقسیم شدہ"
    else -> transaction.paymentMethod
  } else transaction.paymentMethod
""")
replace_once(card, "        text = transaction.title,", "        text = localizedTitle,")
old = '          text = "$formattedTime • ' + chr(36) + '{transaction.accountName}",'
new = '          text = formattedTime + " • " + localizedAccount,'
replace_once(card, old, new)
replace_once(card, "              text = transaction.paymentMethod,", "              text = localizedPayment,")
replace_once(card, '              text = "📸 Proof",', '              text = if (isUrdu) "📸 ثبوت" else "📸 Proof",')
replace_once(card, "private fun formatTransactionDate(timeMillis: Long): String {",
             "private fun formatTransactionDate(timeMillis: Long, isUrdu: Boolean): String {")
old = '      val timeFormat = SimpleDateFormat("h:mm a", Locale.getDefault())\n      "Today, ' + chr(36) + '{timeFormat.format(Date(timeMillis))}"'
new = '      val timeFormat = SimpleDateFormat("h:mm a", if (isUrdu) Locale("ur", "PK") else Locale.ENGLISH)\n      (if (isUrdu) "آج، " else "Today, ") + timeFormat.format(Date(timeMillis))'
replace_once(card, old, new)
replace_once(card, '      "Yesterday"', '      if (isUrdu) "گزشتہ روز" else "Yesterday"')
replace_once(card, '      val dateFormat = SimpleDateFormat("MMM d, yyyy", Locale.getDefault())',
             '      val dateFormat = SimpleDateFormat("d MMM yyyy", if (isUrdu) Locale("ur", "PK") else Locale.ENGLISH)')

for rel, old, new in [
("app/src/main/java/com/example/ui/screens/HomeScreen.kt",
'''          onClick = { onTransactionClick(tx) }
        )''',
'''          onClick = { onTransactionClick(tx) },
          appLanguage = uiState.appLanguage
        )'''),
("app/src/main/java/com/example/ui/screens/BusinessHomeScreen.kt",
'''TransactionItemCard(tx, uiState.currencySymbol, { onTransactionClick(tx) })''',
'''TransactionItemCard(tx, uiState.currencySymbol, { onTransactionClick(tx) }, appLanguage = uiState.appLanguage)'''),
("app/src/main/java/com/example/ui/screens/StatsScreen.kt",
'''        onClick = { onTransactionClick(tx) }
      )''',
'''        onClick = { onTransactionClick(tx) },
        appLanguage = uiState.appLanguage
      )''')]:
    replace_once(rel, old, new)

receipt = "app/src/main/java/com/example/util/ThermalReceiptImage.kt"
replace_once(receipt, "import com.example.data.model.Invoice\n",
             "import com.example.data.model.Invoice\nimport com.example.data.model.AppLanguage\nimport com.example.data.local.BusinessPreferences\n")
replace_once(receipt,
'''  fun text(invoice: Invoice, profile: BusinessProfile, currency: String): String {
    fun money(n:Double)=String.format(Locale.US,"%s %,.2f",currency,n)
    val date=SimpleDateFormat("yyyy-MM-dd | hh:mm a",Locale.ENGLISH).apply { timeZone=TimeZone.getTimeZone("Asia/Karachi") }.format(Date(invoice.dateMillis))''',
'''  fun text(invoice: Invoice, profile: BusinessProfile, currency: String, appLanguage: AppLanguage = AppLanguage.URDU): String {
    val isUrdu = appLanguage == AppLanguage.URDU
    fun money(n:Double)=String.format(Locale.US,"%s %,.2f",currency,n)
    val date=SimpleDateFormat("yyyy-MM-dd | hh:mm a",if(isUrdu) Locale("ur","PK") else Locale.ENGLISH).apply { timeZone=TimeZone.getTimeZone("Asia/Karachi") }.format(Date(invoice.dateMillis))''')
replace_once(receipt, "    return buildString {", "    val body = buildString {")
replace_once(receipt,
'''      appendLine("Thank you / شکریہ")
    }
  }
  fun bitmap(invoice:Invoice,profile:BusinessProfile,currency:String):Bitmap {
    val paint=TextPaint(Paint.ANTI_ALIAS_FLAG).apply {color=Color.rgb(25,35,30);textSize=27f;typeface=Typeface.MONOSPACE}
    val body=text(invoice,profile,currency)''',
'''      appendLine("Thank you / شکریہ")
    }
    return if (isUrdu) body
      .replace("INVOICE / بل کی تفصیل", "بل کی تفصیل")
      .replace("Bill / بل:", "بل نمبر:")
      .replace("Date / تاریخ:", "تاریخ:")
      .replace("Customer / گاہک:", "گاہک:")
      .replace("Subtotal / رقم:", "ذیلی رقم:")
      .replace("Discount / رعایت:", "رعایت:")
      .replace("Tax / ٹیکس:", "ٹیکس:")
      .replace("Delivery / Labour:", "ترسیل / مزدوری:")
      .replace("TOTAL BILL / کل بل:", "کل بل:")
      .replace("Returned / واپس:", "واپس شدہ:")
      .replace("Net bill / موجودہ بل:", "خالص بل:")
      .replace("Received / وصول:", "وصول شدہ:")
      .replace("Due / بقایا:", "بقایا:")
      .replace("Payment / ادائیگی:", "ادائیگی:")
      .replace("Thank you / شکریہ", "شکریہ")
      else body
        .replace("INVOICE / بل کی تفصیل", "INVOICE DETAILS")
        .replace("Bill / بل:", "Bill No:")
        .replace("Date / تاریخ:", "Date:")
        .replace("Customer / گاہک:", "Customer:")
        .replace("Subtotal / رقم:", "Subtotal:")
        .replace("Discount / رعایت:", "Discount:")
        .replace("Tax / ٹیکس:", "Tax:")
        .replace("Delivery / Labour:", "Delivery / Labour:")
        .replace("TOTAL BILL / کل بل:", "TOTAL BILL:")
        .replace("Returned / واپس:", "Returned:")
        .replace("Net bill / موجودہ بل:", "Net bill:")
        .replace("Received / وصول:", "Received:")
        .replace("Due / بقایا:", "Due:")
        .replace("Payment / ادائیگی:", "Payment:")
        .replace("Thank you / شکریہ", "Thank you")
  }
  fun bitmap(invoice:Invoice,profile:BusinessProfile,currency:String,appLanguage: AppLanguage = AppLanguage.URDU):Bitmap {
    val paint=TextPaint(Paint.ANTI_ALIAS_FLAG).apply {color=Color.rgb(25,35,30);textSize=27f;typeface=Typeface.MONOSPACE}
    val body=text(invoice,profile,currency,appLanguage)''')
replace_once(receipt,
'''    val bmp=bitmap(invoice,profile,currency)''',
'''    val language = BusinessPreferences(context).read("language", AppLanguage.URDU)
    val bmp=bitmap(invoice,profile,currency,language)''')
replace_once(receipt,
'''    val receipt = bitmap(invoice, profile, currency)''',
'''    val language = BusinessPreferences(context).read("language", AppLanguage.URDU)
    val receipt = bitmap(invoice, profile, currency, language)''')
print("Urdu/English dashboard activity and thermal receipt image fixes applied.")
