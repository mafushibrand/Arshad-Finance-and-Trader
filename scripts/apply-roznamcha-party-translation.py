from pathlib import Path
import sys

root = Path(sys.argv[1])
def replace(rel, old, new, label):
    p = root / rel
    s = p.read_text(encoding='utf-8')
    if new in s: return
    if old not in s: raise SystemExit(f'{label}: expected source anchor missing in {rel}')
    p.write_text(s.replace(old, new, 1), encoding='utf-8')

# Translation language detection and offline-safe fallback.
p = root / 'app/src/main/java/com/example/util/UrduAutoTranslator.kt'
s = p.read_text(encoding='utf-8')
if 'fun needsEnglishTranslation' not in s:
    s = s.replace("  fun needsUrduTranslation(value:String):Boolean = value.any { it in 'A'..'Z' || it in 'a'..'z' }\n", "  fun needsUrduTranslation(value:String):Boolean = value.any { it in 'A'..'Z' || it in 'a'..'z' }\n  fun needsEnglishTranslation(value:String):Boolean = value.any { it in '\\u0600'..'\\u06FF' || it in '\\u0750'..'\\u077F' || it in '\\uFB50'..'\\uFDFF' || it in '\\uFE70'..'\\uFEFF' }\n", 1)
old = '''    val input=value.trim()\n    if(input.isBlank()) return value\n    val source=if(targetUrdu) TranslateLanguage.ENGLISH else TranslateLanguage.URDU\n'''
new = '''    val input=value.trim()\n    if(input.isBlank()) return value\n    if(targetUrdu && !needsUrduTranslation(input)) return value\n    if(!targetUrdu && !needsEnglishTranslation(input)) return value\n    val source=if(targetUrdu) TranslateLanguage.ENGLISH else TranslateLanguage.URDU\n'''
if new not in s:
    if old not in s: raise SystemExit('Translator language guard anchor missing')
    s=s.replace(old,new,1)
if 'suspend fun translateOrOriginal' not in s:
    s=s.replace('''  suspend fun englishToUrdu(value:String):String = translateForLanguage(value,true)\n''', '''  suspend fun translateOrOriginal(value:String,targetUrdu:Boolean,onFailure:(String)->Unit = {}):String =\n    try { translateForLanguage(value,targetUrdu) }\n    catch(error:Exception) { onFailure(error.message ?: "Translation model unavailable / ترجمے کا ماڈل دستیاب نہیں"); value.trim() }\n  suspend fun englishToUrdu(value:String):String = translateForLanguage(value,true)\n''',1)
p.write_text(s,encoding='utf-8')

# Party identities, reusable names and consolidated party history.
p = root / 'app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt'
s = p.read_text(encoding='utf-8')
if 'var selectedRoznamchaParty' not in s:
    s=s.replace('''  var roznamchaPeriod by remember { mutableStateOf("TODAY") }\n''','''  var roznamchaPeriod by remember { mutableStateOf("TODAY") }\n  var selectedRoznamchaParty by remember { mutableStateOf("") }\n''',1)
old='''        val all = state.transactions.filter { it.category == "Roznamcha" }.sortedByDescending { it.dateMillis }\n        val today = SimpleDateFormat("yyyyMMdd",Locale.US).format(Date())\n'''
new='''        val all = state.transactions.filter { it.category == "Roznamcha" }.sortedByDescending { it.dateMillis }\n        val partyNames = all.map { it.recipientInfo.trim() }.filter { it.isNotBlank() }.distinctBy { it.lowercase(Locale.ROOT) }.sortedBy { it.lowercase(Locale.ROOT) }\n        val today = SimpleDateFormat("yyyyMMdd",Locale.US).format(Date())\n'''
if new not in s:
    if old not in s: raise SystemExit('Roznamcha all entries anchor missing')
    s=s.replace(old,new,1)
old='''          inPeriod && (query.isBlank() || tx.title.contains(query,true) || tx.note.contains(query,true) || tx.accountName.contains(query,true))\n'''
new='''          inPeriod && (selectedRoznamchaParty.isBlank() || tx.recipientInfo.equals(selectedRoznamchaParty,true)) &&\n            (query.isBlank() || tx.recipientInfo.contains(query,true) || tx.title.contains(query,true) || tx.note.contains(query,true) || tx.accountName.contains(query,true))\n'''
if new not in s:
    if old not in s: raise SystemExit('Roznamcha row filter anchor missing')
    s=s.replace(old,new,1)
anchor='''        item {\n          Column(verticalArrangement=Arrangement.spacedBy(10.dp)) {\n            Row(horizontalArrangement=Arrangement.spacedBy(8.dp)) {\n'''
insert='''        if(partyNames.isNotEmpty()) item {\n          Column(verticalArrangement=Arrangement.spacedBy(8.dp)) {\n            Text(text("Client / Vendor / Supplier history","گاہک / وینڈر / سپلائر کی ہسٹری"),fontWeight=FontWeight.SemiBold)\n            Row(Modifier.horizontalScroll(rememberScrollState()),horizontalArrangement=Arrangement.spacedBy(8.dp)) {\n              FilterChip(selectedRoznamchaParty.isBlank(),{selectedRoznamchaParty=""},label={Text(text("All parties","تمام نام"))})\n              partyNames.forEach { name -> FilterChip(selectedRoznamchaParty.equals(name,true),{selectedRoznamchaParty=if(selectedRoznamchaParty.equals(name,true)) "" else name},label={Text(name)}) }\n            }\n            if(selectedRoznamchaParty.isNotBlank()) {\n              val history=all.filter { it.recipientInfo.equals(selectedRoznamchaParty,true) }\n              val received=history.filter { it.type==TransactionType.INCOME }.sumOf { it.amount }\n              val paid=history.filter { it.type==TransactionType.EXPENSE }.sumOf { it.amount }\n              Card(Modifier.fillMaxWidth(),colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.secondaryContainer)) {\n                Column(Modifier.padding(14.dp),verticalArrangement=Arrangement.spacedBy(5.dp)) {\n                  Text(selectedRoznamchaParty,fontWeight=FontWeight.Bold,style=MaterialTheme.typography.titleMedium)\n                  Text(text("${history.size} total records","کل ${history.size} ریکارڈ"))\n                  Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween) {\n                    Text(text("Received: ${state.money(received)}","وصولی: ${state.money(received)}"))\n                    Text(text("Paid: ${state.money(paid)}","ادائیگی: ${state.money(paid)}"))\n                  }\n                  Text(text("Net: ${state.money(received-paid)}","خالص: ${state.money(received-paid)}"),fontWeight=FontWeight.Bold)\n                }\n              }\n            }\n          }\n        }\n        item {\n          Column(verticalArrangement=Arrangement.spacedBy(10.dp)) {\n            Row(horizontalArrangement=Arrangement.spacedBy(8.dp)) {\n'''
if 'Client / Vendor / Supplier history' not in s:
    if anchor not in s: raise SystemExit('Roznamcha summary card anchor missing')
    s=s.replace(anchor,insert,1)
old='''                  appendLine(state.businessProfile.businessName)
                  appendLine(text("ROZNAMCHA RECEIPT","روزنامچہ رسید"))
                  appendLine(text("Client / Party: ","گاہک / فریق: ")+tx.recipientInfo)
'''
new='''                  appendLine(state.businessProfile.businessName)
                  if(state.businessProfile.address.isNotBlank()) appendLine(state.businessProfile.address)
                  if(state.businessProfile.phone.isNotBlank()) appendLine(state.businessProfile.phone)
                  appendLine(text("ROZNAMCHA RECEIPT","روزنامچہ رسید"))
                  appendLine(text("Client / Party: ","گاہک / فریق: ")+tx.recipientInfo)
'''
if new not in s:
    if old not in s: raise SystemExit('Roznamcha receipt header anchor missing')
    s=s.replace(old,new,1)
old='''                  if(tx.note.isNotBlank()) appendLine(text("Note: ","تفصیل: ")+tx.note)
'''
new='''                  if(tx.note.isNotBlank()) appendLine(text("Note: ","تفصیل: ")+tx.note)
                  appendLine(text("Generated: ","تیار کرنے کا وقت: ")+SimpleDateFormat("dd MMM yyyy • hh:mm a",Locale.getDefault()).format(Date()))
                  appendLine("Developed by Muhammad Arshad • 03027761415")
'''
if new not in s:
    if old not in s: raise SystemExit('Roznamcha receipt footer anchor missing')
    s=s.replace(old,new,1)
old='''          if(tx.note.isNotBlank()) appendLine(text("Note: ","تفصیل: ")+tx.note)\n'''
new='''          if(tx.note.isNotBlank()) appendLine(text("Note: ","تفصیل: ")+tx.note)\n          appendLine(text("Generated: ","تیار کرنے کا وقت: ")+SimpleDateFormat("dd MMM yyyy • hh:mm a",Locale.getDefault()).format(Date()))\n          appendLine("Developed by Muhammad Arshad • 03027761415")\n'''
if new not in s:
    if old not in s: raise SystemExit('Roznamcha receipt footer anchor missing')
    s=s.replace(old,new,1)
old='''    BusinessField(party,t("Client / Party","گاہک / فریق")){party=it}\n    BusinessField(note,t("Description / detail","تفصیل / وضاحت")){note=it}\n'''
new='''    BusinessField(party,t("Client / Vendor / Supplier name","گاہک / وینڈر / سپلائر کا نام")){party=it}\n    val knownParties=state.transactions.filter { it.category=="Roznamcha" }.map { it.recipientInfo.trim() }.filter { it.isNotBlank() }.distinctBy { it.lowercase(Locale.ROOT) }.sortedBy { it.lowercase(Locale.ROOT) }\n    if(knownParties.isNotEmpty()) Row(Modifier.horizontalScroll(rememberScrollState()),horizontalArrangement=Arrangement.spacedBy(6.dp)) { knownParties.forEach { name -> FilterChip(party.equals(name,true),{party=name},label={Text(name)}) } }\n    BusinessField(note,t("Description / detail","تفصیل / وضاحت")){note=it}\n'''
if new not in s:
    if old not in s: raise SystemExit('Roznamcha party input anchor missing')
    s=s.replace(old,new,1)
old='''            val savedParty=UrduAutoTranslator.translateForLanguage(party.trim(),urdu)\n            val savedNote=UrduAutoTranslator.translateForLanguage(note.trim(),urdu)\n            save(value,incoming,date,savedNote,accountId,savedParty)\n'''
new='''            val savedParty=UrduAutoTranslator.translateOrOriginal(party.trim(),urdu) { error=it }\n            val savedNote=UrduAutoTranslator.translateOrOriginal(note.trim(),urdu) { error=it }\n            save(value,incoming,date,savedNote,accountId,savedParty)\n'''
if new not in s:
    if old not in s: raise SystemExit('Roznamcha translator save anchor missing')
    s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# Customer fields use the same resilient translator; don't leave the save coroutine failed without feedback.
p = root / 'app/src/main/java/com/example/ui/dialogs/PremiumAddCustomerDialog.kt'
s = p.read_text(encoding='utf-8')
for old,new in [
('UrduAutoTranslator.translateForLanguage(name,urdu)','UrduAutoTranslator.translateOrOriginal(name,urdu) { error=it }'),
('UrduAutoTranslator.translateForLanguage(address,urdu)','UrduAutoTranslator.translateOrOriginal(address,urdu) { error=it }'),
('UrduAutoTranslator.translateForLanguage(description,urdu)','UrduAutoTranslator.translateOrOriginal(description,urdu) { error=it }'),
('UrduAutoTranslator.translateForLanguage(note,urdu)','UrduAutoTranslator.translateOrOriginal(note,urdu) { error=it }'),
('UrduAutoTranslator.translateForLanguage(type,urdu)','UrduAutoTranslator.translateOrOriginal(type,urdu) { error=it }')]: s=s.replace(old,new)
p.write_text(s,encoding='utf-8')

# Put the requested developer credit at the bottom of generated Khata/Roznamcha PNG receipts.
p = root / 'app/src/main/java/com/example/util/ThermalReceiptImage.kt'
s = p.read_text(encoding='utf-8')
old='''    canvas.drawText("Thank you • شکریہ",margin,height-38f,footer)\n'''
new='''    canvas.drawText("Thank you • شکریہ",margin,height-66f,footer)\n    val credit=TextPaint(TextPaint.ANTI_ALIAS_FLAG).apply { color=Color.rgb(110,120,114); textSize=15f }\n    canvas.drawText("Developed by Muhammad Arshad • 03027761415",margin,height-34f,credit)\n'''
if new not in s:
    if old not in s: raise SystemExit('Receipt footer anchor missing')
    s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('Applied Roznamcha party history, party quick-pick, receipt metadata/footer and resilient bilingual translation.')
