from pathlib import Path
import sys
p=Path(sys.argv[1])/"app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt"
s=p.read_text()
fixes=[
('Card(Modifier.weight(1f),colors=CardDefaults.cardColors(containerColor=if(roznamchaSubTab=="PARTIES") Color(0xFF172554) else MaterialTheme.colorScheme.surfaceVariant),onClick={roznamchaSubTab="PARTIES"})','Card(onClick={roznamchaSubTab="PARTIES"},modifier=Modifier.weight(1f),colors=CardDefaults.cardColors(containerColor=if(roznamchaSubTab=="PARTIES") Color(0xFF172554) else MaterialTheme.colorScheme.surfaceVariant))'),
('Card(Modifier.weight(1f),colors=CardDefaults.cardColors(containerColor=if(roznamchaSubTab=="RECORDS") Color(0xFF172554) else MaterialTheme.colorScheme.surfaceVariant),onClick={roznamchaSubTab="RECORDS"})','Card(onClick={roznamchaSubTab="RECORDS"},modifier=Modifier.weight(1f),colors=CardDefaults.cardColors(containerColor=if(roznamchaSubTab=="RECORDS") Color(0xFF172554) else MaterialTheme.colorScheme.surfaceVariant))'),
('Card(Modifier.fillMaxWidth(),colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.surface),border=androidx.compose.foundation.BorderStroke(1.dp,MaterialTheme.colorScheme.outlineVariant),onClick={selectedRoznamchaParty=master.title;query=""})','Card(onClick={selectedRoznamchaParty=master.title;query=""},modifier=Modifier.fillMaxWidth(),colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.surface),border=androidx.compose.foundation.BorderStroke(1.dp,MaterialTheme.colorScheme.outlineVariant))')
]
for old,new in fixes:
 if old in s: s=s.replace(old,new,1)
 elif new not in s: raise SystemExit("Expected Card callback anchor not found")
p.write_text(s)
print("Corrected Material3 clickable Card parameter ordering.")
