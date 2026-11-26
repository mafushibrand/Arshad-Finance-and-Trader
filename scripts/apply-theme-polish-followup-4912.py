from pathlib import Path
import sys

root = Path(sys.argv[1])

def edit(rel, fn):
    p = root / rel
    s = p.read_text(encoding="utf-8")
    updated = fn(s)
    if updated != s:
        p.write_text(updated, encoding="utf-8")
        print("Updated", rel)
    else:
        print("Already current:", rel)

def business(s):
    if "var timeText by remember(initial?.id)" not in s:
        anchor = 'var dateText by remember(initial?.id) { mutableStateOf(SimpleDateFormat("yyyy-MM-dd",Locale.US).apply { timeZone=TimeZone.getTimeZone("Asia/Karachi") }.format(Date(initial?.dateMillis ?: System.currentTimeMillis()))) }'
        addition = anchor + '\n  var timeText by remember(initial?.id) { mutableStateOf(SimpleDateFormat("HH:mm",Locale.US).apply { timeZone=TimeZone.getTimeZone("Asia/Karachi") }.format(Date(initial?.dateMillis ?: System.currentTimeMillis()))) }'
        if anchor not in s:
            raise SystemExit("Cannot find Roznamcha date field anchor")
        s = s.replace(anchor, addition, 1)
    old = 'SimpleDateFormat("yyyy-MM-dd",Locale.US).apply { isLenient=false; timeZone=TimeZone.getTimeZone("Asia/Karachi") }.parse(dateText)?.time'
    new = 'SimpleDateFormat("yyyy-MM-dd HH:mm",Locale.US).apply { isLenient=false; timeZone=TimeZone.getTimeZone("Asia/Karachi") }.parse("$dateText $timeText")?.time'
    if old in s:
        s = s.replace(old, new, 1)
    s = s.replace('date==null -> error=t("Use date format YYYY-MM-DD","تاریخ YYYY-MM-DD میں لکھیں")',
                  'date==null -> error=t("Enter date as YYYY-MM-DD and time as HH:mm","تاریخ YYYY-MM-DD اور وقت HH:mm میں درج کریں")', 1)
    date_field = 'BusinessField(dateText,t("Entry date (YYYY-MM-DD)","اندراج کی تاریخ (سال-مہینہ-دن)")){dateText=it}'
    time_field = 'BusinessField(timeText,t("Entry time (24-hour HH:mm)","اندراج کا وقت (24 گھنٹے HH:mm)")){timeText=it}'
    if time_field not in s:
        if date_field not in s:
            raise SystemExit("Cannot find Roznamcha date field in form")
        s = s.replace(date_field, date_field + '\n    ' + time_field, 1)
    if 'val savedAddress=UrduAutoTranslator.translateOrOriginal(partyAddress.trim(),urdu)' not in s:
        old_translate = 'val savedNote=UrduAutoTranslator.translateOrOriginal(note.trim(),urdu) { error=it }\n            save(value,incoming,date,savedNote,accountId,savedParty,partyType,partyPhone,partyAddress,requestId)'
        new_translate = 'val savedNote=UrduAutoTranslator.translateOrOriginal(note.trim(),urdu) { error=it }\n            val savedAddress=UrduAutoTranslator.translateOrOriginal(partyAddress.trim(),urdu) { error=it }\n            save(value,incoming,date,savedNote,accountId,savedParty,partyType,partyPhone,savedAddress,requestId)'
        if old_translate in s:
            s = s.replace(old_translate, new_translate, 1)
    return s

def login(s):
    s = s.replace('color = MaterialTheme.colorScheme.onPrimary,\n        shadowElevation = 12.dp',
                  'color = MaterialTheme.colorScheme.surface,\n        shadowElevation = 12.dp')
    s = s.replace('color = if (!isSignUp) Color.White else MaterialTheme.colorScheme.onSurfaceVariant',
                  'color = if (!isSignUp) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurfaceVariant')
    s = s.replace('color = if (isSignUp) Color.White else MaterialTheme.colorScheme.onSurfaceVariant',
                  'color = if (isSignUp) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurfaceVariant')
    return s

def role(s):
    s = s.replace('color = if (selectedRole == UserRole.EMPLOYEE) EmeraldSuccess else MaterialTheme.colorScheme.surface',
                  'color = if (selectedRole == UserRole.EMPLOYEE) MaterialTheme.colorScheme.secondary else MaterialTheme.colorScheme.surface')
    s = s.replace('import com.example.ui.theme.EmeraldSuccess\n', '')
    return s

edit("app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt", business)
edit("app/src/main/java/com/example/ui/screens/LoginScreen.kt", login)
edit("app/src/main/java/com/example/ui/dialogs/RoleLoginDialog.kt", role)
