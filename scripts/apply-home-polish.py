#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1])
p = root / "app/src/main/java/com/example/ui/components/HomePromoBannerSlider.kt"
s = p.read_text(encoding="utf-8")
s = s.replace("import androidx.compose.foundation.background\n",
              "import androidx.compose.foundation.background\nimport androidx.compose.foundation.horizontalScroll\nimport androidx.compose.foundation.rememberScrollState\n", 1)
s = s.replace(
"""          Box(
            Modifier.align(Alignment.CenterEnd).size(150.dp)""",
"""          Box(Modifier.fillMaxSize().background(
            Brush.horizontalGradient(listOf(Color(0xD9002418), Color(0x99002418), Color(0x16002418)))))
          Box(
            Modifier.align(Alignment.CenterEnd).size(150.dp)""", 1)
s = s.replace("Column(Modifier.fillMaxWidth(0.76f), verticalArrangement = Arrangement.spacedBy(6.dp)) {",
              "Column(Modifier.fillMaxWidth(0.66f), verticalArrangement = Arrangement.spacedBy(5.dp)) {", 1)
s = s.replace("style = MaterialTheme.typography.titleLarge, color = Color.White,",
              "style = MaterialTheme.typography.titleMedium, color = Color.White,", 1)
anchor = """    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center,
      verticalAlignment = Alignment.CenterVertically) {
      repeat(slides.size) { index ->
        val selected = pagerState.currentPage == index
        Box(Modifier.padding(horizontal = 4.dp).size(width = if (selected) 22.dp else 7.dp, height = 7.dp)
          .clip(CircleShape).background(if (selected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outlineVariant)
          .testTag("home_promo_dot_$index"))
      }
    }
  }
}"""
addition = """    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center,
      verticalAlignment = Alignment.CenterVertically) {
      repeat(slides.size) { index ->
        val selected = pagerState.currentPage == index
        Box(Modifier.padding(horizontal = 4.dp).size(width = if (selected) 22.dp else 7.dp, height = 7.dp)
          .clip(CircleShape).background(if (selected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outlineVariant)
          .testTag("home_promo_dot_$index"))
      }
    }
    Spacer(Modifier.height(4.dp))
    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically,
      horizontalArrangement = Arrangement.SpaceBetween) {
      Text(if (isUrdu) "🔥 آج کی خصوصی ڈیلز" else "🔥 Today's Deals",
        style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
      TextButton(onClick = onProductsClick) { Text(if (isUrdu) "سب دیکھیں" else "See All") }
    }
    Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
      horizontalArrangement = Arrangement.spacedBy(10.dp)) {
      val demoDeals = listOf(
        Triple(com.example.R.drawable.af_demo_tomatoes, if (isUrdu) "ٹماٹر" else "Tomatoes", "PKR 112.50"),
        Triple(com.example.R.drawable.af_demo_onions, if (isUrdu) "پیاز" else "Onions", "PKR 99.50"),
        Triple(com.example.R.drawable.af_demo_chicken, if (isUrdu) "چکن" else "Chicken mince", "PKR 424.50"),
        Triple(com.example.R.drawable.af_demo_bananas, if (isUrdu) "کیلے" else "Bananas", "PKR 119.50")
      )
      demoDeals.forEach { (photo, title, price) ->
        Card(Modifier.width(118.dp), shape = RoundedCornerShape(16.dp),
          colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
          Column(Modifier.padding(8.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            AsyncImage(model = photo, contentDescription = title, contentScale = ContentScale.Crop,
              modifier = Modifier.fillMaxWidth().height(82.dp).clip(RoundedCornerShape(11.dp)))
            Text(title, style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.SemiBold,
              maxLines = 1, overflow = TextOverflow.Ellipsis)
            Text(price, style = MaterialTheme.typography.labelMedium,
              color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
          }
        }
      }
    }
    OutlinedButton(onClick = onServicesClick, modifier = Modifier.fillMaxWidth()) {
      Icon(Icons.Default.Handyman, null)
      Spacer(Modifier.width(8.dp))
      Text(if (isUrdu) "تمام سروسز دیکھیں" else "Explore all Services")
    }
  }
}"""
if anchor not in s:
    if "Today's Deals" not in s:
        raise SystemExit("Home slider anchor changed; refusing unsafe patch")
else:
    s = s.replace(anchor, addition, 1)
p.write_text(s, encoding="utf-8")
print("Home slider text constrained with contrast scrim; grocery deal cards and Services shortcut added.")
