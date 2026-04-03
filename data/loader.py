import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

_LOCAL_CSV = os.path.join(os.path.dirname(__file__), "titanic.csv")


def load_titanic() -> pd.DataFrame:
    try:
        if os.path.exists(_LOCAL_CSV):
            logger.info(f"Chargement depuis CSV local : {_LOCAL_CSV}")
            df = pd.read_csv(_LOCAL_CSV)
            df = _normalize_columns(df)
        else:
            logger.info("CSV local absent — tentative seaborn...")
            import seaborn as sns
            df = sns.load_dataset("titanic")
        logger.info(f"Dataset charge : {len(df)} lignes, {len(df.columns)} colonnes")
    except Exception as e:
        raise RuntimeError(f"Impossible de charger le dataset Titanic : {e}")
    df = clean_data(df)
    return df


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rename_map = {
        "PassengerId": "passenger_id", "Survived": "survived",
        "Pclass": "pclass", "Name": "name", "Sex": "sex",
        "Age": "age", "SibSp": "sibsp", "Parch": "parch",
        "Ticket": "ticket", "Fare": "fare",
        "Cabin": "cabin", "Embarked": "embarked",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    df["class"] = df["pclass"].map({1: "First", 2: "Second", 3: "Third"})
    df["embark_town"] = df["embarked"].map(
        {"S": "Southampton", "C": "Cherbourg", "Q": "Queenstown"})
    df["alive"] = df["survived"].map({1: "yes", 0: "no"})
    df["alone"] = (df["sibsp"] + df["parch"]) == 0
    df["deck"] = df["cabin"].str[0] if "cabin" in df.columns else None
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    median_age = df["age"].median()
    df["age"] = df["age"].fillna(median_age)

    def _who(row):
        if row["age"] < 16:
            return "child"
        return "man" if row["sex"] == "male" else "woman"

    df["who"] = df.apply(_who, axis=1)
    df["adult_male"] = (df["sex"] == "male") & (df["age"] >= 16)

    if "embarked" in df.columns:
        df["embarked"] = df["embarked"].fillna(df["embarked"].mode()[0])
    if "embark_town" in df.columns:
        df["embark_town"] = df["embark_town"].fillna(df["embark_town"].mode()[0])

    for col in ["deck", "cabin"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    df = df.reset_index(drop=True)
    logger.info(f"Nettoyage : {df.isnull().sum().sum()} NaN restants")
    return df


def get_age_group(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bins = [0, 12, 18, 35, 60, 100]
    labels = ["Enfant (0-12)", "Ado (13-18)", "Adulte (19-35)", "Senior (36-60)", "Aine (60+)"]
    df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels, right=True)
    return df