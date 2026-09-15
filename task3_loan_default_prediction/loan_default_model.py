import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

# load the loan book
df = pd.read_csv("Task_3_and_4_Loan_Data.csv")

# rather than feeding in raw dollar amounts, use ratios - they tend to
# generalize better across borrowers with very different income levels
df["payment_to_income"] = df["loan_amt_outstanding"] / df["income"]
df["debt_to_income"] = df["total_debt_outstanding"] / df["income"]

features = ["credit_lines_outstanding", "debt_to_income",
            "payment_to_income", "years_employed", "fico_score"]

clf = LogisticRegression(random_state=0, solver="liblinear", tol=1e-5, max_iter=10000)
clf.fit(df[features], df["default"])

print("coefficients:", clf.coef_)
print("intercept:", clf.intercept_)

# quick check of how well it's doing on the training data itself
y_pred = clf.predict(df[features])
misclass_rate = (1.0 * (abs(df["default"] - y_pred)).sum()) / len(df)
fpr, tpr, thresholds = metrics.roc_curve(df["default"], y_pred)
auc = metrics.auc(fpr, tpr)

print("misclassification rate:", round(misclass_rate, 4))
print("AUC:", round(auc, 4))

RECOVERY_RATE = 0.10  # given in the brief

def predict_expected_loss(credit_lines_outstanding, loan_amt_outstanding,
                           total_debt_outstanding, income, years_employed, fico_score):
    """
    Takes the raw loan details for a borrower, builds the same ratio
    features the model was trained on, and returns the PD plus the
    expected loss on the loan.
    """
    payment_to_income = loan_amt_outstanding / income
    debt_to_income = total_debt_outstanding / income

    loan_features = pd.DataFrame([{
        "credit_lines_outstanding": credit_lines_outstanding,
        "debt_to_income": debt_to_income,
        "payment_to_income": payment_to_income,
        "years_employed": years_employed,
        "fico_score": fico_score,
    }])

    pd_estimate = clf.predict_proba(loan_features)[:, 1][0]
    expected_loss = pd_estimate * (1 - RECOVERY_RATE) * loan_amt_outstanding

    return {
        "probability_of_default": round(float(pd_estimate), 4),
        "expected_loss": round(float(expected_loss), 2),
    }


if __name__ == "__main__":
    # a borrower who looks fairly safe
    result1 = predict_expected_loss(
        credit_lines_outstanding=1,
        loan_amt_outstanding=3000,
        total_debt_outstanding=4000,
        income=70000,
        years_employed=6,
        fico_score=700,
    )
    print("\nBorrower 1 (looks low risk):", result1)

    # a borrower who looks riskier
    result2 = predict_expected_loss(
        credit_lines_outstanding=5,
        loan_amt_outstanding=8000,
        total_debt_outstanding=15000,
        income=28000,
        years_employed=1,
        fico_score=580,
    )
    print("Borrower 2 (looks higher risk):", result2)

    # sanity check against a real row from the data
    row = df.iloc[0]
    result3 = predict_expected_loss(
        credit_lines_outstanding=row["credit_lines_outstanding"],
        loan_amt_outstanding=row["loan_amt_outstanding"],
        total_debt_outstanding=row["total_debt_outstanding"],
        income=row["income"],
        years_employed=row["years_employed"],
        fico_score=row["fico_score"],
    )
    print(f"Borrower 3 (real row, actual default was {row['default']}):", result3)
