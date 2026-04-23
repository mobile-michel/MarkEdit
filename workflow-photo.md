# Workflow photo — digiKam, ART et DS925+

## Architecture de stockage

```
Silverstone
└── /photo-library/          ← disque 10 To local
    └── tous les originaux   (RAW, JPEG, JPEG+RAW)

DS925+ /volume1/
├── homes/michel/Photos/     ← espace personnel Synology Photos
└── photo-published/         ← espace partagé Synology Photos
    ├── Portfolio/
    ├── Famille/
    └── Voyages/
```

---

## Workflow par source

### Photos smartphone (Pixel 8 Pro)
```
Pixel 8 Pro
    ↓ sauvegarde automatique (Synology Photos app)
DS925+ /homes/michel/Photos/     ← dépôt temporaire
    ↓ import périodique via digiKam (hebdomadaire ou mensuel)
/photo-library/                  ← librairie complète unifiée
    ↓ tri et notation (optionnel)
```
- Sauvegarde automatique sans intervention
- Import périodique dans digiKam pour intégration à la librairie complète
- `homes/michel/Photos/` sert de dépôt temporaire — photos supprimées ou conservées comme backup après import

---

### Photos Z6III
```
Nikon Z6III
    ↓ import USB
digiKam (Silverstone)
    BDD + thumbnails : ~/.local/share/digikam/   (local)
    Originaux        : /photo-library/            (disque 10 To local)
    ↓ tri et notation (optionnel)
```

#### Sans tri (par défaut)
- Les photos restent dans `/photo-library/` sur Silverstone
- Accessibles via digiKam uniquement
- Aucune pression de tri

#### Avec tri (≥ 2 étoiles)
```
digiKam — noter ≥ 2 étoiles
    ↓ script rsync automatique
DS925+ /homes/michel/Photos/
    ↓
Synology Photos — espace personnel
```

#### Meilleures photos (≥ 4 étoiles, retouchées)
```
digiKam — sélection ≥ 4 étoiles
    ↓
ART/ARTherapie — développement RAW ou retouche JPEG
    ↓ export JPEG direct
DS925+ /photo-published/Portfolio/ (ou Famille, Voyages...)
    ↓
Synology Photos — espace partagé
```

---

## Synology Photos — configuration

| Espace | Dossier source | Contenu |
|---|---|---|
| Personnel Michel | `homes/michel/Photos/` | Smartphone (dépôt temporaire avant import digiKam) |
| Partagé | `photo-published/` | Meilleures photos retouchées |

---

## Prérequis digiKam

Activer l'écriture des métadonnées dans les fichiers pour que le script puisse lire les étoiles :

**Paramètres → Configurer digiKam → Métadonnées :**
- ✅ Enregistrer les métadonnées dans les fichiers
- ✅ Enregistrer les notes/étoiles dans les fichiers

---

## Script de synchronisation (à développer)

Un script rsync/Python tournant automatiquement sur Silverstone :
- Lit les métadonnées XMP des fichiers dans `/photo-library/`
- Filtre les JPEGs avec ≥ 2 étoiles
- Copie vers `homes/michel/Photos/` sur le DS925+ via NFS

> À développer une fois le DS925+ installé et les montages NFS en place.

---

## Résumé

| Source | Tri requis | Destination | Accès mobile |
|---|---|---|---|
| Smartphone | Aucun | `homes/michel/Photos/` (temporaire) → `/photo-library/` | ✅ Synology Photos |
| Z6III non triées | Aucun | `/photo-library/` (local) | ❌ digiKam uniquement |
| Z6III ≥ 2 étoiles | Optionnel | `homes/michel/Photos/` | ✅ Synology Photos |
| Z6III ≥ 4 étoiles retouchées | Oui | `photo-published/` | ✅ Synology Photos |
