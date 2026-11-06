#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1])

def edit(rel, replacements):
    p = root / rel
    s = p.read_text(encoding="utf-8")
    for old, new, label in replacements:
        if new in s:
            continue
        if old not in s:
            raise SystemExit(f"{rel}: missing safe patch anchor: {label}")
        s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8")
    print("Patched", rel)

edit("app/src/main/java/com/example/util/BusinessUtils.kt", [
('  val logoEmoji: String = "🏪",\n','  val logoEmoji: String = "🏪",\n  val logoImageUri: String = "",\n  val bannerImageUri: String = "",\n',"profile image fields")
])

edit("app/src/main/java/com/example/ui/dialogs/PremiumAddEditInventoryDialog.kt", [
('package com.example.ui.dialogs\n','''package com.example.ui.dialogs

import android.content.Intent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.layout.ContentScale
import coil.compose.AsyncImage
''',"picker imports"),
('  var confirmDelete by remember { mutableStateOf(false) }\n','''  var confirmDelete by remember { mutableStateOf(false) }
  val context = LocalContext.current
  var productImageUri by remember { mutableStateOf(value("imageUri")) }
  val productImagePicker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
    if (uri != null) {
      runCatching { context.contentResolver.takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION) }
      productImageUri = uri.toString()
      change("imageUri", productImageUri)
    }
  }
''',"product image state"),
('    Text(label("Product details", "سامان کی تفصیل"), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)\n','''    Text(label("Product details", "سامان کی تفصیل"), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
    Text(label("Product photo", "مصنوعات کی تصویر"), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.CenterVertically) {
      if (productImageUri.isNotBlank()) AsyncImage(model=productImageUri, contentDescription=label("Product photo","مصنوعات کی تصویر"), contentScale=ContentScale.Crop, modifier=Modifier.size(88.dp).clip(androidx.compose.foundation.shape.RoundedCornerShape(14.dp)))
      else Surface(Modifier.size(88.dp), shape=androidx.compose.foundation.shape.RoundedCornerShape(14.dp), color=MaterialTheme.colorScheme.surfaceVariant) { Box(contentAlignment=Alignment.Center) { Icon(Icons.Default.Image, null, modifier=Modifier.size(32.dp)) } }
      Column(Modifier.weight(1f), verticalArrangement=Arrangement.spacedBy(4.dp)) {
        OutlinedButton(onClick={productImagePicker.launch(arrayOf("image/*"))}) { Text(label("Upload / Change photo","تصویر اپ لوڈ / تبدیل کریں")) }
        if(productImageUri.isNotBlank()) TextButton(onClick={productImageUri="";change("imageUri","")}) { Text(label("Remove photo","تصویر ہٹائیں")) }
      }
    }
''',"product image controls")
])

edit("app/src/main/java/com/example/ui/components/InventoryItemCard.kt", [
('import com.example.data.model.InventoryItem\n','import com.example.data.model.InventoryItem\nimport com.example.business.BusinessLibrary\nimport androidx.compose.ui.layout.ContentScale\nimport coil.compose.AsyncImage\n',"product image imports"),
('            Text(text = item.icon, fontSize = 22.sp)\n','''            val photo = BusinessLibrary.details(item.detailsJson).optString("imageUri")
            if (photo.isNotBlank()) AsyncImage(model=photo, contentDescription=item.name, contentScale=ContentScale.Crop,
              modifier=Modifier.fillMaxWidth().height(46.dp).clip(RoundedCornerShape(14.dp)))
            else Text(text = item.icon, fontSize = 22.sp)
''',"product image display")
])

edit("app/src/main/java/com/example/data/model/ServiceItem.kt", [
('  val isFeatured: Boolean = false\n','  val isFeatured: Boolean = false,\n  val imageUri: String = ""\n',"service image field")
])

edit("app/src/main/java/com/example/ui/screens/PremiumServiceDialog.kt", [
('package com.example.ui.screens\n','''package com.example.ui.screens

import android.content.Intent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Image
import androidx.compose.material3.Icon
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.TextButton
import androidx.compose.ui.Alignment
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import coil.compose.AsyncImage
''',"service picker imports"),
('  var icon by remember{mutableStateOf(service?.icon ?: "🛠️")};var description by remember{mutableStateOf(service?.description ?: "")};var error by remember{mutableStateOf("")}\n','''  var icon by remember{mutableStateOf(service?.icon ?: "🛠️")};var description by remember{mutableStateOf(service?.description ?: "")};var error by remember{mutableStateOf("")}
  val context = LocalContext.current
  var imageUri by remember { mutableStateOf(service?.imageUri ?: "") }
  val imagePicker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
    if (uri != null) {
      runCatching { context.contentResolver.takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION) }
      imageUri = uri.toString()
    }
  }
''',"service image state"),
('description=description));onDismiss()','description=description,imageUri=imageUri));onDismiss()',"persist service image"),
('    BusinessField(icon,t("Icon","آئیکن")){icon=it};BusinessField(description,t("Description","تفصیل")){description=it}\n','''    Text(t("Service image","سروس کی تصویر"), style=MaterialTheme.typography.titleSmall)
    Row(Modifier.fillMaxWidth(), horizontalArrangement=Arrangement.spacedBy(10.dp), verticalAlignment=Alignment.CenterVertically) {
      if(imageUri.isNotBlank()) AsyncImage(model=imageUri, contentDescription=t("Service image","سروس کی تصویر"), contentScale=ContentScale.Crop, modifier=Modifier.size(76.dp)) else Icon(Icons.Default.Image,null,modifier=Modifier.size(42.dp))
      OutlinedButton(onClick={imagePicker.launch(arrayOf("image/*"))}) { Text(t("Upload / Change","اپ لوڈ / تبدیل کریں")) }
      if(imageUri.isNotBlank()) TextButton(onClick={imageUri=""}) { Text(t("Remove","ہٹائیں")) }
    }
    BusinessField(icon,t("Icon","آئیکن")){icon=it};BusinessField(description,t("Description","تفصیل")){description=it}
''',"service image controls")
])

edit("app/src/main/java/com/example/ui/screens/ServicesScreen.kt", [
('import com.example.data.model.AppLanguage\n','import com.example.data.model.AppLanguage\nimport coil.compose.AsyncImage\nimport androidx.compose.ui.layout.ContentScale\n',"service card imports"),
('              Text(service.icon, fontSize = 22.sp)\n','''              if(service.imageUri.isNotBlank()) AsyncImage(model=service.imageUri, contentDescription=service.name, contentScale=ContentScale.Crop, modifier=Modifier.fillMaxWidth().height(42.dp).clip(CircleShape))
              else Text(service.icon, fontSize = 22.sp)
''',"service card image")
])

edit("app/src/main/java/com/example/ui/dialogs/BusinessBuilderDialog.kt", [
('package com.example.ui.dialogs\n','''package com.example.ui.dialogs

import android.content.Intent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.layout.ContentScale
import coil.compose.AsyncImage
''',"business picker imports"),
('  var error by remember { mutableStateOf(false) }\n','''  var error by remember { mutableStateOf(false) }
  val context = LocalContext.current
  var logoImageUri by remember { mutableStateOf(state.businessProfile.logoImageUri) }
  var bannerImageUri by remember { mutableStateOf(state.businessProfile.bannerImageUri) }
  var pendingBrandImage by remember { mutableStateOf("logo") }
  val brandImagePicker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
    if (uri != null) {
      runCatching { context.contentResolver.takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION) }
      if (pendingBrandImage == "logo") logoImageUri = uri.toString() else bannerImageUri = uri.toString()
    }
  }
''',"business image state"),
('subcategory = subcategory.trim()), features, currency.trim())','subcategory = subcategory.trim(), logoImageUri = logoImageUri, bannerImageUri = bannerImageUri), features, currency.trim())',"save brand images"),
('          Text(text("Enable features", "فیچرز فعال کریں"), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)\n','''          Text(text("Business branding", "کاروبار کی برانڈنگ"), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
          Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
            if (logoImageUri.isNotBlank()) AsyncImage(model=logoImageUri, contentDescription=text("Business logo","کاروبار کا لوگو"), contentScale=ContentScale.Crop, modifier=Modifier.size(56.dp))
            OutlinedButton(onClick={pendingBrandImage="logo";brandImagePicker.launch(arrayOf("image/*"))}) { Text(text("Upload logo","لوگو اپ لوڈ")) }
            if (logoImageUri.isNotBlank()) TextButton(onClick={logoImageUri=""}) { Text(text("Remove","ہٹائیں")) }
          }
          Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
            if (bannerImageUri.isNotBlank()) AsyncImage(model=bannerImageUri, contentDescription=text("Promotional banner","تشہیری بینر"), contentScale=ContentScale.Crop, modifier=Modifier.size(width=112.dp,height=56.dp))
            OutlinedButton(onClick={pendingBrandImage="banner";brandImagePicker.launch(arrayOf("image/*"))}) { Text(text("Upload banner","بینر اپ لوڈ")) }
            if (bannerImageUri.isNotBlank()) TextButton(onClick={bannerImageUri=""}) { Text(text("Remove","ہٹائیں")) }
          }
          Text(text("Enable features", "فیچرز فعال کریں"), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
''',"business image controls")
])

edit("app/src/main/java/com/example/ui/dialogs/ShopProfileDialog.kt", [
('import android.widget.Toast\n','''import android.widget.Toast
import android.content.Intent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.ui.layout.ContentScale
import coil.compose.AsyncImage
''',"shop profile picker imports"),
('import androidx.compose.material3.OutlinedTextField\n','import androidx.compose.material3.OutlinedButton\nimport androidx.compose.material3.TextButton\nimport androidx.compose.material3.OutlinedTextField\n',"shop profile buttons"),
('  var logoEmoji by remember { mutableStateOf(currentProfile.logoEmoji.ifBlank { "🏪" }) }\n','''  var logoEmoji by remember { mutableStateOf(currentProfile.logoEmoji.ifBlank { "🏪" }) }
  var logoImageUri by remember { mutableStateOf(currentProfile.logoImageUri) }
  var bannerImageUri by remember { mutableStateOf(currentProfile.bannerImageUri) }
  var pendingBrandImage by remember { mutableStateOf("logo") }
  val brandImagePicker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
    if (uri != null) {
      runCatching { context.contentResolver.takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION) }
      if (pendingBrandImage == "logo") logoImageUri = uri.toString() else bannerImageUri = uri.toString()
    }
  }
''',"shop profile image state"),
('        Spacer(modifier = Modifier.height(6.dp))\n\n        // 2. Shop / Business Name (Mandatory)\n','''        Spacer(modifier = Modifier.height(6.dp))
        Text("Business logo image / کاروبار کا لوگو", fontWeight = FontWeight.Bold, fontSize = 12.sp)
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
          if (logoImageUri.isNotBlank()) AsyncImage(model=logoImageUri, contentDescription="Business logo", contentScale=ContentScale.Crop, modifier=Modifier.size(56.dp).clip(RoundedCornerShape(12.dp)))
          OutlinedButton(onClick={pendingBrandImage="logo";brandImagePicker.launch(arrayOf("image/*"))}) { Text("Upload / Change logo") }
          if (logoImageUri.isNotBlank()) TextButton(onClick={logoImageUri=""}) { Text("Remove") }
        }
        Text("Promotional banner / تشہیری بینر", fontWeight = FontWeight.Bold, fontSize = 12.sp)
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
          if (bannerImageUri.isNotBlank()) AsyncImage(model=bannerImageUri, contentDescription="Business banner", contentScale=ContentScale.Crop, modifier=Modifier.size(width=104.dp,height=52.dp).clip(RoundedCornerShape(10.dp)))
          OutlinedButton(onClick={pendingBrandImage="banner";brandImagePicker.launch(arrayOf("image/*"))}) { Text("Upload / Change banner") }
          if (bannerImageUri.isNotBlank()) TextButton(onClick={bannerImageUri=""}) { Text("Remove") }
        }

        // 2. Shop / Business Name (Mandatory)
''',"shop profile image controls"),
('              logoEmoji = logoEmoji.trim(),\n','              logoEmoji = logoEmoji.trim(),\n              logoImageUri = logoImageUri,\n              bannerImageUri = bannerImageUri,\n',"save shop images")
])

edit("app/src/main/java/com/example/ui/components/HeaderBar.kt", [
('import androidx.compose.ui.text.style.TextOverflow\n','import androidx.compose.ui.text.style.TextOverflow\nimport androidx.compose.ui.layout.ContentScale\nimport coil.compose.AsyncImage\n',"header image imports"),
('  showSubscriptionAccess: Boolean = false\n','  showSubscriptionAccess: Boolean = false,\n  businessLogoUri: String = ""\n',"header logo parameter"),
('''        Surface(shape = RoundedCornerShape(16.dp), color = MaterialTheme.colorScheme.primaryContainer) {
          Icon(Icons.Default.Storefront, null, tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.padding(12.dp).size(24.dp))
        }
''','''        Surface(shape = RoundedCornerShape(16.dp), color = MaterialTheme.colorScheme.primaryContainer) {
          if (businessLogoUri.isNotBlank()) AsyncImage(model=businessLogoUri, contentDescription=businessName,
            contentScale=ContentScale.Crop, modifier=Modifier.size(48.dp))
          else Icon(Icons.Default.Storefront, null, tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.padding(12.dp).size(24.dp))
        }
''',"render business logo")
])

edit("app/src/main/java/com/example/MainActivity.kt", [
('            showSubscriptionAccess = uiState.selectedTab == FinanceTab.HOME\n','            showSubscriptionAccess = uiState.selectedTab == FinanceTab.HOME,\n            businessLogoUri = uiState.businessProfile.logoImageUri\n',"pass logo URI to header")
])

print("Multi-business product/service image upload, persistent branding, and editable business banners applied.")
