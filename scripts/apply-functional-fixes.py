from pathlib import Path
import sys
root = Path(sys.argv[1])

def replace_once(rel, old, new):
    p = root / rel
    s = p.read_text()
    n = s.count(old)
    if n == 0 and new in s:
        print("Already patched:", rel)
        return
    if n != 1:
        raise SystemExit(f"Unsafe source mismatch in {rel}: expected 1 match, got {n}")
    p.write_text(s.replace(old, new, 1))
    print("Patched:", rel)

replace_once("app/src/main/java/com/example/data/local/FinanceDao.kt",
'''  @Query("UPDATE inventory_items SET currentStock = currentStock - :quantity, lastUpdatedMillis = :now WHERE id = :id")
  suspend fun deductInventoryStock(id: Long, quantity: Double, now: Long = System.currentTimeMillis())''',
'''  @Query("UPDATE inventory_items SET currentStock = currentStock - :quantity, lastUpdatedMillis = :now WHERE id = :id AND :quantity > 0 AND currentStock + 0.000001 >= :quantity")
  suspend fun deductInventoryStock(id: Long, quantity: Double, now: Long = System.currentTimeMillis()): Int''')
replace_once("app/src/main/java/com/example/data/local/FinanceDao.kt",
'''  @Query("SELECT * FROM invoices WHERE id = :id LIMIT 1")
  suspend fun getInvoiceById(id: Long): Invoice?''',
'''  @Query("SELECT * FROM invoices WHERE id = :id LIMIT 1")
  suspend fun getInvoiceById(id: Long): Invoice?

  @Query("SELECT * FROM invoices WHERE invoiceNumber = :invoiceNumber ORDER BY id ASC LIMIT 1")
  suspend fun getInvoiceByNumber(invoiceNumber: String): Invoice?''')
replace_once("app/src/main/java/com/example/data/repository/FinanceRepository.kt",
'''    val old = if (invoice.id > 0L) dao.getInvoiceById(invoice.id) else null
    require(invoice.id == 0L || old != null) { "Bill no longer exists / بل موجود نہیں" }''',
'''    val normalizedInvoiceNumber = invoice.invoiceNumber.trim()
    require(normalizedInvoiceNumber.isNotBlank()) { "Bill number is required / بل نمبر ضروری ہے" }
    val old = if (invoice.id > 0L) dao.getInvoiceById(invoice.id) else null
    require(invoice.id == 0L || old != null) { "Bill no longer exists / بل موجود نہیں" }
    if (old == null) {
      require(dao.getInvoiceByNumber(normalizedInvoiceNumber) == null) {
        "This bill has already been saved. Open the existing bill instead of submitting it again / یہ بل پہلے ہی محفوظ ہو چکا ہے، دوبارہ جمع نہ کریں"
      }
    } else {
      require(old.invoiceNumber == normalizedInvoiceNumber) { "Bill number cannot be changed / بل نمبر تبدیل نہیں ہو سکتا" }
    }''')
replace_once("app/src/main/java/com/example/data/repository/FinanceRepository.kt",
'''      try {stockItems.forEach { (id, entries) -> dao.deductInventoryStock(id, entries.sumOf { it.quantity }) }} finally {database.businessDao().context(context)}''',
'''      try {
        stockItems.forEach { (id, entries) ->
          val quantity = entries.sumOf { it.quantity }
          require(dao.deductInventoryStock(id, quantity) == 1) {
            "Stock changed before this bill could be saved. Refresh the product quantity and try again / بل محفوظ ہونے سے پہلے اسٹاک تبدیل ہو گیا، مقدار دوبارہ چیک کریں"
          }
        }
      } finally { database.businessDao().context(context) }''')
replace_once("app/src/main/java/com/example/ui/FinanceViewModel.kt",
'''  val cartItemCount: Int
    get() = cartItems.size

  val cartSubtotal: Double
    get() = cartItems.entries.sumOf { (id, qty) ->
      val itm = inventoryItems.find { it.id == id }
      (itm?.salePrice ?: 0.0) * qty
    }''',
'''  val posCatalogItems: List<InventoryItem>
    get() = inventoryItems + services
      .filter { service -> inventoryItems.none { it.id == -kotlin.math.abs(service.id) } }
      .map { service ->
        InventoryItem(
          id = -kotlin.math.abs(service.id),
          name = service.name,
          category = service.businessCategory,
          icon = service.icon,
          salePrice = service.effectivePrice,
          currentStock = service.stockOrSlots,
          unit = service.unit,
          barcode = "SRV-SERVICE-${service.id}",
          note = service.description,
          detailsJson = org.json.JSONObject()
            .put("itemType", "Service")
            .put("serviceId", service.id)
            .put("urduName", service.urduName)
            .put("serviceType", service.serviceType)
            .toString()
        )
      }

  val cartItemCount: Int
    get() = cartItems.size

  val cartSubtotal: Double
    get() = cartItems.entries.sumOf { (id, qty) ->
      val itm = posCatalogItems.find { it.id == id }
      (itm?.salePrice ?: 0.0) * qty
    }''')
replace_once("app/src/main/java/com/example/ui/screens/PremiumPosCounterScreen.kt",
'''  val catalog = uiState.inventoryItems.filter { (search.isBlank() || it.name.contains(search, true) || it.barcode.contains(search, true)) && (tab != 1 || uiState.cartItems.containsKey(it.id)) }''',
'''  val catalog = uiState.posCatalogItems.filter {
    (search.isBlank() || it.name.contains(search, true) || it.barcode.contains(search, true) ||
      it.category.contains(search, true) || org.json.JSONObject(it.detailsJson).optString("urduName").contains(search, true)) &&
      (tab != 1 || uiState.cartItems.containsKey(it.id))
  }''')
replace_once("app/src/main/java/com/example/ui/screens/PremiumPosCounterScreen.kt",
'''      ListTile(product.name, if (product.isServiceItem()) uiState.word("Service", "سروس") else "${product.currentStock} ${product.unit} • ${product.category}", Icons.Default.ShoppingBasket, uiState.money(product.salePrice), click = { if (product.currentStock > 0 || product.isServiceItem()) onAddToCart(product, 1.0) }) {''',
'''      val urduName = org.json.JSONObject(product.detailsJson).optString("urduName", product.name).ifBlank { product.name }
      ListTile(uiState.word(product.name, urduName), if (product.isServiceItem()) uiState.word("Service", "سروس") else "${product.currentStock} ${product.unit} • ${product.category}", Icons.Default.ShoppingBasket, uiState.money(product.salePrice), click = { if (product.currentStock > 0 || product.isServiceItem()) onAddToCart(product, 1.0) }) {''')
replace_once("app/src/main/java/com/example/ui/screens/PremiumCheckout.kt",
'''  var copying by remember { mutableStateOf(false) }
  var branch by remember {mutableStateOf("main")};var warehouse by remember {mutableStateOf("main")}''',
'''  var copying by remember { mutableStateOf(false) }
  var submittingSale by remember { mutableStateOf(false) }
  val checkoutInvoiceNumber = remember { "${state.businessProfile.invoicePrefix}-${java.util.UUID.randomUUID()}" }
  var branch by remember {mutableStateOf("main")};var warehouse by remember {mutableStateOf("main")}''')
replace_once("app/src/main/java/com/example/ui/screens/PremiumCheckout.kt",
'''        Button(enabled = !copying && state.cartItems.isNotEmpty(), onClick = {
          val valid = cut.isFinite() && cut >= 0 && cut <= subtotal && cashPaid.isFinite() && cashPaid >= 0 && onlinePaid.isFinite() && onlinePaid >= 0 && paid <= total + 0.001
          if (!valid) { error = state.word("Check discount and payment amounts", "رعایت اور ادائیگی کی رقم درست کریں"); return@Button }
          if (paid < total && name.isBlank() && customer == null) { error = state.word("Select a customer for khata", "کھاتے کے لیے گاہک منتخب کریں"); return@Button }
          val number = "${state.businessProfile.invoicePrefix}-${System.currentTimeMillis()}"
          val entries = state.cartItems.mapNotNull { (id, qty) -> state.inventoryItems.find { it.id == id }?.let { item -> InvoiceItemEntry(itemId = id, itemName = item.name, category = item.category, quantity = qty * item.saleFactor(), unit = item.unit, unitPrice = item.salePrice / item.saleFactor(), total = item.salePrice * qty, isService = item.isServiceItem()) } }''',
'''        Button(enabled = !copying && !submittingSale && state.cartItems.isNotEmpty(), onClick = {
          if (submittingSale) return@Button
          submittingSale = true
          val valid = cut.isFinite() && cut >= 0 && cut <= subtotal && cashPaid.isFinite() && cashPaid >= 0 && onlinePaid.isFinite() && onlinePaid >= 0 && paid <= total + 0.001
          if (!valid) { submittingSale = false; error = state.word("Check discount and payment amounts", "رعایت اور ادائیگی کی رقم درست کریں"); return@Button }
          if (paid < total && name.isBlank() && customer == null) { submittingSale = false; error = state.word("Select a customer for khata", "کھاتے کے لیے گاہک منتخب کریں"); return@Button }
          val number = checkoutInvoiceNumber
          val entries = state.cartItems.mapNotNull { (id, qty) -> state.posCatalogItems.find { it.id == id }?.let { item -> InvoiceItemEntry(itemId = id, itemName = state.word(item.name, org.json.JSONObject(item.detailsJson).optString("urduName", item.name).ifBlank { item.name }), category = item.category, quantity = qty * item.saleFactor(), unit = item.unit, unitPrice = item.salePrice / item.saleFactor(), total = item.salePrice * qty, isService = item.isServiceItem()) } }''')
replace_once("app/src/main/java/com/example/ui/screens/PosCounterScreen.kt",
'''  val inventoryItems = uiState.inventoryItems''',
'''  val inventoryItems = uiState.posCatalogItems''')
replace_once("app/src/main/java/com/example/ui/screens/PosCounterScreen.kt",
'''  var copyingReceipt by remember { mutableStateOf(false) }
  val hasAttachedScreenshot = receiptPath.isNotBlank()''',
'''  var copyingReceipt by remember { mutableStateOf(false) }
  var submittingSale by remember { mutableStateOf(false) }
  val checkoutInvoiceNumber = remember { "INV-${java.util.UUID.randomUUID()}" }
  val hasAttachedScreenshot = receiptPath.isNotBlank()''')
replace_once("app/src/main/java/com/example/ui/screens/PosCounterScreen.kt",
'''          enabled = !copyingReceipt && cartItems.isNotEmpty(),
          onClick = {
            val invoiceNumber = "INV-${System.currentTimeMillis()}"''',
'''          enabled = !copyingReceipt && !submittingSale && cartItems.isNotEmpty(),
          onClick = {
            if (submittingSale) return@Button
            submittingSale = true
            val invoiceNumber = checkoutInvoiceNumber''')
replace_once("app/src/main/java/com/example/ui/screens/PosCounterScreen.kt",
'''                itemName = item.name,
                category = item.category,''',
'''                itemName = uiState.word(item.name, org.json.JSONObject(item.detailsJson).optString("urduName", item.name).ifBlank { item.name }),
                category = item.category,''')
replace_once("app/src/main/java/com/example/ui/dialogs/PremiumQuickStockAdjustDialog.kt",
'''var unit by remember {mutableStateOf(item.unit)};var record by remember {mutableStateOf(true)}''',
'''var unit by remember {mutableStateOf(item.unit)};var record by remember {mutableStateOf(false)}''')
replace_once("app/src/main/java/com/example/ui/dialogs/PremiumQuickStockAdjustDialog.kt",
'''    else Row {Text(t("Record as sale","فروخت کے طور پر درج کریں"),Modifier.weight(1f));Switch(record,{record=it})}''',
'''    else Column {
      Row {Text(t("Create a separate sale entry","الگ فروخت کا اندراج بنائیں"),Modifier.weight(1f));Switch(record,{record=it})}
      Text(
        t("POS bills already reduce stock automatically. Turn this on only when this stock-out was NOT already billed in POS.",
          "POS بل سے اسٹاک خود بخود کم ہوتا ہے۔ یہ اختیار صرف تب آن کریں جب یہ مال POS میں پہلے بل نہ ہوا ہو۔"),
        style=MaterialTheme.typography.bodySmall,
        color=MaterialTheme.colorScheme.error
      )
    }''')

print("All functional stock/POS fixes applied.")
