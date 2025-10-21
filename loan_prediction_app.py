import os
os.environ["STREAMLIT_SERVER_ENABLE_FILE_WATCHER"] = "false"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
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
.approved {
    color: #22abc5;
    font-weight: bold;
    font-size: 1.5rem;
}
.rejected {
    color: #F58C29;
    font-weight: bold;
    font-size: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# Create and Train Model
# -----------------------
@st.cache_resource
def create_and_train_model():
    """
    Create and train a loan prediction model from scratch
    """
    try:
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Features for loan prediction
        data = {
            'montant_credit': np.random.normal(200000, 80000, n_samples),
            'salaire_emprunteur': np.random.normal(4000, 1500, n_samples),
            'salaire_co_emprunteur': np.random.normal(3000, 1200, n_samples),
            'apport_personnel': np.random.normal(30000, 15000, n_samples),
            'cout_projet': np.random.normal(250000, 90000, n_samples),
            'duree_emploi': np.random.randint(1, 20, n_samples),
            'nombre_credits': np.random.randint(0, 5, n_samples),
            'age': np.random.randint(25, 65, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Calculate derived features
        df['revenu_total'] = df['salaire_emprunteur'] + df['salaire_co_emprunteur']
        df['ratio_dette_revenu'] = df['montant_credit'] / (df['revenu_total'] * 12)
        df['ratio_apport'] = df['apport_personnel'] / df['cout_projet']
        df['ratio_pret_valeur'] = df['montant_credit'] / df['cout_projet']
        
        # Create target variable (loan approval)
        # Rules for approval:
        conditions = (
            (df['ratio_dette_revenu'] < 0.35) &
            (df['ratio_apport'] > 0.1) &
            (df['revenu_total'] > 3000) &
            (df['duree_emploi'] > 2) &
            (df['nombre_credits'] < 3)
        )
        
        df['approved'] = conditions.astype(int)
        
        # Add some noise to make it more realistic
        noise = np.random.random(n_samples) < 0.1
        df.loc[noise, 'approved'] = 1 - df.loc[noise, 'approved']
        
        # Prepare features for training
        feature_columns = [
            'montant_credit', 'salaire_emprunteur', 'salaire_co_emprunteur',
            'apport_personnel', 'cout_projet', 'duree_emploi', 'nombre_credits', 'age',
            'revenu_total', 'ratio_dette_revenu', 'ratio_apport', 'ratio_pret_valeur'
        ]
        
        X = df[feature_columns]
        y = df['approved']
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            min_samples_split=5,
            min_samples_leaf=2
        )
        
        model.fit(X_scaled, y)
        
        st.success("✅ Modèle entraîné avec succès!")
        return model, scaler, feature_columns
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la création du modèle: {e}")
        return None, None, None

# -----------------------
# Feature Engineering
# -----------------------
def calculate_derived_features(input_data):
    """Calculate derived financial features"""
    data = input_data.copy()
    
    # Calculate total income
    data['revenu_total'] = (
        data.get('salaire_emprunteur', 0.0) +
        data.get('salaire_co_emprunteur', 0.0)
    )
    
    # Calculate financial ratios
    data['ratio_dette_revenu'] = (
        data.get('montant_credit', 0.0) / (data['revenu_total'] * 12)
        if data['revenu_total'] > 0 else 1.0
    )
    
    data['ratio_apport'] = (
        data.get('apport_personnel', 0.0) / data.get('cout_projet', 1.0)
    )
    
    data['ratio_pret_valeur'] = (
        data.get('montant_credit', 0.0) / data.get('cout_projet', 1.0)
    )
    
    return data

def prepare_input_data(input_data, feature_columns, scaler):
    """Prepare input data for prediction"""
    # Create feature vector with all zeros
    df = pd.DataFrame({col: [0.0] for col in feature_columns})
    
    # Fill with actual values
    for feature in feature_columns:
        if feature in input_data:
            df[feature] = input_data[feature]
    
    # Scale features
    if scaler is not None:
        df_scaled = scaler.transform(df)
        return df_scaled
    else:
        return df.values

# -----------------------
# Risk Assessment
# -----------------------
def categorize_risk(probability):
    """Categorize risk based on probability"""
    if probability >= 80:
        return "Risque Très Faible", "🟢", "success"
    elif probability >= 60:
        return "Risque Faible", "🟡", "warning"
    elif probability >= 40:
        return "Risque Moyen", "🟠", "warning"
    elif probability >= 20:
        return "Risque Élevé", "🔴", "error"
    else:
        return "Risque Très Élevé", "💀", "error"

def get_recommendations(input_data, probability):
    """Generate recommendations based on input data"""
    recommendations = []
    
    # Debt-to-income ratio recommendations
    dti = input_data.get('ratio_dette_revenu', 0)
    if dti > 0.4:
        recommendations.append("📉 **Ratio dette/revenu élevé:** Envisagez de réduire le montant du prêt ou d'augmenter vos revenus.")
    elif dti < 0.2:
        recommendations.append("📈 **Bon ratio dette/revenu:** Votre capacité de remboursement est excellente.")
    
    # Down payment recommendations
    apport = input_data.get('ratio_apport', 0)
    if apport < 0.1:
        recommendations.append("💰 **Apport personnel faible:** Un apport de 20% ou plus améliorerait significativement vos chances.")
    elif apport > 0.2:
        recommendations.append("💎 **Excellent apport personnel:** Votre apport important réduit considérablement le risque.")
    
    # Income recommendations
    revenu = input_data.get('revenu_total', 0)
    if revenu < 3000:
        recommendations.append("💼 **Revenus modestes:** Envisagez d'ajouter un co-emprunteur ou d'augmenter vos sources de revenus.")
    elif revenu > 8000:
        recommendations.append("🚀 **Revenus solides:** Votre situation financière est très favorable.")
    
    # Loan amount recommendations
    pret = input_data.get('montant_credit', 0)
    if pret > 400000:
        recommendations.append("🏠 **Prêt important:** Assurez-vous que vos revenus peuvent supporter cette mensualité.")
    
    return recommendations

# -----------------------
# Main Application
# -----------------------
def main():
    # Header
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("""
        <div class="main-header">
            🏦 Prédicteur de Demande de Prêt
        </div>
        """, unsafe_allow_html=True)
    
    # Load/Create model
    model, scaler, feature_columns = create_and_train_model()
    
    if model is None:
        st.error("Impossible de créer le modèle. L'application ne peut pas fonctionner.")
        return
    
    # Define options
    categ_socio_prof_options = {
        "Cadres et professions intellectuelles supérieures": 4,
        "Professions intermédiaires": 3,
        "Employés": 2,
        "Ouvriers": 1,
        "Autres": 0
    }
    
    project_nature_options = {
        "Construction": 2,
        "Achat neuf": 1,
        "Achat ancien": 0
    }
    
    project_destination_options = {
        "Résidence principale": 2,
        "Investissement locatif": 1,
        "Résidence secondaire": 0
    }

    # Create tabs for better organization
    tab1, tab2 = st.tabs(["📋 Informations du Prêt", "📊 Résultats et Analyse"])
    
    with tab1:
        with st.form("loan_form"):
            st.markdown('<div class="section-header">Informations Personnelles</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                age = st.slider("Âge de l'emprunteur", 25, 65, 35)
                duree_emploi = st.slider("Ancienneté dans l'emploi (années)", 1, 20, 5)
                categ_socio_prof = st.selectbox("Catégorie Socio-Professionnelle", list(categ_socio_prof_options.keys()))
                nombre_credits = st.slider("Nombre de crédits en cours", 0, 5, 0)
            
            with col2:
                salaire_emprunteur = st.number_input("Salaire Mensuel Emprunteur (€)", min_value=0, value=3000, step=100)
                salaire_co_emprunteur = st.number_input("Salaire Mensuel Co-Emprunteur (€)", min_value=0, value=2000, step=100)
                project_nature = st.selectbox("Nature du Projet", list(project_nature_options.keys()))
                project_destination = st.selectbox("Destination du Projet", list(project_destination_options.keys()))
            
            st.markdown('<div class="section-header">Détails Financiers du Projet</div>', unsafe_allow_html=True)
            
            col3, col4 = st.columns(2)
            
            with col3:
                montant_credit = st.number_input("Montant du Crédit Demandé (€)", min_value=0, value=200000, step=1000)
                cout_projet = st.number_input("Coût Total du Projet (€)", min_value=0, value=250000, step=1000)
            
            with col4:
                apport_personnel = st.number_input("Apport Personnel (€)", min_value=0, value=30000, step=1000)
                duree_pret = st.slider("Durée du Prêt (années)", 5, 25, 20)
            
            submitted = st.form_submit_button("🎯 Analyser la Demande de Prêt")
    
    if submitted:
        with tab2:
            # Prepare input data
            input_data = {
                'montant_credit': montant_credit,
                'salaire_emprunteur': salaire_emprunteur,
                'salaire_co_emprunteur': salaire_co_emprunteur,
                'apport_personnel': apport_personnel,
                'cout_projet': cout_projet,
                'duree_emploi': duree_emploi,
                'nombre_credits': nombre_credits,
                'age': age,
                'categorie_socio_prof': categ_socio_prof_options[categ_socio_prof],
                'nature_projet': project_nature_options[project_nature],
                'destination_projet': project_destination_options[project_destination]
            }
            
            # Calculate derived features
            input_data = calculate_derived_features(input_data)
            
            try:
                # Prepare data for model
                prepared_data = prepare_input_data(input_data, feature_columns, scaler)
                
                # Make prediction
                probability = model.predict_proba(prepared_data)[0, 1] * 100
                
                # Display results
                st.markdown('<div class="section-header">📈 Résultats de l\'Analyse</div>', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Score d'Acceptation", f"{probability:.1f}%")
                
                with col2:
                    is_approved = probability >= 50
                    status_text = "✅ APPROUVÉ" if is_approved else "❌ REFUSÉ"
                    status_class = "approved" if is_approved else "rejected"
                    st.markdown(f'<div class="{status_class}">{status_text}</div>', unsafe_allow_html=True)
                
                with col3:
                    risk_level, emoji, _ = categorize_risk(probability)
                    st.metric("Niveau de Risque", f"{emoji} {risk_level}")
                
                with col4:
                    mensualite_estimee = (montant_credit * 0.045) / 12  # Estimation simplifiée
                    st.metric("Mensualité Estimée", f"{mensualite_estimee:,.0f} €")
                
                # Financial metrics
                st.markdown('<div class="section-header">📊 Métriques Financières</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f'<div class="metric-card"><span class="info-label">Revenu Mensuel Total:</span> <span class="info-value">{input_data["revenu_total"]:,.0f} €</span></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-card"><span class="info-label">Ratio Dette/Revenu:</span> <span class="info-value">{input_data["ratio_dette_revenu"]:.2f}</span></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-card"><span class="info-label">Ancienneté Professionnelle:</span> <span class="info-value">{duree_emploi} ans</span></div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f'<div class="metric-card"><span class="info-label">Apport Personnel:</span> <span class="info-value">{input_data["ratio_apport"]*100:.1f}%</span></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-card"><span class="info-label">Ratio Prêt/Valeur:</span> <span class="info-value">{input_data["ratio_pret_valeur"]:.2f}</span></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-card"><span class="info-label">Crédits en Cours:</span> <span class="info-value">{nombre_credits}</span></div>', unsafe_allow_html=True)
                
                # Recommendations
                st.markdown('<div class="section-header">💡 Recommandations</div>', unsafe_allow_html=True)
                
                recommendations = get_recommendations(input_data, probability)
                
                if probability >= 70:
                    st.success("**🎉 Excellente candidature!** Votre demande présente de très bonnes chances d'approbation.")
                    for rec in recommendations:
                        if "excellent" in rec.lower() or "bon" in rec.lower():
                            st.info(rec)
                elif probability >= 50:
                    st.warning("**📝 Candidature acceptable.** Votre demande pourrait être approuvée avec quelques ajustements.")
                    for rec in recommendations:
                        st.info(rec)
                else:
                    st.error("**⚠️ Candidature à risque.** Nous recommandons d'améliorer certains aspects avant de soumettre.")
                    for rec in recommendations:
                        st.error(rec)
                
                # Visualization
                st.markdown('<div class="section-header">📊 Analyse Graphique</div>', unsafe_allow_html=True)
                
                fig, ax = plt.subplots(1, 2, figsize=(12, 4))
                
                # Risk gauge
                categories = ['Très Élevé', 'Élevé', 'Moyen', 'Faible', 'Très Faible']
                values = [0, 20, 40, 60, 80, 100]
                colors = ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#27ae60']
                
                ax[0].barh(0, probability, color=colors[min(int(probability/20), 4)], height=0.5)
                ax[0].set_xlim(0, 100)
                ax[0].set_xlabel('Probabilité d\'Acceptation (%)')
                ax[0].set_title('Niveau de Risque')
                ax[0].grid(True, alpha=0.3)
                
                # Key metrics radar (simplified)
                metrics = ['Revenu', 'Apport', 'Stabilité', 'Endettement']
                scores = [
                    min(input_data['revenu_total'] / 8000 * 100, 100),
                    min(input_data['ratio_apport'] * 500, 100),
                    min(duree_emploi * 5, 100),
                    max(100 - input_data['ratio_dette_revenu'] * 200, 0)
                ]
                
                angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False)
                scores += scores[:1]
                angles = np.concatenate((angles, [angles[0]]))
                
                ax[1].plot(angles, scores, 'o-', linewidth=2)
                ax[1].fill(angles, scores, alpha=0.25)
                ax[1].set_xticks(angles[:-1])
                ax[1].set_xticklabels(metrics)
                ax[1].set_ylim(0, 100)
                ax[1].set_title('Profil Financier')
                ax[1].grid(True)
                
                plt.tight_layout()
                st.pyplot(fig)
                
            except Exception as e:
                st.error(f"Erreur lors de l'analyse: {str(e)}")
                st.info("Veuillez vérifier les valeurs saisies et réessayer.")

if __name__ == "__main__":
    main()
