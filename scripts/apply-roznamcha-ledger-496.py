from pathlib import Path
import re,sys
r=Path(sys.argv[1]); p=r/"app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt"; s=p.read_text(encoding="utf-8")
s=s.replace('        val partyNames = all.map { it.recipientInfo.trim() }.filter { it.isNotBlank() }.distinctBy { it.lowercase(Locale.ROOT) }.sortedBy { it.lowercase(Locale.ROOT) }\n','',1)
pat=r'        if\(partyNames\.isNotEmpty\(\)\) item \{.*?\n        \}\n        item \{\n          Column\(verticalArrangement=Arrangement\.spacedBy\(10\.dp\)\)'
rep='''        if(selectedRoznamchaParty.isNotBlank()) item {
          val history=all.filter { it.recipientInfo.equals(selectedRoznamchaParty,true) }
          val received=history.filter { it.type==TransactionType.INCOME }.sumOf { it.amount }
          val paid=history.filter { it.type==TransactionType.EXPENSE }.sumOf { it.amount }
          Card(Modifier.fillMaxWidth(),colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.primaryContainer)) {
            Column(Modifier.fillMaxWidth().padding(16.dp),verticalArrangement=Arrangement.spacedBy(8.dp)) {
              Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween,verticalAlignment=androidx.compose.ui.Alignment.CenterVertically) {
                Column { Text(selectedRoznamchaParty,fontWeight=FontWeight.Bold,style=MaterialTheme.typography.titleLarge); Text(text("Complete party ledger","پارٹی کا مکمل کھاتہ"),style=MaterialTheme.typography.bodySmall) }
                TextButton(onClick={selectedRoznamchaParty=""}) { Text(text("Show all","تمام دکھائیں")) }
              }
              Text(history.size.toString()+" records")
              Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween) {
                Column { Text(text("Received","وصولی")); Text(state.money(received),fontWeight=FontWeight.Bold,color=Color(0xFF087F5B)) }
                Column { Text(text("Paid","ادائیگی")); Text(state.money(paid),fontWeight=FontWeight.Bold,color=Color(0xFFB45309)) }
                Column { Text(text("Balance","بقایا")); Text(state.money(received-paid),fontWeight=FontWeight.Bold) }
              }
            }
          }
        }
        item {
          Column(verticalArrangement=Arrangement.spacedBy(10.dp))'''
s,n=re.subn(pat,rep,s,count=1,flags=re.S)
if n!=1 and "Complete party ledger" not in s: raise SystemExit("Party chip list anchor missing")
s=s.replace('item { SearchBox(query,text("Search records","ریکارڈ تلاش کریں")){query=it} }','item { SearchBox(query,if(section=="ROZNAMCHA") text("Search party name or details","پارٹی کا نام یا تفصیل تلاش کریں") else text("Search records","ریکارڈ تلاش کریں")){query=it} }',1)
s=s.replace('''          ListTile(if(incoming)text("Cash received","نقد وصولی") else text("Cash paid","نقد ادائیگی"),
            (if(tx.recipientInfo.isBlank()) "" else tx.recipientInfo+" • ")+date+" • "+tx.accountName+"\\\\n"+tx.note,Icons.Default.MenuBook,
''','''          ListTile(tx.recipientInfo.ifBlank { text("Unassigned party","غیر مختص فریق") },
            (if(incoming)text("Cash received","نقد وصولی") else text("Cash paid","نقد ادائیگی"))+" • "+date+" • "+tx.accountName+"\\\\n"+tx.note,Icons.Default.MenuBook,
''',1)
if 'ListTile(tx.recipientInfo.ifBlank' not in s: raise SystemExit("Party-first row label patch failed")
s=s.replace('''              IconButton(onClick={deletingRoznamcha=tx}){Icon(Icons.Default.Delete,text("Delete","حذف"),tint=MaterialTheme.colorScheme.error)}
''','''              if(tx.recipientInfo.isNotBlank()) IconButton(onClick={selectedRoznamchaParty=tx.recipientInfo;query=""}){Icon(Icons.Default.History,text("Party history","پارٹی ہسٹری"))}
              IconButton(onClick={deletingRoznamcha=tx}){Icon(Icons.Default.Delete,text("Delete","حذف"),tint=MaterialTheme.colorScheme.error)}
''',1)
old='''    BusinessField(party,t("Client / Vendor / Supplier name","گاہک / وینڈر / سپلائر کا نام")){party=it}
    val knownParties=state.transactions.filter { it.category=="Roznamcha" }.map { it.recipientInfo.trim() }.filter { it.isNotBlank() }.distinctBy { it.lowercase(Locale.ROOT) }.sortedBy { it.lowercase(Locale.ROOT) }
    if(knownParties.isNotEmpty()) Row(Modifier.horizontalScroll(rememberScrollState()),horizontalArrangement=Arrangement.spacedBy(6.dp)) { knownParties.forEach { name -> FilterChip(party.equals(name,true),{party=name},label={Text(name)}) } }
'''
new='''    val knownParties=remember(state.transactions) { state.transactions.asSequence().filter { it.category=="Roznamcha" }.map { it.recipientInfo.trim() }.filter { it.isNotBlank() }.distinctBy { it.lowercase(Locale.ROOT) }.sortedBy { it.lowercase(Locale.ROOT) }.toList() }
    val partyMatches=if(party.isBlank()) emptyList() else knownParties.filter { it.contains(party,true) && !it.equals(party,true) }.take(8)
    var showPartyMatches by remember { mutableStateOf(false) }
    ExposedDropdownMenuBox(expanded=showPartyMatches && partyMatches.isNotEmpty(),onExpandedChange={showPartyMatches=it}) {
      OutlinedTextField(value=party,onValueChange={party=it;showPartyMatches=true},modifier=Modifier.fillMaxWidth().menuAnchor(),singleLine=true,
        label={Text(t("Client / Vendor / Supplier","کلائنٹ / وینڈر / سپلائر"))},placeholder={Text(t("Search or add a party name","نام تلاش کریں یا نیا نام لکھیں"))},
        trailingIcon={ExposedDropdownMenuDefaults.TrailingIcon(expanded=showPartyMatches && partyMatches.isNotEmpty())})
      ExposedDropdownMenu(expanded=showPartyMatches && partyMatches.isNotEmpty(),onDismissRequest={showPartyMatches=false}) {
        partyMatches.forEach { name -> DropdownMenuItem(text={Text(name)},onClick={party=name;showPartyMatches=false}) }
      }
    }
'''
if old in s:s=s.replace(old,new,1)
elif 'Search or add a party name' not in s: raise SystemExit("Party dropdown source anchor missing")
dup='''                  appendLine(text("Generated: ","تیار کرنے کا وقت: ")+SimpleDateFormat("dd MMM yyyy • hh:mm a",Locale.getDefault()).format(Date()))
                  appendLine("Developed by Muhammad Arshad • 03027761415")
                  appendLine(text("Generated: ","تیار کرنے کا وقت: ")+SimpleDateFormat("dd MMM yyyy • hh:mm a",Locale.getDefault()).format(Date()))
                  appendLine("Developed by Muhammad Arshad • 03027761415")
'''
rep='''                  appendLine(text("Generated: ","تیار کرنے کا وقت: ")+SimpleDateFormat("dd MMM yyyy • hh:mm a",Locale.getDefault()).format(Date()))
                  appendLine("Developed by Muhammad Arshad 03027761415")
'''
s=s.replace(dup,rep,1)
p.write_text(s,encoding="utf-8")
print("Applied party search and consolidated party ledger patch.")
