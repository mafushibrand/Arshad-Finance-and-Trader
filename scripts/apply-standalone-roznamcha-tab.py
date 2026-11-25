from pathlib import Path
import sys

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
old='''          ListTile(if(incoming)text("Cash received","نقد وصولی") else text("Cash paid","نقد ادائیگی"),
            date+" • "+tx.accountName+"\\\\n"+tx.note,Icons.Default.MenuBook,
            controls={Text((if(incoming)"+ " else "− ")+state.money(tx.amount),fontWeight=FontWeight.Bold,color=if(incoming)Color(0xFF0F766E) else Color(0xFFB45309))})
'''
new='''          ListTile(if(incoming)text("Cash received","نقد وصولی") else text("Cash paid","نقد ادائیگی"),
            (if(tx.recipientInfo.isBlank()) "" else tx.recipientInfo+" • ")+date+" • "+tx.accountName+"\\\\n"+tx.note,Icons.Default.MenuBook,
            (if(incoming)"+ " else "− ")+state.money(tx.amount),if(incoming)Color(0xFFCCFBF1) else Color(0xFFF3E8FF),
            click={editingRoznamcha=tx},controls={
              IconButton(onClick={editingRoznamcha=tx}){Icon(Icons.Default.Edit,text("Edit","ترمیم"))}
              IconButton(onClick={viewModel.selectTransaction(tx)}){Icon(Icons.Default.Share,text("Share receipt","رسید شیئر کریں"))}
              IconButton(onClick={deletingRoznamcha=tx}){Icon(Icons.Default.Delete,text("Delete","حذف"),tint=MaterialTheme.colorScheme.error)}
            })
'''
if old in s: s=s.replace(old,new,1)
elif 'editingRoznamcha=tx' not in s: raise SystemExit("Roznamcha row controls anchor mismatch")
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

# Khata remains the customer ledger and opens the independent Roznamcha tab.
p=root/"app/src/main/java/com/example/ui/screens/PremiumBillingScreen.kt"
s=p.read_text(encoding="utf-8")
s=s.replace('''  onAddRoznamcha: (Double,TransactionType,Long,String,String) -> Unit = {_,_,_,_,_->},
''','''  onAddRoznamcha: (Double,TransactionType,Long,String,String) -> Unit = {_,_,_,_,_->},
  onOpenRoznamcha: () -> Unit = {},
''',1)
s=s.replace('''  PremiumPage(uiState.word("Khata & customers", "کھاتہ اور گاہک"), uiState.word("Customer ledger and daily cashbook", "گاہکوں کا کھاتہ اور روزانہ نقد کتاب"), Icons.Default.ReceiptLong,''',
'''  PremiumPage(uiState.word("Khata & customers", "کھاتہ اور گاہک"), uiState.word("Customer and supplier ledger", "گاہکوں اور سپلائرز کا کھاتہ"), Icons.Default.ReceiptLong,''',1)
s=s.replace('''      FilterChip(selected=khataTab=="ROZNAMCHA",onClick={khataTab="ROZNAMCHA";search=""},label={Text(uiState.word("Roznamcha", "روزنامچہ"))},modifier=Modifier.weight(1f).testTag("khata_roznamcha_tab"),leadingIcon={Icon(Icons.Default.MenuBook,null)})
''','',1)
s=s.replace('''    } }
    if(khataTab=="ROZNAMCHA") {''','''    } }
    item { OutlinedButton(onClick=onOpenRoznamcha,modifier=Modifier.fillMaxWidth().testTag("khata_open_roznamcha")) { Icon(Icons.Default.MenuBook,null); Spacer(Modifier.width(8.dp)); Text(uiState.word("Open separate Roznamcha","الگ روزنامچہ کھولیں")) } }
    if(khataTab=="ROZNAMCHA") {''',1)
s=s.replace('''      PremiumButton(uiState.word("New bill", "نیا بل"), onOpenAddInvoice, modifier = Modifier.weight(1f))
''','''      PremiumButton(uiState.word("New bill", "نیا بل"), onOpenAddInvoice, modifier = Modifier.weight(1f))
      PremiumButton(uiState.word("Roznamcha", "روزنامچہ"), onOpenRoznamcha, modifier = Modifier.weight(1f).testTag("khata_roznamcha_add"))
''',1)
p.write_text(s,encoding="utf-8")

p=root/"app/src/main/java/com/example/MainActivity.kt"
s=p.read_text(encoding="utf-8")
if "onOpenRoznamcha = { viewModel.selectTab(FinanceTab.ROZNAMCHA) }" not in s:
  anchor='''            onAddRoznamcha = { amount,type,date,note,account -> viewModel.addTransaction(if(type==TransactionType.INCOME) "Cash In / وصولی" else "Cash Out / ادائیگی",amount,type,"Roznamcha",if(type==TransactionType.INCOME) "💰" else "🧾",account,note,dateMillis=date) }
'''
  if anchor in s: s=s.replace(anchor,anchor.rstrip("\\n")+',\\n            onOpenRoznamcha = { viewModel.selectTab(FinanceTab.ROZNAMCHA) }\\n',1)
p.write_text(s,encoding="utf-8")

# Always-visible customer receipt image action, in addition to statement sharing.
p=root/"app/src/main/java/com/example/ui/dialogs/PremiumCustomerDetailDialog.kt"
s=p.read_text(encoding="utf-8")
if "khata_share_receipt" not in s:
  s=s.replace('import androidx.compose.ui.Modifier\\n','import androidx.compose.ui.Modifier\\nimport androidx.compose.ui.platform.testTag\\n',1)
  anchor='''    OutlinedButton(onClick = {
      val statement = businessProfile.businessName + "\\\\n" + customer.name + "\\\\n" + label("Due: ", "بقایا: ") + money(customer.currentBalance) + "\\\\n" + bills.joinToString("\\\\n") { it.invoiceNumber + " • " + money(it.grandTotal) + " • " + label("Due ", "بقایہ ") + money(it.remainingBalance) }
      ThermalReceiptImage.shareKhataStatement(context, label("Customer Khata Statement", "گاہک کے کھاتے کی تفصیل"), statement)
    }, modifier = Modifier.fillMaxWidth()) { Icon(Icons.Default.Share, null); Spacer(Modifier.width(8.dp)); Text(label("Share Statement / WhatsApp", "تفصیل شیئر کریں / واٹس ایپ")) }
'''
  receipt=anchor+'''    OutlinedButton(onClick = {
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
  if s.count(anchor)!=1: raise SystemExit("Khata receipt button anchor mismatch")
  s=s.replace(anchor,receipt,1)
p.write_text(s,encoding="utf-8")

# 4.9.2 / versionCode 62.
p=root/"app/build.gradle.kts"
s=p.read_text(encoding="utf-8")
if 'versionName = "4.9.1"' in s and 'versionCode = 61' in s:
  s=s.replace('versionCode = 61','versionCode = 62',1).replace('versionName = "4.9.1"','versionName = "4.9.2"',1)
elif 'versionName = "4.9.2"' not in s:
  raise SystemExit("Unexpected version metadata before 4.9.2 bump")
p.write_text(s,encoding="utf-8")
print("Applied 4.9.2 independent Roznamcha, Khata shortcut, party edit/delete plumbing, receipt sharing and feature toggle.")
