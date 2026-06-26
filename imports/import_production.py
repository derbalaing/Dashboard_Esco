import pandas as pd
import sys
import os

# Ajoute la racine du projet au PYTHONPATH
sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)


from config.database import engine

# ==========================================
# 1. Lecture du fichier Excel
# ==========================================

df = pd.read_excel("data/Production_Reelle.xlsx")

print(f"Lignes lues : {len(df)}")

# ==========================================
# 2. Lecture des sites depuis PostgreSQL
# ==========================================

sites_df = pd.read_sql(
    """
    SELECT
        site_id,
        code_site
    FROM sites
    """,
    engine
)

# ==========================================
# 3. Correspondance Code Site -> site_id
# ==========================================

df = df.merge(
    sites_df,
    left_on="Site ID",
    right_on="code_site",
    how="left"
)

# ==========================================
# 4. Vérification des sites manquants
# ==========================================

missing = df[df["site_id"].isna()]

if not missing.empty:
    print("\nSites non trouvés :")
    print(missing["Site ID"].unique())

# ==========================================
# 5. Conversion production
# ==========================================

df["Param Value"] = (
    df["Param Value"]
    .astype(str)
    .str.replace(",", ".", regex=False)
)

df["Param Value"] = pd.to_numeric(
    df["Param Value"],
    errors="coerce"
)

# ==========================================
# 6. Détermination du statut
# ==========================================

df["status"] = "NORMAL"

df.loc[
    df["Param Value"].isin([-1, -2]),
    "status"
] = "LOSTCOM"

# ==========================================
# 7. Production réelle
# ==========================================

df["production_kwh"] = df["Param Value"]

df.loc[
    df["status"] == "LOSTCOM",
    "production_kwh"
] = None

# ==========================================
# 8. Conversion date
# ==========================================

df["production_date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
).dt.date

# ==========================================
# 9. Construction DataFrame final
# ==========================================

df_final = pd.DataFrame({
    "site_id": df["site_id"],
    "production_date": df["production_date"],
    "param_name": df["Param Name"],
    "production_kwh": df["production_kwh"],
    "unit": df["Measure"],
    "status": df["status"]
})

# ==========================================
# 10. Suppression lignes invalides
# ==========================================

df_final = df_final.dropna(
    subset=["site_id", "production_date"]
)

# ==========================================
# 11. Contrôles qualité
# ==========================================

print("\nStatistiques :")

print(f"Total lignes : {len(df_final)}")

print("\nStatus :")
print(df_final["status"].value_counts())

print("\nValeurs nulles :")
print(df_final.isnull().sum())

print("\nAperçu :")
print(df_final.head())

# ==========================================
# 12. Import PostgreSQL
# ==========================================

df_final.to_sql(
    "solar_productions",
    engine,
    if_exists="append",
    index=False,
    method="multi",
    chunksize=1000
)

print(
    f"\n✅ {len(df_final)} productions importées avec succès"
)