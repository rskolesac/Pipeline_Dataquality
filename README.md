README — Pipeline d’analyse de la qualité des données
Tech stack : Python 3.10+, pandas, Great Expectations, CLI + CI/CD
🎯 Objectifs
Détecter et prévenir les problèmes de qualité (schéma, valeurs, duplicats, cohérence métier).
Standardiser les contrôles via des expectations versionnées.
Automatiser la validation sur chaque lot/PR (quality gates).
Documenter la qualité (Data Docs) et alerter en cas d’échec (mailing automatique).
🏗️ Architecture (vue d’ensemble)
Ingestion : lecture de fichiers (CSV/Parquet), DB ou API → pandas.DataFrame.
Préparation : typage, normalisation, enrichissements.
Validation : exécution d’un Checkpoint Great Expectations (suites d’expectations).
Reporting : génération des Data Docs (HTML) + export des métriques (JSON).
Quality Gate : le job échoue si la validation échoue.
