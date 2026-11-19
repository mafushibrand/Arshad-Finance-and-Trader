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
print("Applied additive Khata profile-photo and transaction-attachment metadata patches.")
