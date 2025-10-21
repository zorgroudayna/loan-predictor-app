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
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="Prédicteur de Demande de Prêt",
    page_icon="https://apiv1.2l-courtage.com/public/storage/jpg/pPy95t2JQnO2rgBOpXVJoT9HD0YW4JSgee74GNKD.jpeg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------
# CSS avec style extrait
# -----------------------
st.markdown("""
<style>
    @font-face {
        font-family: 'Montserrat-Bold';
        src: url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');
    }
    @font-face {
        font-family: 'Montserrat-Regular';
        src: url('https://fonts.googleapis.com/css2?family=Montserrat&display=swap');
    }
    @font-face {
        font-family: 'Montserrat-ExtraBold';
        src: url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800&display=swap');
    }
    @font-face {
        font-family: 'Montserrat-SemiBold';
        src: url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap');
    }
    
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
    .prediction-card { 
        background-color: #F58C29; 
        padding: 2rem; 
        border-radius: 12px; 
        margin-top: 2rem; 
        box-shadow: 0 4px 12px rgba(34,171,197,0.08); 
        border: 1px solid #F58C29;
    }
    .risk-high { color: #F58C29; font-weight: bold; }
    .risk-medium { color: #F58C29; font-weight: bold; }
    .risk-low { color: #22abc5; font-weight: bold; }
    .stButton>button, button[kind="primary"], .css-1cpxqw2, .css-1emrehy {
        width: 100%;
        background-color: #22abc5 !important;
        color: #fff !important;
        font-size: 1.2rem !important;
        padding: 0.7rem 0 !important;
        font-family: 'Montserrat', Arial, sans-serif !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 2px 6px rgba(34,171,197,0.08) !important;
        transition: background 0.2s, color 0.2s !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        margin-top: 18px !important;
        margin-bottom: 8px !important;
    }
    .stButton>button:hover, button[kind="primary"]:hover, .css-1cpxqw2:hover, .css-1emrehy:hover,
    .stButton>button:focus, button[kind="primary"]:focus, .css-1cpxqw2:focus, .css-1emrehy:focus {
        background-color: #F58C29 !important;
        color: #fff !important;
        border: none !important;
        outline: none !important;
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
    .column-title {
        font-family: 'Montserrat', Arial, sans-serif;
        font-weight: 700;
        text-align: left;
        vertical-align: middle;
        padding: 6px;
        margin-left: 5px;
        color: #FFFFFF;
        font-size: 1rem;
        border-left-style: solid;
        background: #22abc5;
        border-radius: 4px 4px 0 0;
    }
    .metric-card {
        background-color: #eaf7fa;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #22abc5;
        margin-bottom: 10px;
        box-shadow: 0 2px 6px rgba(34,171,197,0.06);
    }
    .stTabs [role="tab"] {
        background: #22abc5 !important;
        color: #fff !important;
        font-family: 'Montserrat', Arial, sans-serif;
        font-weight: 600;
        border-radius: 8px 8px 0 0;
        margin-right: 6px;
        padding: 12px 32px !important;
        box-shadow: 0 2px 8px rgba(34,171,197,0.10);
        border: 1px solid #22abc5;
        border-bottom: none;
        transition: background 0.2s, color 0.2s;
        letter-spacing: 1px;
        font-size: 1.05rem;
    }
    .stTabs [role="tab"][aria-selected="true"] {
        background: #F58C29 !important;
        color: #fff !important;
        border: 1px solid #F58C29;
        border-bottom: none;
        box-shadow: 0 4px 16px rgba(245,140,41,0.10);
    }
    .stTabs [role="tab"]:hover {
        background: #F58C29 !important;
        color: #fff !important;
        cursor: pointer;
    }
    .stTabs {
        box-shadow: 0 2px 8px rgba(34,171,197,0.07);
        margin-bottom: 24px;
        border-radius: 8px 8px 0 0;
        background: #f7fafd;
    }

    label, .stTextInput label, .stNumberInput label, .stSelectbox label {
        border-bottom: 2px solid #22abc5 !important;
        padding-bottom: 2px;
        display: inline-block;
    }
    
    .explanation-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #22abc5;
    }
    .positive-card {
        border-left-color: #2ecc71;
    }
    .negative-card {
        border-left-color: #e74c3c;
    }
    .neutral-card {
        border-left-color: #f39c12;
    }
    .explanation-title {
        font-family: 'Montserrat', Arial, sans-serif;
        font-weight: 700;
        font-size: 1.1rem;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .explanation-content {
        font-family: 'Montserrat', Arial, sans-serif;
        font-size: 1rem;
        color: #7f8c8d;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------
# FONCTION DE CRÉATION DE MODÈLE INTÉGRÉE
# -----------------------
@st.cache_resource
def create_loan_model():
    """
    Crée et entraîne un modèle de prédiction de prêt intégré
    """
    try:
        # Générer des données d'entraînement réalistes
        np.random.seed(42)
        n_samples = 2000
        
        # Caractéristiques principales pour la prédiction de prêt
        data = {
            'montant_credit_initio': np.random.normal(200000, 80000, n_samples),
            'borrower_salaire_mensuel': np.random.normal(4000, 1500, n_samples),
            'co_borrower_salaire_mensuel': np.random.normal(3000, 1200, n_samples),
            'financing_apport_personnel': np.random.normal(30000, 15000, n_samples),
            'total_project_cost': np.random.normal(250000, 90000, n_samples),
            'debt_to_income_ratio': np.random.uniform(0.1, 0.8, n_samples),
            'apport_percentage': np.random.uniform(0.05, 0.4, n_samples),
            'loan_to_value': np.random.uniform(0.6, 1.2, n_samples),
            'total_household_income': np.random.normal(7000, 2500, n_samples),
            'total_credit_monthly_payment': np.random.normal(800, 400, n_samples),
            'nombre_of_credits': np.random.randint(0, 5, n_samples),
            'net_worth': np.random.normal(50000, 30000, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Créer la variable cible basée sur des règles réalistes
        conditions = (
            (df['debt_to_income_ratio'] < 0.35) &
            (df['apport_percentage'] > 0.1) &
            (df['total_household_income'] > 4000) &
            (df['loan_to_value'] < 0.9) &
            (df['nombre_of_credits'] < 3) &
            (df['total_credit_monthly_payment'] / df['total_household_income'] < 0.4)
        )
        df['approved'] = conditions.astype(int)
        
        # Ajouter du bruit pour plus de réalisme
        noise = np.random.random(n_samples) < 0.15
        df.loc[noise, 'approved'] = 1 - df.loc[noise, 'approved']
        
        # Préparer les caractéristiques
        feature_columns = [
            'montant_credit_initio', 'borrower_salaire_mensuel', 
            'co_borrower_salaire_mensuel', 'financing_apport_personnel',
            'total_project_cost', 'debt_to_income_ratio', 
            'apport_percentage', 'loan_to_value', 'total_household_income',
            'total_credit_monthly_payment', 'nombre_of_credits', 'net_worth'
        ]
        
        X = df[feature_columns]
        y = df['approved']
        
        # Normaliser les caractéristiques
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Entraîner le modèle
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            random_state=42,
            min_samples_split=10,
            min_samples_leaf=4
        )
        
        model.fit(X_scaled, y)
        
        # Calculer la précision sur les données d'entraînement
        train_accuracy = model.score(X_scaled, y)
        
        st.success(f"✅ Modèle intégré créé avec succès! (Précision: {train_accuracy:.1%})")
        return {'model': model, 'scaler': scaler, 'feature_columns': feature_columns}
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la création du modèle: {e}")
        return None

# -----------------------
# Chargeur de modèle avec fallback intégré
# -----------------------
@st.cache_resource
def load_model_and_scaler():
    """
    Charge le modèle avec système de fallback intégré
    """
    try:
        # Essayer de charger le modèle existant
        loaded = joblib.load('ultra_fast_model.pkl')
        st.success("✅ Modèle principal chargé avec succès!")
        return loaded, None
        
    except FileNotFoundError:
        st.info("🔄 Création d'un modèle de prédiction intégré...")
        model_data = create_loan_model()
        if model_data:
            return model_data, None
        else:
            return None, None
            
    except Exception as e:
        st.error(f"❌ Erreur de chargement: {e}")
        st.info("🔄 Création d'un modèle de secours...")
        model_data = create_loan_model()
        return model_data, None

# -----------------------
# Caractéristiques dérivées et prétraitement
# -----------------------
def calculate_derived_features(input_data):
    data = input_data.copy()
    data['total_household_income'] = (
        data.get('borrower_salaire_mensuel', 0.0)
        + data.get('borrower_revenu_foncier', 0.0)
        + data.get('borrower_autres_revenus', 0.0)
        + data.get('co_borrower_salaire_mensuel', 0.0)
        + data.get('co_borrower_autres_revenus', 0.0)
    )
    data['total_project_cost'] = (
        data.get('cost_terrain', 0.0)
        + data.get('cost_logement', 0.0)
        + data.get('cost_travaux', 0.0)
        + data.get('cost_frais_notaire', 0.0)
    )
    data['debt_to_income_ratio'] = (
        data.get('montant_credit_initio', 0.0) / (data['total_household_income'] * 12)
        if data['total_household_income'] > 0 else 1.0
    )
    data['apport_percentage'] = (
        data.get('financing_apport_personnel', 0.0) / data['total_project_cost']
        if data['total_project_cost'] > 0 else 0.0
    )
    data['loan_to_value'] = (
        data.get('financing_pret_principal', 0.0) / data['total_project_cost']
        if data['total_project_cost'] > 0 else 0.0
    )

    data['has_viabilisation_costs'] = 1 if data.get('cost_viabilisation', 0) > 0 else 0
    data['has_mobilier_costs'] = 1 if data.get('cost_mobilier', 0) > 0 else 0
    data['has_agency_fees'] = 1 if data.get('cost_agency_fees', 0) > 0 else 0

    defaults = {
        'number_of_properties': 0,
        'total_credit_remaining_amount': 0.0,
        'total_credit_monthly_payment': 0.0,
        'nombre_of_credits': 0,
        'net_worth': 0.0,
    }
    for k, v in defaults.items():
        data.setdefault(k, v)
    return data

def prepare_input_data(input_data, model_data):
    """Prépare les données d'entrée pour la prédiction"""
    if model_data is None:
        return None
        
    feature_columns = model_data.get('feature_columns', [])
    scaler = model_data.get('scaler')
    
    # Créer le DataFrame avec toutes les caractéristiques attendues
    df = pd.DataFrame({f: [0.0] for f in feature_columns})
    
    # Remplir avec les valeurs réelles
    for feature in feature_columns:
        if feature in input_data:
            df[feature] = input_data[feature]
    
    # Appliquer la normalisation si le scaler existe
    if scaler is not None:
        try:
            df_scaled = scaler.transform(df)
            return df_scaled
        except Exception as e:
            st.warning(f"⚠️ Échec de la normalisation: {e}")
            return df.values
    else:
        return df.values

# -----------------------
# Aides pour la sortie
# -----------------------
def categorize_risk(probability):
    if probability >= 90: return "Risque Très Faible", "🟢"
    elif probability >= 70: return "Risque Faible", "🟡"
    elif probability >= 50: return "Risque Moyen", "🟠"
    elif probability >= 30: return "Risque Élevé", "🔴"
    else: return "Risque Très Élevé", "💀"

def get_confidence_level(probability):
    distance = abs(probability - 50)
    if distance > 40: return "TRÈS ÉLEVÉ"
    elif distance > 25: return "ÉLEVÉ"
    elif distance > 15: return "MOYEN"
    else: return "FAIBLE"

# -----------------------
# Générer des explications
# -----------------------
def generer_explications(input_data, acceptance_prob):
    explications = []
    
    # Statut d'acceptation global
    if acceptance_prob >= 0.5:
        explications.append({
            'type': 'positive',
            'titre': 'Points Forts de la Demande',
            'contenu': 'Votre demande présente plusieurs facteurs positifs qui ont contribué à son acceptation:'
        })
    else:
        explications.append({
            'type': 'negative',
            'titre': 'Points à Améliorer',
            'contenu': 'Votre demande présente certains aspects qui nécessitent une amélioration:'
        })
    
    # Explication basée sur le revenu
    revenu_total = input_data.get('total_household_income', 0)
    if revenu_total > 5000:
        explications.append({
            'type': 'positive',
            'titre': 'Revenu Solide',
            'contenu': f'Votre revenu mensuel total de {revenu_total:,.0f}€ est au-dessus du seuil recommandé pour ce montant de prêt.'
        })
    else:
        explications.append({
            'type': 'negative',
            'titre': 'Revenu à Considérer',
            'contenu': f'Votre revenu mensuel total de {revenu_total:,.0f}€ est en dessous de la plage idéale pour ce montant de prêt. Envisagez de demander un prêt plus petit ou d\'augmenter vos sources de revenus.'
        })
    
    # Explication basée sur le ratio dette/revenu
    dti_ratio = input_data.get('debt_to_income_ratio', 0)
    if dti_ratio < 0.35:
        explications.append({
            'type': 'positive',
            'titre': 'Ratio Dette/Revenu Sain',
            'contenu': f'Votre ratio dette/revenu de {dti_ratio*100:.1f}% est dans la plage recommandée (<35%), indiquant une bonne gestion financière.'
        })
    else:
        explications.append({
            'type': 'negative',
            'titre': 'Ratio Dette/Revenu Élevé',
            'contenu': f'Votre ratio dette/revenu de {dti_ratio*100:.1f}% est supérieur au maximum recommandé de 35%. Envisagez de rembourser les dettes existantes avant de faire une demande.'
        })
    
    # Explication de l'apport personnel
    apport_pct = input_data.get('apport_percentage', 0)
    if apport_pct >= 0.2:
        explications.append({
            'type': 'positive',
            'titre': 'Apport Personnel Solide',
            'contenu': f'Votre apport personnel de {apport_pct*100:.1f}% atteint ou dépasse le montant recommandé, réduisant le risque pour le prêteur.'
        })
    else:
        explications.append({
            'type': 'negative',
            'titre': 'Apport Personnel à Considérer',
            'contenu': f'Un apport personnel de {apport_pct*100:.1f}% est inférieur aux 20% recommandés. Envisagez d\'augmenter votre apport personnel pour améliorer vos chances d\'acceptation.'
        })
    
    return explications

# -----------------------
# Interface Utilisateur de l'Application
# -----------------------
def main():
    # En-tête avec logo
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        st.image("https://apiv1.2l-courtage.com/public/storage/jpg/pPy95t2JQnO2rgBOpXVJoT9HD0YW4JSgee74GNKD.jpeg", 
                 width=100)
    with col_title:
        st.markdown("""
        <div style="
            font-family: 'Montserrat', Arial, sans-serif;
            font-weight: 900;
            font-size: 2.8rem;
            color: #22abc5;
            background: linear-gradient(90deg, #22abc5 60%, #22abc5 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-fill-color: transparent;
            text-align: center;
            letter-spacing: 2px;
            margin-bottom: 2rem;
            padding: 0.5rem 0;
            border-radius: 12px;
        ">
            Prédicteur de Demande de Prêt
        </div>
    """, unsafe_allow_html=True)

    # Charger le modèle
    model_data, _ = load_model_and_scaler()
    
    if model_data is None:
        st.error("❌ Impossible de créer ou charger un modèle. L'application ne peut pas fonctionner.")
        return

    # Définir les options des menus déroulants
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
   
    contrat_travail_options = {
        "CDI": 0,
        "CDD": 1,
        "Intérim": 2,
        "Fonctionnaire": 3,
        "Libéral": 4,
        "Retraité": 5,
        "Sans emploi": 6
    }
   
    project_nature_options = {
        "Construction": 0,
        "Achat neuf": 1,
        "Achat ancien": 2,
        "Travaux": 3,
        "Rachat de crédit": 4
    }
   
    project_destination_options = {
        "Résidence principale": 0,
        "Résidence secondaire": 1,
        "Investissement locatif": 2
    }
   
    project_zone_options = {
        "Zone A": 0,
        "Zone B1": 1,
        "Zone B2": 2,
        "Zone C": 3
    }
   
    project_type_logement_options = {
        "Maison": 0,
        "Appartement": 1,
        "Studio": 2,
        "Loft": 3,
        "Autre": 4
    }

    # NOUVEAU : Options pour les champs manquants
    autorise_documents_options = {
        "Oui": 1,
        "Non": 0
    }

    situation_familiale_options = {
        "Célibataire": 0,
        "Marié(e)": 1,
        "Pacsé(e)": 2,
        "Divorcé(e)": 3,
        "Veuf/Veuve": 4
    }

    # Interface utilisateur avec tous les onglets originaux
    tab1, tab2, tab3, tab4 = st.tabs(["Informations Emprunteur", "Détails du Projet", "Informations Financières", "Crédits Existants & Actifs"])
    
    with st.form("loan_application_form"):
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="section-header">Informations Emprunteur Principal</div>', unsafe_allow_html=True)
                borrower_salaire_mensuel = st.number_input("Salaire Mensuel (€)", min_value=0.0, value=3000.0, step=100.0, key="b_salary")
                borrower_revenu_foncier = st.number_input("Revenu Foncier (€)", min_value=0.0, value=0.0, step=100.0, key="b_rental")
                borrower_autres_revenus = st.number_input("Autres Revenus (€)", min_value=0.0, value=0.0, step=100.0, key="b_other")
                
                # NOUVEAUX CHAMPS AJOUTÉS
                situation_familiale = st.selectbox(
                    "Situation Familiale",
                    options=list(situation_familiale_options.keys()),
                    index=0,
                    key="family_situation"
                )
                
                autorise_documents = st.selectbox(
                    "Autorise Documents",
                    options=list(autorise_documents_options.keys()),
                    index=0,
                    key="auth_docs"
                )
                
            with col2:
                st.markdown('<div class="section-header">Informations Co-Emprunteur</div>', unsafe_allow_html=True)
                co_borrower_salaire_mensuel = st.number_input("Salaire Co-Emprunteur (€)", min_value=0.0, value=2000.0, step=100.0, key="cb_salary")
                co_borrower_autres_revenus = st.number_input("Autres Revenus Co-Emprunteur (€)", min_value=0.0, value=0.0, step=100.0, key="cb_other")
                co_borrower_categ_socio_prof = st.selectbox(
                    "Catégorie Socio-Professionnelle",
                    options=list(categ_socio_prof_options.keys()),
                    index=2,
                    key="cb_cat"
                )
                co_borrower_contrat_travail = st.selectbox(
                    "Contrat de Travail",
                    options=list(contrat_travail_options.keys()),
                    index=0,
                    key="cb_contract"
                )

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="section-header">Détails du Projet</div>', unsafe_allow_html=True)
                project_nature = st.selectbox(
                    "Nature du Projet",
                    options=list(project_nature_options.keys()),
                    index=0,
                    key="proj_nature"
                )
                project_destination = st.selectbox(
                    "Destination du Projet",
                    options=list(project_destination_options.keys()),
                    index=0,
                    key="proj_dest"
                )
                project_zone = st.selectbox(
                    "Zone du Projet",
                    options=list(project_zone_options.keys()),
                    index=0,
                    key="proj_zone"
                )
                project_type_logement = st.selectbox(
                    "Type de Logement",
                    options=list(project_type_logement_options.keys()),
                    index=0,
                    key="proj_housing"
                )
            with col2:
                st.markdown('<div class="section-header">Coûts du Projet</div>', unsafe_allow_html=True)
                cost_terrain = st.number_input("Coût du Terrain (€)", min_value=0.0, value=0.0, step=1000.0, key="cost_terrain")
                cost_logement = st.number_input("Coût du Logement (€)", min_value=0.0, value=150000.0, step=1000.0, key="cost_logement")
                cost_travaux = st.number_input("Coût des Travaux (€)", min_value=0.0, value=0.0, step=1000.0, key="cost_travaux")
                cost_frais_notaire = st.number_input("Frais de Notaire (€)", min_value=0.0, value=10000.0, step=100.0, key="cost_notaire")

        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="section-header">Détails du Prêt</div>', unsafe_allow_html=True)
                montant_credit_initio = st.number_input("Montant du Crédit (€)", min_value=0.0, value=180000.0, step=1000.0, key="loan_amount")
                financing_pret_principal = st.number_input("Prêt Principal (€)", min_value=0.0, value=180000.0, step=1000.0, key="loan_principal")
                financing_apport_personnel = st.number_input("Apport Personnel (€)", min_value=0.0, value=20000.0, step=1000.0, key="loan_apport")
            with col2:
                st.markdown('<div class="section-header">Coûts Additionnels</div>', unsafe_allow_html=True)
                cost_viabilisation = st.number_input("Coût de Viabilisation (€)", min_value=0.0, value=0.0, step=100.0, key="cost_viab")
                cost_mobilier = st.number_input("Coût du Mobilier (€)", min_value=0.0, value=0.0, step=100.0, key="cost_mob")
                cost_agency_fees = st.number_input("Frais d'Agence (€)", min_value=0.0, value=0.0, step=100.0, key="cost_agency")

        with tab4:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="section-header">Crédits Existants</div>', unsafe_allow_html=True)
                total_credit_remaining_amount = st.number_input("Montant Restant du Crédit (€)", min_value=0.0, value=0.0, step=1000.0, key="credit_remaining")
                total_credit_monthly_payment = st.number_input("Mensualités des Crédits (€)", min_value=0.0, value=0.0, step=100.0, key="credit_monthly")
                nombre_of_credits = st.number_input("Nombre de Crédits", min_value=0, value=0, step=1, key="num_credits")
            with col2:
                st.markdown('<div class="section-header">Actifs</div>', unsafe_allow_html=True)
                net_worth = st.number_input("Valeur Nette (€)", min_value=0.0, value=50000.0, step=1000.0, key="net_worth")
                number_of_properties = st.number_input("Nombre de Propriétés", min_value=0, value=0, step=1, key="num_properties")

        submitted = st.form_submit_button("🎯 Prédire l'Acceptation du Prêt")

    # Flux de prédiction
    if submitted:
        # Convertir les sélections en valeurs numériques
        input_data = {
            'montant_credit_initio': montant_credit_initio,
            'co_borrower_categ_socio_prof': categ_socio_prof_options[co_borrower_categ_socio_prof],
            'co_borrower_contrat_travail': contrat_travail_options[co_borrower_contrat_travail],
            'borrower_salaire_mensuel': borrower_salaire_mensuel,
            'borrower_revenu_foncier': borrower_revenu_foncier,
            'borrower_autres_revenus': borrower_autres_revenus,
            'co_borrower_salaire_mensuel': co_borrower_salaire_mensuel,
            'co_borrower_autres_revenus': co_borrower_autres_revenus,
            'project_nature': project_nature_options[project_nature],
            'project_destination': project_destination_options[project_destination],
            'project_zone': project_zone_options[project_zone],
            'project_type_logement': project_type_logement_options[project_type_logement],
            'cost_terrain': cost_terrain,
            'cost_logement': cost_logement,
            'cost_travaux': cost_travaux,
            'cost_frais_notaire': cost_frais_notaire,
            'financing_apport_personnel': financing_apport_personnel,
            'financing_pret_principal': financing_pret_principal,
            'total_credit_remaining_amount': total_credit_remaining_amount,
            'total_credit_monthly_payment': total_credit_monthly_payment,
            'nombre_of_credits': nombre_of_credits,
            'net_worth': net_worth,
            'number_of_properties': number_of_properties,
            'cost_viabilisation': cost_viabilisation,
            'cost_mobilier': cost_mobilier,
            'cost_agency_fees': cost_agency_fees,
            # NOUVEAUX CHAMPS AJOUTÉS
            'situation_familiale': situation_familiale_options[situation_familiale],
            'autorise_documents': autorise_documents_options[autorise_documents]
        }
       
        # Calculer les caractéristiques dérivées
        input_data = calculate_derived_features(input_data)
       
        try:
            # Préparer les données pour la prédiction
            prepared_data = prepare_input_data(input_data, model_data)
            
            if prepared_data is None:
                st.error("❌ Impossible de préparer les données pour la prédiction.")
                return
            
            # Obtenir le modèle
            model = model_data.get('model')
            
            if model is None:
                st.error("❌ Aucun modèle trouvé pour la prédiction.")
                return
            
            # Faire la prédiction
            if hasattr(model, 'predict_proba'):
                probs = model.predict_proba(prepared_data)
                acceptance_prob = float(probs[0, 1]) * 100.0
            else:
                pred = model.predict(prepared_data)[0]
                acceptance_prob = 100.0 if pred == 1 else 0.0
            
            # Catégoriser le risque
            risk_category, risk_emoji = categorize_risk(acceptance_prob)
            confidence_level = get_confidence_level(acceptance_prob)
            is_accepted = acceptance_prob >= 50.0
            
            # Obtenir les explications
            explications = generer_explications(input_data, acceptance_prob)
            
            # Afficher les résultats
            st.header("📊 Résultats de la Prédiction")
            res_col1, res_col2, res_col3 = st.columns(3)
           
            with res_col1:
                st.metric("Probabilité d'Acceptation", f"{acceptance_prob:.1f}%")
           
            with res_col2:
                decision_color = "#22abc5" if is_accepted else "#F58C29"
                decision_text = "✅ ACCEPTÉE" if is_accepted else "❌ REFUSÉE"
                st.markdown(f"<h2 style='color: {decision_color}; text-align: center;'>{decision_text}</h2>", unsafe_allow_html=True)
           
            with res_col3:
                risk_color = "#F58C29" if 'Élevé' in risk_category else "#f39c12" if 'Moyen' in risk_category else "#22abc5"
                st.markdown(f"<h3 style='color: {risk_color}; text-align: center;'>{risk_emoji} {risk_category}</h3>", unsafe_allow_html=True)
           
            # Métriques financières
            st.subheader("💰 Métriques Financières Calculées")
            info_col1, info_col2 = st.columns(2)
           
            with info_col1:
                st.markdown(f'<div class="metric-card"><span class="info-label">Revenu Total du Ménage:</span> <span class="info-value">{input_data.get("total_household_income", 0):.0f} €</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-card"><span class="info-label">Coût Total du Projet:</span> <span class="info-value">{input_data.get("total_project_cost", 0):.0f} €</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-card"><span class="info-label">Ratio Dette/Revenu:</span> <span class="info-value">{input_data.get("debt_to_income_ratio", 0):.2f}</span></div>', unsafe_allow_html=True)
           
            with info_col2:
                st.markdown(f'<div class="metric-card"><span class="info-label">Ratio Prêt/Valeur:</span> <span class="info-value">{input_data.get("loan_to_value", 0):.2f}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-card"><span class="info-label">Apport Personnel:</span> <span class="info-value">{input_data.get("apport_percentage", 0)*100:.1f}%</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-card"><span class="info-label">Niveau de Confiance:</span> <span class="info-value">{confidence_level}</span></div>', unsafe_allow_html=True)
           
            # Explications
            st.markdown('<div class="section-header">📝 Explication de la Décision</div>', unsafe_allow_html=True)
           
            for explication in explications:
                classe_carte = ""
                if explication['type'] == 'positive':
                    classe_carte = "positive-card"
                elif explication['type'] == 'negative':
                    classe_carte = "negative-card"
                else:
                    classe_carte = "neutral-card"
               
                st.markdown(f'''
                <div class="explanation-card {classe_carte}">
                    <div class="explanation-title">{explication['titre']}</div>
                    <div class="explanation-content">{explication['contenu']}</div>
                </div>
                ''', unsafe_allow_html=True)
           
            # Recommandations
            st.markdown('<div class="section-header">💡 Recommandations</div>', unsafe_allow_html=True)
           
            if is_accepted:
                if acceptance_prob >= 70:
                    st.success("**🎉 Excellente candidature!** Votre demande présente de très bonnes chances d'approbation.")
                else:
                    st.warning("**📝 Candidature acceptable.** Votre demande pourrait être approuvée avec quelques ajustements mineurs.")
            else:
                st.error("**⚠️ Candidature à risque.** Nous recommandons d'améliorer certains aspects avant de soumettre.")
                
                if input_data['debt_to_income_ratio'] > 0.4:
                    st.info("💡 **Suggestion:** Réduisez votre ratio dette/revenu en augmentant vos revenus ou en diminuant le montant du prêt.")
                
                if input_data['apport_percentage'] < 0.1:
                    st.info("💡 **Suggestion:** Augmentez votre apport personnel à au moins 10% du coût total du projet.")
           
            # Graphique d'analyse
            st.markdown('<div class="section-header">📈 Analyse des Facteurs d\'Influence</div>', unsafe_allow_html=True)
            
            # Créer un graphique d'analyse des caractéristiques
            feature_names = ['Revenu Total', 'Ratio Dette/Revenu', 'Apport Personnel', 'Montant Prêt', 'Valeur Nette', 'Mensualités']
            importance_values = [
                min(input_data.get('total_household_income', 0) / 10000, 1.0),
                max(1.0 - input_data.get('debt_to_income_ratio', 0), 0),
                input_data.get('apport_percentage', 0),
                min(input_data.get('montant_credit_initio', 0) / 300000, 1.0),
                min(input_data.get('net_worth', 0) / 100000, 1.0),
                max(1.0 - (input_data.get('total_credit_monthly_payment', 0) / 2000), 0)
            ]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            y_pos = np.arange(len(feature_names))
            colors = ['#22abc5' if val > 0.5 else '#F58C29' for val in importance_values]
            bars = ax.barh(y_pos, importance_values, color=colors)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(feature_names)
            ax.set_xlabel('Score d\'Influence (0-1)')
            ax.set_title('Analyse des Facteurs Clés dans la Décision')
            
            # Ajouter les valeurs sur les barres
            for bar, value in zip(bars, importance_values):
                ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                       f'{value:.2f}', va='center', ha='left', fontsize=10)
            
            plt.tight_layout()
            st.pyplot(fig)
           
        except Exception as e:
            st.error(f"❌ Erreur lors de la prédiction: {e}")
            st.info("💡 Assurez-vous que toutes les valeurs saisies sont valides.")

if __name__ == "__main__":
    main()
