#!/usr/bin/env python3
"""Add Home slider/offer/demo controls and keep Services inside the Catalog menu."""
from pathlib import Path
import sys

root = Path(sys.argv[1])

prefs = root / "app/src/main/java/com/example/ui/components/HomeExperiencePrefs.kt"
prefs.parent.mkdir(parents=True, exist_ok=True)
prefs.write_text('''package com.example.ui.components

import android.content.Context

/** Local owner-adjustable Home storefront presentation settings. */
object HomeExperiencePrefs {
  private const val FILE = "arshad_home_experience"
  const val SLIDER_ENABLED = "slider_enabled"
  const val OFFER_ENABLED = "offer_enabled"
  const val DEMO_ENABLED = "demo_products_enabled"
  const val OFFER_TITLE = "offer_title"
  const val OFFER_DISCOUNT = "offer_discount"
  const val BANNER_IMAGE_URL = "banner_image_url"

  fun get(context: Context) = context.getSharedPreferences(FILE, Context.MODE_PRIVATE)
  fun isEnabled(context: Context, key: String, default: Boolean = true): Boolean = get(context).getBoolean(key, default)
  fun value(context: Context, key: String, default: String = ""): String = get(context).getString(key, default) ?: default
  fun set(context: Context, key: String, value: Boolean) { get(context).edit().putBoolean(key, value).apply() }
  fun set(context: Context, key: String, value: String) { get(context).edit().putString(key, value).apply() }
}
''', encoding="utf-8")

slider_path = root / "app/src/main/java/com/example/ui/components/HomePromoBannerSlider.kt"
s = slider_path.read_text(encoding="utf-8")
s = s.replace("import androidx.compose.ui.platform.testTag\n", "import androidx.compose.ui.platform.testTag\nimport androidx.compose.ui.platform.LocalContext\n")
s = s.replace('''  val slides = remember(appMode, isUrdu, onPosClick, onProductsClick, onServicesClick, onKhataClick) {
    if (appMode == AppMode.PERSONAL_KHATA) listOf(''','''  val context = LocalContext.current
  val sliderEnabled = HomeExperiencePrefs.isEnabled(context, HomeExperiencePrefs.SLIDER_ENABLED, true)
  val offerEnabled = HomeExperiencePrefs.isEnabled(context, HomeExperiencePrefs.OFFER_ENABLED, true)
  val offerTitle = HomeExperiencePrefs.value(context, HomeExperiencePrefs.OFFER_TITLE, "on Fresh Products")
  val offerDiscount = HomeExperiencePrefs.value(context, HomeExperiencePrefs.OFFER_DISCOUNT, "20%")
  val customImage = HomeExperiencePrefs.value(context, HomeExperiencePrefs.BANNER_IMAGE_URL)
  val activeBannerImage = customImage.ifBlank { bannerImageUri }
  val slides = remember(appMode, isUrdu, onPosClick, onProductsClick, onServicesClick, onKhataClick, offerEnabled, offerTitle, offerDiscount) {
    val standard = if (appMode == AppMode.PERSONAL_KHATA) listOf(''')
if "val context = LocalContext.current" not in s:
    raise SystemExit("Slider state anchor missing")
old_end = '''    )
  }
  val pagerState = rememberPagerState(pageCount = { slides.size })'''
new_end = '''    )
    if (appMode == AppMode.PERSONAL_KHATA) standard else standard + if (offerEnabled) listOf(
      PromoSlide("Special Offer • $offerDiscount OFF", "خصوصی آفر • $offerDiscount رعایت",
        offerTitle.ifBlank { "on Fresh Products" }, offerTitle.ifBlank { "تازہ مصنوعات پر خصوصی رعایت" },
        "Shop Now", "ابھی خریدیں", Icons.Default.LocalOffer,
        listOf(Color(0xFFFFB52E), Color(0xFFF97316)), onProductsClick)
    ) else emptyList()
  }
  if (!sliderEnabled || slides.isEmpty()) return
  val pagerState = rememberPagerState(pageCount = { slides.size })'''
if old_end not in s:
    raise SystemExit("Slider list ending anchor missing")
s = s.replace(old_end, new_end, 1)
s = s.replace("bannerImageUri.takeIf { it.isNotBlank() }", "activeBannerImage.takeIf { it.isNotBlank() }")
slider_path.write_text(s, encoding="utf-8")

home_path = root / "app/src/main/java/com/example/ui/screens/BusinessHomeScreen.kt"
h = home_path.read_text(encoding="utf-8")
h = h.replace("import com.example.ui.components.HomePromoBannerSlider\n", "import com.example.ui.components.HomePromoBannerSlider\nimport com.example.ui.components.HomeExperiencePrefs\n")
h = h.replace('''  val urdu = uiState.appLanguage == AppLanguage.URDU
  fun t(en: String, ur: String) = if (urdu) ur else en''','''  val urdu = uiState.appLanguage == AppLanguage.URDU
  val demoProductsEnabled = HomeExperiencePrefs.isEnabled(LocalContext.current, HomeExperiencePrefs.DEMO_ENABLED, true)
  fun t(en: String, ur: String) = if (urdu) ur else en''', 1)
h = h.replace('''      item {
        OutlinedButton(onClick = onLoadDemoCatalog, modifier = Modifier.fillMaxWidth()) {''','''      if (demoProductsEnabled) item {
        OutlinedButton(onClick = onLoadDemoCatalog, modifier = Modifier.fillMaxWidth()) {''', 1)
h = h.replace('''              Button(onClick = onLoadDemoCatalog, modifier = Modifier.fillMaxWidth()) { Icon(Icons.Default.Storefront, null); Spacer(Modifier.width(6.dp)); Text(t("Load sample products", "نمونہ پروڈکٹس لوڈ کریں")) }
              OutlinedButton(onClick = onAddProduct''','''              if (demoProductsEnabled) Button(onClick = onLoadDemoCatalog, modifier = Modifier.fillMaxWidth()) { Icon(Icons.Default.Storefront, null); Spacer(Modifier.width(6.dp)); Text(t("Load sample products", "نمونہ پروڈکٹس لوڈ کریں")) }
              OutlinedButton(onClick = onAddProduct''', 1)
h = h.replace('''          Button(onClick = onLoadDemoCatalog, modifier = Modifier.fillMaxWidth()) {
            Icon(Icons.Default.Storefront, null)
            Spacer(Modifier.width(8.dp))
            Text(t("Load sample products", "نمونہ پروڈکٹس لوڈ کریں"))
          }''','''          if (demoProductsEnabled) Button(onClick = onLoadDemoCatalog, modifier = Modifier.fillMaxWidth()) {
            Icon(Icons.Default.Storefront, null)
            Spacer(Modifier.width(8.dp))
            Text(t("Load sample products", "نمونہ پروڈکٹس لوڈ کریں"))
          }''', 1)
if "val demoProductsEnabled = HomeExperiencePrefs" not in h:
    raise SystemExit("Home demo preference anchor missing")
home_path.write_text(h, encoding="utf-8")

settings_path = root / "app/src/main/java/com/example/ui/screens/SettingsScreen.kt"
st = settings_path.read_text(encoding="utf-8")
st = st.replace("import androidx.compose.material3.OutlinedButton\n", "import androidx.compose.material3.OutlinedButton\nimport androidx.compose.material3.OutlinedTextField\n")
st = st.replace("import com.example.ui.FinanceUiState\n", "import com.example.ui.FinanceUiState\nimport com.example.ui.components.HomeExperiencePrefs\n")
st = st.replace('''  var showApkDownloadGuideDialog by remember { mutableStateOf(false) }
''','''  var showApkDownloadGuideDialog by remember { mutableStateOf(false) }
  val homePrefs = remember { HomeExperiencePrefs.get(context) }
  var homeSliderEnabled by remember { mutableStateOf(homePrefs.getBoolean(HomeExperiencePrefs.SLIDER_ENABLED, true)) }
  var offerEnabled by remember { mutableStateOf(homePrefs.getBoolean(HomeExperiencePrefs.OFFER_ENABLED, true)) }
  var demoProductsEnabled by remember { mutableStateOf(homePrefs.getBoolean(HomeExperiencePrefs.DEMO_ENABLED, true)) }
  var offerTitle by remember { mutableStateOf(homePrefs.getString(HomeExperiencePrefs.OFFER_TITLE, "on Fresh Products") ?: "on Fresh Products") }
  var offerDiscount by remember { mutableStateOf(homePrefs.getString(HomeExperiencePrefs.OFFER_DISCOUNT, "20%") ?: "20%") }
  var bannerImageUrl by remember { mutableStateOf(homePrefs.getString(HomeExperiencePrefs.BANNER_IMAGE_URL, "") ?: "") }
''', 1)
anchor = '''    // 0. User Account, Cloud Sync & Device Recovery Card
    item {'''
card = '''    // Home storefront controls: persist locally and apply immediately when Home is reopened.
    item {
      Card(shape = RoundedCornerShape(20.dp), colors = CardDefaults.cardColors(containerColor = Color.White),
        modifier = Modifier.fillMaxWidth().testTag("home_experience_settings")) {
        Column(Modifier.fillMaxWidth().padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
          Text(if (isUrdu) "ہوم سلائیڈر اور ڈیمو کنٹرول" else "Home Slider & Demo Controls",
            fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color(0xFF0F172A))
          Text(if (isUrdu) "ہوم بینرز، خصوصی آفر اور نمونہ پروڈکٹس کو یہاں سے کنٹرول کریں۔" else "Control Home banners, special offers and sample products here.",
            fontSize = 12.sp, color = Color(0xFF64748B))
          Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
            Column(Modifier.weight(1f)) {
              Text(if (isUrdu) "ہوم سلائیڈر دکھائیں" else "Show Home slider", fontWeight = FontWeight.SemiBold)
              Text(if (isUrdu) "تمام ہوم بینرز آن یا آف کریں" else "Show or hide all Home banners", fontSize = 11.sp, color = Color(0xFF64748B))
            }
            Switch(checked = homeSliderEnabled, onCheckedChange = { homeSliderEnabled = it; HomeExperiencePrefs.set(context, HomeExperiencePrefs.SLIDER_ENABLED, it) })
          }
          HorizontalDivider(color = Color(0xFFE8EFEA))
          Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
            Column(Modifier.weight(1f)) {
              Text(if (isUrdu) "خصوصی آفر / ڈسکاؤنٹ سلائیڈر" else "Special Offer / Discount slider", fontWeight = FontWeight.SemiBold)
              Text(if (isUrdu) "20% رعایت والا آفر بینر دکھائیں" else "Show a dedicated discount banner", fontSize = 11.sp, color = Color(0xFF64748B))
            }
            Switch(checked = offerEnabled, onCheckedChange = { offerEnabled = it; HomeExperiencePrefs.set(context, HomeExperiencePrefs.OFFER_ENABLED, it) })
          }
          if (offerEnabled) {
            OutlinedTextField(value = offerDiscount, onValueChange = { offerDiscount = it; HomeExperiencePrefs.set(context, HomeExperiencePrefs.OFFER_DISCOUNT, it) },
              modifier = Modifier.fillMaxWidth(), singleLine = true, label = { Text(if (isUrdu) "ڈسکاؤنٹ (مثلاً 20%)" else "Discount (e.g. 20%)") })
            OutlinedTextField(value = offerTitle, onValueChange = { offerTitle = it; HomeExperiencePrefs.set(context, HomeExperiencePrefs.OFFER_TITLE, it) },
              modifier = Modifier.fillMaxWidth(), singleLine = true, label = { Text(if (isUrdu) "آفر کی تفصیل" else "Offer text") })
          }
          OutlinedTextField(value = bannerImageUrl, onValueChange = { bannerImageUrl = it; HomeExperiencePrefs.set(context, HomeExperiencePrefs.BANNER_IMAGE_URL, it) },
            modifier = Modifier.fillMaxWidth(), singleLine = true, label = { Text(if (isUrdu) "بینر تصویر کا URL (اختیاری)" else "Replacement banner image URL (optional)") })
          OutlinedButton(onClick = onOpenShopProfile, modifier = Modifier.fillMaxWidth()) {
            Icon(Icons.Default.Store, null); Spacer(Modifier.width(8.dp))
            Text(if (isUrdu) "اپ لوڈ کی گئی دکان کی بینر تصویر منتخب کریں" else "Choose uploaded shop banner image")
          }
          HorizontalDivider(color = Color(0xFFE8EFEA))
          Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
            Column(Modifier.weight(1f)) {
              Text(if (isUrdu) "نمونہ / ڈیمو پروڈکٹس" else "Sample / Demo products", fontWeight = FontWeight.SemiBold)
              Text(if (isUrdu) "ہوم پر Load Sample Products بٹن دکھائیں یا چھپائیں" else "Show or hide the Load Sample Products buttons on Home", fontSize = 11.sp, color = Color(0xFF64748B))
            }
            Switch(checked = demoProductsEnabled, onCheckedChange = { demoProductsEnabled = it; HomeExperiencePrefs.set(context, HomeExperiencePrefs.DEMO_ENABLED, it) })
          }
        }
      }
    }

    // 0. User Account, Cloud Sync & Device Recovery Card
    item {'''
if anchor not in st:
    raise SystemExit("Settings insertion anchor missing")
st = st.replace(anchor, card, 1)
marker = '''          SettingsMenuItem(
            icon = Icons.Default.Refresh,
            iconTint = Color(0xFF13865F),
            title = "1-Click Pakistani Demo Data",
            subtitle = "Preload customers, stock items, and daily sales",
            onClick = {
              onLoadDemoData()
              Toast.makeText(context, "Demo Data Loaded! ✓", Toast.LENGTH_SHORT).show()
            }
          )'''
st = st.replace(marker, marker.replace("          SettingsMenuItem(", "          if (demoProductsEnabled) SettingsMenuItem(", 1), 1)
settings_path.write_text(st, encoding="utf-8")

nav_path = root / "app/src/main/java/com/example/ui/components/BottomNavBar.kt"
nav = nav_path.read_text(encoding="utf-8")
extra = '''      if (features.services) NavBarChoice(if (urdu) "سروسز" else "Services", Icons.Default.Handyman,
        selectedTab == FinanceTab.SERVICES, "nav_tab_services_direct") { onTabSelected(FinanceTab.SERVICES) }
'''
if extra in nav:
    nav = nav.replace(extra, "", 1)
elif "nav_tab_services_direct" in nav:
    raise SystemExit("Unexpected direct Services nav implementation")
nav_path.write_text(nav, encoding="utf-8")

test = root / "app/src/test/java/com/example/HomeExperienceControlsTest.kt"
test.parent.mkdir(parents=True, exist_ok=True)
test.write_text('''package com.example

import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

class HomeExperienceControlsTest {
  @Test fun homeExperienceControlsAreWiredIntoScreens() {
    val root = File("src/main")
    val slider = File(root, "java/com/example/ui/components/HomePromoBannerSlider.kt").readText()
    val settings = File(root, "java/com/example/ui/screens/SettingsScreen.kt").readText()
    val home = File(root, "java/com/example/ui/screens/BusinessHomeScreen.kt").readText()
    val nav = File(root, "java/com/example/ui/components/BottomNavBar.kt").readText()
    assertTrue(slider.contains("SLIDER_ENABLED") && slider.contains("Special Offer"))
    assertTrue(settings.contains("home_experience_settings") && settings.contains("DEMO_ENABLED"))
    assertTrue(home.contains("demoProductsEnabled"))
    assertTrue(nav.contains("nav_tab_services") && !nav.contains("nav_tab_services_direct"))
  }
}
''', encoding="utf-8")
print("Home slider, special offer, demo toggle, and Catalog-only Services controls applied.")
