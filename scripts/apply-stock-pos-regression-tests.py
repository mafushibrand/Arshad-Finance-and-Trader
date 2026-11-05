from pathlib import Path
import sys
p = Path(sys.argv[1]) / "app/src/test/java/com/example/DataSafetyTest.kt"
s = p.read_text()

def once(old, new):
    global s
    n = s.count(old)
    if n == 0 and new in s:
        return
    if n != 1:
        raise SystemExit(f"Unsafe regression-test patch: expected one match, found {n}")
    s = s.replace(old, new, 1)

once("import com.example.data.repository.FinanceRepository\n",
     "import com.example.data.repository.FinanceRepository\nimport com.example.ui.FinanceUiState\nimport com.example.business.isServiceItem\n")
once("  @Test fun saleEditAndDeleteKeepStockKhataAndCashConsistent() = runBlocking {",
'''  @Test fun savedServicesAppearInPosSearchCatalogueAndDoNotDeductStock() {
    val service = ServiceItem(id = 501L, name = "Hair Cut", urduName = "بال کٹوانا",
      businessCategory = "SALON", serviceType = "Session", price = 500.0, stockOrSlots = 25.0)
    val state = FinanceUiState(services = listOf(service), cartItems = mapOf(-501L to 2.0))
    val posItem = state.posCatalogItems.single()
    assertEquals(-501L, posItem.id)
    assertTrue(posItem.isServiceItem())
    assertEquals("بال کٹوانا", org.json.JSONObject(posItem.detailsJson).optString("urduName"))
    assertEquals(1000.0, state.cartSubtotal, 0.0)
  }

  @Test fun saleEditAndDeleteKeepStockKhataAndCashConsistent() = runBlocking {''')
once("  @Test fun insufficientStockRollsBackEntireSale() = runBlocking {",
'''  @Test fun repeatedCheckoutWithSameBillNumberCannotDeductStockTwice() = runBlocking {
    val db = Room.inMemoryDatabaseBuilder(context, FinanceDatabase::class.java)
      .addCallback(com.example.business.BusinessSchema.callback)
      .build()
    try {
      val dao = db.financeDao()
      val repo = FinanceRepository(dao, db)
      val product = dao.insertInventoryItem(InventoryItem(name = "Rice", currentStock = 10.0, salePrice = 10.0))
      val bill = Invoice(invoiceNumber = "IDEMPOTENT-1", customerName = "Walk-in", grandTotal = 20.0, amountPaid = 20.0)
      val lines = listOf(InvoiceItemEntry(itemId = product, itemName = "Rice", quantity = 2.0, unitPrice = 10.0, total = 20.0))
      repo.saveInvoiceAtomically(bill, lines, true)
      assertEquals(8.0, dao.getInventoryItemById(product)!!.currentStock, 0.0)
      val movementsAfterFirstSave = db.businessDao().allMovements().filter { it.itemId == product }.sumOf { it.quantity }
      assertEquals(8.0, movementsAfterFirstSave, 0.000001)
      assertTrue(runCatching { repo.saveInvoiceAtomically(bill, lines, true) }.isFailure)
      assertEquals(8.0, dao.getInventoryItemById(product)!!.currentStock, 0.0)
      assertEquals(movementsAfterFirstSave, db.businessDao().allMovements().filter { it.itemId == product }.sumOf { it.quantity }, 0.000001)
      assertEquals(1, dao.getInvoiceCount())
    } finally { db.close() }
  }

  @Test fun insufficientStockRollsBackEntireSale() = runBlocking {''')
p.write_text(s)
print("Added service catalogue and duplicate-sale stock regression tests.")
