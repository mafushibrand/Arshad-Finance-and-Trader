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
if "SubscriptionAccessCard(" not in s:
    if anchor not in s:
        raise SystemExit("HeaderBar layout anchor not found; no unsafe edit made")
    s = s.replace(anchor, addition, 1)
header.write_text(s, encoding="utf-8")

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
