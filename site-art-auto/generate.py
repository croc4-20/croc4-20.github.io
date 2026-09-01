#!/usr/bin/env python3
from pathlib import Path
import json
import html
import re
import unicodedata

ROOT = Path(__file__).resolve().parent
IMAGES = ROOT / "images"

CATEGORIES = {
    "peintures": {
        "label": "Peintures",
        "description": "Peintures et œuvres sur toile.",
    },
    "dessins": {
        "label": "Dessins",
        "description": "Dessins, encres, fusains et travaux sur papier.",
    },
    "sculptures": {
        "label": "Sculptures",
        "description": "Sculptures, volumes et travaux en trois dimensions.",
    },
    "aquarelles": {
        "label": "Aquarelles",
        "description": "Aquarelles et travaux à l’eau sur papier.",
    },
    "collages": {
        "label": "Collages",
        "description": "Collages et techniques mixtes.",
    },
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"}

def esc(value):
    return html.escape(str(value or ""), quote=True)

def slugify(value):
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "oeuvre"

def pretty_folder_name(name):
    name = re.sub(r"^\d+[-_ ]*", "", name)
    name = name.replace("_", " ").replace("-", " ")
    return " ".join(part.capitalize() for part in name.split())

def read_info(folder):
    path = folder / "info.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[ATTENTION] Impossible de lire {path}: {exc}")
        return {}

def find_images(folder):
    return sorted(
        [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS],
        key=lambda p: p.name.lower()
    )

def artwork_from_folder(category_slug, folder):
    info = read_info(folder)
    images = find_images(folder)
    title = info.get("titre") or pretty_folder_name(folder.name)

    cover_name = info.get("cover")
    if cover_name:
        cover = next((p for p in images if p.name == cover_name), None)
    else:
        cover = None
    cover = cover or (images[0] if images else None)

    return {
        "category": category_slug,
        "folder": folder,
        "folder_name": folder.name,
        "slug": slugify(folder.name),
        "prix": info.get("prix"),
        "devise": info.get("devise", "EUR"),
        "title": title,
        "year": info.get("annee", ""),
        "technique": info.get("technique", ""),
        "dimensions": info.get("dimensions", ""),
        "description": info.get("description", ""),
        "disponibilite": info.get("disponibilite", ""),
        "images": images,
        "cover": cover,
    }

def scan_category(category_slug):
    category_dir = IMAGES / category_slug
    category_dir.mkdir(parents=True, exist_ok=True)
    works = []
    for folder in sorted(category_dir.iterdir(), key=lambda p: p.name.lower()):
        if folder.is_dir() and not folder.name.startswith("."):
            works.append(artwork_from_folder(category_slug, folder))
    return works

def nav(current=None):
    links = ['<a href="index.html">ACCUEIL</a>']
    for slug, cfg in CATEGORIES.items():
        attr = ' aria-current="page"' if current == slug else ""
        links.append(f'<a href="{slug}.html"{attr}>{esc(cfg["label"]).upper()}</a>')
    return "<nav>" + "\n".join(links) + "</nav>"

def sidebar():
    return """
<aside class="sidebar">
  <div>
    <div class="logo">VÉRONIQUE<br>COLLET</div>
    <div class="logo-line"></div>
    <div class="sidebar-desc">
      Artiste<br>
      peinture, sculpture,<br>
      dessin, aquarelle
    </div>
    <div class="mark">A</div>
  </div>
  <div class="socials">IG<br>BE<br>FB</div>
</aside>
"""

def footer():
    return """
<footer id="contact">
  <div>
    <h3>Véronique Collet</h3>
    <p>© 2026<br>Tous droits réservés<br>Mentions légales</p>
  </div>

  <div>
    <h3>Lettre d'atelier</h3>
    <p>Recevez les nouvelles,<br>expositions et œuvres inédites.</p>
    <div class="newsletter">
      <input type="email" placeholder="votre e-mail">
      <button type="button">→</button>
    </div>
  </div>

  <div>
    <h3>Contact</h3>
    <p>
      atelier@example.art<br>
      Instagram<br>
      Behance
    </p>
  </div>
</footer>
"""

def page(title, body, current=None):
    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} — Véronique Collet</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
<div class="site">
  {sidebar()}
  <main class="content">
    <header>{nav(current)}</header>
    {body}
    {footer()}
  </main>
  <aside class="rightbar">ATELIER OUVERT SUR RENDEZ-VOUS</aside>
</div>
</body>
</html>
"""

def work_filename(work):
    return f"oeuvre-{work['category']}-{work['slug']}.html"

def image_src(work, image):
    return f"images/{work['category']}/{work['folder_name']}/{image.name}"

def artwork_card(work):
    if work["cover"]:
        visual = f'<img src="{esc(image_src(work, work["cover"]))}" alt="{esc(work["title"])}" loading="lazy">'
    else:
        visual = '<div class="hero-placeholder">Ajoutez au moins une photo dans ce dossier.</div>'

    count = len(work["images"])
    badge = f'<span class="photo-count">{count} PHOTO{"S" if count > 1 else ""}</span>' if count else ""

    metadata = " — ".join(x for x in [str(work["year"]) if work["year"] else "", work["technique"]] if x)
    dimensions = work["dimensions"]

    return f"""
<figure class="artwork-card">
  <a class="artwork-link" href="{esc(work_filename(work))}">
    <div class="artwork-image-wrap">
      {visual}
      {badge}
    </div>
    <figcaption>
      <div class="artwork-title">{esc(work["title"])}</div>
      <div class="artwork-meta">{esc(metadata)}</div>
      {'<div class="artwork-meta">' + esc(dimensions) + '</div>' if dimensions else ''}
    </figcaption>
  </a>
</figure>
"""

# def category_page(slug, works):
#     cfg = CATEGORIES[slug]
#     cards = "\n".join(artwork_card(w) for w in works)

#     if not cards:
#         cards = """
# <div class="empty-gallery">
#   Aucun sous-dossier d'œuvre pour le moment.<br><br>
#   Créez par exemple :<br>
#   images/peintures/mon-oeuvre/
# </div>
# """

#     body = f"""
# <section class="category-head">
#   <div class="eyebrow">Collection</div>
#   <h1>{esc(cfg["label"])}</h1>
#   <p>{esc(cfg["description"])} — {len(works)} œuvre{"s" if len(works) != 1 else ""}.</p>
# </section>

# <section class="artworks-grid">
#   {cards}
# </section>
# """
#     return page(cfg["label"], body, current=slug)
def category_page(slug, works):
    cfg = CATEGORIES[slug]

    if slug == "peintures":

        recent = []
        archive = []

        for work in works:
            try:
                year = int(work["year"])
            except (TypeError, ValueError):
                year = 0

            if year >= 2020:
                recent.append(work)
            else:
                archive.append(work)

        recent.sort(
            key=lambda w: int(w["year"]) if str(w["year"]).isdigit() else 0,
            reverse=True
        )

        archive.sort(
            key=lambda w: int(w["year"]) if str(w["year"]).isdigit() else 0,
            reverse=True
        )

        recent_cards = "\n".join(
            artwork_card(w) for w in recent
        )

        archive_cards = "\n".join(
            artwork_card(w) for w in archive
        )

        body = f"""
<section class="category-head">
  <div class="eyebrow">Collection</div>
  <h1>{esc(cfg["label"])}</h1>
  <p>{len(works)} œuvre{"s" if len(works) != 1 else ""}.</p>
</section>

<section class="gallery-period">
  <div class="period-head">
    <h2>Œuvres récentes</h2>
    <span>2020 — aujourd’hui</span>
  </div>

  <div class="artworks-grid">
    {recent_cards}
  </div>
</section>

<section class="gallery-period gallery-archive">
  <div class="period-head">
    <h2>Archives</h2>
    <span>Avant 2020</span>
  </div>

  <div class="artworks-grid">
    {archive_cards}
  </div>
</section>
"""

        return page(
            cfg["label"],
            body,
            current=slug
        )

    # comportement normal pour dessins/sculptures/etc.
    cards = "\n".join(
        artwork_card(w) for w in works
    )

    body = f"""
<section class="category-head">
  <div class="eyebrow">Collection</div>
  <h1>{esc(cfg["label"])}</h1>
  <p>{esc(cfg["description"])} — {len(works)} œuvre{"s" if len(works) != 1 else ""}.</p>
</section>

<section class="artworks-grid">
  {cards}
</section>
"""

    return page(
        cfg["label"],
        body,
        current=slug
    )

def info_row(term, value):
    if not value:
        return ""
    return f"<dt>{esc(term)}</dt><dd>{esc(value)}</dd>"

def work_page(work):
    cfg = CATEGORIES[work["category"]]
    images = work["images"]

    if images:
        first_src = image_src(work, images[0])
        main = f"""
<button class="main-photo-button" type="button" id="main-photo-button">
  <img class="main-photo" id="main-photo" src="{esc(first_src)}" alt="{esc(work["title"])}">
</button>
"""
        thumbs = "\n".join(
            f"""<button class="thumbnail" type="button"
                     data-src="{esc(image_src(work, img))}"
                     aria-current="{'true' if i == 0 else 'false'}">
                   <img src="{esc(image_src(work, img))}" alt="{esc(work["title"])} — vue {i+1}" loading="lazy">
                 </button>"""
            for i, img in enumerate(images)
        )
        thumbs_html = f'<div class="thumbnails">{thumbs}</div>' if len(images) > 1 else ""
        image_array = json.dumps([image_src(work, img) for img in images], ensure_ascii=False)
    else:
        main = '<div class="hero-placeholder">Aucune photo dans ce dossier.</div>'
        thumbs_html = ""
        image_array = "[]"

    summary = " · ".join(
        str(x) for x in [work["year"], work["technique"], work["dimensions"]] if x
    )

    body = f"""
<article class="work-page">
  <header class="work-header">
    <a class="work-back" href="{esc(work["category"])}.html">← {esc(cfg["label"])}</a>
    <h1>{esc(work["title"])}</h1>
    <div class="work-summary">{esc(summary)}</div>
  </header>

  <div class="work-layout">
    <section class="work-gallery">
      {main}
      {thumbs_html}
    </section>

    <aside class="work-info">
      <h2>Informations</h2>
      <dl>
        {info_row("Année", work["year"])}
        {info_row("Technique", work["technique"])}
        {info_row("Dimensions", work["dimensions"])}
        {info_row("Disponibilité", work["disponibilite"])}
        {info_row("Prix", format_price(work["prix"], work["devise"]))}
        {info_row("Photographies", len(images) if images else "")}
      </dl>
      {'<div class="work-description">' + esc(work["description"]) + '</div>' if work["description"] else ''}
    </aside>
  </div>
</article>

<div class="lightbox" id="lightbox" aria-hidden="true">
  <button class="lightbox-close" type="button" aria-label="Fermer">×</button>
  <button class="lightbox-nav lightbox-prev" type="button" aria-label="Photo précédente">‹</button>
  <img id="lightbox-image" alt="">
  <button class="lightbox-nav lightbox-next" type="button" aria-label="Photo suivante">›</button>
</div>

<script>
(() => {{
  const images = {image_array};
  if (!images.length) return;

  const main = document.getElementById('main-photo');
  const mainButton = document.getElementById('main-photo-button');
  const thumbs = [...document.querySelectorAll('.thumbnail')];
  const lightbox = document.getElementById('lightbox');
  const lightboxImage = document.getElementById('lightbox-image');
  const close = lightbox.querySelector('.lightbox-close');
  const prev = lightbox.querySelector('.lightbox-prev');
  const next = lightbox.querySelector('.lightbox-next');

  let currentIndex = 0;

  function setCurrent(index) {{
    currentIndex = (index + images.length) % images.length;
    if (main) main.src = images[currentIndex];
    thumbs.forEach((thumb, i) => {{
      thumb.setAttribute('aria-current', i === currentIndex ? 'true' : 'false');
    }});
  }}

  thumbs.forEach((thumb, index) => {{
    thumb.addEventListener('click', () => setCurrent(index));
  }});

  function openLightbox() {{
    lightboxImage.src = images[currentIndex];
    lightbox.classList.add('open');
    lightbox.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }}

  function closeLightbox() {{
    lightbox.classList.remove('open');
    lightbox.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }}

  function lightboxMove(delta) {{
    setCurrent(currentIndex + delta);
    lightboxImage.src = images[currentIndex];
  }}

  if (mainButton) mainButton.addEventListener('click', openLightbox);
  close.addEventListener('click', closeLightbox);
  prev.addEventListener('click', () => lightboxMove(-1));
  next.addEventListener('click', () => lightboxMove(1));

  lightbox.addEventListener('click', (event) => {{
    if (event.target === lightbox) closeLightbox();
  }});

  document.addEventListener('keydown', (event) => {{
    if (!lightbox.classList.contains('open')) return;
    if (event.key === 'Escape') closeLightbox();
    if (event.key === 'ArrowLeft') lightboxMove(-1);
    if (event.key === 'ArrowRight') lightboxMove(1);
  }});
}})();
</script>
"""
    return page(work["title"], body, current=work["category"])

def format_price(price, currency="EUR"):

    if price is None or price == "":
        return ""

    if currency == "EUR":
        return f"{price:,} €".replace(",", " ")

    return f"{price:,} {currency}".replace(",", " ")

def home_page(all_works):
    latest = []
    for slug in CATEGORIES:
        latest.extend(all_works.get(slug, []))
    latest = latest[:5]

    if latest:
        preview = "".join(
            f"""<a class="work" href="{esc(work_filename(w))}">
                  <img src="{esc(image_src(w, w["cover"]))}" alt="{esc(w["title"])}">
                </a>"""
            if w["cover"] else
            f'<a class="work" href="{esc(work_filename(w))}"><div class="hero-placeholder">{esc(w["title"])}</div></a>'
            for w in latest
        )
    else:
        preview = '<div class="hero-placeholder">Les œuvres apparaîtront ici après avoir ajouté leurs dossiers puis lancé generate.py.</div>'

    category_links = "".join(
        f'<a href="{slug}.html"><span>{esc(cfg["label"])}</span><span>→</span></a>'
        for slug, cfg in CATEGORIES.items()
    )

    body = f"""
<section class="hero" id="travaux">
  <div class="hero-copy">
    <h1>L'ART<br>COMME<br>FRICTION</h1>
    <div class="dash"></div>
    <a class="hero-link" href="#categories">Explorer le travail <span>→</span></a>
  </div>

  <div class="hero-art">
    <div class="hero-placeholder">
      Cet emplacement peut recevoir plus tard une vraie photographie principale.
    </div>
  </div>
</section>

<section class="manifesto-grid" id="infos">
  <div class="manifesto">
    <div class="manifesto-title">Manifeste</div>
    <div>
      <div class="quote">“</div>
      <blockquote>
        Texte de présentation de la démarche artistique à compléter.
      </blockquote>
      <div class="signature">— V. COLLET</div>
    </div>
  </div>

  <div class="exhibitions">
    <div class="label">Explorer</div>
    <h2>ŒUVRES<br>& TECHNIQUES</h2>
    <p>Peinture, dessin, sculpture, aquarelle et collage.</p>
  </div>
</section>

<section class="category-menu" id="categories">
  {category_links}
</section>

<section class="gallery">
  {preview}
</section>
"""
    return page("Accueil", body)

def main():
    all_works = {}

    # Scan folders and generate all category + artwork pages.
    for slug in CATEGORIES:
        works = scan_category(slug)
        all_works[slug] = works

        (ROOT / f"{slug}.html").write_text(
            category_page(slug, works),
            encoding="utf-8"
        )

        for work in works:
            (ROOT / work_filename(work)).write_text(
                work_page(work),
                encoding="utf-8"
            )

    (ROOT / "index.html").write_text(home_page(all_works), encoding="utf-8")

    # Remove obsolete generated artwork pages so renaming/deleting folders is reflected.
    expected = {
        work_filename(work)
        for works in all_works.values()
        for work in works
    }
    for file in ROOT.glob("oeuvre-*.html"):
        if file.name not in expected:
            file.unlink()

    total = sum(len(v) for v in all_works.values())
    print(f"Site généré : {total} œuvre(s).")
    for slug, works in all_works.items():
        print(f"  - {CATEGORIES[slug]['label']}: {len(works)}")

if __name__ == "__main__":
    main()
