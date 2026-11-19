from pathlib import Path
import sys

root = Path(sys.argv[1])
def patch(rel, pairs):
    p = root / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if new in s:
            continue
        if old not in s:
            raise SystemExit(f"Khata attachment patch mismatch in {rel}: {old[:90]!r}")
        s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8")

patch("app/src/main/java/com/example/business/PersonalKhataEngine.kt", [
('suspend fun contact(name: String, phone: String): BusinessRecord = db.withTransaction {','suspend fun contact(name: String, phone: String, photoUri: String = ""): BusinessRecord = db.withTransaction {'),
('payload=JSONObject().put("phone",phone.trim()).toString()','payload=JSONObject().put("phone",phone.trim()).put("profilePhotoUri",photoUri).toString()'),
('suspend fun entry(contactId: String, amount: Double, direction: String, note: String) = db.withTransaction {','suspend fun entry(contactId: String, amount: Double, direction: String, note: String, attachmentUri: String = "") = db.withTransaction {'),
('payload=JSONObject().put("direction",direction).toString()','payload=JSONObject().put("direction",direction).put("note",note.trim()).put("attachmentUri",attachmentUri).toString()')
])
patch("app/src/main/java/com/example/ui/FinanceViewModel.kt", [
('fun personalContact(name:String,phone:String,done:(String?)->Unit) {\n    viewModelScope.launch {try {com.example.business.PersonalKhataEngine(FinanceDatabase.getDatabase(getApplication(),viewModelScope)).contact(name,phone);done(null)}',
 'fun personalContact(name:String,phone:String,photoUri:String = "",done:(String?)->Unit) {\n    viewModelScope.launch {try {com.example.business.PersonalKhataEngine(FinanceDatabase.getDatabase(getApplication(),viewModelScope)).contact(name,phone,photoUri);done(null)}'),
('fun personalEntry(id:String,amount:Double,direction:String,note:String,done:(String?)->Unit) {\n    viewModelScope.launch {try {com.example.business.PersonalKhataEngine(FinanceDatabase.getDatabase(getApplication(),viewModelScope)).entry(id,amount,direction,note);done(null)}',
 'fun personalEntry(id:String,amount:Double,direction:String,note:String,attachmentUri:String = "",done:(String?)->Unit) {\n    viewModelScope.launch {try {com.example.business.PersonalKhataEngine(FinanceDatabase.getDatabase(getApplication(),viewModelScope)).entry(id,amount,direction,note,attachmentUri);done(null)}')
])
patch("app/src/main/java/com/example/MainActivity.kt", [
('{name,phone,done->viewModel.personalContact(name,phone,done)},\n        {id,amount,direction,note,done->viewModel.personalEntry(id,amount,direction,note,done)},',
 '{name,phone,photo,done->viewModel.personalContact(name,phone,photo,done)},\n        {id,amount,direction,note,attachment,done->viewModel.personalEntry(id,amount,direction,note,attachment,done)},')
])
patch("app/src/main/java/com/example/ui/dialogs/PremiumAddCustomerDialog.kt", [
('import androidx.compose.foundation.layout.*\n',
 'import androidx.compose.foundation.layout.*\nimport android.content.Intent\nimport androidx.activity.compose.rememberLauncherForActivityResult\nimport androidx.activity.result.contract.ActivityResultContracts\nimport androidx.compose.ui.platform.LocalContext\nimport androidx.compose.ui.layout.ContentScale\nimport coil.compose.AsyncImage\n'),
('  var note by remember { mutableStateOf(editingCustomer?.note ?: "") }\n',
 '''  var note by remember { mutableStateOf(editingCustomer?.note ?: "") }
  val context = LocalContext.current
  var profilePhotoUri by remember { mutableStateOf(metadata.optString("profilePhotoUri", "")) }
  val photoPicker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
    if (uri != null) {
      runCatching { context.contentResolver.takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION) }
      profilePhotoUri = uri.toString()
    }
  }
'''),
('metadata.put("openingBalance",opening.toDouble()).put("creditLimit",credit.toDouble()).put("cnic",cnic.trim()).put("ntn",ntn.trim());',
 'metadata.put("openingBalance",opening.toDouble()).put("creditLimit",credit.toDouble()).put("cnic",cnic.trim()).put("ntn",ntn.trim()).put("profilePhotoUri",profilePhotoUri);'),
('    Text(label("A clear khata for every customer", "ہر گاہک کے لیے صاف کھاتہ"), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)\n',
 '''    Text(label("A clear khata for every customer", "ہر گاہک کے لیے صاف کھاتہ"), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.CenterVertically) {
      if (profilePhotoUri.isNotBlank()) AsyncImage(model=profilePhotoUri, contentDescription=label("Customer photo", "گاہک کی تصویر"), contentScale=ContentScale.Crop, modifier=Modifier.size(72.dp))
      OutlinedButton(onClick={photoPicker.launch(arrayOf("image/*"))}) { Text(label("Add / change photo", "تصویر شامل / تبدیل کریں")) }
      if (profilePhotoUri.isNotBlank()) TextButton(onClick={profilePhotoUri=""}) { Text(label("Remove", "ہٹائیں")) }
    }
''')
])
# The personal ledger stores profile and attachment URIs in existing JSON payloads; Room schema/version remains unchanged.

patch("app/src/main/java/com/example/ui/screens/PersonalKhataScreen.kt", [
('import androidx.compose.foundation.layout.*\n',
 '''import androidx.compose.foundation.layout.*
import android.content.Intent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.layout.ContentScale
import coil.compose.AsyncImage
'''),
('  addContact:(String,String,(String?)->Unit)->Unit,addEntry:(String,Double,String,String,(String?)->Unit)->Unit,onTheme:()->Unit = {}) {',
 '  addContact:(String,String,String,(String?)->Unit)->Unit,addEntry:(String,Double,String,String,String,(String?)->Unit)->Unit,onTheme:()->Unit = {}) {'),
('  var error by remember {mutableStateOf("")};var busy by remember {mutableStateOf(false)}\n',
 '''  var error by remember {mutableStateOf("")};var busy by remember {mutableStateOf(false)}
  val context=LocalContext.current
  var personPhoto by remember {mutableStateOf("")};var entryAttachment by remember {mutableStateOf("")}
  val photoPicker=rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()){uri->if(uri!=null){runCatching{context.contentResolver.takePersistableUriPermission(uri,Intent.FLAG_GRANT_READ_URI_PERMISSION)};personPhoto=uri.toString()}}
  val attachmentPicker=rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()){uri->if(uri!=null){runCatching{context.contentResolver.takePersistableUriPermission(uri,Intent.FLAG_GRANT_READ_URI_PERMISSION)};entryAttachment=uri.toString()}}
'''),
('  fun done(e:String?){busy=false;error=e ?: "";if(e==null){newPerson=false;selected="";value="";note="";name="";phone=""}}',
 '  fun done(e:String?){busy=false;error=e ?: "";if(e==null){newPerson=false;selected="";value="";note="";name="";phone="";personPhoto="";entryAttachment=""}}'),
('        Text(person.title,style=MaterialTheme.typography.titleLarge)\n',
 '''        val personPayload=runCatching{org.json.JSONObject(person.payload)}.getOrDefault(org.json.JSONObject())
        val avatar=personPayload.optString("profilePhotoUri","")
        Row(verticalAlignment=androidx.compose.ui.Alignment.CenterVertically,horizontalArrangement=Arrangement.spacedBy(10.dp)) {
          if(avatar.isNotBlank()) AsyncImage(model=avatar,contentDescription=state.word("Person photo","شخص کی تصویر"),contentScale=ContentScale.Crop,modifier=Modifier.size(52.dp))
          Text(person.title,style=MaterialTheme.typography.titleLarge)
        }
'''),
('        state.businessRecords.filter {it.kind=="PERSONAL_ENTRY" && it.party==person.id}.take(5).forEach {entry->\n          val gave=org.json.JSONObject(entry.payload).optString("direction")=="GAVE"\n          Text(state.word(if(gave)"Gave " else "Received ",if(gave)"دیے " else "ملے ")+state.money(entry.amount)+" • "+entry.title)\n        }',
 '''        state.businessRecords.filter {it.kind=="PERSONAL_ENTRY" && it.party==person.id && !it.archived}.sortedByDescending{it.createdAt}.forEach {entry->
          val payload=runCatching{org.json.JSONObject(entry.payload)}.getOrDefault(org.json.JSONObject())
          val gave=payload.optString("direction")=="GAVE"
          Column(Modifier.fillMaxWidth().padding(vertical=4.dp)) {
            Text(state.word(if(gave)"Gave " else "Received ",if(gave)"دیے " else "ملے ")+state.money(entry.amount)+" • "+entry.title)
            Text(java.text.SimpleDateFormat("dd MMM yyyy, hh:mm a",java.util.Locale.getDefault()).format(java.util.Date(entry.createdAt)),style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
            val attachment=payload.optString("attachmentUri","")
            if(attachment.isNotBlank()) AsyncImage(model=attachment,contentDescription=state.word("Transaction attachment","لین دین کی منسلک تصویر"),contentScale=ContentScale.Fit,modifier=Modifier.fillMaxWidth().heightIn(max=180.dp))
          }
        }'''),
('  if(newPerson)BusinessForm(state.word("Add person","نام شامل کریں"),state.word("Save","محفوظ کریں"),{if(!busy)newPerson=false},{if(!busy){busy=true;addContact(name,phone,::done)}}) {\n    BusinessField(name,state.word("Name","نام")){name=it};BusinessField(phone,state.word("Phone (optional)","فون (اختیاری)")){phone=it}\n',
 '''  if(newPerson)BusinessForm(state.word("Add person","نام شامل کریں"),state.word("Save","محفوظ کریں"),{if(!busy)newPerson=false},{if(!busy){busy=true;addContact(name,phone,personPhoto,::done)}}) {
    if(personPhoto.isNotBlank()) AsyncImage(model=personPhoto,contentDescription=state.word("Profile photo","پروفائل تصویر"),contentScale=ContentScale.Crop,modifier=Modifier.size(76.dp))
    OutlinedButton(onClick={photoPicker.launch(arrayOf("image/*"))}){Text(state.word("Add profile photo","پروفائل تصویر شامل کریں"))}
    if(personPhoto.isNotBlank()) TextButton(onClick={personPhoto=""}){Text(state.word("Remove photo","تصویر ہٹائیں"))}
    BusinessField(name,state.word("Name","نام")){name=it};BusinessField(phone,state.word("Phone (optional)","فون (اختیاری)")){phone=it}
'''),
('if(!busy){val n=value.toDoubleOrNull();if(n==null||!n.isFinite()||n<=0)error=state.word("Enter a valid amount","درست رقم درج کریں") else {busy=true;addEntry(selected,n,direction,note,::done)}}',
 'if(!busy){val n=value.toDoubleOrNull();if(n==null||!n.isFinite()||n<=0)error=state.word("Enter a valid amount","درست رقم درج کریں") else {busy=true;addEntry(selected,n,direction,note,entryAttachment,::done)}}'),
('    BusinessField(value,state.word("Amount (Rs.)","رقم (روپے)"),true){value=it};BusinessField(note,state.word("Note (optional)","تفصیل (اختیاری)")){note=it}\n',
 '''    BusinessField(value,state.word("Amount (Rs.)","رقم (روپے)"),true){value=it};BusinessField(note,state.word("Note (optional)","تفصیل (اختیاری)")){note=it}
    OutlinedButton(onClick={attachmentPicker.launch(arrayOf("image/*"))}){Text(state.word("Attach transaction photo / document","لین دین کی تصویر / دستاویز منسلک کریں"))}
    if(entryAttachment.isNotBlank()) { AsyncImage(model=entryAttachment,contentDescription=state.word("Attachment preview","منسلک فائل کا پیش منظر"),contentScale=ContentScale.Fit,modifier=Modifier.fillMaxWidth().heightIn(max=180.dp));TextButton(onClick={entryAttachment=""}){Text(state.word("Remove attachment","منسلک فائل ہٹائیں"))} }
''')
])


test_source = Path(__file__).resolve().parent.parent / "app/src/test/java/com/example/PersonalKhataAttachmentTest.kt"
test_target = root / "app/src/test/java/com/example/PersonalKhataAttachmentTest.kt"
test_target.parent.mkdir(parents=True, exist_ok=True)
test_target.write_text(test_source.read_text(encoding="utf-8"), encoding="utf-8")


design_test = root / "app/src/test/java/com/example/AccessDesignTest.kt"
design_source = design_test.read_text(encoding="utf-8")
design_source = design_source.replace("{_,_,_->}", "{_,_,_,_->}")
design_source = design_source.replace("{_,_,_,_,_->}", "{_,_,_,_,_,_->}")
design_test.write_text(design_source, encoding="utf-8")

print("Applied additive Khata profile-photo and transaction-attachment metadata patches.")
