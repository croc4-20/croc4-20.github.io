SITE D'ART — GÉNÉRATION AUTOMATIQUE
====================================

PRINCIPE
--------
Vous ne créez plus de <figure> à la main.

Chaque œuvre est un SOUS-DOSSIER dans sa catégorie :

images/
  peintures/
    les-iris/
      info.json
      01.jpg
      02.jpg
      detail.jpg

  sculptures/
    forme-bleue/
      info.json
      face.jpg
      profil.jpg
      dos.jpg
      detail.jpg

Le script generate.py parcourt automatiquement les dossiers et crée :
- peintures.html
- dessins.html
- sculptures.html
- aquarelles.html
- collages.html
- une page HTML détaillée par œuvre

PLUSIEURS PHOTOS
----------------
Mettez autant de photos que nécessaire dans le dossier de l'œuvre.

La page de l'œuvre crée automatiquement :
- une grande photo principale ;
- des miniatures ;
- le changement de photo au clic ;
- une lightbox plein écran ;
- navigation avec les flèches du clavier.

INFO.JSON
---------
info.json est facultatif.

Exemple :

{
  "titre": "Les Iris",
  "annee": "2026",
  "technique": "Huile sur toile",
  "dimensions": "80 × 100 cm",
  "description": "Texte sur l'œuvre.",
  "disponibilite": "Disponible",
  "cover": "02.jpg"
}

Si "titre" n'existe pas, le nom du dossier sert de titre.
Si "cover" n'existe pas, la première image par ordre alphabétique
sert de couverture.

AJOUTER UNE ŒUVRE
-----------------
1. Créez un dossier :
   images/peintures/les-iris/

2. Ajoutez les photos :
   01.jpg
   02.jpg
   03.jpg

3. Ajoutez éventuellement info.json.

4. Double-cliquez sur :
   generer-site.bat

   ou dans un terminal :
   python generate.py

5. Ouvrez index.html.

SUPPRIMER UNE ŒUVRE
-------------------
Supprimez simplement son sous-dossier, puis relancez generate.py.

RENOMMER UNE ŒUVRE
------------------
Renommez le sous-dossier ou modifiez "titre" dans info.json,
puis relancez generate.py.

GITHUB PAGES
------------
Tous les fichiers générés restent de simples fichiers HTML/CSS/JS,
donc le site est compatible avec GitHub Pages.

IMPORTANT
---------
Le navigateur ne peut pas parcourir librement vos dossiers tout seul.
C'est donc generate.py qui effectue le scan AVANT publication.

Les dossiers fournis ici sont seulement des exemples de structure.
Ils ne contiennent aucune fausse œuvre ou image générée en CSS.
