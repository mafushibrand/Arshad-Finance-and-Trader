from pathlib import Path
import sys
root=Path(sys.argv[1])

p=root/'app/build.gradle.kts'
s=p.read_text(encoding='utf-8')
if 'com.google.mlkit:translate:17.0.3' not in s:
    s=s.replace('  implementation(libs.firebase.ai)\n','  implementation(libs.firebase.ai)\n  implementation("com.google.mlkit:translate:17.0.3")\n',1)
p.write_text(s,encoding='utf-8')

p=root/'app/src/main/java/com/example/util/UrduAutoTranslator.kt'
p.write_text("""package com.example.util
import com.google.android.gms.tasks.Task
import com.google.mlkit.common.model.DownloadConditions
import com.google.mlkit.nl.translate.TranslateLanguage
import com.google.mlkit.nl.translate.Translation
import com.google.mlkit.nl.translate.TranslatorOptions
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
object UrduAutoTranslator {
  fun needsUrduTranslation(value:String):Boolean = value.any { it in 'A'..'Z' || it in 'a'..'z' }
  suspend fun englishToUrdu(value:String):String {
    val input=value.trim()
    if(input.isBlank() || !needsUrduTranslation(input)) return value
    val translator=Translation.getClient(TranslatorOptions.Builder().setSourceLanguage(TranslateLanguage.ENGLISH).setTargetLanguage(TranslateLanguage.URDU).build())
    try {
      translator.downloadModelIfNeeded(DownloadConditions.Builder().build()).awaitResult()
      return translator.translate(input).awaitResult()
    } catch(error:Exception) {
      throw IllegalStateException("Urdu model needs one internet download; after that translation works offline. / اردو ماڈل پہلی مرتبہ انٹرنیٹ سے ڈاؤن لوڈ ہوگا، پھر آف لائن کام کرے گا۔",error)
    } finally { translator.close() }
  }
  private suspend fun <T> Task<T>.awaitResult():T = suspendCancellableCoroutine { c ->
    addOnSuccessListener { if(c.isActive) c.resume(it) }
    addOnFailureListener { if(c.isActive) c.resumeWithException(it) }
    addOnCanceledListener { c.cancel() }
  }
}
""",encoding='utf-8')

p=root/'app/src/main/java/com/example/ui/dialogs/PremiumAddCustomerDialog.kt'
s=p.read_text(encoding='utf-8')
if 'import com.example.util.UrduAutoTranslator' not in s:
    s=s.replace('import com.example.data.model.*','import com.example.data.model.*\nimport com.example.util.UrduAutoTranslator\nimport kotlinx.coroutines.launch',1)
if 'val translationScope = rememberCoroutineScope()' not in s:
    s=s.replace('  val context = LocalContext.current\n','  val context = LocalContext.current\n  val translationScope = rememberCoroutineScope()\n  var translating by remember { mutableStateOf(false) }\n',1)
old='''    else { metadata.put("openingBalance",opening.toDouble()).put("creditLimit",credit.toDouble()).put("cnic",cnic.trim()).put("ntn",ntn.trim()).put("profilePhotoUri",profilePhotoUri).put("description",description.trim());onSaveCustomer((editingCustomer ?: Customer(name = name.trim())).copy(name = name.trim(), phone = phone.trim(), address = address.trim(), customerType = type.trim(), note = note.trim(),detailsJson=metadata.toString()));if(originalPhotoUri.isNotBlank() && originalPhotoUri!=profilePhotoUri)removeOldPhoto(originalPhotoUri); onDismiss() }
'''
new='''    else if(!translating) {
      translating=true
      translationScope.launch {
        try {
          val savedName=if(urdu)UrduAutoTranslator.englishToUrdu(name) else name.trim()
          val savedAddress=if(urdu)UrduAutoTranslator.englishToUrdu(address) else address.trim()
          val savedDescription=if(urdu)UrduAutoTranslator.englishToUrdu(description) else description.trim()
          val savedNote=if(urdu)UrduAutoTranslator.englishToUrdu(note) else note.trim()
          val savedType=if(urdu)UrduAutoTranslator.englishToUrdu(type) else type.trim()
          metadata.put("openingBalance",opening.toDouble()).put("creditLimit",credit.toDouble()).put("cnic",cnic.trim()).put("ntn",ntn.trim()).put("profilePhotoUri",profilePhotoUri).put("description",savedDescription)
          onSaveCustomer((editingCustomer ?: Customer(name=savedName.trim())).copy(name=savedName.trim(),phone=phone.trim(),address=savedAddress.trim(),customerType=savedType.trim(),note=savedNote.trim(),detailsJson=metadata.toString()))
          if(originalPhotoUri.isNotBlank() && originalPhotoUri!=profilePhotoUri)removeOldPhoto(originalPhotoUri)
          onDismiss()
        } catch(failure:Exception) { error=failure.message ?: label("Translation failed","ترجمہ ناکام ہو گیا") }
        finally { translating=false }
      }
    }
'''
if old in s:s=s.replace(old,new,1)
elif 'val savedName=if(urdu)' not in s:raise SystemExit('Customer save anchor missing')
if 'if(translating) LinearProgressIndicator' not in s:
    s=s.replace('    Text(label("A clear khata for every customer", "ہر گاہک کے لیے صاف کھاتہ"), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)\n','    Text(label("A clear khata for every customer", "ہر گاہک کے لیے صاف کھاتہ"), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)\n    if(translating) LinearProgressIndicator(Modifier.fillMaxWidth())\n',1)
p.write_text(s,encoding='utf-8')

p=root/'app/src/main/java/com/example/ui/screens/PremiumBillingScreen.kt'
s=p.read_text(encoding='utf-8')
if 'import com.example.util.UrduAutoTranslator' not in s:
    s=s.replace('import com.example.data.model.*','import com.example.data.model.*\nimport com.example.util.UrduAutoTranslator\nimport kotlinx.coroutines.launch',1)
if 'val translationScope = rememberCoroutineScope()' not in s:
    s=s.replace('  var roznamchaError by rememberSaveable { mutableStateOf("") }\n','  var roznamchaError by rememberSaveable { mutableStateOf("") }\n  var translating by remember { mutableStateOf(false) }\n  val translationScope = rememberCoroutineScope()\n',1)
old='''      else -> { onAddRoznamcha(amount,roznamchaDirection,date,roznamchaNote.trim(),roznamchaAccount);showRoznamchaForm=false;roznamchaAmount="";roznamchaNote="";roznamchaError="" }
'''
new='''      else -> { if(!translating) { translating=true;translationScope.launch { try { val savedNote=if(uiState.appLanguage==AppLanguage.URDU)UrduAutoTranslator.englishToUrdu(roznamchaNote) else roznamchaNote.trim();onAddRoznamcha(amount,roznamchaDirection,date,savedNote,roznamchaAccount);showRoznamchaForm=false;roznamchaAmount="";roznamchaNote="";roznamchaError="" } catch(failure:Exception) {roznamchaError=failure.message ?: uiState.word("Translation failed","ترجمہ ناکام ہو گیا")} finally {translating=false} } } }
'''
if old in s:s=s.replace(old,new,1)
elif 'val savedNote=if(uiState.appLanguage' not in s:raise SystemExit('Roznamcha save anchor missing')
if 'if(translating) LinearProgressIndicator' not in s:
    s=s.replace('    BusinessField(roznamchaNote,uiState.word("Description / note","تفصیل / نوٹ")){roznamchaNote=it}\n','    BusinessField(roznamchaNote,uiState.word("Description / note","تفصیل / نوٹ")){roznamchaNote=it}\n    if(translating) LinearProgressIndicator(Modifier.fillMaxWidth())\n',1)
p.write_text(s,encoding='utf-8')

t=root/'app/src/test/java/com/example/UrduAutoTranslatorTest.kt'
t.write_text("""package com.example
import com.example.util.UrduAutoTranslator
import org.junit.Assert.*
import org.junit.Test
class UrduAutoTranslatorTest {
  @Test fun onlyLatinTextNeedsUrduTranslation() {
    assertTrue(UrduAutoTranslator.needsUrduTranslation("Customer payment received"))
    assertFalse(UrduAutoTranslator.needsUrduTranslation("گاہک کی ادائیگی وصول ہوئی"))
    assertFalse(UrduAutoTranslator.needsUrduTranslation("12345 - 500"))
  }
}
""",encoding='utf-8')
print("Applied on-device Urdu translation to Khata customer fields and Roznamcha notes.")
