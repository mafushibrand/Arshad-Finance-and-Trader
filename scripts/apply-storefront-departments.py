#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1])
p = root / "app/src/main/java/com/example/ui/screens/BusinessHomeScreen.kt"
s = p.read_text(encoding="utf-8")

old = '''  val visibleCategories = if (categories.isNotEmpty()) categories else listOf("Grocery", "Bakery", "Fruit", "Vegetables", "Meat", "Dry Fruits", "Spices")'''
new = '''  // Storefront departments are always visible; real inventory categories remain available too.
  val mainDepartments = listOf(
    "Grocery", "Fresh & Frozen", "Snacks & Beverages", "Personal Care",
    "Household", "Baby Care", "Electronics", "Clothing",
    "Home & Kitchen", "Stationery & Toys"
  )
  val visibleCategories = (mainDepartments + categories)
    .distinctBy { it.lowercase(Locale.ROOT) }
'''
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit("Cannot locate storefront category list")

# Remove the duplicate POS/Billing, Khata and Services shortcut row from Home.
old = '''      item {
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
          StoreShortcut(t("POS & Billing", "POS اور بلنگ"), "🧾", Modifier.weight(1f), onPosClick)
          StoreShortcut(t("Khata", "کھاتہ"), "📒", Modifier.weight(1f), onBillingClick)
          StoreShortcut(t("Services", "سروسز"), "🛠️", Modifier.weight(1f), onServicesClick)
        }
      }
'''
if old in s:
    s = s.replace(old, "", 1)
# Remove now-unused helper.
helper = '''@Composable
private fun StoreShortcut(title: String, emoji: String, modifier: Modifier, onClick: () -> Unit) {
  Card(onClick = onClick, modifier = modifier, shape = RoundedCornerShape(16.dp), colors = CardDefaults.cardColors(containerColor = StoreMint)) {
    Column(Modifier.fillMaxWidth().padding(12.dp), horizontalAlignment = Alignment.CenterHorizontally) { Text(emoji, fontSize = 24.sp); Text(title, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold, maxLines = 1) }
  }
}

'''
s = s.replace(helper, "", 1)

# Product detail view uses a large, full-width HD image; Home cards stay compact.
s = s.replace(
'''items(categoryItems, key = { "product-${it.id}" }) { product -> StoreProductCard(product, uiState.currencySymbol, urdu, { onAddToCart(product.id) }, Modifier.fillMaxWidth()) }''',
'''items(categoryItems, key = { "product-${it.id}" }) { product -> StoreProductCard(product, uiState.currencySymbol, urdu, { onAddToCart(product.id) }, Modifier.fillMaxWidth(), detailed = true) }''',
1
)
s = s.replace(
'''private fun StoreProductCard(item: InventoryItem, currency: String, urdu: Boolean, onAdd: () -> Unit, modifier: Modifier = Modifier) {''',
'''private fun StoreProductCard(item: InventoryItem, currency: String, urdu: Boolean, onAdd: () -> Unit, modifier: Modifier = Modifier, detailed: Boolean = false) {''',
1
)
s = s.replace(
'''if (photo != null || demoPhoto != null) AsyncImage(model = photo ?: demoPhoto, contentDescription = title, contentScale = ContentScale.Crop, modifier = Modifier.fillMaxWidth().height(112.dp).clip(RoundedCornerShape(12.dp)))
      else Box(Modifier.fillMaxWidth().height(112.dp).clip(RoundedCornerShape(12.dp)).background(StoreMint), contentAlignment = Alignment.Center) {''',
'''if (photo != null || demoPhoto != null) AsyncImage(model = photo ?: demoPhoto, contentDescription = title, contentScale = ContentScale.Crop, modifier = Modifier.fillMaxWidth().height(if (detailed) 228.dp else 132.dp).clip(RoundedCornerShape(12.dp)))
      else Box(Modifier.fillMaxWidth().height(if (detailed) 228.dp else 132.dp).clip(RoundedCornerShape(12.dp)).background(StoreMint), contentAlignment = Alignment.Center) {''',
1
)
# Richer product detail spacing and title sizing.
s = s.replace('''Column(Modifier.padding(9.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {''',
'''Column(Modifier.padding(if (detailed) 14.dp else 9.dp), verticalArrangement = Arrangement.spacedBy(if (detailed) 10.dp else 5.dp)) {''', 1)
s = s.replace('''Text(title, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold, maxLines = 2, overflow = TextOverflow.Ellipsis)''',
'''Text(title, style = if (detailed) MaterialTheme.typography.titleLarge else MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold, maxLines = if (detailed) 3 else 2, overflow = TextOverflow.Ellipsis)''', 1)

# Bilingual department labels and icons.
s = s.replace('''    "grocery" -> "کریانہ"; "household" -> "گھریلو اشیاء";''',
'''    "grocery" -> "کریانہ"; "fresh & frozen" -> "تازہ اور منجمد اشیاء"; "snacks & beverages" -> "سنیکس اور مشروبات"
    "personal care" -> "ذاتی نگہداشت"; "baby care" -> "بچوں کی اشیاء"; "electronics" -> "الیکٹرانکس"
    "home & kitchen" -> "گھر اور کچن"; "stationery & toys" -> "اسٹیشنری اور کھلونے"; "household" -> "گھریلو اشیاء";''', 1)
s = s.replace('''  name.contains("grocery", true) || name.contains("general", true) -> "🛒"''',
'''  name.contains("grocery", true) || name.contains("general", true) -> "🛒"
  name.contains("fresh", true) || name.contains("frozen", true) -> "🥬"
  name.contains("snacks", true) || name.contains("beverage", true) -> "🥤"
  name.contains("personal", true) -> "🧴"
  name.contains("baby", true) -> "🍼"
  name.contains("home", true) || name.contains("kitchen", true) -> "🍽️"
  name.contains("stationery", true) || name.contains("toy", true) -> "🧸"''', 1)

p.write_text(s, encoding="utf-8")
print("Applied storefront departments, removed duplicate shortcut row, and enlarged product detail images.")
