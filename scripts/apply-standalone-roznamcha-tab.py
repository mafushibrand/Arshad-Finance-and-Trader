from pathlib import Path
import sys

root=Path(sys.argv[1])

def patch(rel, old, new, label):
    p=root/rel
    s=p.read_text(encoding="utf-8")
    if new in s:
        print("Already applied:",label); return
    if s.count(old)!=1:
        raise SystemExit(f"Safe patch failed for {label}: expected exactly one anchor, got {s.count(old)}")
    p.write_text(s.replace(old,new,1),encoding="utf-8")
    print("Applied:",label)

# Dedicated first-class Roznamcha destination, separate from Khata.
patch("app/src/main/java/com/example/ui/FinanceViewModel.kt",
"""  OPERATIONS,
  PLANNER,""",
"""  OPERATIONS,
  ROZNAMCHA,
  PLANNER,""","FinanceTab.ROZNAMCHA")

patch("app/src/main/java/com/example/ui/components/BottomNavBar.kt",
"""    if (features.khata) NavBarChoice(if (urdu) "کھاتہ" else "Khata", Icons.Default.ReceiptLong,
      selectedTab == FinanceTab.LEDGERS, "nav_tab_ledgers") { onTabSelected(FinanceTab.LEDGERS) }
    NavBarChoice(if (urdu) "مزید" else "More", Icons.Default.MoreHoriz,""",
"""    if (features.khata) NavBarChoice(if (urdu) "کھاتہ" else "Khata", Icons.Default.ReceiptLong,
      selectedTab == FinanceTab.LEDGERS, "nav_tab_ledgers") { onTabSelected(FinanceTab.LEDGERS) }
    if (!personal) NavBarChoice(if (urdu) "روزنامچہ" else "Roznamcha", Icons.Default.MenuBook,
      selectedTab == FinanceTab.ROZNAMCHA, "nav_tab_roznamcha") { onTabSelected(FinanceTab.ROZNAMCHA) }
    NavBarChoice(if (urdu) "مزید" else "More", Icons.Default.MoreHoriz,""","Separate Roznamcha bottom navigation")

patch("app/src/main/java/com/example/ui/FinanceViewModel.kt",
"""      FinanceTab.LEDGERS -> f.khata
      FinanceTab.REPORTS -> f.reports""",
"""      FinanceTab.LEDGERS -> f.khata
      FinanceTab.ROZNAMCHA -> true
      FinanceTab.REPORTS -> f.reports""","Roznamcha tab access")

patch("app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt",
"""fun BusinessOperationsScreen(state: FinanceUiState, viewModel: FinanceViewModel) {""",
"""fun BusinessOperationsScreen(state: FinanceUiState, viewModel: FinanceViewModel, startSection: String? = null) {""","Operations start section parameter")

patch("app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt",
"""  var section by remember { mutableStateOf("JOB") }
  LaunchedEffect(sections.keys) {if(section !in sections)section="JOB"}""",
"""  var section by remember(startSection) { mutableStateOf(startSection ?: "JOB") }
  LaunchedEffect(startSection, sections.keys) {
    if (startSection != null && startSection in sections) section = startSection
    else if(section !in sections)section="JOB"
  }""","Open Roznamcha directly")

patch("app/src/main/java/com/example/MainActivity.kt",
"""        FinanceTab.OPERATIONS -> { com.example.ui.screens.BusinessOperationsScreen(uiState, viewModel) }
        FinanceTab.PURCHASES ->""",
"""        FinanceTab.OPERATIONS -> { com.example.ui.screens.BusinessOperationsScreen(uiState, viewModel) }
        FinanceTab.ROZNAMCHA -> { com.example.ui.screens.BusinessOperationsScreen(uiState, viewModel, "ROZNAMCHA") }
        FinanceTab.PURCHASES ->""","Dedicated Roznamcha screen route")

# Keep the More shortcut as a fallback route too.
p=root/"app/src/main/java/com/example/ui/components/BottomNavBar.kt"
s=p.read_text(encoding="utf-8")
anchor='''          MenuDestination("Business workspace", "کاروباری مرکز", Icons.Default.BusinessCenter, FinanceTab.OPERATIONS, "nav_operations", urdu) { sheet = ""; onTabSelected(FinanceTab.OPERATIONS) }
          MenuDestination("Settings",'''
replace='''          MenuDestination("Business workspace", "کاروباری مرکز", Icons.Default.BusinessCenter, FinanceTab.OPERATIONS, "nav_operations", urdu) { sheet = ""; onTabSelected(FinanceTab.OPERATIONS) }
          MenuDestination("Roznamcha", "روزنامچہ", Icons.Default.MenuBook, FinanceTab.ROZNAMCHA, "nav_more_roznamcha", urdu) { sheet = ""; onTabSelected(FinanceTab.ROZNAMCHA) }
          MenuDestination("Settings",'''
if "nav_more_roznamcha" not in s:
    if s.count(anchor)!=1: raise SystemExit("More menu Roznamcha insertion anchor mismatch")
    p.write_text(s.replace(anchor,replace,1),encoding="utf-8")

# Bump build metadata for a signed in-place update of the existing 4.9 standalone package.
p=root/"app/build.gradle.kts"
s=p.read_text(encoding="utf-8")
if 'versionCode = 61' not in s:
    if 'versionCode = 60' not in s or 'versionName = "4.9.0"' not in s:
        raise SystemExit("Expected 4.9.0 version metadata missing; refusing unsafe bump")
    s=s.replace('versionCode = 60','versionCode = 61',1).replace('versionName = "4.9.0"','versionName = "4.9.1"',1)
    p.write_text(s,encoding="utf-8")
print("Set version 4.9.1 / code 61. Package and cached CI signing identity remain unchanged.")
