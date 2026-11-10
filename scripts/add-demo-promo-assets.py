#!/usr/bin/env python3
"""Download bundled demo photography and wire it into the home promo slider."""
from pathlib import Path
import sys
import urllib.request

root = Path(sys.argv[1])
res = root / "app/src/main/res/drawable-nodpi"
res.mkdir(parents=True, exist_ok=True)

images = {
    "af_demo_grocery.jpg": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=1400&h=700&fit=crop&auto=format&q=88",
    "af_demo_fashion.jpg": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=1400&h=700&fit=crop&auto=format&q=88",
    "af_demo_electronics.jpg": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1400&h=700&fit=crop&auto=format&q=82",
    "af_demo_tomatoes.jpg": "https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=720&h=560&fit=crop&auto=format&q=82",
    "af_demo_onions.jpg": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=720&h=560&fit=crop&auto=format&q=82",
    "af_demo_chicken.jpg": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=720&h=560&fit=crop&auto=format&q=82",
    "af_demo_bananas.jpg": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=720&h=560&fit=crop&fm=jpg&q=82",
    "af_demo_bakery.jpg": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=720&h=560&fit=crop&fm=jpg&q=80",
    "af_demo_dryfruits.jpg": "https://images.unsplash.com/photo-1608797178974-15b35a64ede9?w=720&h=560&fit=crop&fm=jpg&q=80",
    "af_demo_spices.jpg": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=720&h=560&fit=crop&fm=jpg&q=80",
    "af_demo_snacks.jpg": "https://images.unsplash.com/photo-1621939514649-280e2aa2f8a8?w=1200&h=900&fit=crop&fm=jpg&q=88",
    "af_demo_personalcare.jpg": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=1200&h=900&fit=crop&fm=jpg&q=88",
    "af_demo_household.jpg": "https://images.unsplash.com/photo-1585421514284-efb74c2b69ba?w=1200&h=900&fit=crop&fm=jpg&q=88",
    "af_demo_babycare.jpg": "https://images.unsplash.com/photo-1604917877934-07d8d248d396?w=1200&h=900&fit=crop&fm=jpg&q=88",
    "af_demo_kitchen.jpg": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=1200&h=900&fit=crop&fm=jpg&q=88",
    "af_demo_stationery.jpg": "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=1200&h=900&fit=crop&fm=jpg&q=88",
}
for name, url in images.items():
    target = res / name
    request = urllib.request.Request(url, headers={"User-Agent": "ArshadFinance-Android-Build/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        data = response.read()
    if len(data) < 8_000 or not data.startswith(bytes.fromhex("ffd8ff")):
        raise SystemExit(f"Downloaded demo asset is invalid: {name} ({len(data)} bytes)")
    target.write_bytes(data)
    print(f"Bundled {name}: {len(data)} bytes")

component = root / "app/src/main/java/com/example/ui/components/HomePromoBannerSlider.kt"
source = component.read_text(encoding="utf-8")
old = '''          if (bannerImageUri.isNotBlank()) {
            AsyncImage(model = bannerImageUri, contentDescription = null, contentScale = ContentScale.Crop,
              alpha = 0.58f, modifier = Modifier.fillMaxSize())
          }'''
new = '''          AsyncImage(
            model = bannerImageUri.takeIf { it.isNotBlank() } ?: when (page) {
              0 -> com.example.R.drawable.af_demo_grocery
              1 -> com.example.R.drawable.af_demo_fashion
              else -> com.example.R.drawable.af_demo_electronics
            },
            contentDescription = null,
            contentScale = ContentScale.Crop,
            alpha = 0.58f,
            modifier = Modifier.fillMaxSize()
          )'''
if old not in source:
    if "R.drawable.af_demo_grocery" not in source:
        raise SystemExit("Home promo image insertion anchor not found")
else:
    component.write_text(source.replace(old, new, 1), encoding="utf-8")
print("Home slider now uses bundled HD demo photography, while owner-uploaded banner overrides it.")

# Final home polish: improve contrast, prevent headline/icon collision, and show real grocery deal cards.
component_source = component.read_text(encoding="utf-8")
component_source = component_source.replace(
    "import androidx.compose.foundation.background\n",
    "import androidx.compose.foundation.background\nimport androidx.compose.foundation.horizontalScroll\nimport androidx.compose.foundation.rememberScrollState\n", 1
)
component_source = component_source.replace(
    """          Box(
            Modifier.align(Alignment.CenterEnd).size(150.dp)""",
    """          Box(Modifier.fillMaxSize().background(
            Brush.horizontalGradient(listOf(Color(0xD9002418), Color(0x99002418), Color(0x16002418)))))
          Box(
            Modifier.align(Alignment.CenterEnd).size(150.dp)""", 1
)
component_source = component_source.replace(
    "Column(Modifier.fillMaxWidth(0.76f), verticalArrangement = Arrangement.spacedBy(6.dp)) {",
    "Column(Modifier.fillMaxWidth(0.66f), verticalArrangement = Arrangement.spacedBy(5.dp)) {", 1
)
component_source = component_source.replace(
    "style = MaterialTheme.typography.titleLarge, color = Color.White,",
    "style = MaterialTheme.typography.titleMedium, color = Color.White,", 1
)
dots_anchor = """    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center,
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
deals_section = """    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center,
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
if "Today's Deals" not in component_source:
    if dots_anchor not in component_source:
        raise SystemExit("Home promo dots anchor missing; refusing to alter layout")
    component_source = component_source.replace(dots_anchor, deals_section, 1)
component.write_text(component_source, encoding="utf-8")
