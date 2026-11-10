#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1])

def replace(rel, old, new, label):
 p=root/rel; s=p.read_text(encoding='utf-8')
 if new in s: print('Already applied',label); return
 if old not in s: raise SystemExit(f'Missing anchor for {label}: {rel}')
 p.write_text(s.replace(old,new,1),encoding='utf-8'); print('Applied',label)

# Persist owner-managed catalogue categories in the existing business_records table.
core_path = root/'app/src/main/java/com/example/business/BusinessCore.kt'
core_text = core_path.read_text(encoding='utf-8')
if 'import kotlinx.coroutines.flow.first' not in core_text:
 core_text = core_text.replace('import kotlinx.coroutines.flow.Flow\n','import kotlinx.coroutines.flow.Flow\nimport kotlinx.coroutines.flow.first\n',1)
 core_path.write_text(core_text,encoding='utf-8')
replace('app/src/main/java/com/example/business/BusinessCore.kt',
'''class BusinessCore(private val db: FinanceDatabase) {
  val records = db.businessDao().records()
  val movements = db.businessDao().movements()
  private fun validMoney''',
'''class BusinessCore(private val db: FinanceDatabase) {
  val records = db.businessDao().records()
  val movements = db.businessDao().movements()
  suspend fun saveCatalogCategory(name: String, oldName: String? = null) = db.withTransaction {
    val clean = name.trim()
    require(clean.isNotBlank()) { "Enter a category name / کیٹیگری کا نام درج کریں" }
    val dao = db.businessDao()
    val current = dao.allRecords().filter { it.kind == "CATALOG_CATEGORY" && !it.archived }
    require(current.none { it.title.equals(clean, true) && !it.title.equals(oldName ?: "", true) }) { "Category already exists / کیٹیگری پہلے موجود ہے" }
    if (oldName != null) {
      val old = current.firstOrNull { it.title.equals(oldName, true) } ?: error("Category not found / کیٹیگری نہیں ملی")
      dao.update(old.copy(archived = true, updatedAt = System.currentTimeMillis()))
      db.financeDao().getAllInventoryItems().first().filter { it.category.equals(oldName, true) }.forEach { item ->
        db.financeDao().updateInventoryItem(item.copy(category = clean, lastUpdatedMillis = System.currentTimeMillis()))
      }
    }
    dao.insert(BusinessRecord(kind = "CATALOG_CATEGORY", title = clean, payload = "{}"))
  }
  suspend fun deleteCatalogCategory(name: String) = db.withTransaction {
    val dao = db.businessDao()
    val category = dao.allRecords().firstOrNull { it.kind == "CATALOG_CATEGORY" && !it.archived && it.title.equals(name, true) }
    if (category != null) dao.update(category.copy(archived = true, updatedAt = System.currentTimeMillis()))
    db.financeDao().getAllInventoryItems().first().filter { it.category.equals(name, true) }.forEach { item ->
      db.financeDao().updateInventoryItem(item.copy(category = "Uncategorized", lastUpdatedMillis = System.currentTimeMillis()))
    }
  }
  private fun validMoney''','catalog category persistence')

# Owner-checked view-model methods; product records are retained when a category is removed.
replace('app/src/main/java/com/example/ui/FinanceViewModel.kt',
'''  fun addToCart(itemId: Long, qty: Double = 1.0) {''',
'''  fun saveCatalogCategory(name: String, oldName: String? = null, done: (String?) -> Unit = {}) {
    if (!ownerVerified || _userRole.value != UserRole.OWNER) { done("Owner access required / مالک کی اجازت ضروری ہے"); return }
    viewModelScope.launch { try { requireBusinessAccess(); businessCore.saveCatalogCategory(name, oldName); done(null) }
      catch (error: Exception) { done(error.message ?: "Unable to save category") } }
  }
  fun deleteCatalogCategory(name: String, done: (String?) -> Unit = {}) {
    if (!ownerVerified || _userRole.value != UserRole.OWNER) { done("Owner access required / مالک کی اجازت ضروری ہے"); return }
    viewModelScope.launch { try { requireBusinessAccess(); businessCore.deleteCatalogCategory(name); done(null) }
      catch (error: Exception) { done(error.message ?: "Unable to delete category") } }
  }

  fun addToCart(itemId: Long, qty: Double = 1.0) {''','catalog category viewmodel actions')

# Replace the overview/finance dashboard with a real inventory-backed storefront.
home = r'''package com.example.ui.screens

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import com.example.data.model.*
import com.example.ui.FinanceUiState
import com.example.ui.components.HomePromoBannerSlider
import org.json.JSONObject
import java.util.Locale

private val StoreGreen = Color(0xFF086B43)
private val StoreMint = Color(0xFFEAF6EE)

@Composable
fun BusinessHomeScreen(
  uiState: FinanceUiState,
  onSendClick: () -> Unit,
  onReceiveClick: () -> Unit,
  onStockClick: () -> Unit,
  onBillsClick: () -> Unit,
  onBillingClick: () -> Unit = {},
  onServicesClick: () -> Unit = {},
  onFilterSelected: (com.example.ui.FilterCategory) -> Unit,
  onSearchQueryChanged: (String) -> Unit,
  onTransactionClick: (Transaction) -> Unit,
  onAddNewClick: () -> Unit,
  onOpenFbrTaxReport: () -> Unit = {},
  onOpenTrialLock: () -> Unit = {},
  onSelectBusinessCategory: (com.example.ui.components.BusinessCategoryItem) -> Unit = {},
  modifier: Modifier = Modifier,
  onPosClick: () -> Unit = {},
  onReportsClick: () -> Unit = {},
  onBusinessSetup: () -> Unit = {},
  onAddToCart: (Long) -> Unit = {},
  onAddProduct: () -> Unit = {},
  onSaveCategory: (String, String?) -> Unit = { _, _ -> },
  onDeleteCategory: (String) -> Unit = {}
) {
  val urdu = uiState.appLanguage == AppLanguage.URDU
  fun t(en: String, ur: String) = if (urdu) ur else en
  var query by rememberSaveable { mutableStateOf("") }
  var selectedCategory by rememberSaveable { mutableStateOf<String?>(null) }
  var manageCategories by remember { mutableStateOf(false) }
  var editingCategory by remember { mutableStateOf<String?>(null) }
  var categoryName by remember { mutableStateOf("") }
  var showCategoryEditor by remember { mutableStateOf(false) }
  val hidden = uiState.businessRecords.filter { it.kind == "CATALOG_CATEGORY" && it.archived }.map { it.title.lowercase(Locale.ROOT) }.toSet()
  val savedCategories = uiState.businessRecords.filter { it.kind == "CATALOG_CATEGORY" && !it.archived }.map { it.title }
  val categories = (savedCategories + uiState.inventoryItems.map { it.category.trim() }.filter { it.isNotBlank() })
    .distinctBy { it.lowercase(Locale.ROOT) }.filterNot { it.lowercase(Locale.ROOT) in hidden }.sortedBy { it.lowercase(Locale.ROOT) }
  val products = uiState.inventoryItems.filter { it.salePrice > 0.0 && !it.category.equals("Uncategorized", true) }
  val filtered = products.filter { query.isBlank() || it.name.contains(query, true) || it.category.contains(query, true) || it.barcode.contains(query, true) }
  val visibleCategories = if (categories.isNotEmpty()) categories else listOf("Grocery", "Bakery", "Fruit", "Vegetables", "Meat", "Dry Fruits", "Spices")
  val cartCount = uiState.cartItems.values.sumOf { it.toInt() }
  if (selectedCategory != null) BackHandler { selectedCategory = null }

  LazyColumn(modifier.fillMaxSize().background(MaterialTheme.colorScheme.background),
    contentPadding = PaddingValues(start = 16.dp, end = 16.dp, top = 12.dp, bottom = 24.dp),
    verticalArrangement = Arrangement.spacedBy(16.dp)) {
    if (selectedCategory == null) {
      item {
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
          Column(Modifier.weight(1f)) {
            Text(t("Shop by category", "کیٹیگری کے مطابق خریداری"), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)
            Text(uiState.businessProfile.businessName, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
          }
          FilledTonalIconButton(onClick = onBusinessSetup) { Icon(Icons.Default.Tune, t("Customize shop", "دکان کی ترتیب")) }
        }
      }
      item {
        OutlinedTextField(value = query, onValueChange = { query = it }, modifier = Modifier.fillMaxWidth(),
          singleLine = true, shape = RoundedCornerShape(24.dp), placeholder = { Text(t("Search products, brands or services...", "مصنوعات، برانڈ یا سروس تلاش کریں...")) },
          leadingIcon = { Icon(Icons.Default.Search, null) }, trailingIcon = { Icon(Icons.Default.QrCodeScanner, null) })
      }
      item {
        HomePromoBannerSlider(appMode = uiState.appMode, isUrdu = urdu, onPosClick = onPosClick,
          onProductsClick = onStockClick, onServicesClick = onServicesClick, onKhataClick = onBillingClick,
          bannerImageUri = uiState.businessProfile.bannerImageUri)
      }
      item {
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
          Text(t("Categories", "کیٹیگریز"), modifier = Modifier.weight(1f), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)
          TextButton(onClick = { manageCategories = true }) { Text(t("Manage", "ترتیب دیں")) }
        }
        Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
          visibleCategories.forEach { category ->
            val emoji = categoryEmoji(category)
            Card(onClick = { selectedCategory = category }, shape = RoundedCornerShape(18.dp),
              colors = CardDefaults.cardColors(containerColor = StoreMint), modifier = Modifier.width(108.dp)) {
              Column(Modifier.padding(12.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(7.dp)) {
                Text(emoji, fontSize = 30.sp)
                Text(category, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold, maxLines = 2, overflow = TextOverflow.Ellipsis)
              }
            }
          }
        }
      }
      if (products.isEmpty()) {
        item {
          Card(shape = RoundedCornerShape(20.dp), colors = CardDefaults.cardColors(containerColor = StoreMint)) {
            Column(Modifier.fillMaxWidth().padding(20.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
              Text(t("Your catalogue is ready to customize", "آپ کا کیٹلاگ ترتیب دینے کے لیے تیار ہے"), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
              Text(t("Add your own products, categories, prices, stock and HD photos. They will appear here automatically.", "اپنی مصنوعات، کیٹیگریز، قیمتیں، اسٹاک اور HD تصاویر شامل کریں۔ وہ خود بخود یہاں نظر آئیں گی۔"), style = MaterialTheme.typography.bodyMedium)
              Button(onClick = onAddProduct, modifier = Modifier.fillMaxWidth()) { Icon(Icons.Default.Add, null); Spacer(Modifier.width(6.dp)); Text(t("Add first product", "پہلی پروڈکٹ شامل کریں")) }
            }
          }
        }
      } else {
        val grouped = filtered.groupBy { it.category }.toSortedMap(String.CASE_INSENSITIVE_ORDER)
        grouped.forEach { (category, itemsInCategory) ->
          item(key = "category-$category") {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
              Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text(category, modifier = Modifier.weight(1f), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)
                TextButton(onClick = { selectedCategory = category }) { Text(t("See All →", "سب دیکھیں ←")) }
              }
              Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                itemsInCategory.take(8).forEach { product -> StoreProductCard(product, uiState.currencySymbol, urdu, { onAddToCart(product.id) }, Modifier.width(154.dp)) }
              }
            }
          }
        }
      }
      item {
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
          StoreShortcut(t("POS & Billing", "POS اور بلنگ"), "🧾", Modifier.weight(1f), onPosClick)
          StoreShortcut(t("Khata", "کھاتہ"), "📒", Modifier.weight(1f), onBillingClick)
          StoreShortcut(t("Services", "سروسز"), "🛠️", Modifier.weight(1f), onServicesClick)
        }
      }
    } else {
      item {
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
          IconButton(onClick = { selectedCategory = null }) { Icon(Icons.Default.ArrowBack, t("Back", "واپس")) }
          Text(selectedCategory!!, modifier = Modifier.weight(1f), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
          TextButton(onClick = onAddProduct) { Text(t("+ Product", "+ پروڈکٹ")) }
        }
      }
      val categoryItems = products.filter { it.category.equals(selectedCategory, true) }
      if (categoryItems.isEmpty()) item { Text(t("No products in this category yet. Add a product and choose this category.", "اس کیٹیگری میں ابھی پروڈکٹس نہیں۔ پروڈکٹ شامل کرتے وقت یہی کیٹیگری منتخب کریں۔"), color = MaterialTheme.colorScheme.onSurfaceVariant) }
      items(categoryItems, key = { "product-${it.id}" }) { product -> StoreProductCard(product, uiState.currencySymbol, urdu, { onAddToCart(product.id) }, Modifier.fillMaxWidth()) }
    }
  }

  if (manageCategories) AlertDialog(onDismissRequest = { manageCategories = false },
    title = { Text(t("Manage categories", "کیٹیگریز کی ترتیب")) },
    text = { Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
      Button(onClick = { editingCategory = null; categoryName = ""; showCategoryEditor = true }, modifier = Modifier.fillMaxWidth()) { Icon(Icons.Default.Add, null); Text(t("Add category", "کیٹیگری شامل کریں")) }
      categories.forEach { name -> Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
        Text(name, Modifier.weight(1f))
        IconButton(onClick = { editingCategory = name; categoryName = name; showCategoryEditor = true }) { Icon(Icons.Default.Edit, t("Edit", "ترمیم")) }
        IconButton(onClick = { onDeleteCategory(name) }) { Icon(Icons.Default.Delete, t("Delete", "حذف"), tint = MaterialTheme.colorScheme.error) }
      } }
    } }, confirmButton = { TextButton(onClick = { manageCategories = false }) { Text(t("Done", "مکمل")) } })

  if (showCategoryEditor) AlertDialog(onDismissRequest = { showCategoryEditor = false },
    title = { Text(if (editingCategory == null) t("Add category", "کیٹیگری شامل کریں") else t("Edit category", "کیٹیگری تبدیل کریں")) },
    text = { OutlinedTextField(value = categoryName, onValueChange = { categoryName = it }, singleLine = true, label = { Text(t("Category name", "کیٹیگری کا نام")) }) },
    confirmButton = { TextButton(onClick = { if (categoryName.isNotBlank()) { onSaveCategory(categoryName.trim(), editingCategory); showCategoryEditor = false } }) { Text(t("Save", "محفوظ کریں")) } },
    dismissButton = { TextButton(onClick = { showCategoryEditor = false }) { Text(t("Cancel", "منسوخ")) } })
}

@Composable
private fun StoreProductCard(item: InventoryItem, currency: String, urdu: Boolean, onAdd: () -> Unit, modifier: Modifier = Modifier) {
  val details = remember(item.detailsJson) { runCatching { JSONObject(item.detailsJson) }.getOrDefault(JSONObject()) }
  val photo = details.optString("imageUri").takeIf { it.isNotBlank() }
  val title = if (urdu) details.optString("nameUrdu").ifBlank { item.name } else item.name
  Card(modifier, shape = RoundedCornerShape(18.dp), colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface), elevation = CardDefaults.cardElevation(2.dp)) {
    Column(Modifier.padding(9.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
      if (photo != null) AsyncImage(model = photo, contentDescription = title, contentScale = ContentScale.Crop, modifier = Modifier.fillMaxWidth().height(112.dp).clip(RoundedCornerShape(12.dp)))
      else Box(Modifier.fillMaxWidth().height(112.dp).clip(RoundedCornerShape(12.dp)).background(StoreMint), contentAlignment = Alignment.Center) {
        Text(item.icon, fontSize = 42.sp)
      }
      Text(title, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold, maxLines = 2, overflow = TextOverflow.Ellipsis)
      Text(String.format(Locale.US, "%s %,.2f / %s", currency, item.salePrice, item.unit), color = StoreGreen, fontWeight = FontWeight.ExtraBold, style = MaterialTheme.typography.bodyMedium)
      Text(String.format(Locale.US, "Stock: %s %s", item.currentStock, item.unit), style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
      Button(onClick = onAdd, enabled = item.currentStock > 0, modifier = Modifier.fillMaxWidth(), contentPadding = PaddingValues(horizontal = 8.dp, vertical = 7.dp)) {
        Icon(Icons.Default.AddShoppingCart, null, modifier = Modifier.size(17.dp)); Spacer(Modifier.width(5.dp)); Text(if (urdu) "کارٹ میں شامل" else "Add to Cart", maxLines = 1)
      }
    }
  }
}

@Composable
private fun StoreShortcut(title: String, emoji: String, modifier: Modifier, onClick: () -> Unit) {
  Card(onClick = onClick, modifier = modifier, shape = RoundedCornerShape(16.dp), colors = CardDefaults.cardColors(containerColor = StoreMint)) {
    Column(Modifier.fillMaxWidth().padding(12.dp), horizontalAlignment = Alignment.CenterHorizontally) { Text(emoji, fontSize = 24.sp); Text(title, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold, maxLines = 1) }
  }
}

private fun categoryEmoji(name: String): String = when {
  name.contains("grocery", true) || name.contains("general", true) -> "🛒"
  name.contains("bakery", true) || name.contains("cake", true) -> "🥐"
  name.contains("fruit", true) -> "🍎"
  name.contains("veget", true) -> "🥦"
  name.contains("meat", true) || name.contains("chicken", true) || name.contains("beef", true) -> "🥩"
  name.contains("dry", true) || name.contains("nut", true) -> "🥜"
  name.contains("spice", true) || name.contains("masala", true) -> "🌶️"
  name.contains("cloth", true) || name.contains("fashion", true) || name.contains("garment", true) -> "👕"
  name.contains("mobile", true) || name.contains("electronic", true) || name.contains("computer", true) -> "📱"
  name.contains("beauty", true) || name.contains("cosmetic", true) -> "💄"
  name.contains("service", true) -> "🛠️"
  else -> "📦"
}
'''
p=root/'app/src/main/java/com/example/ui/screens/BusinessHomeScreen.kt'; p.write_text(home,encoding='utf-8'); print('Replaced Home with database-backed storefront, category detail pages and cart actions')

# Put trial/payment information on the mode-selection page, not regular Home pages.
mode='app/src/main/java/com/example/ui/screens/ModeSelectionScreen.kt'
s=(root/mode).read_text(encoding='utf-8')
s=s.replace('import com.example.data.model.AppMode\n','import com.example.data.model.AppMode\nimport com.example.data.model.SubscriptionState\nimport com.example.ui.components.SubscriptionAccessCard\n',1)
s=s.replace('''  onModeSelected: (AppMode) -> Unit,
  modifier: Modifier = Modifier
) {''','''  onModeSelected: (AppMode) -> Unit,
  modifier: Modifier = Modifier,
  subscriptionState: SubscriptionState = SubscriptionState(),
  onOpenPlans: () -> Unit = {}
) {''',1)
anchor='''    LazyColumn(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(16.dp)) {'''
s=s.replace(anchor,'''    SubscriptionAccessCard(subscriptionState, appLanguage, onOpenPlans, Modifier.fillMaxWidth())
    Spacer(Modifier.height(8.dp))
    LazyColumn(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(16.dp)) {''',1)
(root/mode).write_text(s,encoding='utf-8'); print('Moved trial/payment card onto mode-selection page')

# Wire new callbacks and mode-selection trial card from MainActivity.
main='app/src/main/java/com/example/MainActivity.kt'; s=(root/main).read_text(encoding='utf-8')
s=s.replace('''        onModeSelected = { mode ->
          viewModel.confirmAppMode(mode)
        }
      )''','''        onModeSelected = { mode ->
          viewModel.confirmAppMode(mode)
        },
        subscriptionState = uiState.subscriptionState,
        onOpenPlans = { viewModel.openTrialLockDialog() }
      )''',1)
s=s.replace('''              onBusinessSetup = { featuresOnly = false; businessBuilder = true }
            )''','''              onBusinessSetup = { featuresOnly = false; businessBuilder = true },
              onAddToCart = { id -> viewModel.addToCart(id) },
              onAddProduct = { viewModel.openAddInventoryDialog() },
              onSaveCategory = { name, old -> viewModel.saveCatalogCategory(name, old) { error -> if (error != null) android.widget.Toast.makeText(viewModel.getApplication(), error, android.widget.Toast.LENGTH_LONG).show() } },
              onDeleteCategory = { name -> viewModel.deleteCatalogCategory(name) { error -> if (error != null) android.widget.Toast.makeText(viewModel.getApplication(), error, android.widget.Toast.LENGTH_LONG).show() } }
            )''',1)
(root/main).write_text(s,encoding='utf-8'); print('Wired cart, product creation and category CRUD callbacks')

# Finance is now an explicit bottom-navigation destination; its sheet groups finance functions.
nav='app/src/main/java/com/example/ui/components/BottomNavBar.kt'; s=(root/nav).read_text(encoding='utf-8')
s=s.replace('''    NavBarChoice(if (urdu) "مزید" else "More", Icons.Default.MoreHoriz,
      selectedTab in listOf(FinanceTab.SETTINGS, FinanceTab.REPORTS, FinanceTab.PLANNER) || (!personal && selectedTab == FinanceTab.ACCOUNTS),
      "nav_more") { sheet = "more" }''','''    NavBarChoice(if (urdu) "فنانس" else "Finance", Icons.Default.AccountBalance,
      selectedTab in listOf(FinanceTab.SETTINGS, FinanceTab.REPORTS, FinanceTab.PLANNER, FinanceTab.PURCHASES, FinanceTab.OPERATIONS) || (!personal && selectedTab == FinanceTab.ACCOUNTS),
      "nav_finance") { sheet = "finance" }''',1)
s=s.replace('''        Text(if (sheet == "catalog") { if (urdu) "آپ کا کیٹلاگ" else "Your catalog" }
          else { if (urdu) "کاروبار کے ٹولز" else "Business tools" }, style = MaterialTheme.typography.headlineSmall)''','''        Text(if (sheet == "catalog") { if (urdu) "آپ کا کیٹلاگ" else "Your catalog" }
          else { if (urdu) "فنانس اور کاروباری ٹولز" else "Finance & business tools" }, style = MaterialTheme.typography.headlineSmall)''',1)
s=s.replace('''        } else {
          MenuDestination("Cash & accounts", "کیش اور اکاؤنٹس", Icons.Default.AccountBalanceWallet, FinanceTab.ACCOUNTS, "nav_tab_accounts", urdu) { sheet = ""; onTabSelected(FinanceTab.ACCOUNTS) }''','''        } else {
          MenuDestination("Sales & invoices", "فروخت اور بل", Icons.Default.ReceiptLong, FinanceTab.LEDGERS, "nav_finance_sales", urdu) { sheet = ""; onTabSelected(FinanceTab.LEDGERS) }
          MenuDestination("Purchases", "خریداری", Icons.Default.LocalShipping, FinanceTab.PURCHASES, "nav_purchases", urdu) { sheet = ""; onTabSelected(FinanceTab.PURCHASES) }
          MenuDestination("Cash & accounts", "کیش اور اکاؤنٹس", Icons.Default.AccountBalanceWallet, FinanceTab.ACCOUNTS, "nav_tab_accounts", urdu) { sheet = ""; onTabSelected(FinanceTab.ACCOUNTS) }''',1)
s=s.replace('''          if (features.purchases) MenuDestination("Purchases", "خریداری", Icons.Default.LocalShipping, FinanceTab.PURCHASES, "nav_purchases", urdu) { sheet = ""; onTabSelected(FinanceTab.PURCHASES) }
          MenuDestination("Business workspace"''','''          MenuDestination("Business workspace"''',1)
(root/nav).write_text(s,encoding='utf-8'); print('Renamed More to Finance and grouped sales, purchases, cash and reports')

# Expand the starter supermarket/kiryana sample with all requested grocery departments.
demo='app/src/main/java/com/example/business/DemoLibrary.kt'; s=(root/demo).read_text(encoding='utf-8')
old='''      Sample("🥣 Sugar / چینی","Grocery","kg",145.0,175.0,100.0,"🥣"),
      Sample("🧼 Detergent / واشنگ پاؤڈر","Household","pack",180.0,220.0,35.0,"🧼")'''
new='''      Sample("🥣 Sugar / چینی","Grocery","kg",145.0,175.0,100.0,"🥣"),
      Sample("🧼 Detergent / واشنگ پاؤڈر","Household","pack",180.0,220.0,35.0,"🧼"),
      Sample("🍎 Fresh Apples / سیب","Fruit","kg",220.0,280.0,45.0,"🍎"),
      Sample("🍌 Bananas / کیلے","Fruit","dozen",100.0,140.0,25.0,"🍌"),
      Sample("🍅 Fresh Tomatoes / ٹماٹر","Vegetables","kg",85.0,112.5,40.0,"🍅"),
      Sample("🧅 Red Onion / پیاز","Vegetables","kg",75.0,99.5,50.0,"🧅"),
      Sample("🍗 Chicken Mince / چکن قیمہ","Meat","kg",350.0,424.5,15.0,"🍗"),
      Sample("🥩 Beef / گائے کا گوشت","Meat","kg",900.0,1080.0,12.0,"🥩"),
      Sample("🍞 Fresh Bread / ڈبل روٹی","Bakery","piece",90.0,120.0,24.0,"🍞"),
      Sample("🎂 Chocolate Cake / چاکلیٹ کیک","Bakery","kg",900.0,1350.0,8.0,"🎂"),
      Sample("🥜 Almonds / بادام","Dry Fruits","kg",1800.0,2200.0,10.0,"🥜"),
      Sample("🌰 Pistachios / پستہ","Dry Fruits","kg",2600.0,3100.0,6.0,"🌰"),
      Sample("🌶️ Red Chilli / لال مرچ","Spices","kg",650.0,820.0,18.0,"🌶️"),
      Sample("🟡 Turmeric / ہلدی","Spices","kg",420.0,560.0,20.0,"🟡")'''
if old not in s: raise SystemExit('Kiryana demo catalogue anchor not found')
s=s.replace(old,new,1); (root/demo).write_text(s,encoding='utf-8'); print('Expanded starter store catalogue with fruit, vegetables, meat, bakery, dry fruits and spices')

# Keep the trial card exclusively on mode selection; the existing header patch is disabled.
main_path = root/'app/src/main/java/com/example/MainActivity.kt'
main_text = main_path.read_text(encoding='utf-8').replace('showSubscriptionAccess = uiState.selectedTab == FinanceTab.HOME','showSubscriptionAccess = false',1)
main_path.write_text(main_text,encoding='utf-8')

# Remove the previous hard-coded deal cards from the promo component. The storefront now
# renders real, database-backed products and prices in category rows.
promo = root/'app/src/main/java/com/example/ui/components/HomePromoBannerSlider.kt'
if promo.exists():
    ps = promo.read_text(encoding='utf-8')
    start = ps.find('    Spacer(Modifier.height(4.dp))')
    end = ps.rfind('  }\n}')
    if start >= 0 and end > start:
        ps = ps[:start] + ps[end:]
        promo.write_text(ps,encoding='utf-8')
        print('Removed static sample-price deals from home banner component')

print('Dynamic home/catalogue patch complete')