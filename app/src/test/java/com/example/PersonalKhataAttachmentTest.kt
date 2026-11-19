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

  @Test fun profileDescriptionCanBeEditedAndArchiveKeepsLedgerHistory() = runBlocking {
    val db = Room.inMemoryDatabaseBuilder(context, FinanceDatabase::class.java)
      .addCallback(BusinessSchema.callback).build()
    try {
      val engine = PersonalKhataEngine(db)
      val person = engine.contact("Editable Person", "03000000000", "content://photo/one", "Initial note")
      engine.entry(person.id, 250.0, "GAVE", "Opening advance", "", 1_700_000_000_000L)
      engine.updateContact(person.id, "Updated Person", "03111111111", "content://photo/two", "Updated description")
      val updated = db.businessDao().record(person.id)!!
      val profile = JSONObject(updated.payload)
      assertEquals("Updated Person", updated.title)
      assertEquals("Updated description", profile.getString("description"))
      assertEquals("content://photo/two", profile.getString("profilePhotoUri"))
      val entry = db.businessDao().allRecords().single { it.kind == "PERSONAL_ENTRY" }
      assertEquals(1_700_000_000_000L, entry.createdAt)
      engine.archiveContact(person.id)
      assertTrue(db.businessDao().record(person.id)!!.archived)
      assertEquals(250.0, PersonalKhataEngine.balance(db.businessDao().allRecords(), person.id), 0.000001)
    } finally { db.close() }
  }
}
