#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1])
component = root / "app/src/main/java/com/example/ui/components/HomePromoBannerSlider.kt"
component.parent.mkdir(parents=True, exist_ok=True)
source = r'''package com.example.ui.components

import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.example.data.model.AppMode
import kotlinx.coroutines.delay

private data class PromoSlide(
  val titleEn: String,
  val titleUr: String,
  val subtitleEn: String,
  val subtitleUr: String,
  val ctaEn: String,
  val ctaUr: String,
  val icon: ImageVector,
  val colors: List<Color>,
  val action: () -> Unit
)

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun HomePromoBannerSlider(
  appMode: AppMode,
  isUrdu: Boolean,
  onPosClick: () -> Unit,
  onProductsClick: () -> Unit,
  onServicesClick: () -> Unit,
  onKhataClick: () -> Unit
) {
  val slides = remember(appMode, isUrdu, onPosClick, onProductsClick, onServicesClick, onKhataClick) {
    if (appMode == AppMode.PERSONAL_KHATA) listOf(
      PromoSlide("Your money, clearly tracked", "اپنے پیسوں کا مکمل حساب",
        "Keep income, expenses and budgets together", "آمدن، اخراجات اور بجٹ ایک جگہ",
        "View khata", "کھاتہ دیکھیں", Icons.Default.AccountBalanceWallet,
        listOf(Color(0xFF123A80), Color(0xFF2563EB)), onKhataClick),
      PromoSlide("Plan bills ahead", "بلوں کی پہلے سے منصوبہ بندی",
        "Stay ready for upcoming payments", "آنے والی ادائیگیوں کے لیے تیار رہیں",
        "Open budgets", "بجٹ کھولیں", Icons.Default.CalendarMonth,
        listOf(Color(0xFF6D28D9), Color(0xFF9333EA)), onKhataClick),
      PromoSlide("Simple daily insights", "روزانہ حساب کی آسان جھلک",
        "See where your money goes", "دیکھیں آپ کا پیسہ کہاں خرچ ہوتا ہے",
        "View reports", "رپورٹس دیکھیں", Icons.Default.Insights,
        listOf(Color(0xFF047857), Color(0xFF10B981)), onKhataClick)
    ) else listOf(
      PromoSlide("Sell smarter, every day", "ہر روز بہتر انداز میں فروخت",
        "Fast checkout, clear bills and fewer mistakes", "تیز فروخت، واضح بل اور کم غلطیاں",
        "Start a sale", "فروخت شروع کریں", Icons.Default.ShoppingCart,
        listOf(Color(0xFF063B82), Color(0xFF1479D2)), onPosClick),
      PromoSlide("Your products, in one place", "آپ کی تمام مصنوعات ایک جگہ",
        "Search stock, prices and low-stock items", "اسٹاک، قیمتیں اور کم مقدار والی اشیاء تلاش کریں",
        "Explore products", "مصنوعات دیکھیں", Icons.Default.Inventory2,
        listOf(Color(0xFF075B46), Color(0xFF12A878)), onProductsClick),
      PromoSlide("Grow with services & khata", "سروسز اور کھاتے کے ساتھ ترقی",
        "Manage jobs, customers and payments", "کام، گاہک اور ادائیگیاں منظم کریں",
        "Explore services", "سروسز دیکھیں", Icons.Default.Handyman,
        listOf(Color(0xFF6B2B91), Color(0xFFB044A6)), onServicesClick)
    )
  }
  val pagerState = rememberPagerState(pageCount = { slides.size })
  LaunchedEffect(pagerState, slides.size) {
    while (true) {
      delay(5000)
      pagerState.animateScrollToPage((pagerState.currentPage + 1) % slides.size)
    }
  }

  Column(Modifier.fillMaxWidth().testTag("home_promo_banner_slider"),
    verticalArrangement = Arrangement.spacedBy(10.dp)) {
    HorizontalPager(
      state = pagerState,
      modifier = Modifier.fillMaxWidth().height(178.dp),
      pageSpacing = 12.dp
    ) { page ->
      val slide = slides[page]
      Card(
        onClick = slide.action,
        modifier = Modifier.fillMaxSize().testTag("home_promo_banner_$page"),
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(containerColor = slide.colors.first())
      ) {
        Box(
          Modifier.fillMaxSize()
            .background(Brush.linearGradient(slide.colors))
            .padding(horizontal = 20.dp, vertical = 16.dp)
        ) {
          Box(
            Modifier.align(Alignment.CenterEnd).size(150.dp)
              .offset(x = 22.dp, y = 18.dp)
              .clip(CircleShape).background(Color.White.copy(alpha = 0.09f))
          )
          Icon(slide.icon, null,
            modifier = Modifier.align(Alignment.CenterEnd).padding(end = 14.dp).size(76.dp),
            tint = Color.White.copy(alpha = 0.25f))
          Column(Modifier.fillMaxWidth(0.76f), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(if (isUrdu) "ارشاد فنانس • اسمارٹ کاروبار" else "ARSHAD FINANCE • SMART BUSINESS",
              style = MaterialTheme.typography.labelSmall, color = Color.White.copy(alpha = 0.82f),
              fontWeight = FontWeight.Bold, maxLines = 1)
            Text(if (isUrdu) slide.titleUr else slide.titleEn,
              style = MaterialTheme.typography.titleLarge, color = Color.White,
              fontWeight = FontWeight.ExtraBold, maxLines = 2, overflow = TextOverflow.Ellipsis)
            Text(if (isUrdu) slide.subtitleUr else slide.subtitleEn,
              style = MaterialTheme.typography.bodySmall, color = Color.White.copy(alpha = 0.9f),
              maxLines = 2, overflow = TextOverflow.Ellipsis)
            Spacer(Modifier.height(2.dp))
            Surface(shape = RoundedCornerShape(50), color = Color.White) {
              Text(if (isUrdu) slide.ctaUr else slide.ctaEn,
                modifier = Modifier.padding(horizontal = 14.dp, vertical = 7.dp),
                color = slide.colors.first(), style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.Bold)
            }
          }
        }
      }
    }
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center,
      verticalAlignment = Alignment.CenterVertically) {
      repeat(slides.size) { index ->
        val selected = pagerState.currentPage == index
        Box(Modifier.padding(horizontal = 4.dp).size(width = if (selected) 22.dp else 7.dp, height = 7.dp)
          .clip(CircleShape).background(if (selected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outlineVariant)
          .testTag("home_promo_dot_$index"))
      }
    }
  }
}
'''
if component.exists():
    old = component.read_text(encoding="utf-8")
    if old != source:
        component.write_text(source, encoding="utf-8")
else:
    component.write_text(source, encoding="utf-8")

home = root / "app/src/main/java/com/example/ui/screens/BusinessHomeScreen.kt"
h = home.read_text(encoding="utf-8")
if "import com.example.ui.components.HomePromoBannerSlider" not in h:
    h = h.replace("import com.example.ui.components.SubscriptionAccessCard\n",
                  "import com.example.ui.components.SubscriptionAccessCard\nimport com.example.ui.components.HomePromoBannerSlider\n", 1)
marker = '''    item {
      SubscriptionAccessCard(
'''
if "HomePromoBannerSlider(" not in h:
    if marker not in h:
        raise SystemExit("BusinessHomeScreen subscription card insertion anchor not found")
    banner = '''    item {
      HomePromoBannerSlider(
        appMode = uiState.appMode,
        isUrdu = urdu,
        onPosClick = onPosClick,
        onProductsClick = onStockClick,
        onServicesClick = onServicesClick,
        onKhataClick = onBillingClick
      )
    }
'''
    h = h.replace(marker, banner + marker, 1)
home.write_text(h, encoding="utf-8")

test = root / "app/src/test/java/com/example/HomePromoBannerTest.kt"
test.write_text(r'''package com.example

import androidx.compose.ui.test.assertExists
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.onNodeWithText
import com.example.data.model.AppMode
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import com.example.ui.components.HomePromoBannerSlider
import com.example.ui.theme.MyApplicationTheme
import org.junit.Rule
import org.junit.Test

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class HomePromoBannerTest {
  @get:Rule val compose = createComposeRule()

  @Test fun businessHomeShowsSwipeablePromoSlider() {
    compose.setContent {
      MyApplicationTheme {
        HomePromoBannerSlider(AppMode.BUSINESS_RETAIL, false, {}, {}, {}, {})
      }
    }
    compose.onNodeWithTag("home_promo_banner_slider").assertExists()
    compose.onNodeWithTag("home_promo_banner_0").assertExists()
    compose.onNodeWithText("Sell smarter, every day").assertExists()
  }

  @Test fun personalModeShowsPersonalFinancePromos() {
    compose.setContent {
      MyApplicationTheme {
        HomePromoBannerSlider(AppMode.PERSONAL_KHATA, true, {}, {}, {}, {})
      }
    }
    compose.onNodeWithTag("home_promo_banner_slider").assertExists()
    compose.onNodeWithText("اپنے پیسوں کا مکمل حساب").assertExists()
  }
}
''', encoding="utf-8")
print("Added auto-advancing, swipeable bilingual home promo slider and two UI tests.")
