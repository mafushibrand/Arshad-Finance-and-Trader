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
ui.write_text(s,encoding="utf-8")
print("Roznamcha patch applied.")

# Show the customer description already saved by the customer form and give
# the business customer Khata a dedicated teal/violet palette.
dialog = root / "app/src/main/java/com/example/ui/dialogs/PremiumCustomerDetailDialog.kt"
d = dialog.read_text(encoding="utf-8")
if "import androidx.compose.ui.graphics.Color" not in d:
    d = d.replace("import androidx.compose.ui.Modifier", "import androidx.compose.ui.Modifier\\nimport androidx.compose.ui.graphics.Color", 1)
if "import org.json.JSONObject" not in d:
    d = d.replace("import com.example.util.BusinessUtils", "import com.example.util.BusinessUtils\\nimport org.json.JSONObject", 1)
if "val khataScheme = MaterialTheme.colorScheme.copy(" not in d:
    anchor = "  val context = androidx.compose.ui.platform.LocalContext.current"
    theme = """  val khataScheme = MaterialTheme.colorScheme.copy(
    primary = Color(0xFF0F766E), secondary = Color(0xFF7C3AED),
    tertiary = Color(0xFFB45309), primaryContainer = Color(0xFFCCFBF1),
    onPrimaryContainer = Color(0xFF134E4A)
  )
  val customerDescription = runCatching { JSONObject(customer.detailsJson).optString("description") }.getOrDefault("")
"""
    if anchor not in d: raise SystemExit("Customer detail context anchor missing")
    d = d.replace(anchor, anchor + "\\n" + theme, 1)
    d = d.replace('  BusinessForm(label("Customer Khata", "گاہک کا کھاتہ"),',
                  '  MaterialTheme(colorScheme=khataScheme) { BusinessForm(label("Customer Khata", "گاہک کا کھاتہ"),', 1)
    needle = """      Spacer(Modifier.width(12.dp)); Column { Text(customer.name, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold); Text(customer.phone) }
    }
"""
    replacement = needle + """    if (customerDescription.isNotBlank()) {
      Surface(color=MaterialTheme.colorScheme.primaryContainer,shape=androidx.compose.foundation.shape.RoundedCornerShape(14.dp),modifier=Modifier.fillMaxWidth()) {
        Column(Modifier.padding(12.dp)) {
          Text(label("Customer description","گاہک کی تفصیل"),style=MaterialTheme.typography.labelLarge,color=MaterialTheme.colorScheme.onPrimaryContainer)
          Text(customerDescription,color=MaterialTheme.colorScheme.onPrimaryContainer)
        }
      }
    }
"""
    if needle not in d: raise SystemExit("Customer detail profile row anchor missing")
    d = d.replace(needle, replacement, 1)
    close = "  }\\n  if (receive) AlertDialog"
    if close not in d: raise SystemExit("Customer detail theme close anchor missing")
    d = d.replace(close, "  } }\\n  if (receive) AlertDialog", 1)
    dialog.write_text(d, encoding="utf-8")
print("Customer Khata description display and dedicated teal/violet styling applied.")
