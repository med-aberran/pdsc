# Déploiement PDSC sur Vercel + Supabase

## 1. Supabase
1. **Base de données** : Project > *Connect* > **Transaction pooler** (port 6543).
   Copiez l'URI `postgresql://postgres.<ref>:<mot_de_passe>@aws-0-<région>.pooler.supabase.com:6543/postgres`
   → c'est votre `DATABASE_URL`.
   ⚠ Utilisez le **pooler** : la connexion directe (`db.<ref>.supabase.co`) est en IPv6 seulement et échoue depuis Vercel.
2. **Storage** : créez deux buckets
   - `pdsc-public` → **Public** (avatars, actualités, galerie, documents publics, plans, QR codes)
   - `pdsc-private` → **Private** (pièces jointes des demandes des citoyens)
3. **Clé API** : Settings > API > copiez la clé **service_role** → `SUPABASE_KEY` (serveur uniquement).

## 2. Créer les tables (depuis votre PC, une seule fois)
```bash
cp .env.example .env     # puis remplir DATABASE_URL, SUPABASE_URL, SUPABASE_KEY...
set FLASK_APP=app.py     # PowerShell : $env:FLASK_APP="app.py"
flask db upgrade
flask seed-db            # rôles, compte admin, services par défaut
```
Changez ensuite le mot de passe du compte `admin@commune.ma` (défini dans `seed-db`).
Les migrations ne se lancent **pas** sur Vercel (fonctions sans état).

## 3. Variables d'environnement Vercel (Settings > Environment Variables)
`SECRET_KEY`, `JWT_SECRET_KEY`, `SECURITY_PASSWORD_SALT` (valeurs longues et aléatoires),
`DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_BUCKET`, `SUPABASE_PRIVATE_BUCKET`,
`MAIL_*`, `COMMUNE_NAME_FR`, `COMMUNE_NAME_AR`.
Ne définissez pas `FLASK_ENV` (production par défaut). L'app refuse de démarrer si les secrets valent encore `change-this-...`.

## 4. Déployer
```bash
git rm -r --cached static/uploads     # retire les fichiers de test du dépôt (les .gitkeep restent)
git add . && git commit -m "Compatibilité Vercel + Supabase" && git push
```
Importez le dépôt dans Vercel (preset *Other*, aucune commande de build).

## Limites à connaître
- Vercel limite le corps d'une requête à **4,5 Mo** : l'upload est plafonné à 4 Mo sur Vercel.
- Le disque est en lecture seule : tous les fichiers passent par Supabase Storage.
- Les anciens fichiers de `static/uploads/` ne sont pas migrés : téléversez-les dans le bucket
  (même chemin relatif, ex. `documents/<nom>`) si vous en avez besoin.
