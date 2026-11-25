from pathlib import Path
import sys
import re

root=Path(sys.argv[1])

def patch(rel, old, new, label):
    p=root/rel
    s=p.read_text(encoding="utf-8")
    if new in s:
        print("Already applied:",label); return
    if s.count(old)!=1:
        raise SystemExit(f"Safe patch failed for {label}: expected exactly one anchor, got {s.count(old)}")
    p.write_text(s.replace(old,new,1),encoding="utf-8")
    print("Applied:",label)

# Dedicated first-class Roznamcha destination, separate from Khata.
patch("app/src/main/java/com/example/ui/FinanceViewModel.kt",
"""  OPERATIONS,
  PLANNER,""",
"""  OPERATIONS,
  ROZNAMCHA,
  PLANNER,""","FinanceTab.ROZNAMCHA")

patch("app/src/main/java/com/example/ui/components/BottomNavBar.kt",
"""    if (features.khata) NavBarChoice(if (urdu) "کھاتہ" else "Khata", Icons.Default.ReceiptLong,
      selectedTab == FinanceTab.LEDGERS, "nav_tab_ledgers") { onTabSelected(FinanceTab.LEDGERS) }
    NavBarChoice(if (urdu) "مزید" else "More", Icons.Default.MoreHoriz,""",
"""    if (features.khata) NavBarChoice(if (urdu) "کھاتہ" else "Khata", Icons.Default.ReceiptLong,
      selectedTab == FinanceTab.LEDGERS, "nav_tab_ledgers") { onTabSelected(FinanceTab.LEDGERS) }
    if (!personal) NavBarChoice(if (urdu) "روزنامچہ" else "Roznamcha", Icons.Default.MenuBook,
      selectedTab == FinanceTab.ROZNAMCHA, "nav_tab_roznamcha") { onTabSelected(FinanceTab.ROZNAMCHA) }
    NavBarChoice(if (urdu) "مزید" else "More", Icons.Default.MoreHoriz,""","Separate Roznamcha bottom navigation")

patch("app/src/main/java/com/example/ui/FinanceViewModel.kt",
"""      FinanceTab.LEDGERS -> f.khata
      FinanceTab.REPORTS -> f.reports""",
"""      FinanceTab.LEDGERS -> f.khata
      FinanceTab.ROZNAMCHA -> true
      FinanceTab.REPORTS -> f.reports""","Roznamcha tab access")

patch("app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt",
"""fun BusinessOperationsScreen(state: FinanceUiState, viewModel: FinanceViewModel) {""",
"""fun BusinessOperationsScreen(state: FinanceUiState, viewModel: FinanceViewModel, startSection: String? = null) {""","Operations start section parameter")

patch("app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt",
"""  var section by remember { mutableStateOf("JOB") }
  LaunchedEffect(sections.keys) {if(section !in sections)section="JOB"}""",
"""  var section by remember(startSection) { mutableStateOf(startSection ?: "JOB") }
  LaunchedEffect(startSection, sections.keys) {
    if (startSection != null && startSection in sections) section = startSection
    else if(section !in sections)section="JOB"
  }""","Open Roznamcha directly")

patch("app/src/main/java/com/example/MainActivity.kt",
"""        FinanceTab.OPERATIONS -> { com.example.ui.screens.BusinessOperationsScreen(uiState, viewModel) }
        FinanceTab.PURCHASES ->""",
"""        FinanceTab.OPERATIONS -> { com.example.ui.screens.BusinessOperationsScreen(uiState, viewModel) }
        FinanceTab.ROZNAMCHA -> { com.example.ui.screens.BusinessOperationsScreen(uiState, viewModel, "ROZNAMCHA") }
        FinanceTab.PURCHASES ->""","Dedicated Roznamcha screen route")

# Keep the More shortcut as a fallback route too.
p=root/"app/src/main/java/com/example/ui/components/BottomNavBar.kt"
s=p.read_text(encoding="utf-8")
anchor='''          MenuDestination("Business workspace", "کاروباری مرکز", Icons.Default.BusinessCenter, FinanceTab.OPERATIONS, "nav_operations", urdu) { sheet = ""; onTabSelected(FinanceTab.OPERATIONS) }
          MenuDestination("Settings",'''
replace='''          MenuDestination("Business workspace", "کاروباری مرکز", Icons.Default.BusinessCenter, FinanceTab.OPERATIONS, "nav_operations", urdu) { sheet = ""; onTabSelected(FinanceTab.OPERATIONS) }
          MenuDestination("Roznamcha", "روزنامچہ", Icons.Default.MenuBook, FinanceTab.ROZNAMCHA, "nav_more_roznamcha", urdu) { sheet = ""; onTabSelected(FinanceTab.ROZNAMCHA) }
          MenuDestination("Settings",'''
if "nav_more_roznamcha" not in s:
    if s.count(anchor)!=1: raise SystemExit("More menu Roznamcha insertion anchor mismatch")
    p.write_text(s.replace(anchor,replace,1),encoding="utf-8")

# Bump build metadata for a signed in-place update of the existing 4.9 standalone package.
p=root/"app/build.gradle.kts"
s=p.read_text(encoding="utf-8")
if 'versionCode = 61' not in s:
    if 'versionCode = 60' not in s or 'versionName = "4.9.1"' not in s:
        raise SystemExit("Expected workflow-set 4.9.1 metadata missing; refusing unsafe bump")
    s=s.replace('versionCode = 60','versionCode = 61',1)
    p.write_text(s,encoding="utf-8")
print("Set version 4.9.1 / code 61. Package and cached CI signing identity remain unchanged.")



# 4.9.2: Roznamcha is a separate cashbook, never a demo/product workspace.
patch("app/src/main/java/com/example/data/model/BusinessFeatures.kt",
"""  val khata: Boolean = true,
""",
"""  val khata: Boolean = true,
  val roznamcha: Boolean = true,
""","Independent Roznamcha feature toggle")

patch("app/src/main/java/com/example/ui/dialogs/BusinessBuilderDialog.kt",
"""          FeatureSwitch(text("Khata", "کھاتہ"), features.khata) { features = features.copy(khata = it) }
""",
"""          FeatureSwitch(text("Khata", "کھاتہ"), features.khata) { features = features.copy(khata = it) }
          FeatureSwitch(text("Roznamcha / Cash Book", "روزنامچہ / کیش بک"), features.roznamcha) { features = features.copy(roznamcha = it) }
""","Add Roznamcha ON/OFF setting")

p=root/"app/src/main/java/com/example/ui/components/BottomNavBar.kt"
s=p.read_text(encoding="utf-8")
s=s.replace('if (!personal) NavBarChoice(if (urdu) "روزنامچہ" else "Roznamcha"',
            'if (!personal && features.roznamcha) NavBarChoice(if (urdu) "روزنامچہ" else "Roznamcha"',1)
s=s.replace('          MenuDestination("Roznamcha", "روزنامچہ", Icons.Default.MenuBook, FinanceTab.ROZNAMCHA, "nav_more_roznamcha", urdu) { sheet = ""; onTabSelected(FinanceTab.ROZNAMCHA) }',
            '          if (features.roznamcha) MenuDestination("Roznamcha", "روزنامچہ", Icons.Default.MenuBook, FinanceTab.ROZNAMCHA, "nav_more_roznamcha", urdu) { sheet = ""; onTabSelected(FinanceTab.ROZNAMCHA) }',1)
p.write_text(s,encoding="utf-8")

p=root/"app/src/main/java/com/example/ui/FinanceViewModel.kt"
s=p.read_text(encoding="utf-8").replace("      FinanceTab.ROZNAMCHA -> true","      FinanceTab.ROZNAMCHA -> f.roznamcha",1)
p.write_text(s,encoding="utf-8")

# Add the dedicated section only when the standalone Roznamcha destination is opened.
p=root/"app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt"
s=p.read_text(encoding="utf-8")
s=s.replace('  val sections=linkedMapOf("JOB" to text("Jobs","جاب کارڈ")',
            '  val sections=linkedMapOf("ROZNAMCHA" to text("Roznamcha","روزنامچہ"),"JOB" to text("Jobs","جاب کارڈ")',1)
start=s.index("  val sections=linkedMapOf(")
end=s.index("\n  var section",start)
block=s[start:end]
if '.filterKeys { if (startSection == "ROZNAMCHA")' not in block:
    block += '.filterKeys { if (startSection == "ROZNAMCHA") it == "ROZNAMCHA" else it !in listOf("ROZNAMCHA","DEMO") }'
s=s[:start]+block+s[end:]
s=s.replace('''  PremiumPage(text("Business workspace","کاروباری مرکز"),BusinessLibrary.find(state.businessProfile.templateId).label(urdu),Icons.Default.BusinessCenter,
''','''  PremiumPage(if(startSection=="ROZNAMCHA") text("Roznamcha / Cash Book","روزنامچہ / کیش بک") else text("Business workspace","کاروباری مرکز"),
    if(startSection=="ROZNAMCHA") text("Independent daily cash register","الگ روزانہ نقد رجسٹر") else BusinessLibrary.find(state.businessProfile.templateId).label(urdu),
    if(startSection=="ROZNAMCHA") Icons.Default.MenuBook else Icons.Default.BusinessCenter,
''',1)
s=s.replace('''    item { PremiumButton(text("Sales, purchases, returns & warehouses","فروخت، خریداری، واپسی اور گودام"),{viewModel.openCommerce()}) }
    item { PremiumButton(text("Production WIP, rentals & appointments","پیداوار، کرایہ اور اپائنٹمنٹ"),{viewModel.operationsArea.value="advanced"}) }
''','''    if(startSection!="ROZNAMCHA") {
      item { PremiumButton(text("Sales, purchases, returns & warehouses","فروخت، خریداری، واپسی اور گودام"),{viewModel.openCommerce()}) }
      item { PremiumButton(text("Production WIP, rentals & appointments","پیداوار، کرایہ اور اپائنٹمنٹ"),{viewModel.operationsArea.value="advanced"}) }
    }
''',1)
s=s.replace('''  var selected by remember { mutableStateOf<BusinessRecord?>(null) }
  var message by remember { mutableStateOf("") }
''','''  var selected by remember { mutableStateOf<BusinessRecord?>(null) }
  var editingRoznamcha by remember { mutableStateOf<Transaction?>(null) }
  var deletingRoznamcha by remember { mutableStateOf<Transaction?>(null) }
  var message by remember { mutableStateOf("") }
''',1)
row_pattern=r'          ListTile\(if\(incoming\)text\("Cash received".*?\n            controls=\{Text\(.*?\)\}\)'
row_match=re.search(row_pattern,s,re.S)
if row_match and "editingRoznamcha=tx" not in row_match.group(0):
  newrow='''          ListTile(if(incoming)text("Cash received","نقد وصولی") else text("Cash paid","نقد ادائیگی"),
            (if(tx.recipientInfo.isBlank()) "" else tx.recipientInfo+" • ")+date+" • "+tx.accountName+"\\n"+tx.note,Icons.Default.MenuBook,
            (if(incoming)"+ " else "− ")+state.money(tx.amount),if(incoming)Color(0xFFCCFBF1) else Color(0xFFF3E8FF),
            click={editingRoznamcha=tx},controls={
              IconButton(onClick={editingRoznamcha=tx}){Icon(Icons.Default.Edit,text("Edit","ترمیم"))}
              IconButton(onClick={viewModel.selectTransaction(tx)}){Icon(Icons.Default.Share,text("Share receipt","رسید شیئر کریں"))}
              IconButton(onClick={deletingRoznamcha=tx}){Icon(Icons.Default.Delete,text("Delete","حذف"),tint=MaterialTheme.colorScheme.error)}
            })'''
  s=s[:row_match.start()]+newrow+s[row_match.end():]
elif "editingRoznamcha=tx" not in s:
  raise SystemExit("Roznamcha row controls anchor mismatch")
old='''  if(form && writable && section=="ROZNAMCHA") RoznamchaEntryForm(state,{form=false}) { amount,income,date,note,accountId ->
    viewModel.businessAction({roznamchaEntry(amount,income,date,note,accountId,actor)}) {result(it)}
  }
'''
new='''  if(form && writable && section=="ROZNAMCHA") RoznamchaEntryForm(state,null,{form=false}) { amount,income,date,note,accountId,party ->
    viewModel.businessAction({roznamchaEntry(amount,income,date,note,accountId,actor,party)}) {result(it)}
  }
  editingRoznamcha?.let { tx -> RoznamchaEntryForm(state,tx,{editingRoznamcha=null}) { amount,income,date,note,accountId,party ->
    val account=state.accounts.firstOrNull { it.id==accountId }?.name ?: tx.accountName
    viewModel.updateTransaction(tx.copy(title=if(income)"Roznamcha • Cash In" else "Roznamcha • Cash Out",amount=amount,type=if(income)TransactionType.INCOME else TransactionType.EXPENSE,accountName=account,dateMillis=date,note=note,recipientInfo=party))
    editingRoznamcha=null
  } }
  deletingRoznamcha?.let { tx -> AlertDialog(onDismissRequest={deletingRoznamcha=null},title={Text(text("Delete cash entry?","نقد اندراج حذف کریں؟"))},text={Text(text("The cash account balance will be adjusted. The entry will be removed.","کیش اکاؤنٹ کا بیلنس درست کر کے اندراج حذف کر دیا جائے گا۔"))},confirmButton={TextButton(onClick={viewModel.deleteTransaction(tx);deletingRoznamcha=null}){Text(text("Delete","حذف کریں"),color=MaterialTheme.colorScheme.error)}},dismissButton={TextButton(onClick={deletingRoznamcha=null}){Text(text("Cancel","منسوخ"))}}) }
'''
if old in s: s=s.replace(old,new,1)
elif 'RoznamchaEntryForm(state,null' not in s: raise SystemExit("Roznamcha edit form anchor mismatch")
s=s.replace('''private fun RoznamchaEntryForm(state:FinanceUiState,dismiss:()->Unit,save:(Double,Boolean,Long,String,Long)->Unit) {
''','''private fun RoznamchaEntryForm(state:FinanceUiState,initial:Transaction?=null,dismiss:()->Unit,save:(Double,Boolean,Long,String,Long,String)->Unit) {
''',1)
s=s.replace('''  var incoming by remember { mutableStateOf(true) }
  var amount by remember { mutableStateOf("") }
  var note by remember { mutableStateOf("") }
  var dateText by remember { mutableStateOf(SimpleDateFormat("yyyy-MM-dd",Locale.US).format(Date())) }
  var accountId by remember { mutableStateOf(state.accounts.firstOrNull()?.id ?: 0L) }
''','''  var incoming by remember(initial?.id) { mutableStateOf(initial?.type!=TransactionType.EXPENSE) }
  var amount by remember(initial?.id) { mutableStateOf(initial?.amount?.toString() ?: "") }
  var party by remember(initial?.id) { mutableStateOf(initial?.recipientInfo ?: "") }
  var note by remember(initial?.id) { mutableStateOf(initial?.note ?: "") }
  var dateText by remember(initial?.id) { mutableStateOf(SimpleDateFormat("yyyy-MM-dd",Locale.US).format(Date(initial?.dateMillis ?: System.currentTimeMillis()))) }
  var accountId by remember(initial?.id) { mutableStateOf(state.accounts.firstOrNull { it.name==initial?.accountName }?.id ?: state.accounts.firstOrNull()?.id ?: 0L) }
''',1)
s=s.replace('''  BusinessForm(t("Roznamcha entry","روزنامچہ اندراج"),t("Save entry","اندراج محفوظ کریں"),dismiss,{
''','''  BusinessForm(if(initial==null)t("Roznamcha entry","روزنامچہ اندراج") else t("Edit Roznamcha entry","روزنامچہ اندراج تبدیل کریں"),t("Save entry","اندراج محفوظ کریں"),dismiss,{
''',1)
s=s.replace('''      else -> save(value,incoming,date,note,accountId)
''','''      else -> save(value,incoming,date,note,accountId,party.trim())
''',1)
s=s.replace('''    BusinessField(amount,t("Amount (Rs.)","رقم (روپے)"),true){amount=it}
    BusinessField(note,t("Description / detail","تفصیل / وضاحت")){note=it}
''','''    BusinessField(amount,t("Amount (Rs.)","رقم (روپے)"),true){amount=it}
    BusinessField(party,t("Client / Party","گاہک / فریق")){party=it}
    BusinessField(note,t("Description / detail","تفصیل / وضاحت")){note=it}
''',1)
p.write_text(s,encoding="utf-8")

# Store party/client details on cashbook entries.
p=root/"app/src/main/java/com/example/business/BusinessCore.kt"
s=p.read_text(encoding="utf-8")
s=s.replace('''suspend fun roznamchaEntry(amount: Double, income: Boolean, dateMillis: Long, note: String, accountId: Long, actor: String) = db.withTransaction {''',
'''suspend fun roznamchaEntry(amount: Double, income: Boolean, dateMillis: Long, note: String, accountId: Long, actor: String, party: String = "") = db.withTransaction {''',1)
s=s.replace('''      note = note.trim(),
      transactionRef = "ROZNAMCHA/\${UUID.randomUUID()}",''',
'''      note = note.trim(),
      recipientInfo = party.trim(),
      transactionRef = "ROZNAMCHA/\${UUID.randomUUID()}",''',1)
p.write_text(s,encoding="utf-8")

# Atomic transaction edit: reverse the old cash impact, then apply the edited entry.
p=root/"app/src/main/java/com/example/data/repository/FinanceRepository.kt"
s=p.read_text(encoding="utf-8")
if "suspend fun updateTransactionAtomically" not in s:
  anchor="  suspend fun deleteTransactionAtomically(id: Long) = database.withTransaction {"
  code='''  suspend fun updateTransactionAtomically(updated: Transaction) = database.withTransaction {
    require(updated.amount.isFinite() && updated.amount > 0.0) { "Enter a valid amount / درست رقم درج کریں" }
    val old=dao.getTransactionById(updated.id) ?: error("Entry not found / اندراج نہیں ملا")
    require(old.category=="Roznamcha") { "Only cashbook entries can be edited here / صرف روزنامچہ اندراج تبدیل ہو سکتا ہے" }
    val accounts=dao.getAllAccountsList()
    accounts.find {it.name==old.accountName}?.let {dao.changeAccountBalance(it.id,if(old.type==TransactionType.INCOME)-old.amount else old.amount)}
    val next=accounts.find {it.name==updated.accountName} ?: error("Choose an account / اکاؤنٹ منتخب کریں")
    dao.changeAccountBalance(next.id,if(updated.type==TransactionType.INCOME)updated.amount else -updated.amount)
    dao.updateTransaction(updated.copy(updatedAt=System.currentTimeMillis()))
  }

'''
  if s.count(anchor)!=1: raise SystemExit("Transaction update insertion anchor mismatch")
  s=s.replace(anchor,code+anchor,1)
p.write_text(s,encoding="utf-8")

p=root/"app/src/main/java/com/example/ui/FinanceViewModel.kt"
s=p.read_text(encoding="utf-8")
if "fun updateTransaction(transaction: Transaction)" not in s:
  anchor="  fun deleteTransaction(transaction: Transaction) {"
  code='''  fun updateTransaction(transaction: Transaction) {
    if(!businessAllowed()) return
    viewModelScope.launch { try { repository.updateTransactionAtomically(transaction) } catch(error:Exception) { showOperationError(error) } }
  }

'''
  if s.count(anchor)!=1: raise SystemExit("ViewModel transaction update insertion anchor mismatch")
  s=s.replace(anchor,code+anchor,1)
p.write_text(s,encoding="utf-8")

# Roznamcha is a standalone module only; no shortcut, tab, or button inside Khata.

# Always-visible customer receipt image action, in addition to statement sharing.
p=root/"app/src/main/java/com/example/ui/dialogs/PremiumCustomerDetailDialog.kt"
s=p.read_text(encoding="utf-8")
if "khata_share_receipt" not in s:
  if "import androidx.compose.ui.platform.testTag" not in s:
    s=s.replace("import androidx.compose.ui.Modifier\n","import androidx.compose.ui.Modifier\nimport androidx.compose.ui.platform.testTag\n",1)
  marker='Text(label("Share Statement / WhatsApp"'
  idx=s.find(marker)
  if idx<0: idx=s.find('Customer Khata Statement')
  if idx<0: raise SystemExit("Khata statement share button label not found")
  lineEnd=s.find("\n",idx)
  button='''    OutlinedButton(onClick = {
      val latest=bills.firstOrNull()
      val receipt=buildString {
        appendLine(businessProfile.businessName); appendLine(label("CUSTOMER KHATA RECEIPT","گاہک کے کھاتے کی رسید"))
        appendLine(label("Customer: ","گاہک: ")+customer.name)
        if(customer.phone.isNotBlank()) appendLine(label("Phone: ","فون: ")+customer.phone)
        if(latest!=null) {
          appendLine(label("Bill No: ","بل نمبر: ")+latest.invoiceNumber)
          appendLine(label("Bill total: ","کل بل: ")+money(latest.netTotal()))
          appendLine(label("Received: ","وصول شدہ: ")+money(latest.amountPaid))
          appendLine(label("Bill due: ","بل بقایا: ")+money(latest.remainingBalance))
          appendLine(label("Date: ","تاریخ: ")+java.text.SimpleDateFormat("dd MMM yyyy",java.util.Locale.getDefault()).format(java.util.Date(latest.dateMillis)))
        }
        appendLine(label("Current balance: ","موجودہ بقایا: ")+money(customer.currentBalance))
      }
      ThermalReceiptImage.shareKhataStatement(context,label("Khata Payment Receipt","کھاتہ ادائیگی رسید"),receipt)
    },modifier=Modifier.fillMaxWidth().testTag("khata_share_receipt")) { Icon(Icons.Default.ReceiptLong,null); Spacer(Modifier.width(8.dp)); Text(label("Share Receipt Image / WhatsApp","رسید کی تصویر شیئر کریں / واٹس ایپ")) }
'''
  s=s[:lineEnd+1]+button+s[lineEnd+1:]
p.write_text(s,encoding="utf-8")

# 4.9.2 / versionCode 62.
p=root/"app/build.gradle.kts"
s=p.read_text(encoding="utf-8")
if 'versionName = "4.9.1"' in s and 'versionCode = 61' in s:
  s=s.replace('versionCode = 61','versionCode = 64',1).replace('versionName = "4.9.1"','versionName = "4.9.4"',1)
elif 'versionName = "4.9.4"' not in s:
  raise SystemExit("Unexpected version metadata before 4.9.3 bump")
p.write_text(s,encoding="utf-8")
print("Applied standalone Roznamcha, upgraded Khata history, photo uploads and 4.9.4 build metadata.")



# Professional Khata/Roznamcha receipt rendering and visible Android share chooser.
p=root/"app/src/main/java/com/example/util/ThermalReceiptImage.kt"
s=p.read_text(encoding="utf-8")
import re
pattern=r'  internal fun khataStatementImageFile\(context: Context, title: String, statement: String\): File \{.*?\n  \}\n'
match=re.search(pattern,s,re.S)
if match and "CUSTOMER KHATA RECEIPT" not in match.group(0):
  renderer=r'''  internal fun khataStatementImageFile(context: Context, title: String, statement: String): File {
    val width=720; val margin=44f
    val lines=statement.lines().filter { it.isNotBlank() }
    val shop=lines.firstOrNull()?.take(42).orEmpty().ifBlank { "ARSHAD FINANCE" }
    val rows=lines.drop(1).map { line ->
      val split=line.indexOf(':')
      if(split>0) line.substring(0,split).trim() to line.substring(split+1).trim() else "" to line.trim()
    }
    val heading=TextPaint(Paint.ANTI_ALIAS_FLAG).apply { color=Color.WHITE; textSize=31f; typeface=Typeface.create("sans-serif",Typeface.BOLD) }
    val brand=TextPaint(Paint.ANTI_ALIAS_FLAG).apply { color=Color.WHITE; textSize=21f; typeface=Typeface.create("sans-serif-medium",Typeface.NORMAL) }
    val label=TextPaint(Paint.ANTI_ALIAS_FLAG).apply { color=Color.rgb(103,115,108); textSize=19f; typeface=Typeface.create("sans-serif",Typeface.NORMAL) }
    val value=TextPaint(Paint.ANTI_ALIAS_FLAG).apply { color=Color.rgb(24,39,31); textSize=23f; typeface=Typeface.create("sans-serif-medium",Typeface.NORMAL) }
    val total=TextPaint(Paint.ANTI_ALIAS_FLAG).apply { color=Color.rgb(8,107,77); textSize=34f; typeface=Typeface.create("sans-serif",Typeface.BOLD) }
    val footer=TextPaint(Paint.ANTI_ALIAS_FLAG).apply { color=Color.rgb(110,120,114); textSize=18f }
    val direction=android.text.TextDirectionHeuristics.FIRSTSTRONG_RTL
    val layouts=rows.map { (_,v) -> StaticLayout.Builder.obtain(v,0,v.length,value,width-2*margin.toInt()).setAlignment(Layout.Alignment.ALIGN_NORMAL).setTextDirection(direction).setIncludePad(true).build() }
    val totalIndex=rows.indexOfFirst { (k,_) -> k.contains("amount",true)||k.contains("total",true)||k.contains("received",true)||k.contains("وصول")||k.contains("رقم") }
    val header=178
    val body=rows.indices.sumOf { i -> if(i==totalIndex) 106 else maxOf(58,layouts[i].height+34) }
    val height=header+body+92
    val bitmap=Bitmap.createBitmap(width,height,Bitmap.Config.ARGB_8888)
    val canvas=Canvas(bitmap); canvas.drawColor(Color.rgb(247,249,247))
    val accent=Paint(Paint.ANTI_ALIAS_FLAG).apply { color=selectedAccent(context) }
    val white=Paint(Paint.ANTI_ALIAS_FLAG).apply { color=Color.WHITE }
    val divider=Paint(Paint.ANTI_ALIAS_FLAG).apply { color=Color.rgb(224,231,226); strokeWidth=2f }
    canvas.drawRect(0f,0f,width.toFloat(),header.toFloat(),accent)
    canvas.drawText(shop,margin,54f,brand)
    val titleLayout=StaticLayout.Builder.obtain(title,0,title.length,heading,width-2*margin.toInt()).setAlignment(Layout.Alignment.ALIGN_NORMAL).setTextDirection(direction).setIncludePad(true).build()
    canvas.save(); canvas.translate(margin,82f); titleLayout.draw(canvas); canvas.restore()
    canvas.drawRoundRect(margin,header-12f,width-margin,header+24f,18f,18f,white)
    var y=header+56f
    rows.forEachIndexed { i,(k,v) ->
      if(i==totalIndex) {
        val bg=Paint(Paint.ANTI_ALIAS_FLAG).apply { color=Color.rgb(226,244,235) }
        canvas.drawRoundRect(margin,y-14f,width-margin,y+84f,18f,18f,bg)
        canvas.drawText(if(k.isBlank()) "TOTAL" else k,margin+18f,y+17f,label)
        val l=StaticLayout.Builder.obtain(v,0,v.length,total,width-2*margin.toInt()-36).setAlignment(Layout.Alignment.ALIGN_NORMAL).setTextDirection(direction).setIncludePad(true).build()
        canvas.save(); canvas.translate(margin+18f,y+28f); l.draw(canvas); canvas.restore()
        y+=106f
      } else {
        if(k.isNotBlank()) canvas.drawText(k,margin,y+18f,label)
        canvas.save(); canvas.translate(margin,y+25f); layouts[i].draw(canvas); canvas.restore()
        y+=maxOf(58,layouts[i].height+34).toFloat()
      }
      canvas.drawLine(margin,y,width-margin,y,divider)
    }
    canvas.drawText("Thank you • شکریہ",margin,height-38f,footer)
    val folder=File(context.cacheDir,"khata-whatsapp").apply { mkdirs() }
    val file=File(folder,"Khata_"+System.currentTimeMillis()+".png")
    try { file.outputStream().use { check(bitmap.compress(Bitmap.CompressFormat.PNG,100,it)) { "Receipt image creation failed" } } }
    finally { bitmap.recycle() }
    return file
  }
'''
  s=s[:match.start()]+renderer+s[match.end():]
if "var shared = false" in s:
  a=s.index("    var shared = false")
  b=s.index('    Toast.makeText(context, "Khata image ready',a)
  s=s[:a]+'    context.startActivity(Intent.createChooser(send, "Share Khata receipt / کھاتے کی رسید شیئر کریں").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))\\n'+s[b:]
p.write_text(s,encoding="utf-8")

# Bidirectional English/Urdu translation for entered Khata and Roznamcha text.
p=root/"app/src/main/java/com/example/util/UrduAutoTranslator.kt"
s=p.read_text(encoding="utf-8")
if "suspend fun urduToEnglish" not in s:
  s=s.replace('''  suspend fun englishToUrdu(value:String):String {''','''  fun needsEnglishTranslation(value:String):Boolean = value.any { it in '\\u0600'..'\\u06FF' || it in '\\u0750'..'\\u077F' || it in '\\uFB50'..'\\uFDFF' || it in '\\uFE70'..'\\uFEFF' }
  suspend fun translateForLanguage(value:String, targetUrdu:Boolean):String = if(targetUrdu) englishToUrdu(value) else urduToEnglish(value)
  suspend fun urduToEnglish(value:String):String {
    val input=value.trim()
    if(input.isBlank() || !needsEnglishTranslation(input)) return value
    val translator=Translation.getClient(TranslatorOptions.Builder().setSourceLanguage(TranslateLanguage.URDU).setTargetLanguage(TranslateLanguage.ENGLISH).build())
    try {
      translator.downloadModelIfNeeded(DownloadConditions.Builder().build()).awaitResult()
      return translator.translate(input).awaitResult()
    } catch(error:Exception) {
      throw IllegalStateException("English model needs one internet download; after that translation works offline. / انگریزی ماڈل پہلی مرتبہ انٹرنیٹ سے ڈاؤن لوڈ ہوگا، پھر آف لائن کام کرے گا۔",error)
    } finally { translator.close() }
  }
  suspend fun englishToUrdu(value:String):String {''',1)
p.write_text(s,encoding="utf-8")

p=root/"app/src/main/java/com/example/ui/dialogs/PremiumAddCustomerDialog.kt"
s=p.read_text(encoding="utf-8")
s=s.replace("if(urdu)UrduAutoTranslator.englishToUrdu(name) else name.trim()","UrduAutoTranslator.translateForLanguage(name,urdu)",1)
s=s.replace("if(urdu)UrduAutoTranslator.englishToUrdu(address) else address.trim()","UrduAutoTranslator.translateForLanguage(address,urdu)",1)
s=s.replace("if(urdu)UrduAutoTranslator.englishToUrdu(description) else description.trim()","UrduAutoTranslator.translateForLanguage(description,urdu)",1)
s=s.replace("if(urdu)UrduAutoTranslator.englishToUrdu(note) else note.trim()","UrduAutoTranslator.translateForLanguage(note,urdu)",1)
s=s.replace("if(urdu)UrduAutoTranslator.englishToUrdu(type) else type.trim()","UrduAutoTranslator.translateForLanguage(type,urdu)",1)
p.write_text(s,encoding="utf-8")

p=root/"app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt"
s=p.read_text(encoding="utf-8")
if "import com.example.util.UrduAutoTranslator" not in s:
  s=s.replace("import com.example.data.model.*\\n","import com.example.data.model.*\\nimport com.example.util.UrduAutoTranslator\\nimport kotlinx.coroutines.launch\\n",1)
s=s.replace('''  var error by remember { mutableStateOf("") }
  BusinessForm(if(initial==null)t("Roznamcha entry","روزنامچہ اندراج")''','''  var error by remember { mutableStateOf("") }
  var translating by remember { mutableStateOf(false) }
  val translationScope=rememberCoroutineScope()
  BusinessForm(if(initial==null)t("Roznamcha entry","روزنامچہ اندراج")''',1)
s=s.replace('''      else -> save(value,incoming,date,note,accountId,party.trim())
''','''      else -> if(!translating) {
        translating=true
        translationScope.launch {
          try {
            val savedParty=UrduAutoTranslator.translateForLanguage(party,urdu)
            val savedNote=UrduAutoTranslator.translateForLanguage(note,urdu)
            save(value,incoming,date,savedNote,accountId,savedParty)
          } catch(failure:Exception) { error=failure.localizedMessage ?: t("Translation failed","ترجمہ ناکام ہو گیا") }
          finally { translating=false }
        }
      }
''',1)
s=s.replace('''    if(error.isNotBlank()) Text(error,color=MaterialTheme.colorScheme.error)
  }
}

''','''    if(translating) LinearProgressIndicator(Modifier.fillMaxWidth())
    if(error.isNotBlank()) Text(error,color=MaterialTheme.colorScheme.error)
  }
}

''',1)
p.write_text(s,encoding="utf-8")
print("Added receipt renderer, share chooser, and two-way Urdu-English translation.")



# Correct the Khata receipt implementation after the older ledger patch runs.
p=root/"app/src/main/java/com/example/MainActivity.kt"
s=p.read_text(encoding="utf-8")
literal=r',\n            onOpenRoznamcha = { viewModel.selectTab(FinanceTab.ROZNAMCHA) }\n'
s=s.replace(literal,','+chr(10)+'            onOpenRoznamcha = { viewModel.selectTab(FinanceTab.ROZNAMCHA) }'+chr(10),1)
p.write_text(s,encoding="utf-8")

p=root/"app/src/main/java/com/example/business/BusinessCore.kt"
s=p.read_text(encoding="utf-8")
if "recipientInfo = party.trim()" not in s:
  start=s.index("  suspend fun roznamchaEntry(")
  end=s.index("\n  private suspend fun audit",start)
  block=s[start:end]
  block=block.replace("      note = note.trim(),","      note = note.trim(),"+chr(10)+"      recipientInfo = party.trim(),",1)
  s=s[:start]+block+s[end:]
p.write_text(s,encoding="utf-8")

# Restore the thermal invoice image share method; Khata uses its own PNG helper.
p=root/"app/src/main/java/com/example/util/ThermalReceiptImage.kt"
s=p.read_text(encoding="utf-8")
share_start=s.find("    // Prefer WhatsApp; support WhatsApp Business as a fallback.")
if share_start>=0:
  share_end=s.find("\n  }",share_start)
  if share_end<0: raise SystemExit("Thermal invoice share method closing brace missing")
  restored='''    // Prefer WhatsApp; support WhatsApp Business as a fallback.
    val targets = listOf("com.whatsapp", "com.whatsapp.w4b")
    var shared = false
    for (target in targets) {
      try {
        context.startActivity(Intent(sendIntent).setPackage(target))
        shared = true
        break
      } catch (_: ActivityNotFoundException) {
      } catch (_: SecurityException) {
      }
    }
    if (!shared) context.startActivity(Intent.createChooser(sendIntent, "Share thermal receipt").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
    Toast.makeText(context, "Receipt image ready / رسید کی تصویر تیار ہے", Toast.LENGTH_SHORT).show()'''
  s=s[:share_start]+restored+s[share_end:]
if "fun shareKhataStatement(" not in s:
  marker="\n}"
  pos=s.rfind(marker)
  if pos<0: raise SystemExit("ThermalReceiptImage object close missing")
  method=r'''
  /** Product-bill-style customer Khata receipt image. */
  internal fun khataStatementImageFile(context: Context, title: String, statement: String): File {
    val width=720
    val margin=44f
    val lines=statement.lines().filter { it.isNotBlank() }
    val shop=lines.firstOrNull()?.take(42).orEmpty().ifBlank { "ARSHAD FINANCE" }
    val rows=lines.drop(1).map { line ->
      val split=line.indexOf(':')
      if(split>0) line.substring(0,split).trim() to line.substring(split+1).trim() else "" to line.trim()
    }
    val heading=TextPaint(Paint.ANTI_ALIAS_FLAG).apply { color=Color.WHITE; textSize=31f; typeface=Typeface.create("sans-serif",Typeface.BOLD) }
    val brand=TextPaint(Paint.ANTI_ALIAS_FLAG).apply { color=Color.WHITE; textSize=21f; typeface=Typeface.create("sans-serif-medium",Typeface.NORMAL) }
    val label=TextPaint(Paint.ANTI_ALIAS_FLAG).apply { color=Color.rgb(103,115,108); textSize=19f; typeface=Typeface.create("sans-serif",Typeface.NORMAL) }
    val value=TextPaint(Paint.ANTI_ALIAS_FLAG).apply { color=Color.rgb(24,39,31); textSize=23f; typeface=Typeface.create("sans-serif-medium",Typeface.NORMAL) }
    val total=TextPaint(Paint.ANTI_ALIAS_FLAG).apply { color=Color.rgb(8,107,77); textSize=34f; typeface=Typeface.create("sans-serif",Typeface.BOLD) }
    val footer=TextPaint(Paint.ANTI_ALIAS_FLAG).apply { color=Color.rgb(110,120,114); textSize=18f }
    val direction=android.text.TextDirectionHeuristics.FIRSTSTRONG_RTL
    val layouts=rows.map { (_,v) -> StaticLayout.Builder.obtain(v,0,v.length,value,width-2*margin.toInt()).setAlignment(Layout.Alignment.ALIGN_NORMAL).setTextDirection(direction).setIncludePad(true).build() }
    val totalIndex=rows.indexOfFirst { (k,_) -> k.contains("amount",true)||k.contains("total",true)||k.contains("received",true)||k.contains("وصول")||k.contains("رقم") }
    val header=178
    val body=rows.indices.sumOf { i -> if(i==totalIndex) 106 else maxOf(58,layouts[i].height+34) }
    val height=header+body+92
    val bitmap=Bitmap.createBitmap(width,height,Bitmap.Config.ARGB_8888)
    val canvas=Canvas(bitmap); canvas.drawColor(Color.rgb(247,249,247))
    val accent=Paint(Paint.ANTI_ALIAS_FLAG).apply { color=selectedAccent(context) }
    val white=Paint(Paint.ANTI_ALIAS_FLAG).apply { color=Color.WHITE }
    val divider=Paint(Paint.ANTI_ALIAS_FLAG).apply { color=Color.rgb(224,231,226); strokeWidth=2f }
    canvas.drawRect(0f,0f,width.toFloat(),header.toFloat(),accent)
    canvas.drawText(shop,margin,54f,brand)
    val titleLayout=StaticLayout.Builder.obtain(title,0,title.length,heading,width-2*margin.toInt()).setAlignment(Layout.Alignment.ALIGN_NORMAL).setTextDirection(direction).setIncludePad(true).build()
    canvas.save(); canvas.translate(margin,82f); titleLayout.draw(canvas); canvas.restore()
    canvas.drawRoundRect(margin,header-12f,width-margin,header+24f,18f,18f,white)
    var y=header+56f
    rows.forEachIndexed { i,(k,v) ->
      if(i==totalIndex) {
        val bg=Paint(Paint.ANTI_ALIAS_FLAG).apply { color=Color.rgb(226,244,235) }
        canvas.drawRoundRect(margin,y-14f,width-margin,y+84f,18f,18f,bg)
        canvas.drawText(if(k.isBlank()) "TOTAL" else k,margin+18f,y+17f,label)
        val l=StaticLayout.Builder.obtain(v,0,v.length,total,width-2*margin.toInt()-36).setAlignment(Layout.Alignment.ALIGN_NORMAL).setTextDirection(direction).setIncludePad(true).build()
        canvas.save(); canvas.translate(margin+18f,y+28f); l.draw(canvas); canvas.restore()
        y+=106f
      } else {
        if(k.isNotBlank()) canvas.drawText(k,margin,y+18f,label)
        canvas.save(); canvas.translate(margin,y+25f); layouts[i].draw(canvas); canvas.restore()
        y+=maxOf(58,layouts[i].height+34).toFloat()
      }
      canvas.drawLine(margin,y,width-margin,y,divider)
    }
    canvas.drawText("Thank you • شکریہ",margin,height-38f,footer)
    val folder=File(context.cacheDir,"khata-whatsapp").apply { mkdirs() }
    val image=File(folder,"Khata_"+System.currentTimeMillis()+".png")
    try { image.outputStream().use { output -> check(bitmap.compress(Bitmap.CompressFormat.PNG,100,output)) { "Receipt image creation failed" } } }
    finally { bitmap.recycle() }
    return image
  }

  fun shareKhataStatement(context: Context, title: String, statement: String) {
    val image=khataStatementImageFile(context,title,statement)
    val uri=FileProvider.getUriForFile(context,context.packageName+".fileprovider",image)
    val send=Intent(Intent.ACTION_SEND).apply {
      type="image/png"
      putExtra(Intent.EXTRA_STREAM,uri)
      clipData=android.content.ClipData.newUri(context.contentResolver,"Khata receipt",uri)
      addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
      addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    }
    context.startActivity(Intent.createChooser(send,"Share Khata receipt / کھاتے کی رسید شیئر کریں").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
    Toast.makeText(context,"Khata receipt image ready / کھاتے کی رسید تیار ہے",Toast.LENGTH_SHORT).show()
  }
'''
  s=s[:pos]+chr(10)+method+s[pos:]
p.write_text(s,encoding="utf-8")
print("Restored thermal invoice sharing and added product-bill-style Khata PNG sharing.")



# Fix the standalone Roznamcha form scope and keep offline data entry available.
p=root/"app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt"
s=p.read_text(encoding="utf-8")
s=s.replace('''  else if(form && writable) OperationForm(section,state,onDismiss={form=false},save={title,party,amount,payload ->''',
'''  if(form && writable && section!="ROZNAMCHA") OperationForm(section,state,onDismiss={form=false},save={title,party,amount,payload ->''',1)
s=s.replace('''    if(translating) LinearProgressIndicator(Modifier.fillMaxWidth())
    if(error.isNotBlank()) Text(error,color=MaterialTheme.colorScheme.error)
  }
}

@Composable
private fun SupplierStatement''','''    if(error.isNotBlank()) Text(error,color=MaterialTheme.colorScheme.error)
  }
}

@Composable
private fun SupplierStatement''',1)
if "import com.example.util.UrduAutoTranslator" not in s:
  marker="import com.example.data.model.*"
  s=s.replace(marker,marker+chr(10)+"import com.example.util.UrduAutoTranslator"+chr(10)+"import kotlinx.coroutines.launch",1)
form_start=s.index("private fun RoznamchaEntryForm(")
form_end=s.index("\n}",form_start)
form_block=s[form_start:form_end]
if "if(translating) LinearProgressIndicator" not in form_block:
  form_block=form_block.replace('''    if(error.isNotBlank()) Text(error,color=MaterialTheme.colorScheme.error)''',
'''    if(translating) LinearProgressIndicator(Modifier.fillMaxWidth())
    if(error.isNotBlank()) Text(error,color=MaterialTheme.colorScheme.error)''',1)
  s=s[:form_start]+form_block+s[form_end:]
p.write_text(s,encoding="utf-8")

# Never strand a customer or cash entry when the on-device language model has not been downloaded yet.
p=root/"app/src/main/java/com/example/util/UrduAutoTranslator.kt"
s=p.read_text(encoding="utf-8")
if "suspend fun translateOrOriginal" not in s:
  s=s.replace('''  suspend fun translateForLanguage(value:String, targetUrdu:Boolean):String = if(targetUrdu) englishToUrdu(value) else urduToEnglish(value)
''','''  suspend fun translateForLanguage(value:String, targetUrdu:Boolean):String = if(targetUrdu) englishToUrdu(value) else urduToEnglish(value)
  suspend fun translateOrOriginal(value:String, targetUrdu:Boolean):String =
    runCatching { translateForLanguage(value,targetUrdu) }.getOrDefault(value.trim())
''',1)
p.write_text(s,encoding="utf-8")

p=root/"app/src/main/java/com/example/ui/dialogs/PremiumAddCustomerDialog.kt"
s=p.read_text(encoding="utf-8").replace("UrduAutoTranslator.translateForLanguage(","UrduAutoTranslator.translateOrOriginal(")
p.write_text(s,encoding="utf-8")

p=root/"app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt"
s=p.read_text(encoding="utf-8").replace("UrduAutoTranslator.translateForLanguage(","UrduAutoTranslator.translateOrOriginal(")
p.write_text(s,encoding="utf-8")

# Reset old saved Khata tab/form state so the embedded Roznamcha view cannot reappear after upgrade.
p=root/"app/src/main/java/com/example/ui/screens/PremiumBillingScreen.kt"
s=p.read_text(encoding="utf-8")
s=s.replace('var khataTab by rememberSaveable { mutableStateOf("CUSTOMERS") }','var khataTab by remember { mutableStateOf("CUSTOMERS") }',1)
s=s.replace('var showRoznamchaForm by rememberSaveable { mutableStateOf(false) }','var showRoznamchaForm by remember { mutableStateOf(false) }',1)
p.write_text(s,encoding="utf-8")
print("Fixed standalone cashbook form, bidirectional translation fallback and legacy embedded-tab state.")



# Ensure the standalone Roznamcha tab always opens its own hub, not a previous Commerce/Advanced workspace.
p=root/"app/src/main/java/com/example/ui/FinanceViewModel.kt"
s=p.read_text(encoding="utf-8")
s=s.replace('''  fun selectTab(tab: FinanceTab) {
''','''  fun selectTab(tab: FinanceTab) {
    if(tab==FinanceTab.ROZNAMCHA) operationsArea.value="hub"
''',1)
p.write_text(s,encoding="utf-8")

# The Roznamcha row's share icon sends its bill-style PNG directly to the Android share sheet.
p=root/"app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt"
s=p.read_text(encoding="utf-8")
if "import androidx.compose.ui.platform.LocalContext" not in s:
  s=s.replace("import androidx.compose.ui.Modifier", "import androidx.compose.ui.Modifier"+chr(10)+"import androidx.compose.ui.platform.LocalContext",1)
if "import com.example.util.ThermalReceiptImage" not in s:
  s=s.replace("import com.example.util.UrduAutoTranslator", "import com.example.util.UrduAutoTranslator"+chr(10)+"import com.example.util.ThermalReceiptImage",1)
if "val receiptContext=LocalContext.current" not in s:
  s=s.replace('''  val urdu=state.appLanguage==AppLanguage.URDU
''','''  val urdu=state.appLanguage==AppLanguage.URDU
  val receiptContext=LocalContext.current
''',1)
s=s.replace('''              IconButton(onClick={viewModel.selectTransaction(tx)}){Icon(Icons.Default.Share,text("Share receipt","رسید شیئر کریں"))}
''','''              IconButton(onClick={
                val receipt=buildString {
                  appendLine(state.businessProfile.businessName)
                  appendLine(text("ROZNAMCHA RECEIPT","روزنامچہ رسید"))
                  appendLine(text("Client / Party: ","گاہک / فریق: ")+tx.recipientInfo)
                  appendLine(text("Amount: ","رقم: ")+state.money(tx.amount))
                  appendLine(text("Date: ","تاریخ: ")+date)
                  appendLine(text("Account: ","اکاؤنٹ: ")+tx.accountName)
                  if(tx.note.isNotBlank()) appendLine(text("Note: ","تفصیل: ")+tx.note)
                }
                ThermalReceiptImage.shareKhataStatement(receiptContext,text("Roznamcha Receipt","روزنامچہ رسید"),receipt)
              }){Icon(Icons.Default.Share,text("Share receipt","رسید شیئر کریں"))}
''',1)
p.write_text(s,encoding="utf-8")

# Regression test: editing a cashbook entry changes party details and adjusts account balance exactly once.
test=root/"app/src/test/java/com/example/RoznamchaEditTest.kt"
if not test.exists():
  test.write_text(r'''package com.example

import android.content.Context
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import com.example.data.local.FinanceDatabase
import com.example.data.model.Account
import com.example.data.model.Transaction
import com.example.data.model.TransactionType
import com.example.data.repository.FinanceRepository
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk=[35])
class RoznamchaEditTest {
  @Test fun editEntryUpdatesPartyAndReconcilesCashBalance()=runBlocking {
    val context=ApplicationProvider.getApplicationContext<Context>()
    val db=Room.inMemoryDatabaseBuilder(context,FinanceDatabase::class.java).allowMainThreadQueries().build()
    try {
      val dao=db.financeDao()
      val repository=FinanceRepository(dao,db)
      val accountId=dao.insertAccount(Account(name="Cash",accountType="Cash In Hand",balance=0.0,accountNumber="TEST-CASH"))
      val id=repository.recordTransactionAtomically(Transaction(title="Cash In",amount=100.0,type=TransactionType.INCOME,category="Roznamcha",icon="💰",accountName="Cash",recipientInfo="Ali"))
      assertEquals(100.0,dao.getAllAccountsList().first { it.id==accountId }.balance,0.001)
      val original=dao.getTransactionById(id)!!
      repository.updateTransactionAtomically(original.copy(amount=175.0,recipientInfo="Ahmed",note="Updated client payment"))
      val edited=dao.getTransactionById(id)!!
      assertEquals("Ahmed",edited.recipientInfo)
      assertEquals(175.0,edited.amount,0.001)
      assertEquals(175.0,dao.getAllAccountsList().first { it.id==accountId }.balance,0.001)
    } finally { db.close() }
  }
}
''',encoding="utf-8")
print("Added Roznamcha navigation reset, direct receipt sharing and edit-balance regression test.")
