# eToro Skill – Setup-Anleitung

## Warum lokal?

Aus Sicherheitsgründen lädt hAI.FIN den eToro Skill **nicht** automatisch
von `skills.bullaware.com` herunter. Ein kompromittierter Remote-Server
könnte bösartigen Code in deinen Agenten einschleusen.

## Setup (einmalig)

```bash
# 1. Skill manuell herunterladen und prüfen
curl -o config/etoro-skill.md https://skills.bullaware.com/etoro-api/SKILL.md

# 2. Inhalt prüfen (manuell lesen!)
cat config/etoro-skill.md

# 3. SHA256-Prüfsumme notieren (für spätere Updates)
sha256sum config/etoro-skill.md
```

## Updates

Bei jedem Update die Datei erneut herunterladen, **diff prüfen**
und erst dann den Container neu starten:

```bash
curl -o config/etoro-skill-new.md https://skills.bullaware.com/etoro-api/SKILL.md
diff config/etoro-skill.md config/etoro-skill-new.md
# Wenn ok:
mv config/etoro-skill-new.md config/etoro-skill.md
```

## .gitignore

`etoro-skill.md` ist bewusst NICHT in `.gitignore` –
die Datei enthält keine Secrets und soll versioniert sein.
