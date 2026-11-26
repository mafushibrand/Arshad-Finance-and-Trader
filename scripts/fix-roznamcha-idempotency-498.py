from pathlib import Path
import sys
root = Path(sys.argv[1])

def patch(rel, old, new):
    p = root / rel
    s = p.read_text(encoding="utf-8")
    if new in s:
        return
    if old not in s:
        raise SystemExit(f"Patch anchor missing in {rel}: {old[:120]!r}")
    p.write_text(s.replace(old, new, 1), encoding="utf-8")

patch("app/src/main/java/com/example/business/BusinessCore.kt",
"""suspend fun roznamchaEntry(amount: Double, income: Boolean, dateMillis: Long, note: String, accountId: Long, actor: String, party: String = "") = db.withTransaction {
    validMoney(amount)
    require(amount > 0.0) { "Enter a positive amount / درست رقم درج کریں" }
    require(note.isNotBlank()) { "Enter entry description / اندراج کی تفصیل درج کریں" }
    val account = db.financeDao().getAllAccountsList().firstOrNull { it.id == accountId }
      ?: error("Choose a valid cash account / درست کیش اکاؤنٹ منتخب کریں")
    val now = System.currentTimeMillis()""",
"""suspend fun roznamchaEntry(amount: Double, income: Boolean, dateMillis: Long, note: String, accountId: Long, actor: String, party: String = "", requestId: String = UUID.randomUUID().toString()) = db.withTransaction {
    validMoney(amount)
    require(amount > 0.0) { "Enter a positive amount / درست رقم درج کریں" }
    require(note.isNotBlank()) { "Enter entry description / اندراج کی تفصیل درج کریں" }
    require(requestId.isNotBlank()) { "Invalid entry request / اندراج کی درخواست درست نہیں" }
    val reference = "ROZNAMCHA/${requestId.trim()}"
    // Reuse one request ID across taps/retries; check before changing the cash balance.
    if (db.financeDao().getTransactionsByReference(reference).isNotEmpty()) return@withTransaction
    val account = db.financeDao().getAllAccountsList().firstOrNull { it.id == accountId }
      ?: error("Choose a valid cash account / درست کیش اکاؤنٹ منتخب کریں")
    val now = System.currentTimeMillis()""")
patch("app/src/main/java/com/example/business/BusinessCore.kt",
"""      transactionRef = "ROZNAMCHA/${UUID.randomUUID()}",""",
"""      transactionRef = reference,""")
patch("app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt",
"""import java.util.Locale
""", """import java.util.Locale
import java.util.UUID
""")
patch("app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt",
"""  if(form && writable && section=="ROZNAMCHA") RoznamchaEntryForm(state,null,{form=false}) { amount,income,date,note,accountId,party ->
    viewModel.businessAction({roznamchaEntry(amount,income,date,note,accountId,actor,party)}) {result(it)}
  }
  editingRoznamcha?.let { tx -> RoznamchaEntryForm(state,tx,{editingRoznamcha=null}) { amount,income,date,note,accountId,party ->""",
"""  if(form && writable && section=="ROZNAMCHA") RoznamchaEntryForm(state,null,{form=false}) { amount,income,date,note,accountId,party,requestId ->
    viewModel.businessAction({roznamchaEntry(amount,income,date,note,accountId,actor,party,requestId)}) {result(it)}
  }
  editingRoznamcha?.let { tx -> RoznamchaEntryForm(state,tx,{editingRoznamcha=null}) { amount,income,date,note,accountId,party,requestId ->""")
patch("app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt",
"""private fun RoznamchaEntryForm(state:FinanceUiState,initial:Transaction?=null,dismiss:()->Unit,save:(Double,Boolean,Long,String,Long,String)->Unit) {""",
"""private fun RoznamchaEntryForm(state:FinanceUiState,initial:Transaction?=null,dismiss:()->Unit,save:(Double,Boolean,Long,String,Long,String,String)->Unit) {""")
patch("app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt",
"""  var error by remember { mutableStateOf("") }
  var translating by remember { mutableStateOf(false) }""",
"""  var error by remember { mutableStateOf("") }
  val requestId by remember(initial?.id) { mutableStateOf(UUID.randomUUID().toString()) }
  var translating by remember { mutableStateOf(false) }""")
patch("app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt",
"""            save(value,incoming,date,savedNote,accountId,savedParty)""",
"""            save(value,incoming,date,savedNote,accountId,savedParty,requestId)""")
patch("app/src/main/java/com/example/ui/screens/BusinessOperationsScreen.kt",
"""                  appendLine(state.businessProfile.businessName)
                  if(state.businessProfile.address.isNotBlank()) appendLine(state.businessProfile.address)
                  if(state.businessProfile.phone.isNotBlank()) appendLine(state.businessProfile.phone)
                  appendLine(text("ROZNAMCHA RECEIPT","روزنامچہ رسید"))
                  appendLine(text("Client / Party: ","گاہک / فریق: ")+tx.recipientInfo)
                  appendLine(text("Amount: ","رقم: ")+state.money(tx.amount))
                  appendLine(text("Date: ","تاریخ: ")+date)
                  appendLine(text("Account: ","اکاؤنٹ: ")+tx.accountName)
                  if(tx.note.isNotBlank()) appendLine(text("Note: ","تفصیل: ")+tx.note)""",
"""                  appendLine("================================")
                  appendLine(state.businessProfile.businessName.ifBlank { "Arshad Finance" })
                  if(state.businessProfile.tagline.isNotBlank()) appendLine(state.businessProfile.tagline)
                  if(state.businessProfile.address.isNotBlank()) appendLine(state.businessProfile.address)
                  if(state.businessProfile.phone.isNotBlank()) appendLine(state.businessProfile.phone)
                  appendLine("--------------------------------")
                  appendLine(text("CASH RECEIPT","نقد رسید"))
                  appendLine(text("Receipt No: ","رسید نمبر: ")+tx.transactionRef.ifBlank { "RF-${tx.id}" })
                  appendLine(text("Party: ","پارٹی: ")+tx.recipientInfo.ifBlank { text("Walk-in / Unassigned","عام / غیر مختص") })
                  appendLine(text("Entry: ","اندراج: ")+if(tx.type==TransactionType.INCOME) text("Cash received","نقد وصولی") else text("Cash paid","نقد ادائیگی"))
                  appendLine(text("Amount: ","رقم: ")+state.money(tx.amount))
                  appendLine(text("Transaction date: ","لین دین کی تاریخ: ")+date)
                  appendLine(text("Account: ","اکاؤنٹ: ")+tx.accountName)
                  if(tx.note.isNotBlank()) appendLine(text("Description: ","تفصیل: ")+tx.note)
                  appendLine("--------------------------------")
                  appendLine(text("Generated: ","تیار کیا گیا: ")+SimpleDateFormat("dd MMM yyyy • hh:mm a",Locale("en","PK")).apply { timeZone=java.util.TimeZone.getTimeZone("Asia/Karachi") }.format(Date()))
                  appendLine("Developed by Muhammad Arshad 03027761415")
                  appendLine("================================")""")

test = root / "app/src/test/java/com/example/RoznamchaIdempotencyTest.kt"
test.parent.mkdir(parents=True, exist_ok=True)
test.write_text("""package com.example

import android.content.Context
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import com.example.business.BusinessCore
import com.example.business.BusinessSchema
import com.example.data.local.FinanceDatabase
import com.example.data.model.Account
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk=[28])
class RoznamchaIdempotencyTest {
  private val context: Context = ApplicationProvider.getApplicationContext()

  @Test fun repeatedSaveWithSameRequestIdPostsOneTransactionAndOneBalanceChange() = runBlocking {
    val db = Room.inMemoryDatabaseBuilder(context, FinanceDatabase::class.java)
      .addCallback(BusinessSchema.callback).build()
    try {
      val accountId = db.financeDao().insertAccount(Account(name="Cash", accountType="Cash", balance=1000.0, accountNumber=""))
      val core = BusinessCore(db)
      repeat(2) {
        core.roznamchaEntry(125.0, false, 1_700_000_000_000L, "Shop expense", accountId, "owner", "Vendor A", "test-request-001")
      }
      val rows = db.financeDao().getTransactionsByReference("ROZNAMCHA/test-request-001")
      assertEquals(1, rows.size)
      assertEquals(875.0, db.financeDao().getAllAccountsList().single().balance, 0.000001)
    } finally { db.close() }
  }
}
""", encoding="utf-8")
print("Applied Roznamcha idempotency, branded receipt, and Room regression test.")
