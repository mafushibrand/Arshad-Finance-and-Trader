#!/usr/bin/env python3
from pathlib import Path
import sys
r=Path(sys.argv[1]); b=r/"app/src/main/java/com/example"
def R(p): return p.read_text(encoding="utf-8")
def W(p,s): p.write_text(s,encoding="utf-8")
def rep(s,a,z):
 if a not in s:
  if z in s:return s
  raise SystemExit("Patch anchor missing: "+a[:70])
 return s.replace(a,z,1)

p=b/"ui/components/HomeExperiencePrefs.kt";s=R(p)
if "data class HomePromoSlideConfig" not in s:
 s=s.replace("import android.content.Context","import android.content.Context\nimport org.json.JSONArray\nimport org.json.JSONObject\nimport java.util.UUID")
 s=s.replace('  const val DEMO_ENABLED = "demo_products_enabled"','  const val DEMO_ENABLED = "demo_products_enabled"\n  private const val SLIDES = "home_slides_json"')
 s=s.replace("\n}",r'''
 fun defaults(personal:Boolean=false)=if(personal) listOf(HomePromoSlideConfig("khata","Your money, clearly tracked","اپنے پیسوں کا حساب","Track income and expenses","آمدن اور اخراجات","View khata","کھاتہ دیکھیں",action="KHATA")) else listOf(
 HomePromoSlideConfig("pos","Sell smarter, every day","ہر روز بہتر فروخت","Fast checkout and clear bills","تیز فروخت اور واضح بل","Start a sale","فروخت شروع کریں",action="POS"),
 HomePromoSlideConfig("products","Your products, in one place","آپ کی مصنوعات ایک جگہ","Search stock and prices","اسٹاک اور قیمتیں تلاش کریں","Explore products","مصنوعات دیکھیں",action="PRODUCTS"),
 HomePromoSlideConfig("services","Grow with services","سروسز کے ساتھ ترقی","Manage jobs and customers","کام اور گاہک منظم کریں","Explore services","سروسز دیکھیں",action="SERVICES"),
 HomePromoSlideConfig("sale","Special Offer • 20% OFF","خصوصی آفر • 20% رعایت","Sale products are waiting","رعایتی مصنوعات موجود ہیں","Shop Sale","سیل دیکھیں",isSale=true,action="PRODUCTS"))
 fun slides(c:Context,personal:Boolean=false):List<HomePromoSlideConfig>{val raw=prefs(c).getString(SLIDES,null)?:return defaults(personal);return runCatching{val a=JSONArray(raw);(0 until a.length()).mapNotNull{i->val o=a.optJSONObject(i)?:return@mapNotNull null;HomePromoSlideConfig(o.optString("id",UUID.randomUUID().toString()),o.optString("titleEn"),o.optString("titleUr"),o.optString("subtitleEn"),o.optString("subtitleUr"),o.optString("buttonEn"),o.optString("buttonUr"),o.optString("imageUri"),o.optBoolean("isSale"),o.optBoolean("enabled",true),o.optString("action","PRODUCTS"))}.filter{it.enabled}}.getOrDefault(defaults(personal))}
 fun saveSlides(c:Context,xs:List<HomePromoSlideConfig>){val a=JSONArray();xs.forEach{x->a.put(JSONObject().put("id",x.id).put("titleEn",x.titleEn).put("titleUr",x.titleUr).put("subtitleEn",x.subtitleEn).put("subtitleUr",x.subtitleUr).put("buttonEn",x.buttonEn).put("buttonUr",x.buttonUr).put("imageUri",x.imageUri).put("isSale",x.isSale).put("enabled",x.enabled).put("action",x.action))};prefs(c).edit().putString(SLIDES,a.toString()).apply()}
}
''')
 s += '\ndata class HomePromoSlideConfig(val id:String,val titleEn:String="",val titleUr:String="",val subtitleEn:String="",val subtitleUr:String="",val buttonEn:String="",val buttonUr:String="",val imageUri:String="",val isSale:Boolean=false,val enabled:Boolean=true,val action:String="PRODUCTS")\n'
 W(p,s)

p=b/"ui/screens/SettingsScreen.kt";s=R(p).replace("import com.example.ui.components.HomeExperiencePrefs\n","")
for x in ['  val homePrefs = remember { HomeExperiencePrefs.prefs(context) }\n','  var homeSliderEnabled by remember { mutableStateOf(homePrefs.getBoolean(HomeExperiencePrefs.SLIDER_ENABLED, true)) }\n','  var offerEnabled by remember { mutableStateOf(homePrefs.getBoolean(HomeExperiencePrefs.OFFER_ENABLED, true)) }\n','  var demoProductsEnabled by remember { mutableStateOf(homePrefs.getBoolean(HomeExperiencePrefs.DEMO_ENABLED, true)) }\n','  var offerTitle by remember { mutableStateOf(homePrefs.getString(HomeExperiencePrefs.OFFER_TITLE, "on Fresh Products") ?: "on Fresh Products") }\n','  var offerDiscount by remember { mutableStateOf(homePrefs.getString(HomeExperiencePrefs.OFFER_DISCOUNT, "20%") ?: "20%") }\n','  var bannerImageUrl by remember { mutableStateOf(homePrefs.getString(HomeExperiencePrefs.BANNER_IMAGE_URL, "") ?: "") }\n']:s=s.replace(x,"")
a=s.find("    // Owner-adjustable Home storefront presentation settings.");z=s.find("    // 0. User Account, Cloud Sync & Device Recovery Card",a)
if a<0 or z<0:raise SystemExit("Settings controls not found")
W(p,s[:a]+s[z:])

p=b/"ui/FinanceViewModel.kt";W(p,rep(R(p),"  SETTINGS;","  SETTINGS,\n  HOME_SLIDERS;"))
p=b/"ui/components/BottomNavBar.kt";s=R(p).replace("FinanceTab.PURCHASES, FinanceTab.OPERATIONS)","FinanceTab.PURCHASES, FinanceTab.OPERATIONS, FinanceTab.HOME_SLIDERS)")
a='          MenuDestination("Settings", "سیٹنگز", Icons.Default.Settings, FinanceTab.SETTINGS, "nav_tab_settings", urdu) { sheet = ""; onTabSelected(FinanceTab.SETTINGS) }'
W(p,rep(s,a,a+'\n          MenuDestination("Home sliders & demo", "ہوم سلائیڈرز اور ڈیمو", Icons.Default.ViewCarousel, FinanceTab.HOME_SLIDERS, "nav_home_sliders", urdu) { sheet = ""; onTabSelected(FinanceTab.HOME_SLIDERS) }'))
p=b/"MainActivity.kt";W(p,rep(R(p),"        FinanceTab.SETTINGS -> {","        FinanceTab.HOME_SLIDERS -> { com.example.ui.screens.HomeSliderManagerScreen(uiState) }\n        FinanceTab.SETTINGS -> {"))

p=b/"ui/screens/HomeSliderManagerScreen.kt";p.parent.mkdir(parents=True,exist_ok=True)
W(p,r'''package com.example.ui.screens
import android.content.Intent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.example.data.model.AppLanguage
import com.example.ui.FinanceUiState
import com.example.ui.components.*
import java.util.UUID
@OptIn(ExperimentalMaterial3Api::class)
@Composable fun HomeSliderManagerScreen(state:FinanceUiState){
 val c=LocalContext.current;val ur=state.appLanguage==AppLanguage.URDU
 fun t(a:String,b:String)=if(ur)b else a
 var enabled by remember{mutableStateOf(HomeExperiencePrefs.enabled(c,HomeExperiencePrefs.SLIDER_ENABLED,true))}
 var demo by remember{mutableStateOf(HomeExperiencePrefs.enabled(c,HomeExperiencePrefs.DEMO_ENABLED,true))}
 var xs by remember{mutableStateOf(HomeExperiencePrefs.slides(c,state.appMode.name=="PERSONAL_KHATA"))}
 var old by remember{mutableStateOf<HomePromoSlideConfig?>(null)};var dialog by remember{mutableStateOf(false)}
 var en by remember{mutableStateOf("")};var urT by remember{mutableStateOf("")};var sub by remember{mutableStateOf("")};var urS by remember{mutableStateOf("")};var btn by remember{mutableStateOf("")};var urB by remember{mutableStateOf("")};var image by remember{mutableStateOf("")};var sale by remember{mutableStateOf(false)};var action by remember{mutableStateOf("PRODUCTS")}
 val picker=rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()){u->if(u!=null){runCatching{c.contentResolver.takePersistableUriPermission(u,Intent.FLAG_GRANT_READ_URI_PERMISSION)};image=u.toString()}}
 fun save(v:List<HomePromoSlideConfig>){xs=v;HomeExperiencePrefs.saveSlides(c,v)}
 fun edit(x:HomePromoSlideConfig?){old=x;en=x?.titleEn.orEmpty();urT=x?.titleUr.orEmpty();sub=x?.subtitleEn.orEmpty();urS=x?.subtitleUr.orEmpty();btn=x?.buttonEn.orEmpty();urB=x?.buttonUr.orEmpty();image=x?.imageUri.orEmpty();sale=x?.isSale?:false;action=x?.action?:"PRODUCTS";dialog=true}
 LazyColumn(contentPadding=PaddingValues(16.dp),verticalArrangement=Arrangement.spacedBy(12.dp)){
 item{Text(t("Home sliders & demo controls","ہوم سلائیڈرز اور ڈیمو کنٹرول"),style=MaterialTheme.typography.headlineSmall,fontWeight=FontWeight.Bold);Text(t("Add, edit, replace, reorder or remove banners. Image-only slides are supported.","بینرز شامل، تبدیل یا حذف کریں۔ صرف تصویر والا سلائیڈر بھی ممکن ہے۔"),style=MaterialTheme.typography.bodySmall)}
 item{Card(shape=RoundedCornerShape(20.dp)){Column(Modifier.padding(14.dp)){Row(verticalAlignment=Alignment.CenterVertically){Text(t("Show Home slider","ہوم سلائیڈر دکھائیں"),Modifier.weight(1f));Switch(enabled,{enabled=it;HomeExperiencePrefs.put(c,HomeExperiencePrefs.SLIDER_ENABLED,it)})};HorizontalDivider();Row(verticalAlignment=Alignment.CenterVertically){Text(t("Demo sample products","ڈیمو نمونہ پروڈکٹس"),Modifier.weight(1f));Switch(demo,{demo=it;HomeExperiencePrefs.put(c,HomeExperiencePrefs.DEMO_ENABLED,it)})}}}}
 item{Row(verticalAlignment=Alignment.CenterVertically){Text(t("Slides: "+xs.size,"سلائیڈرز: "+xs.size),Modifier.weight(1f),style=MaterialTheme.typography.titleLarge);Button(onClick={edit(null)}){Icon(Icons.Default.Add,null);Text(t("Add","شامل کریں"))}}}
 items(xs,key={it.id}){x->Card(shape=RoundedCornerShape(18.dp)){Column(Modifier.padding(10.dp)){if(x.imageUri.isNotBlank())AsyncImage(x.imageUri,null,Modifier.fillMaxWidth().height(120.dp).clip(RoundedCornerShape(12.dp)),contentScale=ContentScale.Crop);Text(x.titleEn.ifBlank{t("Image-only banner","صرف تصویر والا بینر")},fontWeight=FontWeight.Bold);Text(if(x.isSale)"SALE" else x.action,style=MaterialTheme.typography.labelSmall);Row(verticalAlignment=Alignment.CenterVertically){IconButton(onClick={val i=xs.indexOfFirst{it.id==x.id};if(i>0)save(xs.toMutableList().also{val v=it.removeAt(i);it.add(i-1,v)})}){Icon(Icons.Default.KeyboardArrowUp,null)};IconButton(onClick={val i=xs.indexOfFirst{it.id==x.id};if(i>=0&&i<xs.lastIndex)save(xs.toMutableList().also{val v=it.removeAt(i);it.add(i+1,v)})}){Icon(Icons.Default.KeyboardArrowDown,null)};Spacer(Modifier.weight(1f));IconButton(onClick={edit(x)}){Icon(Icons.Default.Edit,null)};IconButton(onClick={save(xs.filterNot{it.id==x.id})}){Icon(Icons.Default.Delete,null,tint=MaterialTheme.colorScheme.error)}}}}}
 item{OutlinedButton(onClick={save(emptyList())},Modifier.fillMaxWidth()){Icon(Icons.Default.DeleteSweep,null);Text(t("Remove all slides","تمام سلائیڈرز حذف کریں"))}}
 }
 if(dialog)AlertDialog(onDismissRequest={dialog=false},title={Text(t("Add / edit slide","سلائیڈر شامل / تبدیل کریں") )},text={Column(Modifier.heightIn(max=560.dp),verticalArrangement=Arrangement.spacedBy(6.dp)){
 OutlinedButton(onClick={picker.launch(arrayOf("image/*"))},Modifier.fillMaxWidth()){Icon(Icons.Default.Image,null);Text(t("Upload / replace image","تصویر اپ لوڈ / تبدیل کریں"))}
 if(image.isNotBlank())AsyncImage(image,null,Modifier.fillMaxWidth().height(90.dp),contentScale=ContentScale.Crop)
 OutlinedTextField(en,{en=it},label={Text(t("Heading (optional)","عنوان (اختیاری)"))},modifier=Modifier.fillMaxWidth())
 OutlinedTextField(urT,{urT=it},label={Text(t("Urdu heading","اردو عنوان"))},modifier=Modifier.fillMaxWidth())
 OutlinedTextField(sub,{sub=it},label={Text(t("Description (optional)","تفصیل (اختیاری)"))},modifier=Modifier.fillMaxWidth())
 OutlinedTextField(urS,{urS=it},label={Text(t("Urdu description","اردو تفصیل"))},modifier=Modifier.fillMaxWidth())
 OutlinedTextField(btn,{btn=it},label={Text(t("Button name (optional)","بٹن کا نام (اختیاری)"))},modifier=Modifier.fillMaxWidth())
 OutlinedTextField(urB,{urB=it},label={Text(t("Urdu button","اردو بٹن"))},modifier=Modifier.fillMaxWidth())
 Row(verticalAlignment=Alignment.CenterVertically){Text(t("SALE banner","سیل بینر"),Modifier.weight(1f));Switch(sale,{sale=it})}
 var menu by remember{mutableStateOf(false)}
 ExposedDropdownMenuBox(expanded=menu,onExpandedChange={menu=it}){OutlinedTextField(value=action,onValueChange={},readOnly=true,label={Text(t("Button action","بٹن کا عمل"))},modifier=Modifier.menuAnchor().fillMaxWidth(),trailingIcon={ExposedDropdownMenuDefaults.TrailingIcon(menu)});ExposedDropdownMenu(expanded=menu,onDismissRequest={menu=false}){listOf("PRODUCTS","POS","SERVICES","KHATA").forEach{v->DropdownMenuItem(text={Text(v)},onClick={action=v;menu=false})}}}
 }},confirmButton={TextButton(onClick={val x=HomePromoSlideConfig(old?.id?:UUID.randomUUID().toString(),en,urT,sub,urS,btn,urB,image,sale,true,action);save(if(old==null)xs+x else xs.map{if(it.id==x.id)x else it});dialog=false}){Text(t("Save","محفوظ کریں"))}},dismissButton={TextButton(onClick={dialog=false}){Text(t("Cancel","منسوخ"))}})
}
''')

# polished carousel, optional copy and CTA, image only supported
p=b/"ui/components/HomePromoBannerSlider.kt"
W(p,r'''package com.example.ui.components
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.pager.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.layout.ContentScale
import coil.compose.AsyncImage
import com.example.data.model.AppMode
import kotlinx.coroutines.delay
@OptIn(ExperimentalFoundationApi::class)
@Composable fun HomePromoBannerSlider(appMode:AppMode,isUrdu:Boolean,onPosClick:()->Unit,onProductsClick:()->Unit,onServicesClick:()->Unit,onKhataClick:()->Unit,bannerImageUri:String=""){
 val c=LocalContext.current;val enabled=HomeExperiencePrefs.enabled(c,HomeExperiencePrefs.SLIDER_ENABLED,true);val xs=remember(appMode){HomeExperiencePrefs.slides(c,appMode==AppMode.PERSONAL_KHATA)}.filter{it.enabled};if(!enabled||xs.isEmpty())return
 val pager=rememberPagerState(pageCount={xs.size});LaunchedEffect(pager,xs.size){while(true){delay(5000);pager.animateScrollToPage((pager.currentPage+1)%xs.size)}}
 fun click(a:String):()->Unit=when(a){"POS"->onPosClick;"SERVICES"->onServicesClick;"KHATA"->onKhataClick;else->onProductsClick}
 Column(Modifier.fillMaxWidth().testTag("home_promo_banner_slider"),verticalArrangement=Arrangement.spacedBy(8.dp)){
 HorizontalPager(state=pager,modifier=Modifier.fillMaxWidth().height(190.dp),pageSpacing=10.dp){i->val x=xs[i];val img=x.imageUri.ifBlank{if(x.id=="sale")"" else bannerImageUri}
 Card(onClick=click(x.action),modifier=Modifier.fillMaxSize().testTag("home_promo_banner_$i"),shape=RoundedCornerShape(25.dp),colors=CardDefaults.cardColors(containerColor=Color(0xFF0B563B)),elevation=CardDefaults.cardElevation(5.dp)){
 Box(Modifier.fillMaxSize()){
 if(img.isNotBlank())AsyncImage(img,null,Modifier.fillMaxSize(),contentScale=ContentScale.Crop)else AsyncImage(when(i%3){0->com.example.R.drawable.af_demo_grocery;1->com.example.R.drawable.af_demo_fashion;else->com.example.R.drawable.af_demo_electronics},null,Modifier.fillMaxSize(),contentScale=ContentScale.Crop)
 val hasText=listOf(x.titleEn,x.titleUr,x.subtitleEn,x.subtitleUr,x.buttonEn,x.buttonUr).any{it.isNotBlank()};if(hasText)Box(Modifier.fillMaxSize().background(Brush.horizontalGradient(listOf(Color(0xD9002016),Color(0xA6002418),Color(0x12002418)))))
 if(x.isSale)Surface(Modifier.align(Alignment.TopEnd).padding(14.dp),shape=RoundedCornerShape(50),color=Color(0xFF16A34A)){Text(if(isUrdu)"سیل" else "SALE",Modifier.padding(horizontal=13.dp,vertical=6.dp),color=Color.White,fontWeight=FontWeight.ExtraBold)}
 if(hasText)Column(Modifier.align(Alignment.CenterStart).fillMaxWidth(.78f).padding(20.dp),verticalArrangement=Arrangement.spacedBy(6.dp)){
 val title=if(isUrdu)x.titleUr.ifBlank{x.titleEn}else x.titleEn.ifBlank{x.titleUr};if(title.isNotBlank())Text(title,color=Color.White,style=MaterialTheme.typography.titleLarge,fontWeight=FontWeight.ExtraBold,maxLines=2)
 val sub=if(isUrdu)x.subtitleUr.ifBlank{x.subtitleEn}else x.subtitleEn.ifBlank{x.subtitleUr};if(sub.isNotBlank())Text(sub,color=Color.White,style=MaterialTheme.typography.bodyMedium,maxLines=2)
 val btn=if(isUrdu)x.buttonUr.ifBlank{x.buttonEn}else x.buttonEn.ifBlank{x.buttonUr};if(btn.isNotBlank())Surface(shape=RoundedCornerShape(50),color=Color.White){Text(btn,Modifier.padding(horizontal=16.dp,vertical=9.dp),color=Color(0xFF075B3C),fontWeight=FontWeight.Bold)}
 }
 }}
 }
 Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.Center,verticalAlignment=Alignment.CenterVertically){repeat(xs.size){i->val active=pager.currentPage==i;Box(Modifier.padding(horizontal=3.dp).size(if(active)22.dp else 7.dp,7.dp).clip(CircleShape).background(if(active)MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outlineVariant).testTag("home_promo_dot_$i"))}}
 }
}
''')

# Product SALE toggle and badge.
p=b/"ui/dialogs/PremiumAddEditInventoryDialog.kt";s=R(p)
if "var isOnSale by remember" not in s:
 s=s.replace('  var productImageUri by remember { mutableStateOf(value("imageUri")) }','  var productImageUri by remember { mutableStateOf(value("imageUri")) }\n  var isOnSale by remember { mutableStateOf(value("isOnSale").toBoolean()) }')
 a='    BusinessField(price, label("Selling price ($currencySymbol)", "فروخت قیمت ($currencySymbol)"), true) { price = it }'
 s=rep(s,a,a+'\n    Row(Modifier.fillMaxWidth(), verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) { Text(label("Mark this product as SALE", "اس پروڈکٹ کو سیل پر لگائیں"), Modifier.weight(1f)); Switch(isOnSale, { isOnSale=it; change("isOnSale",it.toString()) }) }')
 W(p,s)
p=b/"ui/screens/BusinessHomeScreen.kt";s=R(p)
a='      if (photo != null || demoPhoto != null) AsyncImage(model = photo ?: demoPhoto, contentDescription = title, contentScale = ContentScale.Crop, modifier = Modifier.fillMaxWidth().height(if (detailed) 228.dp else 132.dp).clip(RoundedCornerShape(12.dp)))'
z='''      val isOnSale=details.optBoolean("isOnSale",false)||details.optBoolean("saleActive",false)||details.optBoolean("isDiscountActive",false)||details.optDouble("discountPercent",0.0)>0.0
      Box { if(photo!=null||demoPhoto!=null)AsyncImage(model=photo?:demoPhoto,contentDescription=title,contentScale=ContentScale.Crop,modifier=Modifier.fillMaxWidth().height(if(detailed)228.dp else 132.dp).clip(RoundedCornerShape(12.dp))) else Box(Modifier.fillMaxWidth().height(if(detailed)228.dp else 132.dp).clip(RoundedCornerShape(12.dp)).background(StoreMint),contentAlignment=Alignment.Center){Text(item.icon,fontSize=42.sp)}
      if(isOnSale)Surface(Modifier.align(Alignment.TopEnd).padding(7.dp),shape=RoundedCornerShape(50),color=Color(0xFF16A34A)){Text(if(urdu)"سیل" else "SALE",Modifier.padding(horizontal=10.dp,vertical=5.dp),color=Color.White,fontWeight=FontWeight.ExtraBold)} }'''
s=rep(s,a,z);fallback='''      else Box(Modifier.fillMaxWidth().height(if (detailed) 228.dp else 132.dp).clip(RoundedCornerShape(12.dp)).background(StoreMint), contentAlignment = Alignment.Center) {
        Text(item.icon, fontSize = 42.sp)
      }
''';s=s.replace(fallback,"",1);W(p,s)

# next version and tests
p=r/"app/build.gradle.kts";W(p,R(p).replace("versionCode = 55","versionCode = 56").replace('versionName = "4.6.9"','versionName = "4.7.0"'))
p=r/"app/src/test/java/com/example/HomeSliderManagerRegressionTest.kt";p.parent.mkdir(parents=True,exist_ok=True)
W(p,r'''package com.example
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
class HomeSliderManagerRegressionTest{
 @Test fun managerInMoreNotSettings(){val r=File("src/main/java/com/example");assertTrue(File(r,"ui/components/BottomNavBar.kt").readText().contains("nav_home_sliders"));assertTrue(File(r,"MainActivity.kt").readText().contains("HomeSliderManagerScreen(uiState)"));assertTrue(!File(r,"ui/screens/SettingsScreen.kt").readText().contains("Home Slider & Demo Controls"))}
 @Test fun imageOnlyAndCrud(){val r=File("src/main/java/com/example/ui");assertTrue(File(r,"components/HomeExperiencePrefs.kt").readText().contains("saveSlides"));assertTrue(File(r,"components/HomePromoBannerSlider.kt").readText().contains("hasText"));assertTrue(File(r,"screens/HomeSliderManagerScreen.kt").readText().contains("OpenDocument"))}
 @Test fun saleProductCanBeMarkedAndBadged(){val r=File("src/main/java/com/example/ui");assertTrue(File(r,"dialogs/PremiumAddEditInventoryDialog.kt").readText().contains("Mark this product as SALE"));assertTrue(File(r,"screens/BusinessHomeScreen.kt").readText().contains("isOnSale"))}
}
''')
print("Home slider manager patch applied.")
