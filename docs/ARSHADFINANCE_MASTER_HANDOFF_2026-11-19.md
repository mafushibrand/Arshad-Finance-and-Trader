# ArshadFinance Master Handoff & Audit Register
Updated: 2026-11-19
Repository: https://github.com/mafushibrand/Arshad-Finance-and-Trader
Current CI-verified build: APK 4.8.0, versionCode 57, package com.aistudio.arshadfinance.v2stock.standalone5
Current source artifact: ArshadFinance-4.8.0-final-source.zip
Current APK SHA-256: d060cf7528a00da79f60371eca1947e26ed20ff2ec619281d286ffdfb0a18745
Current build run #112: https://github.com/mafushibrand/Arshad-Finance-and-Trader/actions/runs/44465735646
Previous baseline: APK 4.7.0, versionCode 56; preserve it as the prior reference.

## Owner requirements — project constraints
- Preserve the existing three months of work, all screens, business logic, records, and existing features.
- Never delete or replace existing features without explicit approval.
- Android bug audit and repair comes before web and iOS work.
- Web software must work on mobile, tablet, laptop, and desktop.
- Android and Web must share the same central backend/database with secure synchronization.
- After Android stabilizes, plan/build the shared backend and responsive web application; iOS comes later.
- Complete Urdu and English localization parity.
- Requested business modes: Selling Shop, Services, Khata.
- Existing feature expectations: POS, sales, purchases, inventory/stock, customer/supplier, accounts, invoices, thermal receipts, product images, shop branding, demo catalogue, home sliders/promotions, trial/payment UX, reports, backup/restore.
- Do not call a feature complete based only on compilation or unit tests; record manual device checks separately.

## Latest CI-verified build 4.8.0 (not physical-device QA)
Run #112: https://github.com/mafushibrand/Arshad-Finance-and-Trader/actions/runs/44465735646
Commit: 12c95b4d4fce94815aeb5bbb666e6d50e83dbde3
All workflow steps completed successfully, including:
- Khata ledger and global seasonal theme patch
- final source archive creation/upload
- Java 21, Android SDK and Gradle 9.3.1 setup
- APK compilation
- unit tests: 141 tests across 21 suites, 0 failures, 0 errors, 0 skipped
- APK signature/package verification
- APK and test-report artifact uploads
Verified APK metadata:
- versionName 4.8.0; versionCode 57
- package com.aistudio.arshadfinance.v2stock.standalone5
- min SDK 24 (Android 7.0); target SDK 34; compile SDK 36
- APK signature schemes v2 and v3 verify; one signer, CN=Arshad Finance, O=Arshad Finance, C=PK
- APK SHA-256: d060cf7528a00da79f60371eca1947e26ed20ff2ec619281d286ffdfb0a18745
- Artifact IDs: APK 14502810593; source 14500884402; test reports 14501963564
- This is an installable debug/test APK, not a Play Store production release. The manifest dump reports application-debuggable. Keep the CI signing identity for test upgrades; configure a private production keystore separately before release.
Khata enhancements present in source:
- Khata overview includes To collect, Customers, Collected and Due bills metrics.
- Customer search and All customers / To collect / Advance / All bills / Due bills filters.
- Customer detail supports receive-cash entry, bill history, due amounts and WhatsApp statement sharing.
- Existing advanced/legacy statement tools remain accessible; don't remove them.
Theme enhancements present in source:
- More > App theme & colors.
- Presets: Modern Emerald, Pakistan Independence, Eid Celebration, Ramadan Night, Milad Green, Breast Cancer Awareness, Ocean Blue, Royal Violet, Warm Sunrise.
- Custom 6-digit HEX primary color option.
- Selected palette is persisted in app_theme SharedPreferences and applied through a global Material 3 color scheme.
- Automated palette tests verify stable preset IDs, invalid-palette fallback and custom HEX handling.
Remaining verification/quality work:
- Static scan still finds 1,164 explicit Color(0x...) literals across 55 Kotlin files. Some are semantic colors, but many legacy screen/button colors are not yet fully tokenized. Do not claim every old component changes with the selected palette until the remaining hard-coded brand colors are migrated and visually checked.
- Robolectric/Compose unit screenshot tests cover Khata in English and Urdu, plus business data safety invariants; they do not prove actual WhatsApp launch, physical Khata cash collection, or theme appearance across every device screen.
- Real-device QA remains required: Khata receive cash and ledger balances; WhatsApp customer statement; switching each seasonal theme across Home, POS, Catalog, Khata, More, dialogs and buttons; thermal receipt image sharing.
- The previous 4.7.0 APK remains a prior reference. Do not uninstall the original design02 package app to install standalone5.

## Source and build-system caveat
The downloaded final-source artifact contains extracted app source and selected Gradle configuration but not the full original project root (notably AndroidManifest.xml, Gradle wrapper/root build files, and resources needed to validate provider wiring). The repository workflow reconstructs the build from the original source archive and applies scripts/*.py patch steps. Any source change must be made in the correct original source/patch layer and verified in resulting extracted source; editing only a generated file can be overwritten by the next CI run.
Current assistant container has Java 21 but no installed Android SDK or Gradle executable/wrapper in the extracted artifact. Use GitHub Actions for reproducible builds unless a complete build environment is provisioned.

## Confirmed source-inspection findings requiring repair
### Critical: current workspace access and simulated OTP
- app/src/main/java/com/example/ui/screens/PremiumLoginScreen.kt is the active LoginScreen wired by MainActivity. It is a local workspace setup/open flow; “Open existing workspace” invokes the local success callback without checking a password or server identity. The UI itself says workspace data is saved on this device.
- app/src/main/java/com/example/ui/dialogs/AuthDialog.kt is wired from MainActivity/Settings. It generates OTP locally, displays it in a toast/UI, and verification accepts generatedOtp OR any non-empty input. It is not real SMS/WhatsApp verification.
- app/src/main/java/com/example/ui/screens/LoginScreen.kt contains LegacyLoginScreen (not the active MainActivity entry route in the inspected source), with fixed recovery PIN 7861, false SMS/WhatsApp sent wording, and OTP acceptance of 7861 OR any input length >= 4. Do not mistake this legacy screen for the active entry screen.
- app/build.gradle.kts has Firebase AI and App Check active, but Firestore and Firebase Auth dependencies are commented out. This supports the finding that server auth/cloud data sync are not currently integrated in this build configuration.
- Do not simply remove login or lock existing owners out. Design a staged migration: preserve local workspace access for existing data, add genuine server-side account auth only after provider/backend configuration, then bind cloud workspaces to authenticated owners with tenant isolation. Until then, label local/demo verification honestly; never claim SMS/WhatsApp OTP was sent. Password reset must require verified identity.
### Branding screenshot mapped to existing implementation
- app/src/main/java/com/example/ui/dialogs/PremiumShopProfileDialog.kt exposes business name, owner, phone, address, business type, tagline, logo emoji, invoice prefix, NTN, bank/payment details and tax configuration.
- app/src/main/java/com/example/ui/dialogs/ShopProfileDialog.kt (legacy detailed profile) already has logoImageUri and bannerImageUri pickers. Preserve these.
- app/src/main/java/com/example/ui/dialogs/BusinessBuilderDialog.kt already has business branding with upload logo and upload banner.
- Screenshot areas not represented as full profile capabilities in the inspected profile UI: brand voice/messaging guidelines, positioning/differentiators, personality/style profile, reputation/reviews workflow, and saved brand palette/typography tokens applied consistently to storefront/invoices/receipts.
- Implement these as optional, backward-compatible extensions to existing profile; no fabricated ratings/reviews and no removal of current profile fields.
### Cloud restore and sync
- Inspected guide and source configuration indicate local Room persistence; Firebase Auth/Firestore integration is not configured in supplied extracted source.
- Cloud restore and Android-Web sync must not be represented as active until backend, auth, storage, conflict handling, offline queue, and tenant isolation are implemented and tested.
### Thermal receipt WhatsApp
- app/src/main/java/com/example/util/ThermalReceiptImage.kt creates JPEG, uses FileProvider URI, image/jpeg, ClipData and read permission, and attempts WhatsApp / WhatsApp Business before chooser fallback.
- Final-source archive omits AndroidManifest.xml, so provider declaration and file_paths resource could not be checked from this artifact. Verify these in complete original project and test on device with both WhatsApp variants.
### Trial/payment
- UI/logic for trial/access exists; no live payment gateway, merchant credentials, or settlement flow is confirmed. Keep trial UX separate from payment processing; never claim payments work until sandbox and live end-to-end tests pass.
### Database safety
- FinanceDatabase uses Room schema version 8 and exportSchema=false in inspected source. Review every migration from supported prior versions and backup/restore compatibility before schema changes; never use destructive migration or silently reset user data.

## Mandatory audit and regression checklist
Track each as Not started / In progress / Passed / Blocked, with commit, test evidence, and device evidence:
- Authentication: signup, login, logout, session expiry, wrong OTP, resend, rate limits, forgot password, account recovery.
- Data safety: create/edit/delete/restore, duplicate prevention, migrations, export/import, backup, permissions, multi-business isolation.
- Sales/POS: cart, discounts, taxes, partial payment, return/refund, duplicate checkout, stock deduction exactly once.
- Inventory: add/edit/delete, category changes, low stock, units, image upload, import/export.
- Purchase/supplier: receiving stock, payable balance, returns.
- Khata/accounts: credit/debit, settlements, balances, ledger correctness.
- Services: service catalogue, service POS, draft/complete/cancel, stock impact rules.
- Receipts/invoices: Urdu/English, print, save image/PDF, WhatsApp image sharing, provider URI permissions.
- Localization: every visible label, validation, dialog, toast, receipt and report in both languages; RTL alignment for Urdu.
- Branding: logo/banner, brand profile, optional content, color/typography, preview, invoices/receipts, persistence.
- Home slider/promotions: add/edit/reorder/enable/disable/remove, image-only slides, optional text/button, sale badge.
- Trial/payment: trial start/end, expiry, renewal, payment proof/status; no fake payment success.
- UI/device: Android 7+ compatibility, permissions, rotation, process death, offline behavior, small/large screens.
- Web readiness: API contract, auth, tenant scoping, cloud image storage, sync queue, conflict resolution, audit log, backups, responsive access.

## Safe delivery protocol
1. Preserve immutable copies of original uploaded source ZIP and current APK; record hashes.
2. Work on a new branch or commit series; do not overwrite baseline.
3. Before editing, inspect original ZIP, full project tree, manifest, Gradle files, patch scripts and tests.
4. Implement small changes with regression tests; update patch script when CI reapplies it.
5. Run compile + unit tests + lint/static checks; inspect APK package/version/signature/hash.
6. Install on a real device and capture evidence for affected flows.
7. Upload APK, complete source, reports, changelog, commit SHA and run URL together.
8. Do not mark blocked work complete. Do not remove existing features or user data.


## Theme label refinement — 4.8.1 in CI
- User explicitly requested visible theme labels to be actual color names, not occasion/campaign names such as Awareness, Eid, Milad, Pakistan Independence or Ramadan.
- Preserved existing palette IDs (default, pakistan, eid, ramadan, milad, awareness, ocean, royal, sunrise) so previously saved user selections remain valid.
- Visible English/Urdu labels now use color names: Emerald Green / زمردی سبز; Forest Green / گہرا جنگلی سبز; Teal Green / نیلگوں سبز; Indigo Blue / نیلگوں جامنی; Jade Green / یشمی سبز; Rose Pink / گلابی; Ocean Blue / سمندری نیلا; Royal Purple / شاہی جامنی; Amber Orange / عنبر نارنجی. Custom Color / اپنا منتخب رنگ.
- Theme picker helper text now says color palette, not seasonal theme.
- Regression test name changed from seasonal to named color palettes; persisted IDs unchanged.
- Build version bumped to 4.8.1, versionCode 58.
- GitHub Actions run #116: https://github.com/mafushibrand/Arshad-Finance-and-Trader/actions/runs/44470346421
- At handoff update time, workflow had completed all patching and was compiling the APK; unit tests, signature verification and artifact upload were still pending. Do not use 4.8.0 APK as if it contains the renamed labels.
- The wider legacy hard-coded color migration is not marked complete; retain a dedicated visual audit to migrate only brand/action colors safely while preserving semantic colors (success, warning, expense, chart series).
