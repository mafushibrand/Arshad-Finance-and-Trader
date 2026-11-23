from pathlib import Path
import sys
r=Path(sys.argv[1])

p=r/"app/src/main/java/com/example/business/PersonalKhataEngine.kt"
s=p.read_text()
if "suspend fun roznamcha(amount: Double" not in s:
 m="  companion object {"
 f='''  suspend fun roznamcha(amount: Double, direction: String, note: String, dateMillis: Long = System.currentTimeMillis()) = db.withTransaction {
    require(amount.isFinite() && amount > 0 && amount <= 1e12) { "Enter a valid amount / درست رقم درج کریں" }
    require(direction in listOf("CASH_IN", "CASH_OUT")) { "Choose cash in or cash out / وصولی یا ادائیگی منتخب کریں" }
    require(note.isNotBlank()) { "Enter a description / تفصیل درج کریں" }
    val title = if (direction == "CASH_IN") "Cash In / وصولی" else "Cash Out / ادائیگی"
    val row = BusinessRecord(kind="PERSONAL_ROZNAMCHA", title=title, amount=amount, status="POSTED",
      payload=JSONObject().put("direction",direction).put("note",note.trim()).put("transactionDateMillis",dateMillis).toString(),
      createdAt=dateMillis, updatedAt=System.currentTimeMillis(), branchId="personal", warehouseId="personal")
    db.businessDao().insert(row)
    db.businessDao().insert(BusinessRecord(kind="AUDIT",title="PERSONAL_ROZNAMCHA",party=row.id,status="RECORDED",branchId="personal",warehouseId="personal"))
  }
'''
 if m not in s: raise SystemExit("Engine insertion point missing")
 p.write_text(s.replace(m,f+m,1))

p=r/"app/src/main/java/com/example/ui/FinanceViewModel.kt";s=p.read_text()
if "fun personalRoznamcha(" not in s:
 m="  fun personalEntry(id:String,amount:Double,direction:String,note:String,attachmentUri:String = \"\",dateMillis:Long = System.currentTimeMillis(),done:(String?)->Unit) {"
 f='''  fun personalRoznamcha(amount:Double,direction:String,note:String,dateMillis:Long,done:(String?)->Unit) {
    viewModelScope.launch {try {com.example.business.PersonalKhataEngine(FinanceDatabase.getDatabase(getApplication(),viewModelScope)).roznamcha(amount,direction,note,dateMillis);done(null)}catch(e:Exception){if(e is kotlinx.coroutines.CancellationException)throw e;done(e.message)}}
  }
'''
 if m not in s: raise SystemExit("ViewModel insertion point missing")
 p.write_text(s.replace(m,f+m,1))

p=r/"app/src/main/java/com/example/ui/screens/PersonalKhataScreen.kt";s=p.read_text()
old='  deleteContact:(String,(String?)->Unit)->Unit = {_,done->done("Delete unavailable")}) {'
new='  deleteContact:(String,(String?)->Unit)->Unit = {_,done->done("Delete unavailable")},\n  addRoznamcha:(Double,String,String,Long,(String?)->Unit)->Unit = {_,_,_,_,done->done("Roznamcha unavailable")}) {'
if old in s:s=s.replace(old,new,1)
elif "addRoznamcha:(Double,String,String,Long" not in s:raise SystemExit("Screen signature missing")
s=s.replace('  var editingPerson by remember {mutableStateOf("")};var deleteTarget by remember {mutableStateOf("")}','  var editingPerson by remember {mutableStateOf("")};var deleteTarget by remember {mutableStateOf("")}\n  var activeKhataTab by remember { mutableStateOf("KHATA") };var roznamchaForm by remember { mutableStateOf(false) };var roznamchaPeriod by remember { mutableStateOf("TODAY") }',1)
old='footer={PremiumButton(state.word("Add person","نام شامل کریں"),{error="";newPerson=true;editingPerson="";pendingOldPhoto="";name="";phone="";description="";personPhoto=""},modifier=Modifier.padding(16.dp).testTag("personal_add_contact"))}) {'
new='footer={if(activeKhataTab=="ROZNAMCHA") PremiumButton(state.word("Add cash entry","نقد اندراج شامل کریں"),{error="";roznamchaForm=true},modifier=Modifier.padding(16.dp).testTag("personal_roznamcha_add")) else PremiumButton(state.word("Add person","نام شامل کریں"),{error="";newPerson=true;editingPerson="";pendingOldPhoto="";name="";phone="";description="";personPhoto=""},modifier=Modifier.padding(16.dp).testTag("personal_add_contact"))}) {'
if old not in s:raise SystemExit("Footer insertion point missing")
s=s.replace(old,new,1)
anchor='      item {SearchBox(query,state.word("Find a person","نام تلاش کریں")){query=it}}\n'
block='''      item { Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(10.dp)) {
        FilterChip(selected=activeKhataTab=="KHATA",onClick={activeKhataTab="KHATA"},label={Text(state.word("Customer Khata","گاہک کھاتہ"))},modifier=Modifier.weight(1f))
        FilterChip(selected=activeKhataTab=="ROZNAMCHA",onClick={activeKhataTab="ROZNAMCHA"},label={Text(state.word("Roznamcha","روزنامچہ"))},modifier=Modifier.weight(1f),leadingIcon={Icon(Icons.Default.MenuBook,null)})
      } }
      if(activeKhataTab=="ROZNAMCHA") {
        val all=state.businessRecords.filter {it.kind=="PERSONAL_ROZNAMCHA" && !it.archived}.sortedByDescending {it.createdAt}
        val today=SimpleDateFormat("yyyyMMdd",Locale.US).format(Date());val month=SimpleDateFormat("yyyyMM",Locale.US).format(Date())
        val rows=all.filter { row -> val d=Date(row.createdAt);when(roznamchaPeriod) {"TODAY"->SimpleDateFormat("yyyyMMdd",Locale.US).format(d)==today;"MONTH"->SimpleDateFormat("yyyyMM",Locale.US).format(d)==month;else->true} }
        val cashIn=rows.filter {org.json.JSONObject(it.payload).optString("direction")=="CASH_IN"}.sumOf {it.amount}
        val cashOut=rows.filter {org.json.JSONObject(it.payload).optString("direction")=="CASH_OUT"}.sumOf {it.amount}
        item { Row(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
          FilterChip(roznamchaPeriod=="TODAY",{roznamchaPeriod="TODAY"},label={Text(state.word("Today","آج"))})
          FilterChip(roznamchaPeriod=="MONTH",{roznamchaPeriod="MONTH"},label={Text(state.word("This month","اس ماہ"))})
          FilterChip(roznamchaPeriod=="ALL",{roznamchaPeriod="ALL"},label={Text(state.word("All","تمام"))})
        } }
        item { Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(8.dp)) {
          Card(Modifier.weight(1f),colors=CardDefaults.cardColors(containerColor=Color(0xFFCCFBF1))) {Column(Modifier.padding(14.dp)){Text(state.word("Cash In","وصولی"),color=Color(0xFF134E4A));Text(state.money(cashIn),color=Color(0xFF0F766E))}}
          Card(Modifier.weight(1f),colors=CardDefaults.cardColors(containerColor=Color(0xFFF3E8FF))) {Column(Modifier.padding(14.dp)){Text(state.word("Cash Out","ادائیگی"),color=Color(0xFF581C87));Text(state.money(cashOut),color=Color(0xFF7C3AED))}}
        } }
        item {Card(Modifier.fillMaxWidth(),colors=CardDefaults.cardColors(containerColor=Color(0xFFFFF7ED))){Row(Modifier.padding(14.dp).fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween){Text(state.word("Cash balance movement","نقد رقم کا فرق"));Text(state.money(cashIn-cashOut),color=Color(0xFFB45309))}}}
        if(rows.isEmpty()) item {EmptyList(state.word("No Roznamcha entries","روزنامچہ میں کوئی اندراج نہیں"),state.word("Add cash received and paid entries","نقد وصولی اور ادائیگی درج کریں"),Icons.Default.MenuBook)}
        items(rows,key={it.id}) { row ->
          val data=runCatching{org.json.JSONObject(row.payload)}.getOrDefault(org.json.JSONObject());val incoming=data.optString("direction")=="CASH_IN"
          Card {Column(Modifier.fillMaxWidth().padding(14.dp),verticalArrangement=Arrangement.spacedBy(4.dp)){
            Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween){Text(state.word(if(incoming)"Cash received" else "Cash paid",if(incoming)"نقد وصولی" else "نقد ادائیگی"));Text((if(incoming)"+ " else "− ")+state.money(row.amount),color=if(incoming)Color(0xFF0F766E) else Color(0xFF7C3AED))}
            Text(SimpleDateFormat("dd MMM yyyy • hh:mm a",Locale.getDefault()).format(Date(row.createdAt)),style=MaterialTheme.typography.bodySmall)
            Text(data.optString("note"))
          }}
        }
      } else {
'''
if anchor not in s:raise SystemExit("Search anchor missing")
s=s.replace(anchor,block+anchor,1)
old='''      if(error.isNotBlank())item {Text(error,color=MaterialTheme.colorScheme.error)}
    }
  }
  if(newPerson || editingPerson.isNotBlank())'''
new='''      }
      if(error.isNotBlank())item {Text(error,color=MaterialTheme.colorScheme.error)}
    }
  }
  if(roznamchaForm) MaterialTheme(colorScheme=khataScheme) { BusinessForm(state.word("Roznamcha entry","روزنامچہ اندراج"),state.word("Save entry","اندراج محفوظ کریں"),{if(!busy)roznamchaForm=false},{
    if(!busy){val n=value.toDoubleOrNull();val date=runCatching{SimpleDateFormat("yyyy-MM-dd",Locale.US).apply{isLenient=false}.parse(dateText)?.time}.getOrNull();when{n==null||!n.isFinite()||n<=0->error=state.word("Enter a valid amount","درست رقم درج کریں");note.isBlank()->error=state.word("Enter a description","تفصیل درج کریں");date==null->error=state.word("Enter date as YYYY-MM-DD","تاریخ YYYY-MM-DD میں درج کریں");else->{busy=true;addRoznamcha(n,direction,note,date){e->busy=false;error=e ?: "";if(e==null){roznamchaForm=false;value="";note="";dateText=SimpleDateFormat("yyyy-MM-dd",Locale.US).format(Date())}}}}}
  }) {
    Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){FilterChip(direction=="CASH_IN",{direction="CASH_IN"},label={Text(state.word("Cash In","وصولی"))});FilterChip(direction=="CASH_OUT",{direction="CASH_OUT"},label={Text(state.word("Cash Out","ادائیگی"))})}
    BusinessField(value,state.word("Amount (Rs.)","رقم (روپے)"),true){value=it}
    BusinessField(note,state.word("Description / detail","تفصیل / وضاحت")){note=it}
    BusinessField(dateText,state.word("Date (YYYY-MM-DD)","تاریخ (سال-مہینہ-دن)")){dateText=it}
    if(error.isNotBlank())Text(error,color=MaterialTheme.colorScheme.error)
  } }
  if(newPerson || editingPerson.isNotBlank())'''
if old not in s:raise SystemExit("Contact list closing anchor missing")
s=s.replace(old,new,1);p.write_text(s)

p=r/"app/src/main/java/com/example/MainActivity.kt";s=p.read_text()
old='        {id,done->viewModel.personalDeleteContact(id,done)})'
new='        {id,done->viewModel.personalDeleteContact(id,done)},\n        {amount,direction,note,date,done->viewModel.personalRoznamcha(amount,direction,note,date,done)})'
if old in s:s=s.replace(old,new,1)
elif "viewModel.personalRoznamcha(amount,direction,note,date,done)" not in s:raise SystemExit("MainActivity callback point missing")
p.write_text(s)

t=r/"app/src/test/java/com/example/PersonalKhataRoznamchaTest.kt"
if not t.exists():
 t.write_text("""package com.example
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import android.content.Context
import com.example.business.PersonalKhataEngine
import com.example.business.BusinessSchema
import com.example.data.local.FinanceDatabase
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
@RunWith(RobolectricTestRunner::class)
@Config(sdk=[28])
class PersonalKhataRoznamchaTest {
 private val context:Context=ApplicationProvider.getApplicationContext()
 @Test fun cashInOutAreDatedAndSeparateFromCustomerBalance()=runBlocking {
  val db=Room.inMemoryDatabaseBuilder(context,FinanceDatabase::class.java).addCallback(BusinessSchema.callback).build()
  try {
   val engine=PersonalKhataEngine(db);val person=engine.contact("Ledger Customer","")
   engine.entry(person.id,500.0,"GAVE","Advance")
   val date=1700000000000L
   engine.roznamcha(1200.0,"CASH_IN","Cash received",date);engine.roznamcha(350.0,"CASH_OUT","Electricity",date+86400000L)
   val rows=db.businessDao().allRecords().filter{it.kind=="PERSONAL_ROZNAMCHA"}
   assertEquals(2,rows.size);assertEquals(date,rows.first{JSONObject(it.payload).getString("direction")=="CASH_IN"}.createdAt)
   assertEquals("Cash received",JSONObject(rows.first{JSONObject(it.payload).getString("direction")=="CASH_IN"}.payload).getString("note"))
   assertEquals(500.0,PersonalKhataEngine.balance(db.businessDao().allRecords(),person.id),0.000001)
  } finally {db.close()}
 }
 @Test fun invalidRoznamchaEntriesAreRejected()=runBlocking {
  val db=Room.inMemoryDatabaseBuilder(context,FinanceDatabase::class.java).addCallback(BusinessSchema.callback).build()
  try {val e=PersonalKhataEngine(db);assertTrue(runCatching{e.roznamcha(-1.0,"CASH_IN","bad")}.isFailure);assertTrue(runCatching{e.roznamcha(1.0,"bad","bad")}.isFailure)} finally {db.close()}
 }
}
""")
print("Applied personal Khata Roznamcha UI, persistence, ViewModel and regression tests.")
