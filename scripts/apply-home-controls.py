#!/usr/bin/env python3
"""Safely add owner controls for Home promos/demo data and keep Services in Catalog."""
from pathlib import Path
import sys

root = Path(sys.argv[1])

def edit(rel, fn):
    p = root / rel
    if not p.exists():
        raise SystemExit(f"Required source file missing: {rel}")
    old = p.read_text(encoding="utf-8")
    new = fn(old)
    if new == old:
        print(f"Already applied: {rel}")
    else:
        p.write_text(new, encoding="utf-8")
        print(f"Updated: {rel}")

prefs_rel = "app/src/main/java/com/example/ui/components/HomeExperiencePrefs.kt"
prefs = root / prefs_rel
prefs.parent.mkdir(parents=True, exist_ok=True)
prefs.write_text('''package com.example.ui.components

import android.content.Context

/** Owner-controlled presentation preferences for the Home storefront. */
object HomeExperiencePrefs {
  private const val FILE = "arshad_home_experience"
  const val SLIDER_ENABLED = "slider_enabled"
  const val OFFER_ENABLED = "offer_enabled"
  const val OFFER_TITLE = "offer_title"
  const val OFFER_DISCOUNT = "offer_discount"
  const val BANNER_IMAGE_URL = "banner_image_url"
  const val DEMO_ENABLED = "demo_products_enabled"

  fun prefs(context: Context) = context.getSharedPreferences(FILE, Context.MODE_PRIVATE)
  fun enabled(context: Context, key: String, default: Boolean = true) =
    prefs(context).getBoolean(key, default)
  fun text(context: Context, key: String, default: String = "") =
    prefs(context).getString(key, default) ?: default
  fun put(context: Context, key: String, value: Boolean) {
    prefs(context).edit().putBoolean(key, value).apply()
  }
  fun put(context: Context, key: String, value: String) {
    prefs(context).edit().putString(key, value).apply()
  }
}
''', encoding="utf-8")

def patch_slider(s):
    if "HomeExperiencePrefs.SLIDER_ENABLED" in s:
        return s
    s = s.replace(
      "import androidx.compose.ui.platform.testTag\n",
      "import androidx.compose.ui.platform.testTag\nimport androidx.compose.ui.platform.LocalContext\n", 1)
    s = s.replace(
      "  val action: () -> Unit\n)",
      "  val action: () -> Unit,\n  val isOffer: Boolean = false\n)", 1)
    start = "  val slides = remember(appMode, isUrdu, onPosClick, onProductsClick, onServicesClick, onKhataClick) {"
    if start not in s:
        raise SystemExit("Home slider: slides declaration anchor not found")
    s = s.replace(start, '''  val context = LocalContext.current
  val sliderEnabled = HomeExperiencePrefs.enabled(context, HomeExperiencePrefs.SLIDER_ENABLED, true)
  val offerEnabled = HomeExperiencePrefs.enabled(context, HomeExperiencePrefs.OFFER_ENABLED, true)
  val offerTitle = HomeExperiencePrefs.text(context, HomeExperiencePrefs.OFFER_TITLE, "on Fresh Products")
  val offerDiscount = HomeExperiencePrefs.text(context, HomeExperiencePrefs.OFFER_DISCOUNT, "20%")
  val customImage = HomeExperiencePrefs.text(context, HomeExperiencePrefs.BANNER_IMAGE_URL)
  val activeBannerImage = customImage.ifBlank { bannerImageUri }
  val slides = remember(appMode, isUrdu, onPosClick, onProductsClick, onServicesClick, onKhataClick, offerEnabled, offerTitle, offerDiscount) {''', 1)
    # Rename the existing conditional list expression into a local list before appending the offer.
    s = s.replace(
      "    if (appMode == AppMode.PERSONAL_KHATA) listOf(",
      "    val standardSlides = if (appMode == AppMode.PERSONAL_KHATA) listOf(", 1)
    old = '''    )
  }
  val pagerState = rememberPagerState(pageCount = { slides.size })'''
    new = '''    )
    if (appMode == AppMode.PERSONAL_KHATA || !offerEnabled) standardSlides else standardSlides + PromoSlide(
      "Special Offer • $offerDiscount OFF", "خصوصی آفر • $offerDiscount رعایت",
      offerTitle.ifBlank { "on Fresh Products" }, offerTitle.ifBlank { "تازہ مصنوعات پر خصوصی رعایت" },
      "Shop Now", "ابھی خریدیں", Icons.Default.LocalOffer,
      listOf(Color(0xFFFFB52E), Color(0xFFF97316)), onProductsClick, isOffer = true)
  }
  if (!sliderEnabled || slides.isEmpty()) return
  val pagerState = rememberPagerState(pageCount = { slides.size })'''
    if old not in s:
        raise SystemExit("Home slider: end-of-slides anchor not found")
    s = s.replace(old, new, 1)
    s = s.replace(
      "model = bannerImageUri.takeIf { it.isNotBlank() } ?: when (page) {",
      "model = (if (slide.isOffer) com.example.R.drawable.af_demo_grocery else activeBannerImage.takeIf { it.isNotBlank() }) ?: when (page) {", 1)
    return s

edit("app/src/main/java/com/example/ui/components/HomePromoBannerSlider.kt", patch_slider)

def patch_home(s):
    if "HomeExperiencePrefs.DEMO_ENABLED" in s:
        return s
    s = s.replace(
      "import com.example.ui.components.HomePromoBannerSlider\n",
      "import com.example.ui.components.HomePromoBannerSlider\nimport com.example.ui.components.HomeExperiencePrefs\n", 1)
    anchor = "  val urdu = uiState.appLanguage == AppLanguage.URDU\n"
    if anchor not in s:
        raise SystemExit("Business Home: language state anchor not found")
    s = s.replace(anchor, anchor + "  val demoProductsEnabled = HomeExperiencePrefs.enabled(LocalContext.current, HomeExperiencePrefs.DEMO_ENABLED, true)\n", 1)
    s = s.replace("      item {\n        OutlinedButton(onClick = onLoadDemoCatalog", "      if (demoProductsEnabled) item {\n        OutlinedButton(onClick = onLoadDemoCatalog", 1)
    s = s.replace(
      'Button(onClick = onLoadDemoCatalog, modifier = Modifier.fillMaxWidth()) { Icon(Icons.Default.Storefront, null); Spacer(Modifier.width(6.dp)); Text(t("Load sample products", "نمونہ پروڈکٹس لوڈ کریں")) }',
      'if (demoProductsEnabled) Button(onClick = onLoadDemoCatalog, modifier = Modifier.fillMaxWidth()) { Icon(Icons.Default.Storefront, null); Spacer(Modifier.width(6.dp)); Text(t("Load sample products", "نمونہ پروڈکٹس لوڈ کریں")) }', 1)
    s = s.replace(
      "          Button(onClick = onLoadDemoCatalog, modifier = Modifier.fillMaxWidth()) {",
      "          if (demoProductsEnabled) Button(onClick = onLoadDemoCatalog, modifier = Modifier.fillMaxWidth()) {", 1)
    return s

edit("app/src/main/java/com/example/ui/screens/BusinessHomeScreen.kt", patch_home)

def patch_settings(s):
    if "home_experience_settings" in s:
        return s
    if "import androidx.compose.material3.OutlinedTextField\n" not in s:
        s = s.replace("import androidx.compose.material3.OutlinedButton\n",
                      "import androidx.compose.material3.OutlinedButton\nimport androidx.compose.material3.OutlinedTextField\n", 1)
    s = s.replace("import com.example.ui.FinanceUiState\n",
                  "import com.example.ui.FinanceUiState\nimport com.example.ui.components.HomeExperiencePrefs\n", 1)
    anchor = "  var showApkDownloadGuideDialog by remember { mutableStateOf(false) }\n"
    if anchor not in s:
        raise SystemExit("Settings: state insertion anchor not found")
    state = '''  val homePrefs = remember { HomeExperiencePrefs.prefs(context) }
  var homeSliderEnabled by remember { mutableStateOf(homePrefs.getBoolean(HomeExperiencePrefs.SLIDER_ENABLED, true)) }
  var offerEnabled by remember { mutableStateOf(homePrefs.getBoolean(HomeExperiencePrefs.OFFER_ENABLED, true)) }
  var demoProductsEnabled by remember { mutableStateOf(homePrefs.getBoolean(HomeExperiencePrefs.DEMO_ENABLED, true)) }
  var offerTitle by remember { mutableStateOf(homePrefs.getString(HomeExperiencePrefs.OFFER_TITLE, "on Fresh Products") ?: "on Fresh Products") }
  var offerDiscount by remember { mutableStateOf(homePrefs.getString(HomeExperiencePrefs.OFFER_DISCOUNT, "20%") ?: "20%") }
  var bannerImageUrl by remember { mutableStateOf(homePrefs.getString(HomeExperiencePrefs.BANNER_IMAGE_URL, "") ?: "") }
'''
    s = s.replace(anchor, anchor + state, 1)
    anchor = "    // 0. User Account, Cloud Sync & Device Recovery Card\n    item {\n"
    if anchor not in s:
        raise SystemExit("Settings: first settings card insertion point not found")
    card = '''    // Owner-adjustable Home storefront presentation settings.
    item {
      Card(shape = RoundedCornerShape(20.dp), colors = CardDefaults.cardColors(containerColor = Color.White),
        modifier = Modifier.fillMaxWidth().testTag("home_experience_settings")) {
        Column(Modifier.fillMaxWidth().padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
          Text(if (isUrdu) "ہوم سلائیڈر اور ڈیمو کنٹرول" else "Home Slider & Demo Controls",
            fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color(0xFF0F172A))
          Text(if (isUrdu) "ہوم بینرز، خصوصی آفر اور نمونہ پروڈکٹس یہاں سے کنٹرول کریں۔" else "Manage Home banners, special offers and sample products here.",
            fontSize = 12.sp, color = Color(0xFF64748B))
          Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
            Text(if (isUrdu) "ہوم سلائیڈر دکھائیں" else "Show Home slider", modifier = Modifier.weight(1f), fontWeight = FontWeight.SemiBold)
            Switch(checked = homeSliderEnabled, onCheckedChange = {
              homeSliderEnabled = it
              HomeExperiencePrefs.put(context, HomeExperiencePrefs.SLIDER_ENABLED, it)
            })
          }
          HorizontalDivider(color = Color(0xFFE8EFEA))
          Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
            Text(if (isUrdu) "خصوصی آفر / ڈسکاؤنٹ سلائیڈر" else "Special Offer / Discount slider", modifier = Modifier.weight(1f), fontWeight = FontWeight.SemiBold)
            Switch(checked = offerEnabled, onCheckedChange = {
              offerEnabled = it
              HomeExperiencePrefs.put(context, HomeExperiencePrefs.OFFER_ENABLED, it)
            })
          }
          if (offerEnabled) {
            OutlinedTextField(value = offerDiscount, onValueChange = {
              offerDiscount = it
              HomeExperiencePrefs.put(context, HomeExperiencePrefs.OFFER_DISCOUNT, it)
            }, modifier = Modifier.fillMaxWidth(), singleLine = true,
              label = { Text(if (isUrdu) "ڈسکاؤنٹ (مثلاً 20%)" else "Discount (e.g. 20%)") })
            OutlinedTextField(value = offerTitle, onValueChange = {
              offerTitle = it
              HomeExperiencePrefs.put(context, HomeExperiencePrefs.OFFER_TITLE, it)
            }, modifier = Modifier.fillMaxWidth(), singleLine = true,
              label = { Text(if (isUrdu) "آفر کی تفصیل" else "Offer text") })
          }
          OutlinedTextField(value = bannerImageUrl, onValueChange = {
            bannerImageUrl = it
            HomeExperiencePrefs.put(context, HomeExperiencePrefs.BANNER_IMAGE_URL, it)
          }, modifier = Modifier.fillMaxWidth(), singleLine = true,
            label = { Text(if (isUrdu) "متبادل بینر تصویر کا URL (اختیاری)" else "Replacement banner image URL (optional)") })
          OutlinedButton(onClick = onOpenShopProfile, modifier = Modifier.fillMaxWidth()) {
            Icon(Icons.Default.Store, null)
            Spacer(Modifier.width(8.dp))
            Text(if (isUrdu) "دکان کی پروفائل میں بینر تصویر تبدیل کریں" else "Change banner image in Shop Profile")
          }
          HorizontalDivider(color = Color(0xFFE8EFEA))
          Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
            Column(Modifier.weight(1f)) {
              Text(if (isUrdu) "نمونہ / ڈیمو پروڈکٹس" else "Sample / Demo products", fontWeight = FontWeight.SemiBold)
              Text(if (isUrdu) "ہوم پر نمونہ لوڈ کرنے کے بٹن دکھائیں یا چھپائیں" else "Show or hide sample-loading buttons on Home", fontSize = 11.sp, color = Color(0xFF64748B))
            }
            Switch(checked = demoProductsEnabled, onCheckedChange = {
              demoProductsEnabled = it
              HomeExperiencePrefs.put(context, HomeExperiencePrefs.DEMO_ENABLED, it)
            })
          }
        }
      }
    }

    // 0. User Account, Cloud Sync & Device Recovery Card
    item {
'''
    s = s.replace(anchor, card, 1)
    return s

edit("app/src/main/java/com/example/ui/screens/SettingsScreen.kt", patch_settings)

def patch_nav(s):
    s2 = s.replace(
'''      if (features.services) NavBarChoice(if (urdu) "سروسز" else "Services", Icons.Default.Handyman,
        selectedTab == FinanceTab.SERVICES, "nav_tab_services_direct") { onTabSelected(FinanceTab.SERVICES) }
''', "", 1)
    if s2 == s and "nav_tab_services_direct" in s:
        raise SystemExit("Bottom navigation: direct Services tab found but exact safe removal anchor did not match")
    if "nav_tab_services" not in s2:
        raise SystemExit("Bottom navigation: Services destination inside Catalog is missing")
    return s2

edit("app/src/main/java/com/example/ui/components/BottomNavBar.kt", patch_nav)

test = root / "app/src/test/java/com/example/HomeExperienceControlsTest.kt"
test.write_text('''package com.example

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

class HomeExperienceControlsTest {
  @Test fun sliderOfferAndDemoControlsAreConnected() {
    val slider = File("src/main/java/com/example/ui/components/HomePromoBannerSlider.kt").readText()
    val settings = File("src/main/java/com/example/ui/screens/SettingsScreen.kt").readText()
    val home = File("src/main/java/com/example/ui/screens/BusinessHomeScreen.kt").readText()
    assertTrue(slider.contains("HomeExperiencePrefs.SLIDER_ENABLED"))
    assertTrue(slider.contains("Special Offer"))
    assertTrue(slider.contains("isOffer = true"))
    assertTrue(settings.contains("home_experience_settings"))
    assertTrue(settings.contains("HomeExperiencePrefs.DEMO_ENABLED"))
    assertTrue(home.contains("demoProductsEnabled"))
  }

  @Test fun servicesIsAvailableInsideCatalogAndNotAsBottomTab() {
    val nav = File("src/main/java/com/example/ui/components/BottomNavBar.kt").readText()
    assertTrue(nav.contains("MenuDestination(\\"Services\\""))
    assertFalse(nav.contains("nav_tab_services_direct"))
  }
}
''', encoding="utf-8")
print("Home slider, discount offer, demo toggle, Catalog-only Services and regression tests applied.")
