#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1])

header = root / "app/src/main/java/com/example/ui/components/HeaderBar.kt"
s = header.read_text(encoding="utf-8")
anchor = """      Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        TextButton(onClick = onToggleLanguage, modifier = Modifier.testTag("header_language_toggle")) {
          Text(if (urdu) "English" else "اردو")
        }
        TextButton(onClick = onSwitchRole, modifier = Modifier.testTag("header_role_badge")) {
          Text(if (userRole == UserRole.OWNER) { if (urdu) "مالک" else "Owner" }
            else { if (urdu) "عملہ" else "Staff" })
        }
        TextButton(onClick = onAuthClick, modifier = Modifier.testTag("header_auth_cloud_button")) {
          Text(if (urdu) "اکاؤنٹ" else "Account")
        }
      }
"""
addition = anchor + """      // Show plan access after a trial/payment relationship exists, not on every fresh screen.
      if (subscriptionState.trialStartedMillis > 0L || subscriptionState.isActivated ||
        subscriptionState.hasPaidBefore || subscriptionState.clockBlocked) {
        Spacer(Modifier.height(8.dp))
        SubscriptionAccessCard(
          state = subscriptionState,
          language = appLanguage,
          onPlans = onTrialAlertClick,
          modifier = Modifier.padding(bottom = 10.dp)
        )
      }
"""
if "showSubscriptionAccess: Boolean = false" not in s:
    sig = '  businessName: String = "Arshad Finance"\n'
    if sig not in s:
        raise SystemExit("HeaderBar parameter anchor not found")
    s = s.replace(sig, '  businessName: String = "Arshad Finance",\n  showSubscriptionAccess: Boolean = false\n', 1)
if "SubscriptionAccessCard(" not in s:
    if anchor not in s:
        raise SystemExit("HeaderBar layout anchor not found; no unsafe edit made")
    s = s.replace(anchor, addition, 1)
s = s.replace("if (subscriptionState.trialStartedMillis > 0L || subscriptionState.isActivated ||",
              "if (showSubscriptionAccess && (subscriptionState.trialStartedMillis > 0L || subscriptionState.isActivated ||", 1)
s = s.replace("subscriptionState.hasPaidBefore || subscriptionState.clockBlocked) {",
              "subscriptionState.hasPaidBefore || subscriptionState.clockBlocked)) {", 1)
header.write_text(s, encoding="utf-8")

main = root / "app/src/main/java/com/example/MainActivity.kt"
m = main.read_text(encoding="utf-8")
if "showSubscriptionAccess = uiState.selectedTab == FinanceTab.HOME" not in m:
    needle = "            businessName = uiState.businessProfile.businessName\n"
    if needle not in m:
        raise SystemExit("MainActivity HeaderBar call anchor not found")
    m = m.replace(needle, needle + "            showSubscriptionAccess = uiState.selectedTab == FinanceTab.HOME\n", 1)
    main.write_text(m, encoding="utf-8")

test = root / "app/src/test/java/com/example/AccessDesignTest.kt"
t = test.read_text(encoding="utf-8")
needle = "       subscriptionState=SubscriptionState(trialStartedMillis=System.currentTimeMillis()-86_400_000L),onTrialAlertClick={opened=true})"
replacement = "       subscriptionState=SubscriptionState(trialStartedMillis=System.currentTimeMillis()-86_400_000L),onTrialAlertClick={opened=true},showSubscriptionAccess=true)"
if needle in t:
    t = t.replace(needle, replacement, 1)
elif replacement not in t:
    raise SystemExit("AccessDesignTest HeaderBar call anchor not found")
test.write_text(t, encoding="utf-8")

gradle = root / "app/build.gradle.kts"
g = gradle.read_text(encoding="utf-8")
needle = "  testImplementation(libs.robolectric)\n"
dep = '  // Real org.json implementation for JVM tests; Android's mock JSONObject.put throws.\n  testImplementation("org.json:json:20240303")\n'
if "testImplementation(\"org.json:json:20240303\")" not in g:
    if needle not in g:
        raise SystemExit("Robolectric dependency anchor not found; no unsafe edit made")
    g = g.replace(needle, needle + dep, 1)
gradle.write_text(g, encoding="utf-8")
print("Applied trial header UI, real JSON JVM test dependency, and idempotent checks.")
