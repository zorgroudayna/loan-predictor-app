import os
os.environ["STREAMLIT_SERVER_ENABLE_FILE_WATCHER"] = "false"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="Prédicteur de Demande de Prêt",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------
# CSS Styles
# -----------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');

.main-header {
    font-family: 'Montserrat', Arial, sans-serif;
    font-weight: 800;
    font-size: 2.2rem;
    color: #22abc5;
    text-align: center;
    margin-bottom: 2rem;
    letter-spacing: 1px;
}
.section-header {
    font-family: 'Montserrat', Arial, sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    text-align: left;
    margin-top: 15px;
    margin-bottom: 10px;
    width: 100%;
    border-bottom: 3px solid #22abc5;
    color: #22abc5;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.stButton>button {
    width: 100%;
    background-color: #22abc5 !important;
    color: #fff !important;
    font-size: 1.2rem !important;
    padding: 0.7rem 0 !important;
    font-family: 'Montserrat', Arial, sans-serif !important;
    border-radius: 8px !important;
    border: none !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    margin-top: 18px !important;
    margin-bottom: 8px !important;
}
.stButton>button:hover {
    background-color: #F58C29 !important;
}
.info-label {
    font-family: 'Montserrat', Arial, sans-serif;
    font-size: 1rem;
    color: #22abc5;
    font-weight: 500;
}
.info-value {
    font-family: 'Montserrat', Arial, sans-serif;
    font-size: 1rem;
    color: #F58C29;
    font-weight: 700;
}
.metric-card {
    background-color: #eaf7fa;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #22abc5;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# Model Loading with Fallback
# -----------------------
@st.cache_resource
def load_model_with_fallback():
    """
    Try to load model, if not found use a simple fallback model
    """
    try:
        # Try to load existing model
        model = joblib.load('ultra_fast_model.pkl')
        st.success("✅ Modèle chargé avec succès!")
        return model, None
    except FileNotFoundError:
        st.warning("⚠️ Modèle principal non trouvé. Utilisation d'un modèle de secours...")
        # Create a simple fallback model
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.datasets import make_classification
        
        # Create a simple model for demonstration
        X, y = make_classification(n_samples=100, n_features=10, random_state=42)
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        return model, None
    except Exception as e:
        st.error(f"❌ Erreur de chargement du modèle: {e}")
        return None, None

# -----------------------
# Feature Engineering
# -----------------------
def calculate_derived_features(input_data):
    data = input_data.copy()
    
    # Calculate total income
    data['total_household_income'] = (
        data.get('borrower_salaire_mensuel', 0.0) +
        data.get('borrower_revenu_foncier', 0.0) +
        data.get('borrower_autres_revenus', 0.0) +
        data.get('co_borrower_salaire_mensuel', 0.0) +
        data.get('co_borrower_autres_revenus', 0.0)
    )
    
    # Calculate total project cost
    data['total_project_cost'] = (
        data.get('cost_terrain', 0.0) +
        data.get('cost_logement', 0.0) +
        data.get('cost_travaux', 0.0) +
        data.get('cost_frais_notaire', 0.0)
    )
    
    # Calculate financial ratios
    data['debt_to_income_ratio'] = (
        data.get('montant_credit_initio', 0.0) / data['total_household_income']
        if data['total_household_income'] > 0 else 0.0
    )
    
    data['apport_percentage'] = (
        data.get('financing_apport_personnel', 0.0) / data['total_project_cost']
        if data['total_project_cost'] > 0 else 0.0
    )
    
    data['loan_to_value'] = (
        data.get('financing_pret_principal', 0.0) / data['total_project_cost']
        if data['total_project_cost'] > 0 else 0.0
    )
    
    return data

def prepare_input_data(input_data):
    """Prepare input data for prediction"""
    # Create feature vector
    features = [
        'montant_credit_initio', 'borrower_salaire_mensuel', 'co_borrower_salaire_mensuel',
        'total_household_income', 'total_project_cost', 'financing_apport_personnel',
        'financing_pret_principal', 'debt_to_income_ratio', 'apport_percentage', 'loan_to_value'
    ]
    
    # Create DataFrame with all features
    df = pd.DataFrame({f: [0.0] for f in features})
    
    # Fill with actual values
    for feature in features:
        if feature in input_data:
            df[feature] = input_data[feature]
    
    return df

# -----------------------
# Risk Assessment
# -----------------------
def calculate_risk_score(input_data):
    """Calculate risk score based on input parameters"""
    score = 50  # Base score
    
    # Income factors
    total_income = input_data.get('total_household_income', 0)
    if total_income > 10000:
        score += 20
    elif total_income > 5000:
        score += 10
    elif total_income < 2000:
        score -= 15
    
    # Debt-to-income ratio
    dti = input_data.get('debt_to_income_ratio', 0)
    if dti < 0.3:
        score += 15
    elif dti > 0.5:
        score -= 20
    
    # Down payment
    apport = input_data.get('apport_percentage', 0)
    if apport > 0.2:
        score += 15
    elif apport < 0.1:
        score -= 10
    
    # Loan amount
    loan_amount = input_data.get('montant_credit_initio', 0)
    if loan_amount < 100000:
        score += 5
    elif loan_amount > 500000:
        score -= 10
    
    return max(0, min(100, score))

def categorize_risk(probability):
    if probability >= 80:
        return "Risque Très Faible", "🟢"
    elif probability >= 60:
        return "Risque Faible", "🟡"
    elif probability >= 40:
        return "Risque Moyen", "🟠"
    elif probability >= 20:
        return "Risque Élevé", "🔴"
    else:
        return "Risque Très Élevé", "💀"

# -----------------------
# Main Application
# -----------------------
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        🏦 Prédicteur de Demande de Prêt
    </div>
    """, unsafe_allow_html=True)
    
    # Load model
    model, scaler = load_model_with_fallback()
    
    if model is None:
        st.error("Impossible de charger le modèle. L'application ne peut pas fonctionner.")
        return
    
    # Define options
    categ_socio_prof_options = {
        "Agriculteurs exploitants": 0,
        "Artisans, commerçants, chefs d'entreprise": 1,
        "Cadres et professions intellectuelles supérieures": 2,
        "Professions intermédiaires": 3,
        "Employés": 4,
        "Ouvriers": 5,
        "Retraités": 6,
        "Autres personnes sans activité professionnelle": 7
    }
    
    project_nature_options = {
        "Construction": 0,
        "Achat neuf": 1,
        "Achat ancien": 2,
        "Travaux": 3
    }
    
    project_destination_options = {
        "Résidence principale": 0,
        "Résidence secondaire": 1,
        "Investissement locatif": 2
    }
    
    # Create form
    with st.form("loan_form"):
        st.markdown('<div class="section-header">Informations de Base</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            montant_credit_initio = st.number_input("Montant du Crédit (€)", min_value=0, value=100000, step=1000)
            borrower_salaire_mensuel = st.number_input("Salaire Mensuel Emprunteur (€)", min_value=0, value=3000, step=100)
            co_borrower_salaire_mensuel = st.number_input("Salaire Mensuel Co-Emprunteur (€)", min_value=0, value=2000, step=100)
            financing_apport_personnel = st.number_input("Apport Personnel (€)", min_value=0, value=20000, step=1000)
        
        with col2:
            total_project_cost = st.number_input("Coût Total du Projet (€)", min_value=0, value=120000, step=1000)
            project_nature = st.selectbox("Nature du Projet", list(project_nature_options.keys()))
            project_destination = st.selectbox("Destination", list(project_destination_options.keys()))
            co_borrower_categ_socio_prof = st.selectbox("Catégorie Socio-Professionnelle", list(categ_socio_prof_options.keys()))
        
        submitted = st.form_submit_button("📊 Analyser la Demande")
    
    if submitted:
        # Prepare input data
        input_data = {
            'montant_credit_initio': montant_credit_initio,
            'borrower_salaire_mensuel': borrower_salaire_mensuel,
            'co_borrower_salaire_mensuel': co_borrower_salaire_mensuel,
            'financing_apport_personnel': financing_apport_personnel,
            'total_project_cost': total_project_cost,
            'co_borrower_categ_socio_prof': categ_socio_prof_options[co_borrower_categ_socio_prof],
            'project_nature': project_nature_options[project_nature],
            'project_destination': project_destination_options[project_destination],
        }
        
        # Calculate derived features
        input_data = calculate_derived_features(input_data)
        
        try:
            # Prepare data for model
            prepared_data = prepare_input_data(input_data)
            
            # Make prediction
            if hasattr(model, 'predict_proba'):
                probability = model.predict_proba(prepared_data)[0, 1] * 100
            else:
                # Use rule-based approach if model doesn't have predict_proba
                probability = calculate_risk_score(input_data)
            
            # Display results
            st.markdown('<div class="section-header">Résultats de l\'Analyse</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Score d'Acceptation", f"{probability:.1f}%")
            
            with col2:
                is_approved = probability >= 50
                status = "✅ APPROUVÉ" if is_approved else "❌ REFUSÉ"
                st.metric("Recommandation", status)
            
            with col3:
                risk_level, emoji = categorize_risk(probability)
                st.metric("Niveau de Risque", f"{emoji} {risk_level}")
            
            # Financial metrics
            st.markdown('<div class="section-header">Métriques Financières</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f'<div class="metric-card"><span class="info-label">Revenu Mensuel Total:</span> <span class="info-value">{input_data["total_household_income"]:,.0f} €</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-card"><span class="info-label">Ratio Dette/Revenu:</span> <span class="info-value">{input_data["debt_to_income_ratio"]:.2f}</span></div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'<div class="metric-card"><span class="info-label">Apport Personnel:</span> <span class="info-value">{input_data["apport_percentage"]*100:.1f}%</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-card"><span class="info-label">Ratio Prêt/Valeur:</span> <span class="info-value">{input_data["loan_to_value"]:.2f}</span></div>', unsafe_allow_html=True)
            
            # Recommendations
            st.markdown('<div class="section-header">Recommandations</div>', unsafe_allow_html=True)
            
            if probability >= 70:
                st.success("**Excellente candidature!** Votre demande présente de très bonnes chances d'approbation.")
            elif probability >= 50:
                st.warning("**Candidature acceptable.** Votre demande pourrait être approuvée avec quelques ajustements.")
            else:
                st.error("**Candidature à risque.** Nous recommandons d'améliorer certains aspects avant de soumettre.")
                
                if input_data['debt_to_income_ratio'] > 0.4:
                    st.info("💡 **Suggestion:** Réduisez votre ratio dette/revenu en augmentant vos revenus ou en diminuant le montant du prêt.")
                
                if input_data['apport_percentage'] < 0.1:
                    st.info("💡 **Suggestion:** Augmentez votre apport personnel à au moins 10% du coût total.")
        
        except Exception as e:
            st.error(f"Erreur lors de l'analyse: {str(e)}")
            st.info("Utilisation du système d'évaluation de secours...")
            
            # Fallback calculation
            probability = calculate_risk_score(input_data)
            st.metric("Score d'Acceptation (Estimation)", f"{probability:.1f}%")

if __name__ == "__main__":
    main()
