package com.example.ui.theme

import androidx.compose.ui.graphics.Color

data class AppThemePalette(
  val id: String, val nameEn: String, val nameUr: String,
  val primary: Color, val secondary: Color, val tertiary: Color,
  val background: Color, val surface: Color, val container: Color,
  val onPrimary: Color = Color.White
)

object AppThemePalettes {
  // Stable IDs preserve each user's previously selected palette.
  // Visible labels describe the color itself, not an event or campaign.
  val all = listOf(
    AppThemePalette("default","Emerald Green","زمردی سبز",Color(0xFF086B4D),Color(0xFF535F70),Color(0xFF6B5778),Color(0xFFF5F7F2),Color.White,Color(0xFFE5F3EA)),
    AppThemePalette("pakistan","Forest Green","گہرا جنگلی سبز",Color(0xFF006B45),Color(0xFFB9D9C7),Color(0xFFD5AD52),Color(0xFFF2F8F4),Color.White,Color(0xFFDDEFE4)),
    AppThemePalette("eid","Teal Green","نیلگوں سبز",Color(0xFF087F70),Color(0xFFB58A38),Color(0xFF6652A3),Color(0xFFF5F8F6),Color.White,Color(0xFFDDF3EC)),
    AppThemePalette("ramadan","Indigo Blue","نیلگوں جامنی",Color(0xFF4554A3),Color(0xFFB48A45),Color(0xFF287A70),Color(0xFFF5F5FB),Color.White,Color(0xFFE7E9FA)),
    AppThemePalette("milad","Jade Green","یشمی سبز",Color(0xFF087C55),Color(0xFF4F9B80),Color(0xFFC69A43),Color(0xFFF3F8F5),Color.White,Color(0xFFDDF0E5)),
    AppThemePalette("awareness","Rose Pink","گلابی",Color(0xFFB83280),Color(0xFF7B5AA6),Color(0xFFD977A8),Color(0xFFFFF5FA),Color.White,Color(0xFFFCE0EF)),
    AppThemePalette("ocean","Ocean Blue","سمندری نیلا",Color(0xFF1769AA),Color(0xFF397F91),Color(0xFF6757A5),Color(0xFFF3F7FC),Color.White,Color(0xFFDDEBFA)),
    AppThemePalette("royal","Royal Purple","شاہی جامنی",Color(0xFF6542A6),Color(0xFF8A639F),Color(0xFFB07A54),Color(0xFFF7F5FB),Color.White,Color(0xFFECE4F7)),
    AppThemePalette("sunrise","Amber Orange","عنبر نارنجی",Color(0xFFB4532A),Color(0xFF8A6845),Color(0xFF5F7E68),Color(0xFFFCF7F1),Color.White,Color(0xFFF5E8D9))
  )
  fun get(id:String):AppThemePalette {
    if(id.startsWith("custom:")) {
      val raw=id.removePrefix("custom:").removePrefix("#")
      val color=runCatching { Color(raw.toLong(16) or 0xFF000000L) }.getOrNull()
      if(color!=null) return AppThemePalette("custom:$raw","Custom Color","اپنا منتخب رنگ",color,color.copy(alpha=.82f),Color(0xFF64748B),Color(0xFFF7F8FA),Color.White,color.copy(alpha=.12f))
    }
    return all.firstOrNull { it.id==id } ?: all.first()
  }
}