# Loan Application Predictor Model

This project uses a machine learning model to predict the acceptance of loan applications based on financial, personal, and project-related information provided by the user. The model is trained on historical loan data and evaluates the risk of each application using features such as income, assets, credit history, project costs, and more.

## Key Features

- **Input:** Borrower and co-borrower financial details, project information, existing credits, and assets.
- **Output:** Probability of loan acceptance, risk category, and confidence level.
- **Model:** The model is a supervised learning classifier (such as Random Forest, Gradient Boosting, or similar), trained to distinguish between accepted and rejected loan applications.
- **Preprocessing:** Includes feature engineering (e.g., debt-to-income ratio, loan-to-value, total household income) and scaling of numeric features.
- **User Interface:** Built with Streamlit for easy data entry and instant predictions.

## Usage

1. Enter the required financial and project details in the app.
2. The model analyzes the data and provides a prediction with risk assessment.
3. Results include acceptance probability, risk level, and key financial metrics.

## Confidentiality

All data files are ignored in version control for privacy and security. Only the model code and interface are included in the repository.