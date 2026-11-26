from pathlib import Path
import sys

root=Path(sys.argv[1])

def patch(rel, old, new, label):
    p=root/rel
    s=p.read_text(encoding="utf-8")
    if new in s: return
    if s.count(old)!=1:
        raise SystemExit(f"{label}: expected one anchor in {rel}, got {s.count(old)}")
    p.write_text(s.replace(old,new,1),encoding="utf-8")

core="app/src/main/java/com/example/business/BusinessCore.kt"
patch(core,
"""  suspend fun roznamchaEntry(amount: Double, income: Boolean, dateMillis: Long, note: String, accountId: Long, actor: String, party: String = "", requestId: String = UUID.randomUUID().toString()) = db.withTransaction {""",
"""  private suspend fun saveRoznamchaParty(name:String,type:String,phone:String,address:String,actor:String):BusinessRecord? {
    val clean=name.trim()
    if(clean.isBlank()) return null
    require(type in listOf("CLIENT","VENDOR","SUPPLIER","DEALER","OTHER"))
    val dao=db.businessDao()
    val old=dao.allRecords().firstOrNull { it.kind=="ROZNAMCHA_PARTY" && it.title.equals(clean,true) }
    val payload=JSONObject().put("type",type).put("phone",phone.trim()).put("address",address.trim())
    if(old!=null) {
      val updated=old.copy(title=clean,party=type,payload=payload.toString(),updatedAt=System.currentTimeMillis())
      dao.update(updated); return updated
    }
    val created=BusinessRecord(kind="ROZNAMCHA_PARTY",title=clean,party=type,payload=payload.toString(),createdBy=actor)
    dao.insert(created); return created
  }
  suspend fun roznamchaEntry(amount: Double, income: Boolean, dateMillis: Long, note: String, accountId: Long, actor: String, party: String = "", requestId: String = UUID.randomUUID().toString(), partyType:String="CLIENT", partyPhone:String="", partyAddress:String="") = db.withTransaction {""","Party Master and typed Roznamcha entries")
patch(core,
"""    val now = System.currentTimeMillis()
    db.financeDao().changeAccountBalance(account.id, if (income) amount else -amount)
    db.financeDao().insertTransaction(Transaction(""",
"""    val partyRecord=saveRoznamchaParty(party,partyType,partyPhone,partyAddress,actor)
    val now = System.currentTimeMillis()
    db.financeDao().changeAccountBalance(account.id, if (income) amount else -amount)
    db.financeDao().insertTransaction(Transaction(""","Persist party master before posting")
patch(core,
"""      recipientInfo = party.trim(),
      transactionRef = reference,""",
"""      recipientInfo = party.trim(),
      paymentMethod = partyRecord?.let { "ROZNAMCHA_PARTY:${it.id}" } ?: "",
      transactionRef = reference,""","Link cash entry to persistent party ID")
patch(core,
"""  private suspend fun audit(action: String, id: String, actor: String) {""",
"""  suspend fun updateRoznamchaEntry(oldId:Long,amount:Double,income:Boolean,dateMillis:Long,note:String,accountId:Long,party:String,partyType:String,partyPhone:String,partyAddress:String,actor:String) = db.withTransaction {
    validMoney(amount); require(amount>0 && note.isNotBlank())
    val dao=db.financeDao()
    val old=dao.getTransactionById(oldId) ?: error("Roznamcha entry not found / اندراج نہیں ملا")
    require(old.category=="Roznamcha")
    val accounts=dao.getAllAccountsList()
    val newAccount=accounts.firstOrNull { it.id==accountId } ?: error("Choose a valid cash account / درست اکاؤنٹ منتخب کریں")
    val oldAccount=accounts.firstOrNull { it.name==old.accountName } ?: error("Previous cash account missing / پرانا اکاؤنٹ نہیں ملا")
    val oldSigned=if(old.type==TransactionType.INCOME) old.amount else -old.amount
    val newSigned=if(income) amount else -amount
    if(oldAccount.id==newAccount.id) dao.changeAccountBalance(newAccount.id,newSigned-oldSigned)
    else { dao.changeAccountBalance(oldAccount.id,-oldSigned); dao.changeAccountBalance(newAccount.id,newSigned) }
    val master=saveRoznamchaParty(party,partyType,partyPhone,partyAddress,actor)
    dao.updateTransaction(old.copy(title=if(income)"Roznamcha • Cash In" else "Roznamcha • Cash Out",amount=amount,type=if(income)TransactionType.INCOME else TransactionType.EXPENSE,accountName=newAccount.name,dateMillis=dateMillis,note=note.trim(),recipientInfo=party.trim(),paymentMethod=master?.let { "ROZNAMCHA_PARTY:${it.id}" } ?: "",updatedAt=System.currentTimeMillis()))
    audit("ROZNAMCHA_EDIT",oldId.toString(),actor)
  }
  suspend fun addRoznamchaArchive(name:String,mime:String,path:String,size:Long,documentDate:Long,actor:String) = db.withTransaction {
    require(name.isNotBlank() && (mime=="application/pdf" || mime.startsWith("image/")))
    require(path.contains("/roznamcha-archive/") && size>=0)
    val record=BusinessRecord(kind="ROZNAMCHA_ARCHIVE",title=name.trim(),payload=JSONObject().put("mime",mime).put("path",path).put("size",size).put("documentDate",documentDate).toString(),createdAt=documentDate,updatedAt=System.currentTimeMillis(),createdBy=actor)
    db.businessDao().insert(record); record
  }
  private suspend fun audit(action: String, id: String, actor: String) {""","Edit entries atomically and archive metadata storage")

ui="app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt"
patch(ui,
"""import java.util.UUID
""",
"""import java.util.UUID
import android.content.Intent
import android.net.Uri
import android.provider.OpenableColumns
import android.provider.DocumentsContract
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.FileProvider
import java.io.File
import java.io.FileInputStream
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream
""","Archive imports")
patch(ui,
"""  val actor=state.userRole.name.lowercase()
  val writable=state.userRole==UserRole.OWNER""",
"""  val actor=state.userRole.name.lowercase()
  val writable=state.userRole==UserRole.OWNER
  var archiveMessage by remember { mutableStateOf("") }
  var archivePeriod by remember { mutableStateOf("YEAR") }
  var pendingArchiveId by remember { mutableStateOf("") }
  var pendingArchiveZip by remember { mutableStateOf("") }
  val archiveDownload=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("*/*")) { target ->
    if(target!=null) runCatching {
      val record=state.businessRecords.firstOrNull { it.id==pendingArchiveId } ?: error("Archive record not found")
      val path=JSONObject(record.payload).optString("path")
      receiptContext.contentResolver.openOutputStream(target)?.use { out -> FileInputStream(File(path)).use { it.copyTo(out) } } ?: error("Cannot write destination")
    }.onSuccess { archiveMessage=text("File downloaded successfully","فائل ڈاؤن لوڈ ہو گئی") }.onFailure { archiveMessage=it.message ?: "Download failed" }
    pendingArchiveId=""
  }
  val archiveZipDownload=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/zip")) { target ->
    if(target!=null) runCatching { receiptContext.contentResolver.openOutputStream(target)?.use { out -> FileInputStream(File(pendingArchiveZip)).use { it.copyTo(out) } } ?: error("Cannot write destination") }
      .onSuccess { archiveMessage=text("Archive ZIP downloaded","آرکائیو ZIP ڈاؤن لوڈ ہو گئی") }.onFailure { archiveMessage=it.message ?: "ZIP export failed" }
    pendingArchiveZip=""
  }
  val archivePicker=rememberLauncherForActivityResult(ActivityResultContracts.OpenMultipleDocuments()) { uris ->
    var imported=0
    uris.forEach { uri -> runCatching {
      val mime=receiptContext.contentResolver.getType(uri) ?: "application/octet-stream"
      require(mime=="application/pdf" || mime.startsWith("image/")) { "Only image and PDF documents are supported" }
      var name="document-${UUID.randomUUID()}"
      var modified=System.currentTimeMillis()
      receiptContext.contentResolver.query(uri,arrayOf(OpenableColumns.DISPLAY_NAME,OpenableColumns.SIZE,DocumentsContract.Document.COLUMN_LAST_MODIFIED),null,null,null)?.use { c ->
        if(c.moveToFirst()) {
          val ni=c.getColumnIndex(OpenableColumns.DISPLAY_NAME); if(ni>=0) name=c.getString(ni) ?: name
          val mi=c.getColumnIndex(DocumentsContract.Document.COLUMN_LAST_MODIFIED); if(mi>=0 && !c.isNull(mi)) modified=c.getLong(mi)*1000L
        }
      }
      val folder=File(receiptContext.filesDir,"roznamcha-archive").apply { mkdirs() }
      val ext=name.substringAfterLast('.',if(mime=="application/pdf")"pdf" else "img").take(12)
      val dest=File(folder,"${UUID.randomUUID()}.$ext")
      receiptContext.contentResolver.openInputStream(uri).use { input -> requireNotNull(input){"Cannot read selected file"}.use { source -> dest.outputStream().use { source.copyTo(it) } } }
      viewModel.businessAction({ addRoznamchaArchive(name,mime,dest.absolutePath,dest.length(),modified,actor) }) { error ->
        if(error==null) { imported++; archiveMessage=text("Imported $imported document(s)","دستاویزات درآمد ہوئیں: $imported") } else { dest.delete(); archiveMessage=error }
      }
    }.onFailure { archiveMessage=it.message ?: "Import failed" } }
    if(uris.isEmpty()) archiveMessage=text("No files selected","کوئی فائل منتخب نہیں ہوئی")
  }""","Multi-file archive pickers and persistent storage")
patch(ui,
"""              Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween,verticalAlignment=androidx.compose.ui.Alignment.CenterVertically) {
                Column { Text(selectedRoznamchaParty,fontWeight=FontWeight.Bold,style=MaterialTheme.typography.titleLarge); Text(text("Complete party ledger","پارٹی کا مکمل کھاتہ"),style=MaterialTheme.typography.bodySmall) }
                TextButton(onClick={selectedRoznamchaParty=""}) { Text(text("Show all","تمام دکھائیں")) }
              }
              Text(history.size.toString()+" records")""",
"""              val master=state.businessRecords.firstOrNull { it.kind=="ROZNAMCHA_PARTY" && it.title.equals(selectedRoznamchaParty,true) }
              val masterData=runCatching { JSONObject(master?.payload ?: "{}") }.getOrDefault(JSONObject())
              Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween,verticalAlignment=androidx.compose.ui.Alignment.CenterVertically) {
                Column { Text(selectedRoznamchaParty,fontWeight=FontWeight.Bold,style=MaterialTheme.typography.titleLarge); Text(text("Complete party ledger","پارٹی کا مکمل کھاتہ"),style=MaterialTheme.typography.bodySmall); Text(listOf(masterData.optString("type"),masterData.optString("phone"),masterData.optString("address")).filter { it.isNotBlank() }.joinToString(" • "),style=MaterialTheme.typography.bodySmall) }
                TextButton(onClick={selectedRoznamchaParty=""}) { Text(text("Show all","تمام دکھائیں")) }
              }
              Text(history.size.toString()+" records")""","Show Party Master detail in ledger")
patch(ui,
"""        val cashIn=rows.filter { it.type==TransactionType.INCOME }.sumOf { it.amount }
        val cashOut=rows.filter { it.type==TransactionType.EXPENSE }.sumOf { it.amount }""",
"""        val cashIn=rows.filter { it.type==TransactionType.INCOME }.sumOf { it.amount }
        val cashOut=rows.filter { it.type==TransactionType.EXPENSE }.sumOf { it.amount }
        val partyMasters=state.businessRecords.filter { it.kind=="ROZNAMCHA_PARTY" && !it.archived }
        val partyById=partyMasters.associateBy { it.id }""","Party master lookup")
patch(ui,
"""          val history=all.filter { it.recipientInfo.equals(selectedRoznamchaParty,true) }""",
"""          val selectedMaster=partyMasters.firstOrNull { it.title.equals(selectedRoznamchaParty,true) }
          val history=all.filter { it.recipientInfo.equals(selectedRoznamchaParty,true) || (selectedMaster!=null && it.paymentMethod=="ROZNAMCHA_PARTY:${selectedMaster.id}") }""","Use canonical Party Master identity for ledger")
patch(ui,
"""          ListTile(tx.recipientInfo.ifBlank { text("Unassigned party","غیر مختص فریق") },
            date+" • "+tx.accountName+"\\n"+tx.note,Icons.Default.MenuBook,""",
"""          val partyId=tx.paymentMethod.removePrefix("ROZNAMCHA_PARTY:")
          val partyMaster=partyById[partyId]
          val partyData=runCatching { JSONObject(partyMaster?.payload ?: "{}") }.getOrDefault(JSONObject())
          val partyDetail=listOf(partyData.optString("type"),partyData.optString("phone"),date,tx.accountName,tx.note).filter { it.isNotBlank() }.joinToString(" • ")
          ListTile(tx.recipientInfo.ifBlank { text("Unassigned party","غیر مختص فریق") },
            partyDetail,Icons.Default.MenuBook,""","Show party role/contact under party name")
patch(ui,
"""  if(form && writable && section=="ROZNAMCHA") RoznamchaEntryForm(state,null,{form=false}) { amount,income,date,note,accountId,party,requestId ->
    viewModel.businessAction({roznamchaEntry(amount,income,date,note,accountId,actor,party,requestId)}) {result(it)}
  }
  editingRoznamcha?.let { tx -> RoznamchaEntryForm(state,tx,{editingRoznamcha=null}) { amount,income,date,note,accountId,party,requestId ->
    val account=state.accounts.firstOrNull { it.id==accountId }?.name ?: tx.accountName
    viewModel.updateTransaction(tx.copy(title=if(income)"Roznamcha • Cash In" else "Roznamcha • Cash Out",amount=amount,type=if(income)TransactionType.INCOME else TransactionType.EXPENSE,accountName=account,dateMillis=date,note=note,recipientInfo=party))
    editingRoznamcha=null
  } }""",
"""  if(form && writable && section=="ROZNAMCHA") RoznamchaEntryForm(state,null,{form=false}) { amount,income,date,note,accountId,party,partyType,phone,address,requestId ->
    viewModel.businessAction({roznamchaEntry(amount,income,date,note,accountId,actor,party,requestId,partyType,phone,address)}) {result(it)}
  }
  editingRoznamcha?.let { tx -> RoznamchaEntryForm(state,tx,{editingRoznamcha=null}) { amount,income,date,note,accountId,party,partyType,phone,address,requestId ->
    viewModel.businessAction({updateRoznamchaEntry(tx.id,amount,income,date,note,accountId,party,partyType,phone,address,actor)}) { error -> if(error==null) editingRoznamcha=null else message=error }
  } }""","Route edits through atomic ledger and party master")
patch(ui,
"""private fun RoznamchaEntryForm(state:FinanceUiState,initial:Transaction?=null,dismiss:()->Unit,save:(Double,Boolean,Long,String,Long,String,String)->Unit) {""",
"""private fun RoznamchaEntryForm(state:FinanceUiState,initial:Transaction?=null,dismiss:()->Unit,save:(Double,Boolean,Long,String,Long,String,String,String,String,String)->Unit) {""","Expand form data contract")
patch(ui,
"""  var party by remember(initial?.id) { mutableStateOf(initial?.recipientInfo ?: "") }
  var note by remember(initial?.id) { mutableStateOf(initial?.note ?: "") }""",
"""  var party by remember(initial?.id) { mutableStateOf(initial?.recipientInfo ?: "") }
  val initialParty=state.businessRecords.firstOrNull { it.kind=="ROZNAMCHA_PARTY" && it.title.equals(initial?.recipientInfo ?: "",true) }
  val initialPartyData=remember(initial?.id,state.businessRecords) { runCatching { JSONObject(initialParty?.payload ?: "{}") }.getOrDefault(JSONObject()) }
  var partyType by remember(initial?.id) { mutableStateOf(initialPartyData.optString("type","CLIENT")) }
  var partyPhone by remember(initial?.id) { mutableStateOf(initialPartyData.optString("phone")) }
  var partyAddress by remember(initial?.id) { mutableStateOf(initialPartyData.optString("address")) }
  var note by remember(initial?.id) { mutableStateOf(initial?.note ?: "") }""","Party Master details in form")
patch(ui,
"""            save(value,incoming,date,savedNote,accountId,savedParty,requestId)""",
"""            save(value,incoming,date,savedNote,accountId,savedParty,partyType,partyPhone,partyAddress,requestId)""","Save party type and contact details")
patch(ui,
"""    val knownParties=remember(state.transactions) { state.transactions.asSequence().filter { it.category=="Roznamcha" }.map { it.recipientInfo.trim() }.filter { it.isNotBlank() }.distinctBy { it.lowercase(Locale.ROOT) }.sortedBy { it.lowercase(Locale.ROOT) }.toList() }
    val partyMatches=if(party.isBlank()) emptyList() else knownParties.filter { it.contains(party,true) && !it.equals(party,true) }.take(8)""",
"""    val knownParties=remember(state.businessRecords) { state.businessRecords.asSequence().filter { it.kind=="ROZNAMCHA_PARTY" && !it.archived }.sortedBy { it.title.lowercase(Locale.ROOT) }.toList() }
    val partyMatches=if(party.isBlank()) emptyList() else knownParties.filter { it.title.contains(party,true) && !it.title.equals(party,true) }.take(8)""","Search only Party Master, cap suggestions at eight")
patch(ui,
"""        partyMatches.forEach { name -> DropdownMenuItem(text={Text(name)},onClick={party=name;showPartyMatches=false}) }""",
"""        partyMatches.forEach { match -> DropdownMenuItem(text={Column { Text(match.title,fontWeight=FontWeight.SemiBold); Text(listOf(match.party,JSONObject(match.payload).optString("phone")).filter { it.isNotBlank() }.joinToString(" • "),style=MaterialTheme.typography.bodySmall) }},onClick={
          party=match.title;partyType=match.party.ifBlank { "CLIENT" };val d=JSONObject(match.payload);partyPhone=d.optString("phone");partyAddress=d.optString("address");showPartyMatches=false
        }) }""","Suggestions show name, party type and phone")
patch(ui,
"""    BusinessField(note,t("Description / detail","تفصیل / وضاحت")){note=it}""",
"""    Row(horizontalArrangement=Arrangement.spacedBy(6.dp)) {
      listOf("CLIENT" to t("Client","کلائنٹ"),"VENDOR" to t("Vendor","وینڈر"),"SUPPLIER" to t("Supplier","سپلائر"),"DEALER" to t("Dealer","ڈیلر"),"OTHER" to t("Other","دیگر")).forEach { (key,label) -> FilterChip(partyType==key,{partyType=key},label={Text(label)}) }
    }
    BusinessField(partyPhone,t("Party contact number","پارٹی کا رابطہ نمبر")){partyPhone=it}
    BusinessField(partyAddress,t("Party address / details","پارٹی کا پتہ / تفصیل")){partyAddress=it}
    BusinessField(note,t("Description / detail","تفصیل / وضاحت")){note=it}""","Party type, phone and address controls")

# Archive section in the Roznamcha list. Keep archive metadata independent from cash transactions.
needle='''        }
      }
      "MOVEMENTS" -> {'''
archive='''        }
        item {
          val archives=state.businessRecords.filter { it.kind=="ROZNAMCHA_ARCHIVE" && !it.archived }.sortedByDescending { it.createdAt }
          val cutoff=System.currentTimeMillis()-365L*24*60*60*1000
          val visibleArchives=if(archivePeriod=="YEAR") archives.filter { it.createdAt>=cutoff } else archives
          Column(verticalArrangement=Arrangement.spacedBy(10.dp)) {
            Divider()
            Text(text("Documents & 12-month archive","دستاویزات اور بارہ ماہ کا آرکائیو"),style=MaterialTheme.typography.titleLarge,fontWeight=FontWeight.Bold)
            Text(text("Import multiple images and PDFs. Originals are copied into app storage and remain separate from cash entries.","متعدد تصاویر اور PDF درآمد کریں۔ اصل فائلیں ایپ میں محفوظ رہیں گی اور نقد اندراجات سے الگ رہیں گی۔"),style=MaterialTheme.typography.bodySmall)
            Row(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
              Button(onClick={archivePicker.launch(arrayOf("image/*","application/pdf"))}) { Icon(Icons.Default.UploadFile,null);Text(text("Bulk upload","ایک ساتھ اپ لوڈ")) }
              OutlinedButton(onClick={
                runCatching {
                  val folder=File(receiptContext.cacheDir,"roznamcha-export").apply { mkdirs() }
                  val zip=File(folder,"ArshadFinance-Roznamcha-${System.currentTimeMillis()}.zip")
                  ZipOutputStream(zip.outputStream().buffered()).use { zos ->
                    visibleArchives.forEach { record ->
                      val d=JSONObject(record.payload);val f=File(d.optString("path"));if(f.isFile) {
                        zos.putNextEntry(ZipEntry(record.id+"_"+record.title.replace(Regex("[^A-Za-z0-9._-]"),"_")))
                        f.inputStream().buffered().use { it.copyTo(zos) };zos.closeEntry()
                      }
                    }
                    zos.putNextEntry(ZipEntry("README.txt"));zos.write(("Arshad Finance Roznamcha archive export\nBusiness: "+state.businessProfile.businessName+"\nDeveloped by Muhammad Arshad 03027761415\n").toByteArray());zos.closeEntry()
                  }
                  pendingArchiveZip=zip.absolutePath;archiveZipDownload.launch("ArshadFinance-Roznamcha-Archive.zip")
                }.onFailure { archiveMessage=it.message ?: "Archive export failed" }
              }) { Icon(Icons.Default.Download,null);Text(text("Download ZIP","ZIP ڈاؤن لوڈ")) }
            }
            Row(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
              FilterChip(archivePeriod=="YEAR",{archivePeriod="YEAR"},label={Text(text("Last 12 months","گزشتہ 12 ماہ"))})
              FilterChip(archivePeriod=="ALL",{archivePeriod="ALL"},label={Text(text("All records","تمام ریکارڈ"))})
              Text("${visibleArchives.size} files",style=MaterialTheme.typography.bodySmall)
            }
            if(visibleArchives.isEmpty()) Text(text("No archived documents yet","ابھی کوئی دستاویز آرکائیو نہیں"),style=MaterialTheme.typography.bodySmall)
            visibleArchives.take(500).forEach { record ->
              val d=JSONObject(record.payload)
              Card(Modifier.fillMaxWidth()) {
                Row(Modifier.fillMaxWidth().padding(12.dp),horizontalArrangement=Arrangement.SpaceBetween,verticalAlignment=androidx.compose.ui.Alignment.CenterVertically) {
                  Column(Modifier.weight(1f)) {
                    Text(record.title,fontWeight=FontWeight.SemiBold,maxLines=2)
                    Text(d.optString("mime")+" • "+android.text.format.Formatter.formatShortFileSize(receiptContext,d.optLong("size"))+" • "+SimpleDateFormat("dd MMM yyyy",Locale("en","PK")).format(Date(record.createdAt)),style=MaterialTheme.typography.bodySmall)
                  }
                  IconButton(onClick={pendingArchiveId=record.id;archiveDownload.launch(record.title)}) { Icon(Icons.Default.Download,text("Download","ڈاؤن لوڈ")) }
                }
              }
            }
            if(archiveMessage.isNotBlank()) Text(archiveMessage,color=MaterialTheme.colorScheme.primary)
          }
        }
      }
      "MOVEMENTS" -> {'''
if needle not in s:
    raise SystemExit("Could not locate Roznamcha branch end for archive panel")
s=s.replace(needle,archive,1)
p.write_text(s,encoding="utf-8")
print("Applied persistent Party Master, atomic edit, and multi-file 12-month archive.")


test=root/"app/src/test/java/com/example/RoznamchaPartyArchiveTest.kt"
if not test.exists():
  test.write_text("""package com.example
import android.content.Context
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import com.example.business.BusinessCore
import com.example.business.BusinessSchema
import com.example.data.local.FinanceDatabase
import com.example.data.model.Account
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
@RunWith(RobolectricTestRunner::class)
@Config(sdk=[28])
class RoznamchaPartyArchiveTest {
 private val context:Context=ApplicationProvider.getApplicationContext()
 @Test fun partyMasterIsCanonicalAndEditAdjustsCashExactlyOnce()=runBlocking {
  val db=Room.inMemoryDatabaseBuilder(context,FinanceDatabase::class.java).addCallback(BusinessSchema.callback).build()
  try {
   val account=db.financeDao().insertAccount(Account(name="Cash",accountType="Cash",balance=1000.0,accountNumber=""))
   val core=BusinessCore(db)
   core.roznamchaEntry(100.0,true,1700000000000L,"Advance",account,"owner","Ali Traders","request-a","VENDOR","03001234567","Lahore")
   core.roznamchaEntry(50.0,false,1700000001000L,"Return",account,"owner","ali traders","request-b","VENDOR","03001234567","Lahore")
   val masters=db.businessDao().allRecords().filter{it.kind=="ROZNAMCHA_PARTY"}
   assertEquals(1,masters.size)
   assertEquals("VENDOR",masters.single().party)
   val linked=db.financeDao().getAllTransactions().first().filter{it.category=="Roznamcha"}
   assertEquals(2,linked.size)
   assertTrue(linked.all{it.paymentMethod=="ROZNAMCHA_PARTY:"+masters.single().id})
   val second=linked.first{it.amount==50.0}
   core.updateRoznamchaEntry(second.id,75.0,false,1700000002000L,"Corrected return",account,"Ali Traders","VENDOR","03001234567","Lahore","owner")
   assertEquals(1025.0,db.financeDao().getAllAccountsList().single().balance,0.000001)
   assertEquals(1,db.businessDao().allRecords().count{it.kind=="ROZNAMCHA_PARTY"})
  } finally { db.close() }
 }
 @Test fun archiveMetadataRetainsDocumentTypeAndOriginalDate()=runBlocking {
  val db=Room.inMemoryDatabaseBuilder(context,FinanceDatabase::class.java).addCallback(BusinessSchema.callback).build()
  try {
   val core=BusinessCore(db);val original=1700000000000L
   core.addRoznamchaArchive("invoice-2023.pdf","application/pdf","/data/user/0/app/files/roznamcha-archive/a.pdf",1024,original,"owner")
   val record=db.businessDao().allRecords().single{it.kind=="ROZNAMCHA_ARCHIVE"}
   assertEquals(original,record.createdAt)
   assertEquals("application/pdf",JSONObject(record.payload).getString("mime"))
   assertEquals(1024L,JSONObject(record.payload).getLong("size"))
  } finally { db.close() }
 }
}
""",encoding="utf-8")


# Upgrade legacy Roznamcha free-text party names into persistent Party Master rows.
corep=root/"app/src/main/java/com/example/business/BusinessCore.kt"
cs=corep.read_text(encoding="utf-8")
migration="""  suspend fun migrateLegacyRoznamchaParties(actor:String) = db.withTransaction {
    val dao=db.businessDao()
    val txs=db.financeDao().getAllTransactions().first().filter { it.category=="Roznamcha" && it.recipientInfo.isNotBlank() }
    val masters=dao.allRecords().filter { it.kind=="ROZNAMCHA_PARTY" }.toMutableList()
    txs.forEach { tx ->
      val name=tx.recipientInfo.trim()
      var master=masters.firstOrNull { it.title.equals(name,true) }
      if(master==null) {
        master=BusinessRecord(kind="ROZNAMCHA_PARTY",title=name,party="OTHER",payload=JSONObject().put("type","OTHER").put("phone","").put("address","").toString(),createdBy=actor)
        dao.insert(master);masters.add(master)
      }
      val link="ROZNAMCHA_PARTY:${master.id}"
      if(tx.paymentMethod!=link) db.financeDao().updateTransaction(tx.copy(paymentMethod=link,updatedAt=System.currentTimeMillis()))
    }
  }
"""
if "suspend fun migrateLegacyRoznamchaParties" not in cs:
  anchor="  suspend fun updateRoznamchaEntry("
  if cs.count(anchor)!=1: raise SystemExit("Legacy party migration insertion anchor missing")
  cs=cs.replace(anchor,migration+anchor,1);corep.write_text(cs,encoding="utf-8")

uip=root/"app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt"
us=uip.read_text(encoding="utf-8")
if "legacyPartyMigrationStarted" not in us:
  anchor="""  var selectedRoznamchaParty by remember { mutableStateOf("") }"""
  add=anchor+"""
  var legacyPartyMigrationStarted by remember { mutableStateOf(false) }
  LaunchedEffect(startSection,writable) {
    if(startSection=="ROZNAMCHA" && writable && !legacyPartyMigrationStarted) {
      legacyPartyMigrationStarted=true
      viewModel.businessAction({ migrateLegacyRoznamchaParties(actor) }) { error -> if(error!=null) message=error }
    }
  }"""
  if us.count(anchor)!=1: raise SystemExit("Legacy migration UI trigger anchor missing")
  us=us.replace(anchor,add,1);uip.write_text(us,encoding="utf-8")
