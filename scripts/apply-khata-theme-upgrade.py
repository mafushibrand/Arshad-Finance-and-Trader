from pathlib import Path
import shutil, sys

root=Path(sys.argv[1])
base=root/"app/src/main/java/com/example"
repo=Path(__file__).resolve().parent.parent
patch_dir=repo/"patches/khata-theme"

def replace(path, old, new, label):
    p=root/path
    s=p.read_text(encoding="utf-8")
    if new in s:
        return
    if old not in s:
        raise SystemExit(f"Patch anchor missing ({label}) in {path}; stopping without overwriting.")
    p.write_text(s.replace(old,new,1),encoding="utf-8")

# Copy reviewable Kotlin sources from the repository patch folder into the extracted Android project.
shutil.copy2(patch_dir/"AppThemePalettes.kt",base/"ui/theme/AppThemePalettes.kt")
shutil.copy2(patch_dir/"ThemeSettingsScreen.kt",base/"ui/screens/ThemeSettingsScreen.kt")

theme=base/"ui/theme/Theme.kt"
theme.write_text("""package com.example.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

private fun lightScheme(p: AppThemePalette) = lightColorScheme(
  primary=p.primary,onPrimary=p.onPrimary,primaryContainer=p.container,onPrimaryContainer=p.primary,
  secondary=p.secondary,onSecondary=Color.White,secondaryContainer=p.container.copy(alpha=.72f),onSecondaryContainer=p.primary,
  tertiary=p.tertiary,onTertiary=Color.White,tertiaryContainer=p.container,onTertiaryContainer=p.primary,
  background=p.background,onBackground=TextPrimary,surface=p.surface,onSurface=TextPrimary,
  surfaceVariant=p.container.copy(alpha=.55f),onSurfaceVariant=TextSecondary,outline=LightOutline,outlineVariant=LightOutlineVariant,
  error=ExpenseRed,onError=Color.White,errorContainer=ExpenseRedContainer,onErrorContainer=OnExpenseRedContainer
)

private fun darkScheme(p: AppThemePalette) = darkColorScheme(
  primary=p.primary.copy(red=(p.primary.red*.75f+.25f).coerceAtMost(1f),green=(p.primary.green*.75f+.25f).coerceAtMost(1f),blue=(p.primary.blue*.75f+.25f).coerceAtMost(1f)),
  onPrimary=Color(0xFF101318),primaryContainer=p.primary.copy(alpha=.35f),onPrimaryContainer=Color(0xFFF4F5F8),
  secondary=p.secondary,onSecondary=Color(0xFF101318),secondaryContainer=Color(0xFF35404A),onSecondaryContainer=Color(0xFFE7EAF0),
  tertiary=p.tertiary,onTertiary=Color(0xFF101318),background=Color(0xFF111318),onBackground=Color(0xFFE2E2E9),
  surface=Color(0xFF191C20),onSurface=Color(0xFFE2E2E9),surfaceVariant=Color(0xFF343941),onSurfaceVariant=Color(0xFFC4C6CF),
  outline=Color(0xFF8E9099),error=Color(0xFFFFB4AB),onError=Color(0xFF690005)
)

@Composable
fun MyApplicationTheme(themeId:String="default",darkTheme:Boolean=false,dynamicColor:Boolean=false,content:@Composable ()->Unit) {
  val palette=AppThemePalettes.get(themeId)
  val scheme=if(darkTheme) darkScheme(palette) else lightScheme(palette)
  MaterialTheme(colorScheme=scheme,typography=Typography,shapes=androidx.compose.material3.Shapes(
    small=androidx.compose.foundation.shape.RoundedCornerShape(12.dp),
    medium=androidx.compose.foundation.shape.RoundedCornerShape(18.dp),
    large=androidx.compose.foundation.shape.RoundedCornerShape(24.dp)
  ),content=content)
}
""",encoding="utf-8")

# Add THEME destination.
replace("app/src/main/java/com/example/ui/FinanceViewModel.kt",
"""  HOME_SLIDERS;
""","""  HOME_SLIDERS,
  THEME;
""","FinanceTab enum")
replace("app/src/main/java/com/example/ui/FinanceViewModel.kt",
"""    if (tab == FinanceTab.HOME_SLIDERS) { _selectedTab.value = tab; return }""",
"""    if (tab in listOf(FinanceTab.HOME_SLIDERS, FinanceTab.THEME)) { _selectedTab.value = tab; return }""","theme route access")

# More menu destination.
replace("app/src/main/java/com/example/ui/components/BottomNavBar.kt",
"FinanceTab.OPERATIONS, FinanceTab.HOME_SLIDERS)",
"FinanceTab.OPERATIONS, FinanceTab.HOME_SLIDERS, FinanceTab.THEME)","More selected state")
replace("app/src/main/java/com/example/ui/components/BottomNavBar.kt",
"""          MenuDestination("Settings", "سیٹنگز", Icons.Default.Settings, FinanceTab.SETTINGS, "nav_tab_settings", urdu) { sheet = ""; onTabSelected(FinanceTab.SETTINGS) }""",
"""          MenuDestination("Settings", "سیٹنگز", Icons.Default.Settings, FinanceTab.SETTINGS, "nav_tab_settings", urdu) { sheet = ""; onTabSelected(FinanceTab.SETTINGS) }
          MenuDestination("App theme & colors", "ایپ تھیم اور رنگ", Icons.Default.Palette, FinanceTab.THEME, "nav_app_theme", urdu) { sheet = ""; onTabSelected(FinanceTab.THEME) }""","More theme item")

# Activity-level persisted theme means it applies before the first screen is drawn.
replace("app/src/main/java/com/example/MainActivity.kt",
"""      MyApplicationTheme {
        FinanceApp(viewModel = viewModel)
      }""",
"""      var selectedTheme by remember { mutableStateOf(getSharedPreferences("app_theme", MODE_PRIVATE).getString("selected_theme", "default") ?: "default") }
      MyApplicationTheme(themeId=selectedTheme) {
        FinanceApp(viewModel=viewModel,selectedTheme=selectedTheme,onThemeSelected={ theme ->
          selectedTheme=theme
          getSharedPreferences("app_theme",MODE_PRIVATE).edit().putString("selected_theme",theme).apply()
        })
      }""","persist selected theme")
replace("app/src/main/java/com/example/MainActivity.kt",
"""  viewModel: FinanceViewModel,
  modifier: Modifier = Modifier
)""",
"""  viewModel: FinanceViewModel,
  selectedTheme:String="default",
  onThemeSelected:(String)->Unit={},
  modifier: Modifier = Modifier
)""","FinanceApp parameters")
replace("app/src/main/java/com/example/MainActivity.kt",
"""      com.example.ui.screens.PersonalKhataScreen(uiState,
        {viewModel.openTrialLockDialog()}, {viewModel.toggleLanguage()}, {backupDialog=true},
        {name,phone,done->viewModel.personalContact(name,phone,done)},
        {id,amount,direction,note,done->viewModel.personalEntry(id,amount,direction,note,done)})""",
"""      if(uiState.selectedTab==FinanceTab.THEME) {
        com.example.ui.screens.ThemeSettingsScreen(uiState,selectedTheme,onThemeSelected) { viewModel.selectTab(FinanceTab.HOME) }
      } else com.example.ui.screens.PersonalKhataScreen(uiState,
        {viewModel.openTrialLockDialog()}, {viewModel.toggleLanguage()}, {backupDialog=true},
        {name,phone,done->viewModel.personalContact(name,phone,done)},
        {id,amount,direction,note,done->viewModel.personalEntry(id,amount,direction,note,done)},
        {viewModel.selectTab(FinanceTab.THEME)})""","personal khata theme entry")
replace("app/src/main/java/com/example/MainActivity.kt",
"""        FinanceTab.HOME_SLIDERS -> { com.example.ui.screens.HomeSliderManagerScreen(uiState) }
        FinanceTab.SETTINGS -> {""",
"""        FinanceTab.HOME_SLIDERS -> { com.example.ui.screens.HomeSliderManagerScreen(uiState) }
        FinanceTab.THEME -> { com.example.ui.screens.ThemeSettingsScreen(uiState,selectedTheme,onThemeSelected) { viewModel.selectTab(FinanceTab.HOME) } }
        FinanceTab.SETTINGS -> {""","theme route")
replace("app/src/main/java/com/example/MainActivity.kt",".background(LightBackground),",".background(MaterialTheme.colorScheme.background),","theme scaffold background")
replace("app/src/main/java/com/example/MainActivity.kt","containerColor = LightBackground","containerColor = MaterialTheme.colorScheme.background","theme scaffold container")

# Personal Khata gets a Theme shortcut beside language and backup.
replace("app/src/main/java/com/example/ui/screens/PersonalKhataScreen.kt",
"""addEntry:(String,Double,String,String,(String?)->Unit)->Unit) {""",
"""addEntry:(String,Double,String,String,(String?)->Unit)->Unit,onTheme:()->Unit = {}) {""","personal khata callback")
replace("app/src/main/java/com/example/ui/screens/PersonalKhataScreen.kt",
"""      TextButton(onClick=onBackup){Icon(Icons.Default.Backup,null);Text(state.word("Backup","بیک اپ"))}
    }}""",
"""      TextButton(onClick=onBackup){Icon(Icons.Default.Backup,null);Text(state.word("Backup","بیک اپ"))}
      TextButton(onClick=onTheme){Icon(Icons.Default.Palette,null);Text(state.word("Theme","تھیم"))}
    }}""","personal khata theme shortcut")

# Khata overview: receivables, collected amount, advance balances, searchable due bills.
replace("app/src/main/java/com/example/ui/screens/PremiumBillingScreen.kt",
"""  var filter by rememberSaveable { mutableIntStateOf(0) }
  val customers = uiState.customers.filter { search.isBlank() || it.name.contains(search, true) || it.phone.contains(search, true) }
  val bills = uiState.invoices.filter { (search.isBlank() || it.customerName.contains(search, true) || it.invoiceNumber.contains(search, true)) && (filter != 2 || it.remainingBalance > 0.0) }""",
"""  var filter by rememberSaveable { mutableIntStateOf(0) }
  val customers = uiState.customers.filter { search.isBlank() || it.name.contains(search, true) || it.phone.contains(search, true) }
    .let { list -> when(filter) { 1 -> list.filter { it.currentBalance > .000001 }; 2 -> list.filter { it.currentBalance < -.000001 }; else -> list } }
    .sortedByDescending { kotlin.math.abs(it.currentBalance) }
  val bills = uiState.invoices.filter { (search.isBlank() || it.customerName.contains(search, true) || it.invoiceNumber.contains(search, true)) && (filter != 4 || it.remainingBalance > 0.0) }""","Khata customer filters")
replace("app/src/main/java/com/example/ui/screens/PremiumBillingScreen.kt",
"""    item { Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
      Metric(uiState.word("To collect", "وصول طلب"), uiState.money(uiState.totalActiveUdhar), Peach, Modifier.weight(1f))
      Metric(uiState.word("Customers", "گاہک"), uiState.customers.size.toString(), modifier = Modifier.weight(1f))
    } }
    item { SearchBox(search, uiState.word("Search customer, phone or invoice", "گاہک، فون یا بل تلاش کریں")) { search = it } }
    item { FilterRow(listOf(uiState.word("Customers", "گاہک"), uiState.word("All bills", "تمام بل"), uiState.word("Due bills", "بقایہ بل")), filter) { filter = it } }
    if (filter == 0) {""",
"""    item { Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
      Metric(uiState.word("To collect", "وصول طلب"), uiState.money(uiState.totalActiveUdhar), MaterialTheme.colorScheme.primaryContainer, Modifier.weight(1f))
      Metric(uiState.word("Customers", "گاہک"), uiState.customers.size.toString(), modifier = Modifier.weight(1f))
    } }
    item { Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
      Metric(uiState.word("Collected", "وصول شدہ"), uiState.money(uiState.invoices.sumOf { it.amountPaid }), MaterialTheme.colorScheme.secondaryContainer, Modifier.weight(1f))
      Metric(uiState.word("Due bills", "بقایا بل"), uiState.invoices.count { it.remainingBalance > .000001 }.toString(), MaterialTheme.colorScheme.primaryContainer, Modifier.weight(1f))
    } }
    item { SearchBox(search, uiState.word("Search customer, phone or invoice", "گاہک، فون یا بل تلاش کریں")) { search = it } }
    item { FilterRow(listOf(uiState.word("All customers", "تمام گاہک"), uiState.word("To collect", "وصول طلب"), uiState.word("Advance", "ایڈوانس"), uiState.word("All bills", "تمام بل"), uiState.word("Due bills", "بقایا بل")), filter) { filter = it } }
    if (filter in 0..2) {""","Khata overview and filters")
replace("app/src/main/java/com/example/ui/screens/PremiumBillingScreen.kt",
"""      items(customers, key = { it.id }) { customer -> ListTile(customer.name, customer.phone.ifBlank { customer.customerType }, Icons.Default.Person, uiState.money(customer.currentBalance), Peach, { onSelectCustomer(customer) }) {""",
"""      items(customers, key = { it.id }) { customer ->
        val balanceLabel=when { customer.currentBalance > .000001 -> uiState.word("To collect","وصول طلب"); customer.currentBalance < -.000001 -> uiState.word("Advance","ایڈوانس"); else -> uiState.word("Clear","حساب صاف") }
        ListTile(customer.name, customer.phone.ifBlank { customer.customerType } + " • " + balanceLabel, Icons.Default.Person, uiState.money(kotlin.math.abs(customer.currentBalance)), MaterialTheme.colorScheme.primaryContainer, { onSelectCustomer(customer) }) {""","Khata balance labels")

# Shared premium UI primitives use the active palette instead of fixed emerald/white values.
p=base/"ui/screens/PremiumInventoryScreen.kt"
s=p.read_text(encoding="utf-8")
s=s.replace("Column(modifier.fillMaxSize().background(Cream)) {","Column(modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {",1)
s=s.replace("color = Mint) { Icon(icon, null, Modifier.padding(12.dp).size(24.dp), tint = Forest) }","color = MaterialTheme.colorScheme.primaryContainer) { Icon(icon, null, Modifier.padding(12.dp).size(24.dp), tint = MaterialTheme.colorScheme.primary) }",1)
s=s.replace("color = Ink)","color = MaterialTheme.colorScheme.onSurface)",1)
s=s.replace("unfocusedContainerColor = Color.White, focusedContainerColor = Color.White,","unfocusedContainerColor = MaterialTheme.colorScheme.surface, focusedContainerColor = MaterialTheme.colorScheme.surface,",1)
s=s.replace("unfocusedBorderColor = Color(0xFFDEE8DF)","unfocusedBorderColor = MaterialTheme.colorScheme.outlineVariant",1)
s=s.replace("containerColor = Forest","containerColor = MaterialTheme.colorScheme.primary",1)
s=s.replace("color = Color.White,\n    border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFEBEFE8))","color = MaterialTheme.colorScheme.surface,\n    border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)",1)
s=s.replace("color = Forest)","color = MaterialTheme.colorScheme.primary)",1)
s=s.replace("color = Color.White)","color = MaterialTheme.colorScheme.surface)",1)
s=s.replace("color = Forest, maxLines = 2)","color = MaterialTheme.colorScheme.primary, maxLines = 2)",1)
p.write_text(s,encoding="utf-8")

# Theme-aware page scaffold.
replace("app/src/main/java/com/example/ui/screens/PremiumBillingScreen.kt","Column(modifier.fillMaxSize().background(Cream)) {","Column(modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {","Khata legacy background")

# Unit coverage for palette IDs and custom hex parsing.
test=root/"app/src/test/java/com/example/AppThemePalettesTest.kt"
test.parent.mkdir(parents=True,exist_ok=True)
test.write_text("""package com.example

import com.example.ui.theme.AppThemePalettes
import org.junit.Assert.assertEquals
import org.junit.Test

class AppThemePalettesTest {
  @Test fun seasonalPalettesAreStable() {
    listOf("default","pakistan","eid","ramadan","milad","awareness","ocean","royal","sunrise").forEach {
      assertEquals(it,AppThemePalettes.get(it).id)
    }
  }
  @Test fun invalidPaletteFallsBackToDefault() {
    assertEquals("default",AppThemePalettes.get("unknown").id)
    assertEquals("default",AppThemePalettes.get("custom:not-hex").id)
  }
  @Test fun customPaletteKeepsSelectedHex() {
    assertEquals("custom:086B4D",AppThemePalettes.get("custom:086B4D").id)
  }
}
""",encoding="utf-8")

print("Khata overview and global theme upgrade applied.")
