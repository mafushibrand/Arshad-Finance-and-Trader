# ArshadFinance Master Handoff & Audit Register
Updated: 2026-11-19
Repository: https://github.com/mafushibrand/Arshad-Finance-and-Trader
Current reviewed baseline: APK 4.7.0, versionCode 56, package com.aistudio.arshadfinance.v2stock.standalone5
Baseline source artifact: ArshadFinance-4.7.0-source / ArshadFinance-4.7.0-final-source.zip
Baseline APK SHA-256: c89f77fb6d3cbcfe4bde2692594856be2a7494e945b6d67f7fbccf197307d281
Baseline build run: https://github.com/mafushibrand/Arshad-Finance-and-Trader/actions/runs/43181899850

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

## Latest CI baseline (not physical-device QA)
Run #102: https://github.com/mafushibrand/Arshad-Finance-and-Trader/actions/runs/43181899850
Prior run report indicated build, unit tests, signature/package verification, and artifact upload succeeded. Downloaded APK metadata confirms:
- versionName 4.7.0; versionCode 56
- package com.aistudio.arshadfinance.v2stock.standalone5
- min SDK 24 (Android 7.0); target SDK 34; compile SDK 36
- APK signature schemes v2 and v3 verify
- SHA-256: c89f77fb6d3cbcfe4bde2692594856be2a7494e945b6d67f7fbccf197307d281
Physical installation, WhatsApp handoff, camera/gallery behavior, and full workflow QA remain unverified on a real phone.
The APK is a debug build signed by the CI debug keystore, not a Play Store production release. Preserve signing continuity and do not publish a release until a private production keystore and secure backup are configured.

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
