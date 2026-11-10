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
    "af_demo_bananas.jpg": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=720&h=560&fit=crop&auto=format&q=82",
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
