#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1])

def patch(rel, old, new, label):
    p = root / rel
    s = p.read_text(encoding="utf-8")
    if new in s:
        print("Already applied:", label)
        return
    if old not in s:
        raise SystemExit("Missing patch anchor for " + label + " in " + rel)
    p.write_text(s.replace(old, new, 1), encoding="utf-8")
    print("Applied:", label)

home = "app/src/main/java/com/example/ui/screens/BusinessHomeScreen.kt"
p = root / home
s = p.read_text(encoding="utf-8")
old = '''  val categories = (savedCategories + uiState.inventoryItems.map { it.category.trim() }.filter { it.isNotBlank() })
    .distinctBy { it.lowercase(Locale.ROOT) }.filterNot { it.lowercase(Locale.ROOT) in hidden }.sortedBy { it.lowercase(Locale.ROOT) }
'''
new = '''  val mainDepartments = listOf(
    "Grocery", "Fresh & Frozen", "Snacks & Beverages", "Personal Care",
    "Household", "Baby Care", "Electronics", "Clothing",
    "Home & Kitchen", "Stationery & Toys"
  )
  val categories = (mainDepartments + savedCategories + uiState.inventoryItems.map { it.category.trim() }.filter { it.isNotBlank() })
    .distinctBy { it.lowercase(Locale.ROOT) }.filterNot { it.lowercase(Locale.ROOT) in hidden }.sortedBy { it.lowercase(Locale.ROOT) }
'''
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit("Missing category management list anchor")
old = '''  // Storefront departments are always visible; real inventory categories remain available too.
  val mainDepartments = listOf(
    "Grocery", "Fresh & Frozen", "Snacks & Beverages", "Personal Care",
    "Household", "Baby Care", "Electronics", "Clothing",
    "Home & Kitchen", "Stationery & Toys"
  )
  val visibleCategories = (mainDepartments + categories)
    .distinctBy { it.lowercase(Locale.ROOT) }
'''
new = '''  val visibleCategories = categories
'''
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit("Missing visible department list anchor")
old = '''  val products = uiState.inventoryItems.filter { it.salePrice > 0.0 && !it.category.equals("Uncategorized", true) }
'''
new = '''  val products = uiState.inventoryItems.filter { it.salePrice > 0.0 && !it.category.equals("Uncategorized", true) && !it.barcode.startsWith("SRV-") }
'''
if old in s: s = s.replace(old, new, 1)
elif new not in s: raise SystemExit("Missing Home product filter")
old = '''      val categoryItems = products.filter { it.category.equals(selectedCategory, true) }
'''
new = '''      val categoryItems = products.filter { categoryMatchesDepartment(it.category, selectedCategory!!) }
'''
if old in s: s = s.replace(old, new, 1)
elif new not in s: raise SystemExit("Missing category detail filter")
anchor = '''@Composable
private fun StoreProductCard'''
matcher = '''private fun categoryMatchesDepartment(productCategory: String, selected: String): Boolean {
  if (productCategory.equals(selected, true)) return true
  val c = productCategory.lowercase(Locale.ROOT)
  val d = selected.lowercase(Locale.ROOT)
  val aliases = mapOf(
    "grocery" to listOf("grocery", "kiryana", "grain", "rice", "pulses", "oil", "ghee", "spice", "dairy", "dry fruit"),
    "fresh & frozen" to listOf("fruit", "vegetable", "meat", "seafood", "frozen", "bakery", "cake"),
    "snacks & beverages" to listOf("snack", "beverage", "drink", "noodle", "chocolate"),
    "personal care" to listOf("personal care", "beauty", "skincare", "cosmetic", "hair", "perfume"),
    "household" to listOf("household", "clean", "detergent", "tissue", "disposable"),
    "baby care" to listOf("baby", "diaper", "maternity"),
    "electronics" to listOf("electronic", "computer", "appliance", "accessor"),
    "clothing" to listOf("clothing", "garment", "fashion", "footwear", "shoe", "bag"),
    "home & kitchen" to listOf("home", "kitchen", "crockery", "furniture", "glassware"),
    "stationery & toys" to listOf("stationery", "toy", "book", "game", "pet", "medical", "medicine")
  )
  return aliases[d]?.any { it in c } == true
}

@Composable
private fun StoreProductCard'''
if anchor in s:
    s = s.replace(anchor, matcher, 1)
elif "private fun categoryMatchesDepartment" not in s:
    raise SystemExit("Missing product card anchor")
old = '''  onDeleteCategory: (String) -> Unit = {}
'''
new = '''  onDeleteCategory: (String) -> Unit = {},
  onLoadDemoCatalog: () -> Unit = {}
'''
if old in s: s = s.replace(old, new, 1)
elif new not in s: raise SystemExit("Missing Home callback signature")
old = '''              Button(onClick = onAddProduct, modifier = Modifier.fillMaxWidth()) { Icon(Icons.Default.Add, null); Spacer(Modifier.width(6.dp)); Text(t("Add first product", "پہلی پروڈکٹ شامل کریں")) }
'''
new = '''              Button(onClick = onLoadDemoCatalog, modifier = Modifier.fillMaxWidth()) { Icon(Icons.Default.Storefront, null); Spacer(Modifier.width(6.dp)); Text(t("Load sample products", "نمونہ پروڈکٹس لوڈ کریں")) }
              OutlinedButton(onClick = onAddProduct, modifier = Modifier.fillMaxWidth()) { Icon(Icons.Default.Add, null); Spacer(Modifier.width(6.dp)); Text(t("Add your own product", "اپنی پروڈکٹ شامل کریں")) }
'''
if old in s: s = s.replace(old, new, 1)
elif new not in s: raise SystemExit("Missing empty catalogue CTA")
p.write_text(s, encoding="utf-8")

core = "app/src/main/java/com/example/business/BusinessCore.kt"
p = root / core
s = p.read_text(encoding="utf-8")
old = '''      if (old != null) dao.update(old.copy(archived = true, updatedAt = System.currentTimeMillis()))
      db.financeDao().getAllInventoryItems().first().filter { it.category.equals(oldName, true) }.forEach { item ->
'''
new = '''      if (old != null) dao.update(old.copy(archived = true, updatedAt = System.currentTimeMillis()))
      else dao.insert(BusinessRecord(kind = "CATALOG_CATEGORY", title = oldName.trim(), payload = "{}", archived = true))
      db.financeDao().getAllInventoryItems().first().filter { it.category.equals(oldName, true) }.forEach { item ->
'''
if old in s: s = s.replace(old, new, 1)
elif new not in s: raise SystemExit("Missing category rename archive anchor")
old = '''    if (category != null) dao.update(category.copy(archived = true, updatedAt = System.currentTimeMillis()))
    db.financeDao().getAllInventoryItems().first().filter { it.category.equals(name, true) }.forEach { item ->
'''
new = '''    if (category != null) dao.update(category.copy(archived = true, updatedAt = System.currentTimeMillis()))
    else dao.insert(BusinessRecord(kind = "CATALOG_CATEGORY", title = name.trim(), payload = "{}", archived = true))
    db.financeDao().getAllInventoryItems().first().filter { it.category.equals(name, true) }.forEach { item ->
'''
if old in s: s = s.replace(old, new, 1)
elif new not in s: raise SystemExit("Missing category delete archive anchor")
p.write_text(s, encoding="utf-8")

main = "app/src/main/java/com/example/MainActivity.kt"
p = root / main
s = p.read_text(encoding="utf-8")
old = '''              onDeleteCategory = { name -> viewModel.deleteCatalogCategory(name) { error -> if (error != null) android.widget.Toast.makeText(viewModel.getApplication(), error, android.widget.Toast.LENGTH_LONG).show() } }
'''
new = '''              onDeleteCategory = { name -> viewModel.deleteCatalogCategory(name) { error -> if (error != null) android.widget.Toast.makeText(viewModel.getApplication(), error, android.widget.Toast.LENGTH_LONG).show() } },
              onLoadDemoCatalog = { viewModel.seedTemplateDemo(uiState.businessProfile.templateId.ifBlank { "kiryana" }) { error -> if (error != null) android.widget.Toast.makeText(viewModel.getApplication(), error, android.widget.Toast.LENGTH_LONG).show() } }
'''
if old in s: s = s.replace(old, new, 1)
elif new not in s: raise SystemExit("Missing Home category callback wiring")
old = '''            onGoToPos = { viewModel.selectTab(FinanceTab.POS) }
'''
new = '''            onGoToPos = { viewModel.selectTab(FinanceTab.POS) },
            onLoadDemoCatalog = { viewModel.seedTemplateDemo(uiState.businessProfile.templateId.ifBlank { "kiryana" }) { error -> if (error != null) android.widget.Toast.makeText(viewModel.getApplication(), error, android.widget.Toast.LENGTH_LONG).show() } }
'''
stock = s.find("        FinanceTab.STOCK -> {")
pos = s.find(old, stock)
if pos >= 0:
    s = s[:pos] + s[pos:].replace(old, new, 1)
elif new not in s: raise SystemExit("Missing Products page sample CTA wiring")
p.write_text(s, encoding="utf-8")

inventory = "app/src/main/java/com/example/ui/screens/PremiumInventoryScreen.kt"
p = root / inventory
s = p.read_text(encoding="utf-8")
old = '''  onGoToPos: () -> Unit = {},
  modifier: Modifier = Modifier
) {
  var advanced'''
new = '''  onGoToPos: () -> Unit = {},
  onLoadDemoCatalog: () -> Unit = {},
  modifier: Modifier = Modifier
) {
  var advanced'''
if old in s: s = s.replace(old, new, 1)
elif new not in s: raise SystemExit("Missing InventoryScreen callback anchor")
old = '''    if (visible.isEmpty()) item { EmptyList(uiState.word("No products found", "کوئی سامان نہیں ملا"), uiState.word("Add your first product to start billing.", "بلنگ شروع کرنے کے لیے پہلا سامان شامل کریں۔"), Icons.Default.Inventory2) }
'''
new = '''    if (visible.isEmpty()) item {
      EmptyList(uiState.word("No products found", "کوئی سامان نہیں ملا"), uiState.word("Load sample products for a demo shop, or add your own products.", "ڈیمو دکان کے لیے نمونہ پروڈکٹس لوڈ کریں یا اپنا سامان شامل کریں۔"), Icons.Default.Inventory2)
      Spacer(Modifier.height(10.dp))
      PremiumButton(uiState.word("Load sample products", "نمونہ پروڈکٹس لوڈ کریں"), onLoadDemoCatalog)
    }
'''
if old in s: s = s.replace(old, new, 1)
elif new not in s: raise SystemExit("Missing Products empty state")
p.write_text(s, encoding="utf-8")

nav = "app/src/main/java/com/example/ui/components/BottomNavBar.kt"
p = root / nav
s = p.read_text(encoding="utf-8")
old = '''    NavBarChoice(if (urdu) "فنانس" else "Finance", Icons.Default.AccountBalance,
'''
new = '''    NavBarChoice(if (urdu) "مزید" else "More", Icons.Default.MoreHoriz,
'''
if old in s: s = s.replace(old, new, 1)
elif new not in s: raise SystemExit("Missing Finance nav label")
s = s.replace('''else { if (urdu) "فنانس اور کاروباری ٹولز" else "Finance & business tools" }''',
              '''else { if (urdu) "مزید کاروباری ٹولز" else "More tools" }''', 1)
p.write_text(s, encoding="utf-8")

# Include the real category matcher and sample catalogue actions in the Home screen;
# demo seeding merges missing records and never clears an existing business catalogue.
print("Catalogue CRUD, department matching, demo product loading, and Finance -> More applied.")
