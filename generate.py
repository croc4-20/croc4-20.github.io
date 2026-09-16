from pathlib import Path
import json
import html
import re
import unicodedata


# ============================================================
# CONFIGURATION
# ============================================================

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
    "atelier": {
        "label": "Atelier",
        "description": "Photos d'atelier.",
    },
}
HOME_SECTIONS = {
    "peintures-recentes": {
        "label": "Peintures récentes",
        "href": "peinturerec.html",
    },
    "peintures-anciennes": {
        "label": "Peintures anciennes",
        "href": "peintureanc.html",
    },
    "dessins": {
        "label": "Dessins",
        "href": "dessins.html",
    },
    "sculptures": {
        "label": "Sculptures",
        "href": "sculptures.html",
    },
    "aquarelles": {
        "label": "Aquarelles",
        "href": "aquarelles.html",
    },
    "atelier": {
        "label": "Atelier",
        "href": "atelier.html",
    },
}
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".avif",
    ".gif",
}


# ============================================================
# OUTILS
# ============================================================
def split_paintings(works):
    recent = []
    old = []

    for work in works:
        try:
            year = int(work["year"])
        except (TypeError, ValueError):
            year = 0

        if year >= 2020:
            recent.append(work)
        else:
            old.append(work)

    recent.sort(
        key=lambda w: int(w["year"]) if str(w["year"]).isdigit() else 0,
        reverse=True
    )

    old.sort(
        key=lambda w: int(w["year"]) if str(w["year"]).isdigit() else 0,
        reverse=True
    )

    return recent, old


def painting_period_page(title, works, period_label, current=None):
    cards = "\n".join(
        artwork_card(work)
        for work in works
    )

    if not cards:
        cards = """
<div class="empty-gallery">
  Aucune œuvre pour le moment.
</div>
"""

    body = f"""
<section class="category-head">
  <div class="eyebrow">Peintures</div>

  <h1>{esc(title)}</h1>

  <p>
    {esc(period_label)} —
    {len(works)} œuvre{"s" if len(works) != 1 else ""}.
  </p>
</section>

<section class="artworks-grid">
  {cards}
</section>
"""

    return page(
        title,
        body,
        current=current
    )
def esc(value):
    return html.escape(
        str(value or ""),
        quote=True
    )


def slugify(value):
    value = unicodedata.normalize(
        "NFKD",
        value
    )

    value = "".join(
        c for c in value
        if not unicodedata.combining(c)
    )

    value = value.lower()

    value = re.sub(
        r"[^a-z0-9]+",
        "-",
        value
    ).strip("-")

    return value or "oeuvre"


def pretty_folder_name(name):
    name = re.sub(
        r"^\d+[-_ ]*",
        "",
        name
    )

    name = (
        name
        .replace("_", " ")
        .replace("-", " ")
    )

    return " ".join(
        part.capitalize()
        for part in name.split()
    )


# ============================================================
# LECTURE JSON
# ============================================================

def read_info(folder):
    path = folder / "info.json"

    if not path.exists():
        return {}

    try:

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except Exception as exc:

        print(
            f"[ATTENTION] Impossible de lire {path}: {exc}"
        )

        return {}


# ============================================================
# IMAGES
# ============================================================

def find_images(folder):

    return sorted(
        [
            p
            for p in folder.iterdir()
            if (
                p.is_file()
                and
                p.suffix.lower() in IMAGE_EXTENSIONS
            )
        ],
        key=lambda p: p.name.lower()
    )


# ============================================================
# CONSTRUCTION D'UNE ŒUVRE
# ============================================================

def artwork_from_folder(category_slug, folder):

    info = read_info(folder)

    images = find_images(folder)

    title = (
        info.get("titre")
        or
        pretty_folder_name(folder.name)
    )

    cover_name = info.get("cover")

    if cover_name:

        cover = next(
            (
                p
                for p in images
                if p.name == cover_name
            ),
            None
        )

    else:

        cover = None

    cover = (
        cover
        or
        (
            images[0]
            if images
            else None
        )
    )

    return {
        "category": category_slug,
        "folder": folder,
        "folder_name": folder.name,
        "slug": slugify(folder.name),

        "prix": info.get("prix"),
        "devise": info.get(
            "devise",
            "EUR"
        ),

        "title": title,

        "year": info.get(
            "annee",
            ""
        ),

        "date": info.get(
            "date",
            ""
        ),

        "technique": info.get(
            "technique",
            ""
        ),

        "dimensions": info.get(
            "dimensions",
            ""
        ),

        "description": info.get(
            "description",
            ""
        ),

        "disponibilite": info.get(
            "disponibilite",
            ""
        ),

        "images": images,
        "cover": cover,
    }


# ============================================================
# SCAN D'UNE CATÉGORIE
# ============================================================

def scan_category(category_slug):

    category_dir = (
        IMAGES
        / category_slug
    )

    category_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    works = []

    for folder in sorted(
        category_dir.iterdir(),
        key=lambda p: p.name.lower()
    ):

        if (
            folder.is_dir()
            and
            not folder.name.startswith(".")
        ):

            works.append(
                artwork_from_folder(
                    category_slug,
                    folder
                )
            )

    return works


# ============================================================
# NAVIGATION
# ============================================================

def nav(current=None):
    links = [
        '<a href="index.html">ACCUEIL</a>'
    ]

    for slug, cfg in HOME_SECTIONS.items():
        attr = (
            ' aria-current="page"'
            if current == slug
            else ""
        )

        links.append(
            f'<a href="{cfg["href"]}"{attr}>'
            f'{esc(cfg["label"]).upper()}'
            f'</a>'
        )

    return (
        "<nav>"
        + "\n".join(links)
        + "</nav>"
    )


# ============================================================
# SIDEBAR
# ============================================================

def sidebar():

    return """
<aside class="sidebar">

  <div>

    <div class="logo">
      VÉRONIQUE<br>
      COLLET
    </div>

    <div class="logo-line"></div>

    <div class="sidebar-desc">
      Artiste<br>
      peinture, sculpture,<br>
      dessin, aquarelle
    </div>

    <div class="mark">
      A
    </div>

  </div>

  <div class="socials">
    IG<br>
    BE<br>
    FB
  </div>

</aside>
"""


# ============================================================
# FOOTER
# ============================================================

def footer():

    return """
<footer id="contact">

  <div>

    <h3>
      Véronique Collet
    </h3>

    <p>
      © 2026<br>
      Tous droits réservés<br>
      Mentions légales
    </p>

  </div>

  <div>

    <h3>
      Contact
    </h3>

    <p>
      vro.collet@orange.fr<br>
      0675726927
    </p>

  </div>

</footer>
"""


# ============================================================
# PAGE HTML GÉNÉRALE
# ============================================================

def page(title, body, current=None):

    return f"""<!doctype html>

<html lang="fr">

<head>

  <meta charset="utf-8">

  <meta
    name="viewport"
    content="width=device-width, initial-scale=1"
  >

  <title>
    {esc(title)} — Véronique Collet
  </title>

  <link
    rel="stylesheet"
    href="style.css"
  >

</head>

<body>

<div class="site">

  {sidebar()}

  <main class="content">

    <header>
      {nav(current)}
    </header>

    {body}

    {footer()}

  </main>

  <aside class="rightbar">
    ATELIER OUVERT SUR RENDEZ-VOUS
  </aside>

</div>

</body>

</html>
"""


# ============================================================
# NOM DES PAGES D'ŒUVRES
# ============================================================

def work_filename(work):

    return (
        f"oeuvre-"
        f"{work['category']}-"
        f"{work['slug']}.html"
    )


# ============================================================
# URL IMAGE
# ============================================================

def image_src(work, image):

    return (
        f"images/"
        f"{work['category']}/"
        f"{work['folder_name']}/"
        f"{image.name}"
    )


# ============================================================
# CARTE D'UNE ŒUVRE
# ============================================================

def artwork_card(work):

    if work["cover"]:

        visual = (
            f'<img '
            f'src="{esc(image_src(work, work["cover"]))}" '
            f'alt="{esc(work["title"])}" '
            f'loading="lazy">'
        )

    else:

        visual = """
<div class="hero-placeholder">
  Ajoutez au moins une photo dans ce dossier.
</div>
"""

    count = len(
        work["images"]
    )

    # Afficher le badge uniquement à partir de 2 photos
    badge = (
        f'<span class="photo-count">'
        f'{count} PHOTOS'
        f'</span>'
        if count > 1
        else ""
    )

    metadata = " — ".join(
        x
        for x in [
            (
                str(work["year"])
                if work["year"]
                else ""
            ),
            work["technique"]
        ]
        if x
    )

    dimensions = (
        work["dimensions"]
    )

    return f"""
<figure class="artwork-card">

  <a
    class="artwork-link"
    href="{esc(work_filename(work))}"
  >

    <div class="artwork-image-wrap">

      {visual}

      {badge}

    </div>

    <figcaption>

      <div class="artwork-title">
        {esc(work["title"])}
      </div>

      <div class="artwork-meta">
        {esc(metadata)}
      </div>

      {
        '<div class="artwork-meta">'
        +
        esc(dimensions)
        +
        '</div>'
        if dimensions
        else ''
      }

    </figcaption>

  </a>

</figure>
"""


# ============================================================
# PAGE CATÉGORIE
# ============================================================

def category_page(slug, works):

    cfg = CATEGORIES[slug]

    # ========================================================
    # PEINTURES
    # Séparation récentes / anciennes
    # ========================================================

    if slug == "peintures":

        recent = []
        archive = []

        for work in works:

            try:

                year = int(
                    work["year"]
                )

            except (
                TypeError,
                ValueError
            ):

                year = 0

            if year >= 2020:

                recent.append(
                    work
                )

            else:

                archive.append(
                    work
                )

        recent.sort(
            key=lambda w:
                int(w["year"])
                if str(
                    w["year"]
                ).isdigit()
                else 0,
            reverse=True
        )

        archive.sort(
            key=lambda w:
                int(w["year"])
                if str(
                    w["year"]
                ).isdigit()
                else 0,
            reverse=True
        )

        recent_cards = "\n".join(
            artwork_card(w)
            for w in recent
        )

        archive_cards = "\n".join(
            artwork_card(w)
            for w in archive
        )

        recent_section = ""

        if recent_cards:

            recent_section = f"""
<section class="gallery-period">

  <div class="period-head">

    <h2>
      Œuvres récentes
    </h2>

    <span>
      2020 — aujourd’hui
    </span>

  </div>

  <div class="artworks-grid">

    {recent_cards}

  </div>

</section>
"""

        archive_section = ""

        if archive_cards:

            archive_section = f"""
<section class="gallery-period gallery-archive">

  <div class="period-head">

    <h2>
      Œuvres anciennes
    </h2>

    <span>
      Avant 2020
    </span>

  </div>

  <div class="artworks-grid">

    {archive_cards}

  </div>

</section>
"""

        body = f"""
<section class="category-head">

  <div class="eyebrow">
    Collection
  </div>

  <h1>
    {esc(cfg["label"])}
  </h1>

  <p>
    {len(works)}
    œuvre{"s" if len(works) != 1 else ""}.
  </p>

</section>

{recent_section}

{archive_section}
"""

        return page(
            cfg["label"],
            body,
            current=slug
        )


    # ========================================================
    # AUTRES CATÉGORIES
    # ========================================================

    cards = "\n".join(
        artwork_card(w)
        for w in works
    )

    if not cards:

        cards = """
<div class="empty-gallery">

  Aucun contenu
  pour le moment.

</div>
"""

    body = f"""
<section class="category-head">

  <div class="eyebrow">
    Collection
  </div>

  <h1>
    {esc(cfg["label"])}
  </h1>

  <p>
    {esc(cfg["description"])}
    —
    {len(works)}
    œuvre{"s" if len(works) != 1 else ""}.
  </p>

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


# ============================================================
# LIGNE D'INFORMATION
# ============================================================

def info_row(term, value):

    if not value:
        return ""

    return (
        f"<dt>"
        f"{esc(term)}"
        f"</dt>"
        f"<dd>"
        f"{esc(value)}"
        f"</dd>"
    )


# ============================================================
# FORMATAGE PRIX
# ============================================================

def format_price(
    price,
    currency="EUR"
):

    if (
        price is None
        or
        price == ""
    ):
        return ""

    if currency == "EUR":

        return (
            f"{price:,} €"
            .replace(
                ",",
                " "
            )
        )

    return (
        f"{price:,} {currency}"
        .replace(
            ",",
            " "
        )
    )


# ============================================================
# PAGE D'UNE ŒUVRE
# ============================================================

def work_page(work):

    cfg = CATEGORIES[
        work["category"]
    ]

    images = work["images"]

    # ========================================================
    # IMAGE PRINCIPALE
    # ========================================================

    if images:

        first_src = image_src(
            work,
            images[0]
        )

        main = f"""
<button
  class="main-photo-button"
  type="button"
  id="main-photo-button"
>

  <img
    class="main-photo"
    id="main-photo"
    src="{esc(first_src)}"
    alt="{esc(work["title"])}"
  >

</button>
"""

        thumbs = "\n".join(
            f"""
<button
  class="thumbnail"
  type="button"
  data-src="{esc(image_src(work, img))}"
  aria-current="{'true' if i == 0 else 'false'}"
>

  <img
    src="{esc(image_src(work, img))}"
    alt="{esc(work["title"])} — vue {i + 1}"
    loading="lazy"
  >

</button>
"""
            for i, img
            in enumerate(images)
        )

        thumbs_html = (
            f'<div class="thumbnails">'
            f'{thumbs}'
            f'</div>'
            if len(images) > 1
            else ""
        )

        image_array = json.dumps(
            [
                image_src(
                    work,
                    img
                )
                for img in images
            ],
            ensure_ascii=False
        )

    else:

        main = """
<div class="hero-placeholder">
  Aucune photo dans ce dossier.
</div>
"""

        thumbs_html = ""

        image_array = "[]"


    # ========================================================
    # RÉSUMÉ
    # ========================================================

    summary = " · ".join(
        str(x)
        for x in [
            work["date"]
            or
            work["year"],
            work["technique"],
            work["dimensions"]
        ]
        if x
    )


    # ========================================================
    # HTML
    # ========================================================

    body = f"""
<article class="work-page">

  <header class="work-header">

    <a
      class="work-back"
      href="{esc(work["category"])}.html"
    >
      ← {esc(cfg["label"])}
    </a>

    <h1>
      {esc(work["title"])}
    </h1>

    <div class="work-summary">
      {esc(summary)}
    </div>

  </header>

  <div class="work-layout">

    <section class="work-gallery">

      {main}

      {thumbs_html}

    </section>

    <aside class="work-info">

      <h2>
        Informations
      </h2>

      <dl>

        {info_row(
            "Date",
            work["date"]
            or
            work["year"]
        )}

        {info_row(
            "Technique",
            work["technique"]
        )}

        {info_row(
            "Dimensions",
            work["dimensions"]
        )}

        {info_row(
            "Disponibilité",
            work["disponibilite"]
        )}

        {info_row(
            "Prix",
            format_price(
                work["prix"],
                work["devise"]
            )
        )}

        {
            info_row(
                "Photographies",
                len(images)
            )
            if len(images) > 1
            else ""
        }

      </dl>

      {
        '<div class="work-description">'
        +
        esc(
            work["description"]
        )
        +
        '</div>'
        if work["description"]
        else ''
      }

    </aside>

  </div>

</article>


<div
  class="lightbox"
  id="lightbox"
  aria-hidden="true"
>

  <button
    class="lightbox-close"
    type="button"
    aria-label="Fermer"
  >
    ×
  </button>

  <button
    class="lightbox-nav lightbox-prev"
    type="button"
    aria-label="Photo précédente"
  >
    ‹
  </button>

  <img
    id="lightbox-image"
    alt=""
  >

  <button
    class="lightbox-nav lightbox-next"
    type="button"
    aria-label="Photo suivante"
  >
    ›
  </button>

</div>


<script>

(() => {{

  const images = {image_array};

  if (!images.length) {{
    return;
  }}

  const main =
    document.getElementById(
      "main-photo"
    );

  const mainButton =
    document.getElementById(
      "main-photo-button"
    );

  const thumbs = [
    ...document.querySelectorAll(
      ".thumbnail"
    )
  ];

  const lightbox =
    document.getElementById(
      "lightbox"
    );

  const lightboxImage =
    document.getElementById(
      "lightbox-image"
    );

  const close =
    lightbox.querySelector(
      ".lightbox-close"
    );

  const prev =
    lightbox.querySelector(
      ".lightbox-prev"
    );

  const next =
    lightbox.querySelector(
      ".lightbox-next"
    );

  let currentIndex = 0;


  function setCurrent(index) {{

    currentIndex =
      (
        index
        +
        images.length
      )
      %
      images.length;

    if (main) {{
      main.src =
        images[currentIndex];
    }}

    thumbs.forEach(
      (thumb, i) => {{

        thumb.setAttribute(
          "aria-current",
          i === currentIndex
            ? "true"
            : "false"
        );

      }}
    );

  }}


  thumbs.forEach(
    (thumb, index) => {{

      thumb.addEventListener(
        "click",
        () => setCurrent(index)
      );

    }}
  );


  function openLightbox() {{

    lightboxImage.src =
      images[currentIndex];

    lightbox.classList.add(
      "open"
    );

    lightbox.setAttribute(
      "aria-hidden",
      "false"
    );

    document.body.style.overflow =
      "hidden";

  }}


  function closeLightbox() {{

    lightbox.classList.remove(
      "open"
    );

    lightbox.setAttribute(
      "aria-hidden",
      "true"
    );

    document.body.style.overflow =
      "";

  }}


  function lightboxMove(delta) {{

    setCurrent(
      currentIndex
      +
      delta
    );

    lightboxImage.src =
      images[currentIndex];

  }}


  if (mainButton) {{

    mainButton.addEventListener(
      "click",
      openLightbox
    );

  }}


  close.addEventListener(
    "click",
    closeLightbox
  );


  prev.addEventListener(
    "click",
    () => lightboxMove(-1)
  );


  next.addEventListener(
    "click",
    () => lightboxMove(1)
  );


  lightbox.addEventListener(
    "click",
    (event) => {{

      if (
        event.target
        ===
        lightbox
      ) {{

        closeLightbox();

      }}

    }}
  );


  document.addEventListener(
    "keydown",
    (event) => {{

      if (
        !lightbox.classList.contains(
          "open"
        )
      ) {{
        return;
      }}

      if (
        event.key === "Escape"
      ) {{
        closeLightbox();
      }}

      if (
        event.key === "ArrowLeft"
      ) {{
        lightboxMove(-1);
      }}

      if (
        event.key === "ArrowRight"
      ) {{
        lightboxMove(1);
      }}

    }}
  );

}})();

</script>
"""

    return page(
        work["title"],
        body,
        current=work["category"]
    )


# ============================================================
# PAGE D'ACCUEIL
# ============================================================
def home_page(all_works):

    paintings = all_works.get(
        "peintures",
        []
    )

    recent_paintings, old_paintings = split_paintings(
        paintings
    )

    section_works = {
        "peintures-recentes": recent_paintings,
        "peintures-anciennes": old_paintings,
        "dessins": all_works.get("dessins", []),
        "sculptures": all_works.get("sculptures", []),
        "aquarelles": all_works.get("aquarelles", []),
        "atelier": all_works.get("atelier", []),
    }

    section_images = {}

    for section_slug, works in section_works.items():

        images = []

        for work in works:
            for image in work["images"]:
                images.append(
                    image_src(
                        work,
                        image
                    )
                )

        section_images[section_slug] = images


    preview_parts = []

    for slug, cfg in HOME_SECTIONS.items():

        images = section_images.get(
            slug,
            []
        )

        href = cfg["href"]
        label = cfg["label"]

        if images:

            first_image = images[0]

            preview_parts.append(
                f"""
<a
  class="home-category-card category-random-image"
  href="{esc(href)}"
  data-category="{esc(slug)}"
>

  <img
    src="{esc(first_image)}"
    alt="{esc(label)}"
  >

  <div class="home-category-overlay">
    <span>{esc(label)}</span>
    <span>→</span>
  </div>

</a>
"""
            )

        else:

            preview_parts.append(
                f"""
<a
  class="home-category-card"
  href="{esc(href)}"
>

  <div class="hero-placeholder">
    {esc(label)}
  </div>

  <div class="home-category-overlay">
    <span>{esc(label)}</span>
    <span>→</span>
  </div>

</a>
"""
            )

    preview = "".join(
        preview_parts
    )

    section_images_json = json.dumps(
        section_images,
        ensure_ascii=False
    )

    body = f"""
<section class="hero" id="travaux">

  <div class="hero-copy">
    <h1>
      L'ART<br>
      COMME<br>
      EXPRESSION
    </h1>

    <div class="dash"></div>

    <a
      class="hero-link"
      href="#categories"
    >
      Explorer le travail
      <span>→</span>
    </a>
  </div>

  <div class="hero-art">
    <img
      class="hero-photo"
      src="images/atelier/003/003.JPG"
      alt="Atelier"
    >
  </div>

</section>


<section class="manifesto-grid" id="infos">

  <div class="manifesto">

    <div class="manifesto-title">
      Manifeste
    </div>

    <div>

      <div class="quote">“</div>

      <blockquote>
        Avant, le corps humain était ma préoccupation artistique,
        sa posture, son cadrage, sa force. Aujourd’hui, ce sont
        les éléments naturels qui m’inspirent, les rapports
        qu’ils entretiennent, leurs imbrications, leurs mouvements,
        leurs lignes ou matières.
      </blockquote>

      <div class="signature">
        — V. COLLET
      </div>

    </div>

  </div>

  <div class="exhibitions">

    <div class="label">
      Explorer
    </div>

    <h2>
      ŒUVRES<br>
      & TECHNIQUES
    </h2>

    <p>
      Peinture, dessin, sculpture,
      aquarelle et atelier.
    </p>

  </div>

</section>


<section
  class="home-category-gallery"
  id="categories"
>

  {preview}

</section>


<script>

(() => {{

  const categoryImages =
    {section_images_json};


  function randomImage(images, current) {{

    if (!images || images.length === 0) {{
      return current;
    }}

    if (images.length === 1) {{
      return images[0];
    }}

    let next;

    do {{
      next =
        images[
          Math.floor(
            Math.random()
            *
            images.length
          )
        ];
    }}
    while (next === current);

    return next;
  }}


  function changeGalleryImages() {{

    document
      .querySelectorAll(
        ".category-random-image"
      )
      .forEach((item) => {{

        const category =
          item.dataset.category;

        const img =
          item.querySelector("img");

        const images =
          categoryImages[category];

        if (!img || !images) {{
          return;
        }}

        img.src =
          randomImage(
            images,
            img.getAttribute("src")
          );

      }});
  }}


  setInterval(
    changeGalleryImages,
    5000
  );

}})();

</script>
"""

    return page(
        "Accueil",
        body
    )
# def home_page(all_works):

#     # ========================================================
#     # LISTE DE TOUTES LES IMAGES PAR CATÉGORIE
#     # ========================================================

#     category_images = {}

#     for slug in CATEGORIES:

#         images = []

#         for work in all_works.get(
#             slug,
#             []
#         ):

#             for image in work["images"]:

#                 images.append(
#                     image_src(
#                         work,
#                         image
#                     )
#                 )

#         category_images[
#             slug
#         ] = images


#     # ========================================================
#     # UNE VIGNETTE PAR CATÉGORIE
#     # ========================================================

#     preview_parts = []

# for slug, cfg in HOME_SECTIONS.items():

#     images = section_images.get(
#         slug,
#         []
#     )

#     href = cfg["href"]
#     label = cfg["label"]

#     if images:

#         first_image = images[0]

#         preview_parts.append(
#             f"""
# <a
#   class="home-category-card category-random-image"
#   href="{esc(href)}"
#   data-category="{esc(slug)}"
# >

#   <img
#     src="{esc(first_image)}"
#     alt="{esc(label)}"
#   >

#   <div class="home-category-overlay">

#     <span>
#       {esc(label)}
#     </span>

#     <span>
#       →
#     </span>

#   </div>

# </a>
# """
#         )

#     else:

#         preview_parts.append(
#             f"""
# <a
#   class="home-category-card"
#   href="{esc(href)}"
# >

#   <div class="hero-placeholder">
#     {esc(label)}
#   </div>

#   <div class="home-category-overlay">

#     <span>
#       {esc(label)}
#     </span>

#     <span>
#       →
#     </span>

#   </div>

# </a>
# """
#         )

# preview = "".join(
#     preview_parts
# )


#     # ========================================================
#     # DONNÉES JS
#     # ========================================================

#     category_images_json = (
#         json.dumps(
#             category_images,
#             ensure_ascii=False
#         )
#     )
#     section_images_json = json.dumps(
#         section_images,
#         ensure_ascii=False
#     )
# const categoryImages = {section_images_json};

#     # ========================================================
#     # LIENS DES CATÉGORIES
#     # ========================================================

#     category_links = "".join(
#         (
#             f'<a href="{slug}.html">'
#             f'<span>{esc(cfg["label"])}</span>'
#             f'<span>→</span>'
#             f'</a>'
#         )
#         for slug, cfg
#         in CATEGORIES.items()
#     )


#     # ========================================================
#     # HTML ACCUEIL
#     # ========================================================

#     body = f"""
# <section
#   class="hero"
#   id="travaux"
# >

#   <div class="hero-copy">

#     <h1>
#       L'ART<br>
#       COMME<br>
#       EXPRESSION
#     </h1>

#     <div class="dash"></div>

#     <a
#       class="hero-link"
#       href="#categories"
#     >
#       Explorer le travail
#       <span>→</span>
#     </a>

#   </div>


#   <div class="hero-art">

#     <img
#       class="hero-photo"
#       src="images/atelier/003/003.JPG"
#       alt="Atelier"
#     >

#   </div>

# </section>


# <section
#   class="manifesto-grid"
#   id="infos"
# >

#   <div class="manifesto">

#     <div class="manifesto-title">
#       Manifeste
#     </div>

#     <div>

#       <div class="quote">
#         “
#       </div>

#       <blockquote>

#         Avant, le corps humain était ma préoccupation artistique,
#         sa posture, son cadrage, sa force.

#         Aujourd’hui, ce sont les éléments naturels qui m’inspirent,
#         les rapports qu’ils entretiennent,
#         leurs imbrications,
#         leurs mouvements,
#         leurs lignes ou matières.

#       </blockquote>

#       <div class="signature">
#         — V. COLLET
#       </div>

#     </div>

#   </div>


#   <div class="exhibitions">

#     <div class="label">
#       Explorer
#     </div>

#     <h2>
#       ŒUVRES<br>
#       & TECHNIQUES
#     </h2>

#     <p>
#       Peinture, dessin,
#       sculpture, aquarelle
#       et atelier.
#     </p>

#   </div>

# </section>


# <section
#   class="category-menu"
#   id="categories"
# >

#   {category_links}

# </section>
# <section class="home-category-gallery">
#   {preview}
# </section>

# <section class="gallery">

#   {preview}

# </section>


# <script>

# (() => {{

#   const categoryImages =
#     {category_images_json};


#   function randomImage(
#     images,
#     current
#   ) {{

#     if (
#       !images
#       ||
#       images.length === 0
#     ) {{
#       return current;
#     }}

#     if (
#       images.length === 1
#     ) {{
#       return images[0];
#     }}

#     let next;

#     do {{

#       next =
#         images[
#           Math.floor(
#             Math.random()
#             *
#             images.length
#           )
#         ];

#     }}
#     while (
#       next === current
#     );

#     return next;

#   }}


#   function changeGalleryImages() {{

#     document
#       .querySelectorAll(
#         ".category-random-image"
#       )
#       .forEach(
#         (item) => {{

#           const category =
#             item.dataset.category;

#           const img =
#             item.querySelector(
#               "img"
#             );

#           const images =
#             categoryImages[
#               category
#             ];

#           if (
#             !img
#             ||
#             !images
#           ) {{
#             return;
#           }}

#           img.src =
#             randomImage(
#               images,
#               img.getAttribute(
#                 "src"
#               )
#             );

#         }}
#       );

#   }}


#   setInterval(
#     changeGalleryImages,
#     5000
#   );

# }})();

# </script>
# """

#     return page(
#         "Accueil",
#         body
#     )


# ============================================================
# MAIN
# ============================================================
def main():

    all_works = {}

    # Scanner toutes les catégories
    for slug in CATEGORIES:

        works = scan_category(
            slug
        )

        all_works[slug] = works

        # Catégories normales
        if slug != "peintures":

            (
                ROOT
                /
                f"{slug}.html"
            ).write_text(
                category_page(
                    slug,
                    works
                ),
                encoding="utf-8"
            )

        # Pages individuelles
        for work in works:

            (
                ROOT
                /
                work_filename(work)
            ).write_text(
                work_page(work),
                encoding="utf-8"
            )


    # Séparation des peintures
    recent_paintings, old_paintings = split_paintings(
        all_works.get(
            "peintures",
            []
        )
    )


    # Peintures récentes
    (
        ROOT
        /
        "peinturerec.html"
    ).write_text(
        painting_period_page(
            "Peintures récentes",
            recent_paintings,
            "2020 — aujourd’hui",
            current="peintures-recentes"
        ),
        encoding="utf-8"
    )


    # Peintures anciennes
    (
        ROOT
        /
        "peintureanc.html"
    ).write_text(
        painting_period_page(
            "Peintures anciennes",
            old_paintings,
            "Avant 2020",
            current="peintures-anciennes"
        ),
        encoding="utf-8"
    )


    # Accueil
    (
        ROOT
        /
        "index.html"
    ).write_text(
        home_page(
            all_works
        ),
        encoding="utf-8"
    )


    # Nettoyage anciennes pages individuelles
    expected = {
        work_filename(work)
        for works in all_works.values()
        for work in works
    }

    for file in ROOT.glob(
        "oeuvre-*.html"
    ):

        if file.name not in expected:
            file.unlink()


    total = sum(
        len(v)
        for v in all_works.values()
    )

    print(
        f"Site généré : {total} œuvre(s)."
    )

    print(
        f"  - Peintures récentes : "
        f"{len(recent_paintings)}"
    )

    print(
        f"  - Peintures anciennes : "
        f"{len(old_paintings)}"
    )

    for slug in [
        "dessins",
        "sculptures",
        "aquarelles",
        "atelier",
    ]:

        print(
            f"  - "
            f"{CATEGORIES[slug]['label']}: "
            f"{len(all_works.get(slug, []))}"
        )
# def main():

#     all_works = {}


#     # ========================================================
#     # SCAN + GÉNÉRATION
#     # ========================================================

#     for slug in CATEGORIES:

#         works = scan_category(
#             slug
#         )

#         all_works[
#             slug
#         ] = works


#         # Page catégorie
#         (
#             ROOT
#             /
#             f"{slug}.html"
#         ).write_text(
#             category_page(
#                 slug,
#                 works
#             ),
#             encoding="utf-8"
#         )
#         paintings = all_works.get("peintures", [])

# recent_paintings, old_paintings = split_paintings(
#     paintings
# )
# section_works = {
#     "peintures-recentes": recent_paintings,
#     "peintures-anciennes": old_paintings,
#     "dessins": all_works.get("dessins", []),
#     "sculptures": all_works.get("sculptures", []),
#     "aquarelles": all_works.get("aquarelles", []),
#     "atelier": all_works.get("atelier", []),
# }
# section_images = {}

# for section_slug, works in section_works.items():

#     images = []

#     for work in works:

#         for image in work["images"]:

#             images.append(
#                 image_src(
#                     work,
#                     image
#                 )
#             )

#     section_images[section_slug] = images

# (ROOT / "peinturerec.html").write_text(
#     painting_period_page(
#         "Peintures récentes",
#         recent_paintings,
#         "2020 — aujourd’hui"
#     ),
#     encoding="utf-8"
# )

# (ROOT / "peintureanc.html").write_text(
#     painting_period_page(
#         "Peintures anciennes",
#         old_paintings,
#         "Avant 2020"
#     ),
#     encoding="utf-8"
# )


#         # Pages œuvres
#         for work in works:

#             (
#                 ROOT
#                 /
#                 work_filename(
#                     work
#                 )
#             ).write_text(
#                 work_page(
#                     work
#                 ),
#                 encoding="utf-8"
#             )


#     # ========================================================
#     # ACCUEIL
#     # ========================================================

#     (
#         ROOT
#         /
#         "index.html"
#     ).write_text(
#         home_page(
#             all_works
#         ),
#         encoding="utf-8"
#     )


#     # ========================================================
#     # SUPPRESSION DES ANCIENNES PAGES ŒUVRES
#     # ========================================================

#     expected = {
#         work_filename(
#             work
#         )
#         for works
#         in all_works.values()
#         for work
#         in works
#     }

#     for file in ROOT.glob(
#         "oeuvre-*.html"
#     ):

#         if (
#             file.name
#             not in expected
#         ):

#             file.unlink()


#     # ========================================================
#     # RÉSUMÉ
#     # ========================================================

#     total = sum(
#         len(v)
#         for v
#         in all_works.values()
#     )

#     print(
#         f"Site généré : "
#         f"{total} œuvre(s)."
#     )

#     for slug, works in all_works.items():

#         print(
#             f"  - "
#             f"{CATEGORIES[slug]['label']}: "
#             f"{len(works)}"
#         )


# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":
    main()
