from pathlib import Path
import sys

root = Path(sys.argv[1])

core = root / "app/src/main/java/com/example/business/BusinessCore.kt"
s = core.read_text(encoding="utf-8")
marker = "  private suspend fun audit(action: String, id: String, actor: String) {"
method = """  suspend fun roznamchaEntry(amount: Double, income: Boolean, dateMillis: Long, note: String, accountId: Long, actor: String) = db.withTransaction {
    validMoney(amount)
    require(amount > 0.0) { "Enter a positive amount / درست رقم درج کریں" }
    require(note.isNotBlank()) { "Enter entry description / اندراج کی تفصیل درج کریں" }
    val account = db.financeDao().getAllAccountsList().firstOrNull { it.id == accountId }
      ?: error("Choose a valid cash account / درست کیش اکاؤنٹ منتخب کریں")
    val now = System.currentTimeMillis()
    db.financeDao().changeAccountBalance(account.id, if (income) amount else -amount)
    db.financeDao().insertTransaction(Transaction(
      title = if (income) "Roznamcha • Cash In" else "Roznamcha • Cash Out",
      amount = amount,
      type = if (income) TransactionType.INCOME else TransactionType.EXPENSE,
      category = "Roznamcha",
      icon = if (income) "💰" else "🧾",
      accountName = account.name,
      dateMillis = dateMillis,
      note = note.trim(),
      transactionRef = "ROZNAMCHA/${UUID.randomUUID()}",
      updatedAt = now,
      createdBy = actor
    ))
  }
"""
if "suspend fun roznamchaEntry(" not in s:
    if marker not in s:
        raise SystemExit("BusinessCore audit insertion point missing")
    s = s.replace(marker, method + marker, 1)
    core.write_text(s, encoding="utf-8")

ui = root / "app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt"
s = ui.read_text(encoding="utf-8")
if "import androidx.compose.ui.graphics.Color" not in s:
    s = s.replace("import androidx.compose.ui.Modifier\n", "import androidx.compose.ui.Modifier\nimport androidx.compose.ui.graphics.Color\n", 1)
if '"ROZNAMCHA" to text("Roznamcha","روزنامچہ")' not in s:
    s = s.replace('"JOB" to text("Jobs","جاب کارڈ"),', '"ROZNAMCHA" to text("Roznamcha","روزنامچہ"),"JOB" to text("Jobs","جاب کارڈ"),', 1)
s = s.replace('if(section=="PRODUCTION") text("Record production","پیداوار درج کریں") else text("Add ${sections[section]}","نیا ریکارڈ شامل کریں")',
              'if(section=="PRODUCTION") text("Record production","پیداوار درج کریں") else if(section=="ROZNAMCHA") text("Add cash entry","نیا نقد اندراج") else text("Add ${sections[section]}","نیا ریکارڈ شامل کریں")', 1)
branch_marker = '      "MOVEMENTS" -> {\n'
branch = """      "ROZNAMCHA" -> {
        var period by remember { mutableStateOf("TODAY") }
        val all = state.transactions.filter { it.category == "Roznamcha" }.sortedByDescending { it.dateMillis }
        val today = SimpleDateFormat("yyyyMMdd",Locale.US).format(Date())
        val month = SimpleDateFormat("yyyyMM",Locale.US).format(Date())
        val rows = all.filter { tx ->
          val date=Date(tx.dateMillis)
          val inPeriod=when(period) {
            "TODAY" -> SimpleDateFormat("yyyyMMdd",Locale.US).format(date)==today
            "MONTH" -> SimpleDateFormat("yyyyMM",Locale.US).format(date)==month
            else -> true
          }
          inPeriod && (query.isBlank() || tx.title.contains(query,true) || tx.note.contains(query,true) || tx.accountName.contains(query,true))
        }
        val cashIn=rows.filter { it.type==TransactionType.INCOME }.sumOf { it.amount }
        val cashOut=rows.filter { it.type==TransactionType.EXPENSE }.sumOf { it.amount }
        item {
          Column(verticalArrangement=Arrangement.spacedBy(10.dp)) {
            Row(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
              FilterChip(period=="TODAY",{period="TODAY"},label={Text(text("Today","آج"))})
              FilterChip(period=="MONTH",{period="MONTH"},label={Text(text("This month","اس ماہ"))})
              FilterChip(period=="ALL",{period="ALL"},label={Text(text("All entries","تمام اندراجات"))})
            }
            Row(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
              Card(Modifier.weight(1f),colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.primaryContainer)) {
                Column(Modifier.padding(12.dp)) { Text(text("Cash In","آمدن"),color=MaterialTheme.colorScheme.onPrimaryContainer);Text(state.money(cashIn),fontWeight=FontWeight.Bold,color=MaterialTheme.colorScheme.onPrimaryContainer) }
              }
              Card(Modifier.weight(1f),colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.secondaryContainer)) {
                Column(Modifier.padding(12.dp)) { Text(text("Cash Out","خرچ"),color=MaterialTheme.colorScheme.onSecondaryContainer);Text(state.money(cashOut),fontWeight=FontWeight.Bold,color=MaterialTheme.colorScheme.onSecondaryContainer) }
              }
            }
            Card(colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.tertiaryContainer)) {
              Row(Modifier.fillMaxWidth().padding(14.dp),horizontalArrangement=Arrangement.SpaceBetween) {
                Text(text("Net cash movement","خالص نقد فرق"),fontWeight=FontWeight.SemiBold)
                Text(state.money(cashIn-cashOut),fontWeight=FontWeight.Bold)
              }
            }
          }
        }
        if(rows.isEmpty()) item { EmptyList(text("No Roznamcha entries","روزنامچہ میں ابھی کوئی اندراج نہیں"),text("Add daily cash received or paid","روزانہ وصولی یا ادائیگی درج کریں"),Icons.Default.MenuBook) }
        items(rows,key={it.id}) { tx ->
          val incoming=tx.type==TransactionType.INCOME
          val date=SimpleDateFormat("dd MMM yyyy • hh:mm a",Locale.getDefault()).format(Date(tx.dateMillis))
          ListTile(if(incoming)text("Cash received","نقد وصولی") else text("Cash paid","نقد ادائیگی"),
            date+" • "+tx.accountName+"\\n"+tx.note,Icons.Default.MenuBook,
            controls={Text((if(incoming)"+ " else "− ")+state.money(tx.amount),fontWeight=FontWeight.Bold,color=if(incoming)Color(0xFF0F766E) else Color(0xFFB45309))})
        }
      }
"""
if '"ROZNAMCHA" -> {' not in s:
    if branch_marker not in s:
        raise SystemExit("BusinessOperations MOVEMENTS branch missing")
    s = s.replace(branch_marker, branch + branch_marker, 1)
old = """  if(form && writable) OperationForm(section,state,onDismiss={form=false},save={title,party,amount,payload ->
    viewModel.businessAction({create(section,title,party,amount,payload,actor)}) {result(it)}
  },produce={id,qty,waste -> viewModel.businessAction({produce(id,qty,waste,actor)}) {result(it)}})
"""
new = """  if(form && writable && section=="ROZNAMCHA") RoznamchaEntryForm(state,{form=false}) { amount,income,date,note,accountId ->
    viewModel.businessAction({roznamchaEntry(amount,income,date,note,accountId,actor)}) {result(it)}
  }
  else if(form && writable) OperationForm(section,state,onDismiss={form=false},save={title,party,amount,payload ->
    viewModel.businessAction({create(section,title,party,amount,payload,actor)}) {result(it)}
  },produce={id,qty,waste -> viewModel.businessAction({produce(id,qty,waste,actor)}) {result(it)}})
"""
if "RoznamchaEntryForm(state" not in s:
    if old not in s:
        raise SystemExit("BusinessOperations form block missing")
    s = s.replace(old, new, 1)
if "private fun RoznamchaEntryForm" not in s:
    s += '''
          
@Composable
private fun RoznamchaEntryForm(state:FinanceUiState,dismiss:()->Unit,save:(Double,Boolean,Long,String,Long)->Unit) {
  val urdu=state.appLanguage==AppLanguage.URDU
  fun t(en:String,ur:String)=if(urdu)ur else en
  var incoming by remember { mutableStateOf(true) }
  var amount by remember { mutableStateOf("") }
  var note by remember { mutableStateOf("") }
  var dateText by remember { mutableStateOf(SimpleDateFormat("yyyy-MM-dd",Locale.US).format(Date())) }
  var accountId by remember { mutableStateOf(state.accounts.firstOrNull()?.id ?: 0L) }
  var error by remember { mutableStateOf("") }
  BusinessForm(t("Roznamcha entry","روزنامچہ اندراج"),t("Save entry","اندراج محفوظ کریں"),dismiss,{
    val value=amount.toDoubleOrNull()
    val date=runCatching { SimpleDateFormat("yyyy-MM-dd",Locale.US).apply { isLenient=false }.parse(dateText)?.time }.getOrNull()
    when {
      value==null || !value.isFinite() || value<=0 -> error=t("Enter a valid amount","درست رقم درج کریں")
      note.isBlank() -> error=t("Add a description for this entry","اس اندراج کی تفصیل لکھیں")
      date==null -> error=t("Use date format YYYY-MM-DD","تاریخ YYYY-MM-DD میں لکھیں")
      accountId<=0 -> error=t("Create or select a cash account first","پہلے کیش اکاؤنٹ بنائیں یا منتخب کریں")
      else -> save(value,incoming,date,note,accountId)
    }
  }) {
    Row(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
      FilterChip(incoming,{incoming=true},label={Text(t("Cash In / وصولی","نقد آمدن / وصولی"))})
      FilterChip(!incoming,{incoming=false},label={Text(t("Cash Out / ادائیگی","نقد خرچ / ادائیگی"))})
    }
    BusinessField(amount,t("Amount (Rs.)","رقم (روپے)"),true){amount=it}
    BusinessField(note,t("Description / detail","تفصیل / وضاحت")){note=it}
    BusinessField(dateText,t("Entry date (YYYY-MM-DD)","اندراج کی تاریخ (سال-مہینہ-دن)")){dateText=it}
    BusinessChoice(state.accounts.find { it.id==accountId }?.name ?: "",t("Cash / bank account","کیش / بینک اکاؤنٹ"),state.accounts.map { it.name }) { name -> accountId=state.accounts.first { it.name==name }.id }
    if(error.isNotBlank()) Text(error,color=MaterialTheme.colorScheme.error)
  }
}
'''
# Compose state must be declared in the composable body, not inside the lazy-list builder branch.
if "var roznamchaPeriod by remember" not in s:
    s = s.replace('  var message by remember { mutableStateOf("") }',
                  '  var message by remember { mutableStateOf("") }' + chr(10) + '  var roznamchaPeriod by remember { mutableStateOf("TODAY") }', 1)
s = s.replace('        var period by remember { mutableStateOf("TODAY") }','')
s = s.replace('when(period)', 'when(roznamchaPeriod)')
s = s.replace('period=="TODAY"', 'roznamchaPeriod=="TODAY"')
s = s.replace('period=="MONTH"', 'roznamchaPeriod=="MONTH"')
s = s.replace('period=="ALL"', 'roznamchaPeriod=="ALL"')
s = s.replace('{period="TODAY"}', '{roznamchaPeriod="TODAY"}')
s = s.replace('{period="MONTH"}', '{roznamchaPeriod="MONTH"}')
s = s.replace('{period="ALL"}', '{roznamchaPeriod="ALL"}')
ui.write_text(s,encoding="utf-8")
print("Roznamcha patch applied.")

# Show customer description and give business customer Khata its own accent.
dialog = root / "app/src/main/java/com/example/ui/dialogs/PremiumCustomerDetailDialog.kt"
d = dialog.read_text(encoding="utf-8")
lines = d.splitlines()
if not any("import androidx.compose.ui.graphics.Color" in line for line in lines):
    pos = next(i for i,line in enumerate(lines) if line == "import androidx.compose.ui.Modifier")
    lines.insert(pos+1, "import androidx.compose.ui.graphics.Color")
if not any("import org.json.JSONObject" in line for line in lines):
    pos = next(i for i,line in enumerate(lines) if line == "import com.example.util.BusinessUtils")
    lines.insert(pos+1, "import org.json.JSONObject")
if not any("val khataScheme = MaterialTheme.colorScheme.copy(" in line for line in lines):
    pos = next(i for i,line in enumerate(lines) if "val context = androidx.compose.ui.platform.LocalContext.current" in line)
    theme = [
      "  val khataScheme = MaterialTheme.colorScheme.copy(",
      "    primary = Color(0xFF0F766E), secondary = Color(0xFF7C3AED),",
      "    tertiary = Color(0xFFB45309), primaryContainer = Color(0xFFCCFBF1),",
      "    onPrimaryContainer = Color(0xFF134E4A)",
      "  )",
      '  val customerDescription = runCatching { JSONObject(customer.detailsJson).optString("description") }.getOrDefault("")'
    ]
    lines[pos+1:pos+1] = theme
    d = chr(10).join(lines) + chr(10)
    d = d.replace('  BusinessForm(label("Customer Khata", "گاہک کا کھاتہ"),',
                  '  MaterialTheme(colorScheme=khataScheme) { BusinessForm(label("Customer Khata", "گاہک کا کھاتہ"),', 1)
    lines = d.splitlines()
    row = next(i for i,line in enumerate(lines) if "Spacer(Modifier.width(12.dp)); Column { Text(customer.name" in line)
    insert = [
      "    if (customerDescription.isNotBlank()) {",
      "      Surface(color=MaterialTheme.colorScheme.primaryContainer,shape=androidx.compose.foundation.shape.RoundedCornerShape(14.dp),modifier=Modifier.fillMaxWidth()) {",
      "        Column(Modifier.padding(12.dp)) {",
      '          Text(label("Customer description","گاہک کی تفصیل"),style=MaterialTheme.typography.labelLarge,color=MaterialTheme.colorScheme.onPrimaryContainer)',
      "          Text(customerDescription,color=MaterialTheme.colorScheme.onPrimaryContainer)",
      "        }",
      "      }",
      "    }"
    ]
    lines[row+2:row+2] = insert
    close = next(i for i,line in enumerate(lines) if "if (receive) AlertDialog" in line)
    if lines[close-1].strip() != "}":
        raise SystemExit("Customer detail close brace anchor missing")
    lines[close-1] = "  } }"
    d = chr(10).join(lines) + chr(10)
    dialog.write_text(d, encoding="utf-8")
print("Customer Khata description display and dedicated teal/violet styling applied.")


# Share the customer Khata statement as a real image attachment (not text-only).
receipt = root / "app/src/main/java/com/example/util/ThermalReceiptImage.kt"
rs = receipt.read_text(encoding="utf-8")
if "fun shareKhataStatement(" not in rs:
    marker = "\n}"
    pos = rs.rfind(marker)
    if pos < 0:
        raise SystemExit("ThermalReceiptImage object closing brace not found")
    method = r'''
  /** Render and share a customer ledger statement as a PNG attachment. */
  fun shareKhataStatement(context: Context, title: String, statement: String) {
    val body = "$title\n\n$statement"
    val paint = TextPaint(Paint.ANTI_ALIAS_FLAG).apply {
      color = Color.rgb(28, 38, 34)
      textSize = 27f
      typeface = Typeface.create("sans-serif", Typeface.NORMAL)
    }
    val layout = StaticLayout.Builder.obtain(body, 0, body.length, paint, 632)
      .setAlignment(Layout.Alignment.ALIGN_NORMAL)
      .setIncludePad(true)
      .setLineSpacing(7f, 1f)
      .build()
    val bitmap = Bitmap.createBitmap(720, layout.height + 100, Bitmap.Config.ARGB_8888)
    val canvas = Canvas(bitmap)
    canvas.drawColor(Color.WHITE)
    val accent = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.rgb(15, 118, 110) }
    canvas.drawRect(0f, 0f, 720f, 16f, accent)
    canvas.save()
    canvas.translate(44f, 52f)
    layout.draw(canvas)
    canvas.restore()
    val folder = File(context.cacheDir, "khata-whatsapp").apply { mkdirs() }
    val image = File(folder, "Khata_\${System.currentTimeMillis()}.png")
    try {
      image.outputStream().use { output ->
        check(bitmap.compress(Bitmap.CompressFormat.PNG, 100, output)) { "Could not create Khata statement image" }
      }
    } finally {
      bitmap.recycle()
    }
    val uri = FileProvider.getUriForFile(context, "\${context.packageName}.fileprovider", image)
    val send = Intent(Intent.ACTION_SEND).apply {
      type = "image/png"
      putExtra(Intent.EXTRA_STREAM, uri)
      clipData = android.content.ClipData.newUri(context.contentResolver, "Khata statement", uri)
      addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
      addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    }
    var shared = false
    for (target in listOf("com.whatsapp", "com.whatsapp.w4b")) {
      try {
        context.startActivity(Intent(send).setPackage(target))
        shared = true
        break
      } catch (_: ActivityNotFoundException) {
      } catch (_: SecurityException) {
      }
    }
    if (!shared) context.startActivity(Intent.createChooser(send, "Share Khata statement / کھاتے کی تفصیل شیئر کریں").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
    Toast.makeText(context, "Khata image ready / کھاتے کی تصویر تیار ہے", Toast.LENGTH_SHORT).show()
  }
'''
    method = method.replace(r"\${", "${")
    rs = rs[:pos] + "\n" + method + rs[pos:]
    receipt.write_text(rs, encoding="utf-8")

dialog = root / "app/src/main/java/com/example/ui/dialogs/PremiumCustomerDetailDialog.kt"
ds = dialog.read_text(encoding="utf-8")
if "import com.example.util.ThermalReceiptImage" not in ds:
    anchor = "import com.example.util.BusinessUtils"
    if anchor not in ds:
        raise SystemExit("BusinessUtils import not found in customer Khata dialog")
    ds = ds.replace(anchor, anchor + "\nimport com.example.util.ThermalReceiptImage", 1)
old_share = "BusinessUtils.shareWhatsAppMessage(context, customer.phone, statement)"
new_share = 'ThermalReceiptImage.shareKhataStatement(context, label("Customer Khata Statement", "گاہک کے کھاتے کی تفصیل"), statement)'
if old_share in ds:
    ds = ds.replace(old_share, new_share, 1)
elif new_share not in ds:
    raise SystemExit("Customer Khata text-share call not found")
dialog.write_text(ds, encoding="utf-8")
print("Customer Khata WhatsApp share now sends a PNG image attachment.")
