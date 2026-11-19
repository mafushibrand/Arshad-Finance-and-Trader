package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Palette
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.ui.FinanceUiState
import com.example.ui.theme.AppThemePalettes

@Composable
fun ThemeSettingsScreen(state:FinanceUiState,selectedTheme:String,onSelectTheme:(String)->Unit,onBack:()->Unit={}) {
  var customHex by remember { mutableStateOf("086B4D") }
  var customError by remember { mutableStateOf("") }
  val urdu=state.appLanguage==com.example.data.model.AppLanguage.URDU
  fun label(en:String,ur:String)=if(urdu) ur else en
  PremiumPage(label("App theme & colors","ایپ تھیم اور رنگ"),label("One consistent look across your business","آپ کی پوری ایپ کے لیے ایک جیسا خوبصورت انداز"),Icons.Default.Palette) {
    item { TextButton(onClick=onBack){Text(label("Back","واپس"))} }
    item {
      Card(colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.primaryContainer),shape=RoundedCornerShape(22.dp)) {
        Column(Modifier.fillMaxWidth().padding(18.dp),verticalArrangement=Arrangement.spacedBy(6.dp)) {
          Text(label("Your app, your colors","آپ کی ایپ، آپ کے پسندیدہ رنگ"),style=MaterialTheme.typography.titleLarge,fontWeight=FontWeight.Bold,color=MaterialTheme.colorScheme.onPrimaryContainer)
          Text(label("Choose a seasonal theme or create your own primary color. Your records and business data stay unchanged.","موسمی تھیم منتخب کریں یا اپنا بنیادی رنگ بنائیں۔ آپ کا کاروباری ڈیٹا اور ریکارڈ محفوظ رہیں گے۔"),color=MaterialTheme.colorScheme.onPrimaryContainer)
        }
      }
    }
    items(AppThemePalettes.all,key={it.id}) { palette ->
      val active=selectedTheme==palette.id
      Card(modifier=Modifier.fillMaxWidth().clickable{onSelectTheme(palette.id)}.testTag("theme_${palette.id}"),border=androidx.compose.foundation.BorderStroke(if(active)2.dp else 1.dp,if(active)MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outlineVariant),colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.surface)) {
        Row(Modifier.fillMaxWidth().padding(14.dp),verticalAlignment=Alignment.CenterVertically,horizontalArrangement=Arrangement.spacedBy(12.dp)) {
          Row(horizontalArrangement=Arrangement.spacedBy(4.dp)) {
            listOf(palette.primary,palette.secondary,palette.tertiary,palette.container).forEach { color -> Box(Modifier.size(25.dp).background(color,CircleShape).border(1.dp,MaterialTheme.colorScheme.outlineVariant,CircleShape)) }
          }
          Column(Modifier.weight(1f)) {
            Text(if(urdu)palette.nameUr else palette.nameEn,fontWeight=FontWeight.SemiBold)
            Text(palette.nameEn,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
          }
          if(active) Icon(Icons.Default.Check,contentDescription=label("Selected","منتخب"),tint=MaterialTheme.colorScheme.primary)
        }
      }
    }
    item {
      Card(shape=RoundedCornerShape(20.dp)) {
        Column(Modifier.fillMaxWidth().padding(16.dp),verticalArrangement=Arrangement.spacedBy(10.dp)) {
          Text(label("Custom primary color","اپنا بنیادی رنگ"),style=MaterialTheme.typography.titleMedium,fontWeight=FontWeight.Bold)
          OutlinedTextField(value=customHex,onValueChange={customHex=it.trim().removePrefix("#").take(6);customError=""},label={Text(label("Hex color (e.g. 086B4D)","کلر کوڈ (مثلاً 086B4D)"))},singleLine=true,modifier=Modifier.fillMaxWidth().testTag("custom_theme_hex"),leadingIcon={Text("#")})
          if(customError.isNotBlank()) Text(customError,color=MaterialTheme.colorScheme.error,style=MaterialTheme.typography.bodySmall)
          Button(onClick={if(customHex.matches(Regex("[0-9A-Fa-f]{6}")))onSelectTheme("custom:$customHex") else customError=label("Enter a valid 6-digit hex color.","درست 6 ہندسوں کا کلر کوڈ درج کریں۔")},modifier=Modifier.fillMaxWidth().heightIn(min=50.dp).testTag("apply_custom_theme")){Text(label("Apply my color","میرا رنگ لگائیں"))}
        }
      }
    }
    item { Text(label("Theme changes affect app colors only; financial records, invoices and stock are not modified.","تھیم تبدیل کرنے سے صرف ایپ کے رنگ بدلیں گے؛ مالی ریکارڈ، بل اور اسٹاک تبدیل نہیں ہوں گے۔"),style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant,modifier=Modifier.padding(vertical=8.dp)) }
  }
}