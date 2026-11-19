# ArshadFinance Master Handoff & Audit Register
Updated: 2026-11-19
Repository: https://github.com/mafushibrand/Arshad-Finance-and-Trader
Current reviewed baseline: APK 4.7.0, versionCode 56, package com.aistudio.arshadfinance.v2stock.standalone5
Baseline source artifact: ArshadFinance-4.7.0-source / ArshadFinance-4.7.0-final-source.zip
Baseline APK SHA-256: c89f77fb6d3cbcfe4bde2692594856be2a7494e945b6d67f7fbccf197307d281
Baseline build run: https://github.com/mafushibrand/Arshad-Finance-and-Trader/actions/runs/43181899850

## Owner requirements — preserve verbatim as project constraints
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

## Latest CI baseline (not a claim of physical-device QA)
Run #102: https://github.com/mafushibrand/Arshad-Finance-and-Trader/actions/runs/43181899850
The prior run report indicated build, unit tests, signature/package verification, and artifact upload succeeded. Downloaded APK metadata confirms:
- versionName 4.7.0; versionCode 56
- package com.aistudio.arshadfinance.v2stock.standalone5
- min SDK 24 (Android 7.0); target SDK 34; compile SDK 36
- APK signature schemes v2 and v3 verify
- SHA-256: c89f77fb6d3cbcfe4bde2692594856be2a7494e945b6d67f7fbccf197307d281
Physical installation, WhatsApp handoff, camera/gallery behavior, and full workflow QA remain unverified on a real phone.
The APK is a debug build signed by the CI debug keystore, not a Play Store production release. Preserve signing continuity and do not publish a release until a private production keystore and secure backup are configured.

## Source and build-system caveat
The downloaded final-source artifact contains extracted app source and selected Gradle configuration but does not include the full original project root (notably AndroidManifest.xml and Gradle wrapper/root build files). The repository workflow reconstructs the build from the original source archive and applies scripts/*.py patch steps. Any source change must be made in the correct original source/patch layer and verified in the resulting extracted source; editing only a generated file can be overwritten by the next CI run.
Current assistant container has Java 21 but no installed Android SDK or Gradle executable/wrapper in the extracted artifact. Use GitHub Actions for reproducible builds unless a complete build environment is provisioned.

## Confirmed source-inspection findings requiring repair
### Critical: fake OTP and password recovery
- app/src/main/java/com/example/ui/screens/LoginScreen.kt: LegacyLoginScreen exposes a fixed recovery PIN 7861, claims SMS/WhatsApp was sent without sending it, and accepts OTP 7861 OR any input of length >= 4.
- app/src/main/java/com/example/ui/dialogs/AuthDialog.kt: OTP is generated locally, displayed in a toast/UI, and verification accepts generatedOtp OR any non-empty input. This is not real identity verification.
- Do not simply remove login or lock users out. Replace demo simulation with server-side OTP/auth only after backend/provider configuration is available. Until then, clearly label any demo mode and never claim an SMS/WhatsApp OTP was sent. Password reset must require verified identity.
### Cloud restore and sync
- The inspected technical guide and source configuration indicate local Room persistence; Firebase Auth/Firestore integration is not configured in the supplied extracted source.
- Cloud restore and Android-Web sync are not to be represented as active until backend, auth, storage, conflict handling, offline queue, and tenant isolation are implemented and tested.
### Thermal receipt WhatsApp
- app/src/main/java/com/example/util/ThermalReceiptImage.kt creates a JPEG, uses FileProvider URI, image/jpeg, ClipData and read permission, and attempts WhatsApp / WhatsApp Business before chooser fallback.
- Final-source archive omits AndroidManifest.xml, so provider declaration and file_paths resource could not be checked from this artifact. Verify these in the complete original project and test on device with both WhatsApp variants.
### Trial/payment
- UI/logic for trial/access exists; no live payment gateway, merchant credentials, or settlement flow is confirmed. Keep trial UX separate from payment processing; never claim payments work until sandbox and live end-to-end tests pass.
### Branding screenshot request (2026-11-19)
Implement as an extension of existing Shop Profile / business customization, not as a destructive replacement:
1. Brand identity and visual direction: logo, palette, typography, imagery.
2. Brand voice and messaging: tagline, story, tone, customer messages.
3. Brand positioning: audience, differentiators, market promise.
4. Brand personality: configurable style (e.g. premium, friendly, professional, traditional).
5. Brand reputation: customer reviews/testimonials and response workflow (do not fabricate ratings).
6. Brand consistency: reuse saved brand settings in app header, home/storefront, invoices, receipts, and future web storefront.
The screenshot's stated goal: make the brand recognisable, memorable, and different.
Preserve existing logo/banner upload, shop profile, and home slider capabilities. Make new brand fields optional and backward-compatible.

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
3. Before editing, inspect the original ZIP, full project tree, manifest, Gradle files, patch scripts and tests.
4. Implement small changes with regression tests; update the patch script when CI reapplies it.
5. Run compile + unit tests + lint/static checks; inspect APK package/version/signature/hash.
6. Install on a real device and capture evidence for the affected flows.
7. Upload APK, complete source, reports, changelog, commit SHA and run URL together.
8. Do not mark blocked work as complete. Do not remove existing features or user data.
