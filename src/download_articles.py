
import requests
import time
from pathlib import Path

articles = {
    "Eugene Wigner": "eugene_wigner.txt",
    "Charles H. Townes": "charles_h_townes.txt",
    "Richard Feynman": "richard_feynman.txt",
    "Erwin Schrödinger": "erwin_schrodinger.txt",
    "Murray Gell-Mann": "murray_gell_mann.txt"
}

url = "https://en.wikipedia.org/w/api.php"

headers = {
    "User-Agent": "KRR-Assignment-Student/1.0 (contact: p240009@pwr.nu.edu.pk)"
}

output_folder = Path("data/raw")
output_folder.mkdir(parents=True, exist_ok=True)

for title, filename in articles.items():

    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": 1,
        "redirects": 1,
        "titles": title,
        "format": "json"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))

    if "missing" in page:
        print("Article not found:", title)
        continue

    text = page.get("extract", "")

    if not text.strip():
        print("Empty article:", title)
        continue

    file_path = output_folder / filename
    file_path.write_text(text, encoding="utf-8")

    print("Downloaded:", title)

    time.sleep(1)

print("\nAll downloads completed!")
