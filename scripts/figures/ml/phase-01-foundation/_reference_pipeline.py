"""A complete, runnable end-to-end pipeline — the one printed on the Roadmap page.

Every code line carries a ``# @stage:`` marker naming which part of the workflow
it belongs to. ``the-machine-learning-roadmap.py`` parses those markers to build
its figure, so the chart and the listing can never drift apart.

Blank lines, comments and imports are not counted.
"""

import joblib                                                   # @stage:serve
import pandas as pd                                             # @stage:load
from sklearn.compose import ColumnTransformer                   # @stage:encode
from sklearn.ensemble import HistGradientBoostingRegressor      # @stage:model
from sklearn.impute import SimpleImputer                        # @stage:clean
from sklearn.metrics import mean_absolute_error                 # @stage:evaluate
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline                           # @stage:encode
from sklearn.preprocessing import OneHotEncoder, StandardScaler  # @stage:encode


def run(csv_path: str, target: str, out_path: str = "model.joblib"):
    df = pd.read_csv(csv_path)                                  # @stage:load
    print(df.shape)                                             # @stage:load
    print(df.dtypes)                                            # @stage:load
    print(df.isna().mean().sort_values(ascending=False).head())  # @stage:load
    print(df[target].describe())                                # @stage:load

    y = df.pop(target)                                          # @stage:split
    X_train, X_test, y_train, y_test = train_test_split(        # @stage:split
        X := df, y, test_size=0.2, random_state=42)             # @stage:split

    num_cols = X.select_dtypes("number").columns.tolist()       # @stage:clean
    cat_cols = X.select_dtypes("object").columns.tolist()       # @stage:clean
    num_impute = SimpleImputer(strategy="median")               # @stage:clean
    cat_impute = SimpleImputer(strategy="most_frequent")        # @stage:clean

    numeric = Pipeline([("impute", num_impute),                 # @stage:encode
                        ("scale", StandardScaler())])           # @stage:encode
    categorical = Pipeline([                                    # @stage:encode
        ("impute", cat_impute),                                 # @stage:encode
        ("onehot", OneHotEncoder(handle_unknown="ignore"))])    # @stage:encode
    prep = ColumnTransformer([("num", numeric, num_cols),       # @stage:encode
                              ("cat", categorical, cat_cols)])  # @stage:encode

    model = HistGradientBoostingRegressor(random_state=42)      # @stage:model
    pipe = Pipeline([("prep", prep), ("model", model)])         # @stage:model

    grid = {"model__max_depth": [None, 4, 8],                   # @stage:tune
            "model__learning_rate": [0.05, 0.1, 0.2]}           # @stage:tune
    search = GridSearchCV(pipe, grid, cv=5,                     # @stage:tune
                          scoring="neg_mean_absolute_error",    # @stage:tune
                          n_jobs=-1)                            # @stage:tune
    search.fit(X_train, y_train)                                # @stage:tune
    print(search.best_params_, -search.best_score_)             # @stage:tune

    best = search.best_estimator_                               # @stage:evaluate
    preds = best.predict(X_test)                                # @stage:evaluate
    mae = mean_absolute_error(y_test, preds)                    # @stage:evaluate
    baseline = mean_absolute_error(y_test,                      # @stage:evaluate
                                   [y_train.median()] * len(y_test))  # @stage:evaluate
    print(f"test MAE {mae:.3f} vs baseline {baseline:.3f}")     # @stage:evaluate

    joblib.dump(best, out_path)                                 # @stage:serve
    reloaded = joblib.load(out_path)                            # @stage:serve
    assert reloaded.predict(X_test[:5]).shape == (5,)           # @stage:serve
    return best, mae                                            # @stage:serve
