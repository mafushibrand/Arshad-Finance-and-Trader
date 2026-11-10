#!/usr/bin/env python3
"""Populate every general-store storefront department and show sample loading actions."""
from pathlib import Path
import sys

root = Path(sys.argv[1])
demo_path = root / "app/src/main/java/com/example/business/DemoLibrary.kt"
source = demo_path.read_text(encoding="utf-8")
old = '''  fun items(template: String): List<InventoryItem> {
    val samples = catalog[template] ?: catalog.getValue("custom")
    return samples.map { sample ->
      item(sample.name, sample.category, sample.unit, sample.cost, sample.price, sample.stock,
        sample.type, JSONObject().put("demoImageEmoji", sample.emoji).put("demoSample", true))
    }
  }'''
new = '''  // Extra retail storefront samples ensure every Home department has real inventory.
  // These are demo records only; seedTemplateDemo merges by name and never replaces user data.
  private val retailStorefrontExtras = listOf(
    Sample("🍚 Rice Bag / چاول", "Grocery", "bag", 2200.0, 2600.0, 18.0, "🍚"),
    Sample("🍬 Sugar Bag / چینی", "Grocery", "kg", 145.0, 175.0, 40.0, "🍬"),
    Sample("🍅 Tomatoes / ٹماٹر", "Fresh & Frozen", "kg", 70.0, 110.0, 60.0, "🍅"),
    Sample("🧅 Onions / پیاز", "Fresh & Frozen", "kg", 85.0, 125.0, 55.0, "🧅"),
    Sample("🍗 Chicken / مرغی", "Fresh & Frozen", "kg", 520.0, 620.0, 35.0, "🍗"),
    Sample("🍌 Bananas / کیلے", "Fresh & Frozen", "dozen", 100.0, 140.0, 25.0, "🍌"),
    Sample("🍪 Family Biscuits / بسکٹ", "Snacks & Beverages", "pack", 65.0, 90.0, 60.0, "🍪"),
    Sample("🥔 Potato Chips / چپس", "Snacks & Beverages", "pack", 45.0, 65.0, 50.0, "🥔"),
    Sample("🥤 Cola Drink / کولڈ ڈرنک", "Snacks & Beverages", "bottle", 75.0, 100.0, 48.0, "🥤"),
    Sample("🧴 Herbal Shampoo / شیمپو", "Personal Care", "bottle", 280.0, 390.0, 24.0, "🧴"),
    Sample("🧼 Bath Soap / صابن", "Personal Care", "piece", 90.0, 130.0, 40.0, "🧼"),
    Sample("🫧 Face Wash / فیس واش", "Personal Care", "tube", 250.0, 350.0, 20.0, "🫧"),
    Sample("🧽 Dishwashing Liquid / برتن دھونے کا لیکوئڈ", "Household", "bottle", 150.0, 210.0, 30.0, "🧽"),
    Sample("🧻 Tissue Box / ٹشو", "Household", "box", 95.0, 135.0, 36.0, "🧻"),
    Sample("🍼 Baby Diapers / بچوں کے ڈائپر", "Baby Care", "pack", 650.0, 790.0, 18.0, "🍼"),
    Sample("🧴 Baby Lotion / بے بی لوشن", "Baby Care", "bottle", 320.0, 430.0, 16.0, "🧴"),
    Sample("🧻 Baby Wipes / بے بی وائپس", "Baby Care", "pack", 140.0, 195.0, 25.0, "🧻"),
    Sample("💡 LED Bulb / ایل ای ڈی بلب", "Electronics", "piece", 180.0, 260.0, 50.0, "💡"),
    Sample("🔌 Fast Charger / فاسٹ چارجر", "Electronics", "piece", 650.0, 950.0, 30.0, "🔌"),
    Sample("🎧 Wireless Earbuds / وائرلیس ایئربڈز", "Electronics", "piece", 1800.0, 2600.0, 20.0, "🎧"),
    Sample("👕 Cotton Shirt / کاٹن شرٹ", "Clothing", "piece", 650.0, 1100.0, 18.0, "👕"),
    Sample("🧣 Lawn Suit / لان سوٹ", "Clothing", "suit", 1400.0, 2200.0, 12.0, "🧣"),
    Sample("👖 Denim Jeans / جینز", "Clothing", "piece", 900.0, 1500.0, 14.0, "👖"),
    Sample("🍳 Non-stick Pan / فرائنگ پین", "Home & Kitchen", "piece", 850.0, 1200.0, 12.0, "🍳"),
    Sample("🍽️ Dinner Set / ڈنر سیٹ", "Home & Kitchen", "set", 2400.0, 3200.0, 8.0, "🍽️"),
    Sample("🥣 Storage Container / اسٹوریج ڈبہ", "Home & Kitchen", "piece", 180.0, 260.0, 35.0, "🥣"),
    Sample("📓 School Notebook / سکول کاپی", "Stationery & Toys", "piece", 90.0, 130.0, 50.0, "📓"),
    Sample("🖊️ Ball Pen Pack / بال پین", "Stationery & Toys", "pack", 100.0, 150.0, 35.0, "🖊️"),
    Sample("🚗 Toy Car / کھلونا گاڑی", "Stationery & Toys", "piece", 220.0, 320.0, 15.0, "🚗")
  )

  fun items(template: String): List<InventoryItem> {
    val key = template.trim().lowercase().replace('-', '_').replace(' ', '_')
    val base = catalog[key] ?: catalog.getValue("custom")
    val isRetail = BusinessLibrary.find(key).sector == "Retail" || key == "custom"
    val samples = if (isRetail) (base + retailStorefrontExtras) else base
    return samples.map { sample ->
      item(sample.name, sample.category, sample.unit, sample.cost, sample.price, sample.stock,
        sample.type, JSONObject().put("demoImageEmoji", sample.emoji).put("demoSample", true))
    }
  }'''
if old in source:
    source = source.replace(old, new, 1)
elif "retailStorefrontExtras" not in source:
    raise SystemExit("DemoLibrary.items patch anchor missing")
demo_path.write_text(source, encoding="utf-8")
print("Added 29 additional retail demo products across all 10 Home departments.")

home_path = root / "app/src/main/java/com/example/ui/screens/BusinessHomeScreen.kt"
home = home_path.read_text(encoding="utf-8")
button_anchor = '''      if (products.isEmpty()) {'''
button_block = '''      item {
        OutlinedButton(onClick = onLoadDemoCatalog, modifier = Modifier.fillMaxWidth()) {
          Icon(Icons.Default.Storefront, null)
          Spacer(Modifier.width(8.dp))
          Text(t("Load sample products for all categories", "تمام کیٹیگریز کے نمونہ پروڈکٹس لوڈ کریں"))
        }
      }
'''
if button_anchor in home:
    home = home.replace(button_anchor, button_block + button_anchor, 1)
elif "Load sample products for all categories" not in home:
    raise SystemExit("Home product-list insertion anchor not found")
empty = '''      if (categoryItems.isEmpty()) item { Text(t("No products in this category yet. Add a product and choose this category.", "اس کیٹیگری میں ابھی پروڈکٹس نہیں۔ پروڈکٹ شامل کرتے وقت یہی کیٹیگری منتخب کریں۔"), color = MaterialTheme.colorScheme.onSurfaceVariant) }'''
empty_new = '''      if (categoryItems.isEmpty()) item {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
          Text(t("No products in this category yet.", "اس کیٹیگری میں ابھی پروڈکٹس موجود نہیں۔"), color = MaterialTheme.colorScheme.onSurfaceVariant)
          Button(onClick = onLoadDemoCatalog, modifier = Modifier.fillMaxWidth()) {
            Icon(Icons.Default.Storefront, null)
            Spacer(Modifier.width(8.dp))
            Text(t("Load sample products", "نمونہ پروڈکٹس لوڈ کریں"))
          }
        }
      }'''
if empty in home:
    home = home.replace(empty, empty_new, 1)
elif "No products in this category yet." not in home:
    raise SystemExit("See All empty category anchor not found")

image_anchor = '''  return when {
    "tomato" in text || "vegetable" in text || "سبزی" in text -> com.example.R.drawable.af_demo_tomatoes'''
image_replacement = '''  return when {
    "tomato" in text || "ٹماٹر" in text -> com.example.R.drawable.af_demo_tomatoes
    "onion" in text || "پیاز" in text -> com.example.R.drawable.af_demo_onions
    "chicken" in text || "meat" in text || "beef" in text || "گوشت" in text -> com.example.R.drawable.af_demo_chicken
    "banana" in text || "fruit" in text || "سیب" in text || "کیلے" in text -> com.example.R.drawable.af_demo_bananas
    "bakery" in text || "bread" in text || "cake" in text || "بیکری" in text -> com.example.R.drawable.af_demo_bakery
    "dry fruit" in text || "almond" in text || "pistachio" in text || "بادام" in text -> com.example.R.drawable.af_demo_dryfruits
    "spice" in text || "masala" in text || "مرچ" in text || "ہلدی" in text -> com.example.R.drawable.af_demo_spices
    "snack" in text || "beverage" in text || "biscuit" in text || "chips" in text || "چپس" in text -> com.example.R.drawable.af_demo_snacks
    "personal care" in text || "beauty" in text || "shampoo" in text || "soap" in text || "face wash" in text -> com.example.R.drawable.af_demo_personalcare
    "household" in text || "detergent" in text || "tissue" in text || "dishwash" in text -> com.example.R.drawable.af_demo_household
    "baby" in text || "diaper" in text || "بچوں" in text || "ڈائپر" in text -> com.example.R.drawable.af_demo_babycare
    "electronics" in text || "charger" in text || "earbud" in text || "bulb" in text || "mobile" in text || "computer" in text || "laptop" in text -> com.example.R.drawable.af_demo_electronics
    "clothing" in text || "garment" in text || "fashion" in text || "shirt" in text || "jeans" in text || "کپڑے" in text -> com.example.R.drawable.af_demo_fashion
    "home & kitchen" in text || "kitchen" in text || "cookware" in text || "dinner set" in text -> com.example.R.drawable.af_demo_kitchen
    "stationery" in text || "toy" in text || "notebook" in text || "pen pack" in text || "اسٹیشنری" in text -> com.example.R.drawable.af_demo_stationery
    "vegetable" in text || "سبزی" in text -> com.example.R.drawable.af_demo_tomatoes'''
if image_anchor in home:
    home = home.replace(image_anchor, image_replacement, 1)
elif "af_demo_personalcare" not in home:
    raise SystemExit("Product image mapping anchor not found")
home_path.write_text(home, encoding="utf-8")

test_path = root / "app/src/test/java/com/example/DemoLibraryCoverageTest.kt"
test = test_path.read_text(encoding="utf-8")
test_anchor = '''  @Test fun serviceBusinessesReceiveTheirOwnServiceMenu() {'''
test_add = '''  @Test fun retailTemplatesPopulateAllTenHomeDepartments() {
    val expected = setOf(
      "Grocery", "Fresh & Frozen", "Snacks & Beverages", "Personal Care",
      "Household", "Baby Care", "Electronics", "Clothing",
      "Home & Kitchen", "Stationery & Toys"
    )
    listOf("kiryana", "supermarket", "produce", "garments", "mobile", "custom").forEach { id ->
      val categories = DemoLibrary.items(id).map { it.category }.toSet()
      expected.forEach { category ->
        assertTrue("$id should contain sample products in $category", category in categories)
      }
    }
  }

'''
if test_add not in test:
    if test_anchor not in test:
        raise SystemExit("DemoLibrary coverage test anchor not found")
    test = test.replace(test_anchor, test_add + test_anchor, 1)
test_path.write_text(test, encoding="utf-8")
print("Applied Home, See All, HD product mapping, and retail catalogue regression test.")
