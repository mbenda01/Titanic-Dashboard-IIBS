# tests/test_loader.py
import sys
import os
import pytest
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from data.loader import load_titanic, clean_data, get_age_group  # noqa: E402


@pytest.fixture(scope="module")
def df():
    return load_titanic()


@pytest.fixture(scope="module")
def df_with_age_groups(df):
    return get_age_group(df)


class TestLoadTitanic:

    def test_dataframe_not_empty(self, df):
        assert len(df) > 0, "Le DataFrame est vide !"

    def test_minimum_rows(self, df):
        assert len(df) >= 800, f"Trop peu de lignes : {len(df)}"

    def test_returns_dataframe(self, df):
        assert isinstance(df, pd.DataFrame)

    def test_expected_columns_exist(self, df):
        required = ["survived", "pclass", "sex", "age", "fare"]
        for col in required:
            assert col in df.columns, f"Colonne manquante : {col}"

    def test_survived_column_binary(self, df):
        assert set(df["survived"].unique()).issubset({0, 1}), \
            f"Valeurs inattendues dans 'survived' : {df['survived'].unique()}"

    def test_pclass_valid_values(self, df):
        assert set(df["pclass"].unique()).issubset({1, 2, 3}), \
            f"Valeurs inattendues dans 'pclass' : {df['pclass'].unique()}"

    def test_sex_valid_values(self, df):
        assert set(df["sex"].unique()).issubset({"male", "female"}), \
            f"Valeurs inattendues dans 'sex' : {df['sex'].unique()}"


class TestCleanData:

    def test_no_null_age(self, df):
        assert df["age"].isnull().sum() == 0, \
            f"{df['age'].isnull().sum()} valeurs nulles dans 'age'"

    def test_no_null_embarked(self, df):
        assert df["embarked"].isnull().sum() == 0, \
            f"{df['embarked'].isnull().sum()} valeurs nulles dans 'embarked'"

    def test_deck_column_removed(self, df):
        assert "deck" not in df.columns, \
            "La colonne 'deck' n'a pas ete supprimee"

    def test_age_within_range(self, df):
        assert df["age"].min() >= 0, "Age negatif detecte"
        assert df["age"].max() <= 120, f"Age impossible : {df['age'].max()}"

    def test_fare_not_negative(self, df):
        assert (df["fare"] >= 0).all(), "Tarif negatif detecte"

    def test_clean_data_preserves_rows(self):
        cache = os.path.expanduser("~/seaborn-data/titanic.csv")
        if os.path.exists(cache):
            raw = pd.read_csv(cache)
        else:
            raw = __import__('seaborn').load_dataset("titanic")
        cleaned = clean_data(raw)
        assert len(cleaned) == len(raw), \
            f"Des lignes ont ete supprimees : {len(raw)} -> {len(cleaned)}"

    def test_clean_data_returns_copy(self):
        cache = os.path.expanduser("~/seaborn-data/titanic.csv")
        if os.path.exists(cache):
            raw = pd.read_csv(cache)
        else:
            raw = __import__('seaborn').load_dataset("titanic")
        cleaned = clean_data(raw)
        assert cleaned is not raw, "clean_data retourne la meme reference"


class TestGetAgeGroup:

    def test_age_group_column_added(self, df_with_age_groups):
        assert "age_group" in df_with_age_groups.columns

    def test_age_group_no_nulls(self, df_with_age_groups):
        nulls = df_with_age_groups["age_group"].isnull().sum()
        assert nulls == 0, f"{nulls} valeurs nulles dans 'age_group'"

    def test_age_group_expected_categories(self, df_with_age_groups):
        expected = {"Enfant (0-12)", "Ado (13-18)", "Adulte (19-35)",
                    "Senior (36-60)", "Aine (60+)"}
        actual = set(df_with_age_groups["age_group"].cat.categories)
        assert expected == actual, f"Categories inattendues : {actual}"

    def test_original_df_unchanged(self, df):
        original_cols = set(df.columns)
        get_age_group(df)
        assert set(df.columns) == original_cols, \
            "Le DataFrame original a ete modifie"


class TestBasicStats:

    def test_survival_rate_plausible(self, df):
        rate = df["survived"].mean()
        assert 0.30 <= rate <= 0.50, \
            f"Taux de survie improbable : {rate:.1%}"

    def test_female_survival_higher_than_male(self, df):
        female_rate = df[df["sex"] == "female"]["survived"].mean()
        male_rate = df[df["sex"] == "male"]["survived"].mean()
        assert female_rate > male_rate, \
            "Le taux de survie femmes < hommes (inattendu)"

    def test_first_class_best_survival(self, df):
        class1 = df[df["pclass"] == 1]["survived"].mean()
        class3 = df[df["pclass"] == 3]["survived"].mean()
        assert class1 > class3, \
            "1ere classe n'a pas un meilleur taux que 3eme (inattendu)"