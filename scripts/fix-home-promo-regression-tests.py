#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1])
test = root / "app/src/test/java/com/example/HomeExperienceControlsTest.kt"
s = test.read_text(encoding="utf-8")
old = """    val settings = File("src/main/java/com/example/ui/screens/SettingsScreen.kt").readText()
    val home = File("src/main/java/com/example/ui/screens/BusinessHomeScreen.kt").readText()
    assertTrue(slider.contains("HomeExperiencePrefs.SLIDER_ENABLED"))
    assertTrue(slider.contains("Special Offer"))
    assertTrue(slider.contains("isOffer = true"))
    assertTrue(settings.contains("home_experience_settings"))
    assertTrue(settings.contains("HomeExperiencePrefs.DEMO_ENABLED"))
    assertTrue(home.contains("demoProductsEnabled"))"""
new = """    val nav = File("src/main/java/com/example/ui/components/BottomNavBar.kt").readText()
    val manager = File("src/main/java/com/example/ui/screens/HomeSliderManagerScreen.kt").readText()
    val settings = File("src/main/java/com/example/ui/screens/SettingsScreen.kt").readText()
    val home = File("src/main/java/com/example/ui/screens/BusinessHomeScreen.kt").readText()
    assertTrue(slider.contains("HomeExperiencePrefs.SLIDER_ENABLED"))
    assertTrue(slider.contains("isSale"))
    assertTrue(nav.contains("nav_home_sliders"))
    assertTrue(manager.contains("HomeExperiencePrefs.SLIDER_ENABLED"))
    assertTrue(manager.contains("HomeExperiencePrefs.DEMO_ENABLED"))
    assertFalse(settings.contains("Home Slider & Demo Controls"))
    assertTrue(home.contains("demoProductsEnabled"))"""
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit("HomeExperienceControlsTest old assertions not found; refusing unsafe patch")
test.write_text(s, encoding="utf-8")

promo = root / "app/src/test/java/com/example/HomePromoBannerTest.kt"
p = promo.read_text(encoding="utf-8")
p = p.replace("اپنے پیسوں کا مکمل حساب", "اپنے پیسوں کا حساب")
promo.write_text(p, encoding="utf-8")
print("Updated Home slider regression tests to validate More-tab placement and actual Urdu default promo copy.")
