package com.example

import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import android.content.Context
import com.example.business.PersonalKhataEngine
import com.example.business.BusinessSchema
import com.example.data.local.FinanceDatabase
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk=[28])
class PersonalKhataAttachmentTest {
  private val context: Context = ApplicationProvider.getApplicationContext()

  @Test fun personalContactPhotoAndEntryAttachmentPersistWithoutChangingLedgerMath() = runBlocking {
    val db = Room.inMemoryDatabaseBuilder(context, FinanceDatabase::class.java)
      .addCallback(BusinessSchema.callback).build()
    try {
      val engine = PersonalKhataEngine(db)
      val contact = engine.contact("Test Person", "03000000000", "content://photos/profile")
      assertEquals("content://photos/profile", JSONObject(contact.payload).getString("profilePhotoUri"))
      engine.entry(contact.id, 125.0, "GAVE", "Advance payment", "content://photos/receipt")
      val entry = db.businessDao().allRecords().single { it.kind == "PERSONAL_ENTRY" }
      val payload = JSONObject(entry.payload)
      assertEquals("GAVE", payload.getString("direction"))
      assertEquals("Advance payment", payload.getString("note"))
      assertEquals("content://photos/receipt", payload.getString("attachmentUri"))
      assertTrue(entry.createdAt > 0L)
      assertEquals(125.0, PersonalKhataEngine.balance(db.businessDao().allRecords(), contact.id), 0.000001)
    } finally { db.close() }
  }

  @Test fun personalKhataRejectsInvalidAmountsAndKeepsBusinessLedgerSeparate() = runBlocking {
    val db = Room.inMemoryDatabaseBuilder(context, FinanceDatabase::class.java)
      .addCallback(BusinessSchema.callback).build()
    try {
      val engine = PersonalKhataEngine(db)
      val contact = engine.contact("Separate Person", "")
      assertTrue(runCatching { engine.entry(contact.id, -1.0, "GAVE", "bad") }.isFailure)
      assertTrue(db.businessDao().allRecords().none { it.kind == "INVOICE" || it.kind == "CUSTOMER" })
      assertEquals(0.0, PersonalKhataEngine.balance(db.businessDao().allRecords(), contact.id), 0.000001)
    } finally { db.close() }
  }
}
