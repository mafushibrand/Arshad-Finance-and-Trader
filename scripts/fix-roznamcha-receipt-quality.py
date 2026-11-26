from pathlib import Path
import sys
root=Path(sys.argv[1])
p=root/'app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt'
s=p.read_text(encoding='utf-8')
old='''          val date=SimpleDateFormat("dd MMM yyyy • hh:mm a",Locale.getDefault()).format(Date(tx.dateMillis))'''
new='''          val date=SimpleDateFormat("dd MMM yyyy • hh:mm a",Locale("en","PK")).apply { timeZone=java.util.TimeZone.getTimeZone("Asia/Karachi") }.format(Date(tx.dateMillis))'''
if old in s: s=s.replace(old,new,1)
elif new not in s: raise SystemExit("Roznamcha date formatter anchor missing")
old='''          appendLine(text("Generated: ","تیار کرنے کا وقت: ")+SimpleDateFormat("dd MMM yyyy • hh:mm a",Locale.getDefault()).format(Date()))
          appendLine("Developed by Muhammad Arshad • 03027761415")
                  appendLine(text("Generated: ","تیار کرنے کا وقت: ")+SimpleDateFormat("dd MMM yyyy • hh:mm a",Locale.getDefault()).format(Date()))
                  appendLine("Developed by Muhammad Arshad • 03027761415")'''
if old in s: s=s.replace(old,"",1)
elif 'appendLine(text("Generated: ","تیار کرنے کا وقت: ")' in s or 'appendLine("Developed by Muhammad Arshad • 03027761415")' in s:
    raise SystemExit("Expected duplicate receipt lines differ; refusing unsafe patch")
s=s.replace('''val today = SimpleDateFormat("yyyyMMdd",Locale.US).format(Date())
        val month = SimpleDateFormat("yyyyMM",Locale.US).format(Date())''','''val today = SimpleDateFormat("yyyyMMdd",Locale.US).apply { timeZone=java.util.TimeZone.getTimeZone("Asia/Karachi") }.format(Date())
        val month = SimpleDateFormat("yyyyMM",Locale.US).apply { timeZone=java.util.TimeZone.getTimeZone("Asia/Karachi") }.format(Date())''',1)
s=s.replace('''SimpleDateFormat("yyyyMMdd",Locale.US).format(date)==today
            "MONTH" -> SimpleDateFormat("yyyyMM",Locale.US).format(date)==month''','''SimpleDateFormat("yyyyMMdd",Locale.US).apply { timeZone=java.util.TimeZone.getTimeZone("Asia/Karachi") }.format(date)==today
            "MONTH" -> SimpleDateFormat("yyyyMM",Locale.US).apply { timeZone=java.util.TimeZone.getTimeZone("Asia/Karachi") }.format(date)==month''',1)
p.write_text(s,encoding='utf-8')
check=p.read_text(encoding='utf-8')
assert 'appendLine(text("Generated: ","تیار کرنے کا وقت: ")' not in check
assert 'appendLine("Developed by Muhammad Arshad • 03027761415")' not in check
assert 'timeZone=java.util.TimeZone.getTimeZone("Asia/Karachi")' in check
print("PASS: original transaction timestamp and PK timezone retained; duplicate generated time/footer removed.")
