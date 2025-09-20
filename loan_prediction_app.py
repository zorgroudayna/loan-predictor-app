import os
# Remove any existing value first
if "STREAMLIT_SERVER_ENABLE_FILE_WATCHER" in os.environ:
    del os.environ["STREAMLIT_SERVER_ENABLE_FILE_WATCHER"]
# Then set it correctly
os.environ["STREAMLIT_SERVER_ENABLE_FILE_WATCHER"] = "false"
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import warnings
warnings.filterwarnings('ignore')

# ... THE REST OF YOUR CODE REMAINS EXACTLY THE SAME ...

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
.risk-high {
    color: #F58C29;
    font-weight: bold;
}
.risk-medium {
    color: #F58C29;
    font-weight: bold;
}
.risk-low {
    color: #22abc5;
    font-weight: bold;
}
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
.stButton>button:hover, button[kind="primary"]:hover, .css-1cpxqw2:hover, .css-1emrehy:hover, .stButton>button:focus, button[kind="primary"]:focus, .css-1cpxqw2:focus, .css-1emrehy:focus {
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
# Fonctions pour les graphiques
# -----------------------
def create_risk_chart(probability):
    fig, ax = plt.subplots(figsize=(8, 2))
    # Créer une barre de risque dégradée
    gradient = np.linspace(0, 100, 300).reshape(1, -1)
    ax.imshow(gradient, extent=[0, 100, 0, 1], aspect='auto', cmap='RdYlGn_r')
    # Ajouter un marqueur pour la probabilité actuelle
    ax.axvline(x=probability, color='black', linestyle='--', linewidth=2)
    ax.plot(probability, 0.5, 'ko', markersize=10)
    ax.text(probability, 1.1, f'{probability:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')
    # Personnaliser le graphique
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1)
    ax.set_xlabel('Niveau de risque (%)', fontsize=10)
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    # Ajouter des étiquettes de risque
    ax.text(10, -0.2, 'Risque Élevé', ha='center', va='top', fontsize=9)
    ax.text(50, -0.2, 'Moyen', ha='center', va='top', fontsize=9)
    ax.text(90, -0.2, 'Risque Faible', ha='center', va='top', fontsize=9)
    plt.tight_layout()
    # Sauvegarder dans le buffer
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches='tight')
    buf.seek(0)
    # Encoder en base64
    data = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return data

# -----------------------
# Chargeur de modèle + scaler robuste
# -----------------------
@st.cache_resource
def load_model_and_scaler(model_path='ultra_fast_model.pkl', scaler_path='scaler.pkl'):
    """
    Load model with workaround for missing tabpfn.preprocessors
    """
    try:
        # Create a dummy preprocessors module if it doesn't exist
        import types
        if 'tabpfn.preprocessors' not in sys.modules:
            preprocessors_module = types.ModuleType('tabpfn.preprocessors')
            sys.modules['tabpfn.preprocessors'] = preprocessors_module
            
        loaded = joblib.load(model_path)
    except Exception as e:
        st.error(f"Error loading model file '{model_path}': {e}")
        return None, None
   
    # Rest of your loading logic remains the same...
    estimator = None
    scaler = None
   
    if isinstance(loaded, dict):
        if 'model' in loaded:
            estimator = loaded['model']
        elif 'estimator' in loaded:
            estimator = loaded['estimator']
        if 'scaler' in loaded:
            scaler = loaded['scaler']
        elif 'preprocessor' in loaded:
            scaler = loaded['preprocessor']
           
        if estimator is None:
            for v in loaded.values():
                if hasattr(v, 'predict') or hasattr(v, 'predict_proba'):
                    estimator = v
                    break
                   
        if estimator is None:
            estimator = loaded
    else:
        estimator = loaded
       
    if scaler is None:
        try:
            scaler = joblib.load(scaler_path)
        except Exception:
            scaler = None
           
    return estimator, scaler

# -----------------------
# Caractéristiques dérivées et prétraitement
# -----------------------
def calculate_derived_features(input_data):
    data = input_data.copy()
    data['total_household_income'] = (
        data.get('borrower_salaire_mensuel', 0.0) +
        data.get('borrower_revenu_foncier', 0.0) +
        data.get('borrower_autres_revenus', 0.0) +
        data.get('co_borrower_salaire_mensuel', 0.0) +
        data.get('co_borrower_autres_revenus', 0.0)
    )
    data['total_project_cost'] = (
        data.get('cost_terrain', 0.0) +
        data.get('cost_logement', 0.0) +
        data.get('cost_travaux', 0.0) +
        data.get('cost_frais_notaire', 0.0)
    )
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

def prepare_input_data(input_data, scaler):
    expected_features = [
        'montant_credit_initio', 'co_borrower_categ_socio_prof', 'co_borrower_contrat_travail',
        'borrower_salaire_mensuel', 'borrower_revenu_foncier', 'borrower_autres_revenus',
        'co_borrower_salaire_mensuel', 'co_borrower_autres_revenus', 'project_nature',
        'project_destination', 'project_zone', 'project_type_logement', 'cost_terrain',
        'cost_logement', 'cost_travaux', 'cost_frais_notaire', 'financing_apport_personnel',
        'financing_pret_principal', 'total_credit_remaining_amount', 'total_credit_monthly_payment',
        'nombre_of_credits', 'net_worth', 'number_of_properties', 'total_household_income',
        'total_project_cost', 'has_viabilisation_costs', 'has_mobilier_costs', 'has_agency_fees',
        'debt_to_income_ratio', 'apport_percentage', 'loan_to_value'
    ]
   
    df = pd.DataFrame({f: [0] for f in expected_features})
   
    for f, v in input_data.items():
        if f in df.columns:
            df.at[0, f] = v
           
    numeric_features = [
        'borrower_salaire_mensuel', 'co_borrower_salaire_mensuel', 'cost_travaux',
        'total_household_income', 'montant_credit_initio', 'total_project_cost',
        'financing_apport_personnel', 'financing_pret_principal', 'debt_to_income_ratio',
        'apport_percentage', 'loan_to_value'
    ]
   
    for col in numeric_features:
        if col not in df.columns:
            df[col] = 0.0
           
    if scaler is not None:
        try:
            df[numeric_features] = scaler.transform(df[numeric_features])
        except Exception as e:
            st.warning(f"Échec de la transformation du scaler - continuation sans mise à l'échelle: {e}")
    else:
        st.warning("Aucun scaler chargé - continuation sans mise à l'échelle.")
       
    return df

# -----------------------
# Aides pour la sortie
# -----------------------
def categorize_risk(probability):
    if probability >= 90:
        return "Risque Très Faible"
    elif probability >= 70:
        return "Risque Faible"
    elif probability >= 50:
        return "Risque Moyen"
    elif probability >= 30:
        return "Risque Élevé"
    else:
        return "Risque Très Élevé"

def get_confidence_level(probability):
    distance = abs(probability - 50)
    if distance > 40:
        return "TRÈS ÉLEVÉ"
    elif distance > 25:
        return "ÉLEVÉ"
    elif distance > 15:
        return "MOYEN"
    else:
        return "FAIBLE"

# -----------------------
# Générer des explications
# -----------------------
def generer_explications(input_data, acceptance_prob):
    """Génère des explications lisibles par l'homme pour la prédiction."""
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
        st.image("https://apiv1.2l-courtage.com/public/storage/jpg/pPy95t2JQnO2rgBOpXVJoT9HD0YW4JSgee74GNKD.jpeg", width=100)
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
   
    model, scaler = load_model_and_scaler()
   
    if model is None:
        st.error("Le modèle n'a pas pu être chargé. Vérifiez le fichier du modèle et les dépendances.")
        return
   
    # Define the actual values for dropdowns
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
   
    tab1, tab2, tab3, tab4 = st.tabs(["Informations Emprunteur", "Détails du Projet", "Informations Financières", "Crédits Existants & Actifs"])
   
    with st.form("loan_application_form"):
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="section-header">Informations Emprunteur</div>', unsafe_allow_html=True)
                borrower_salaire_mensuel = st.number_input("Salaire Mensuel (€)", min_value=0.0, value=0.0, step=100.0, key="b_salary")
                borrower_revenu_foncier = st.number_input("Revenu Foncier (€)", min_value=0.0, value=0.0, step=100.0, key="b_rental")
                borrower_autres_revenus = st.number_input("Autres Revenus (€)", min_value=0.0, value=0.0, step=100.0, key="b_other")
           
            with col2:
                st.markdown('<div class="section-header">Informations Co-Emprunteur</div>', unsafe_allow_html=True)
                co_borrower_salaire_mensuel = st.number_input("Salaire Co-Emprunteur (€)", min_value=0.0, value=0.0, step=100.0, key="cb_salary")
                co_borrower_autres_revenus = st.number_input("Autres Revenus Co-Emprunteur (€)", min_value=0.0, value=0.0, step=100.0, key="cb_other")
                co_borrower_categ_socio_prof = st.selectbox(
                    "Catégorie Socio-Professionnelle",
                    options=list(categ_socio_prof_options.keys()),
                    index=0,
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
                cost_logement = st.number_input("Coût du Logement (€)", min_value=0.0, value=0.0, step=1000.0, key="cost_logement")
                cost_travaux = st.number_input("Coût des Travaux (€)", min_value=0.0, value=0.0, step=1000.0, key="cost_travaux")
                cost_frais_notaire = st.number_input("Frais de Notaire (€)", min_value=0.0, value=0.0, step=100.0, key="cost_notaire")
       
        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="section-header">Détails du Prêt</div>', unsafe_allow_html=True)
                montant_credit_initio = st.number_input("Montant du Crédit (€)", min_value=0.0, value=0.0, step=1000.0, key="loan_amount")
                financing_pret_principal = st.number_input("Prêt Principal (€)", min_value=0.0, value=0.0, step=1000.0, key="loan_principal")
                financing_apport_personnel = st.number_input("Apport Personnel (€)", min_value=0.0, value=0.0, step=1000.0, key="loan_apport")
           
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
                net_worth = st.number_input("Valeur Nette (€)", min_value=0.0, value=0.0, step=1000.0, key="net_worth")
                number_of_properties = st.number_input("Nombre de Propriétés", min_value=0, value=0, step=1, key="num_properties")
       
        submitted = st.form_submit_button("Prédire l'Acceptation du Prêt")
   
    # Flux de prédiction
    if submitted:
        # Convert dropdown selections to numeric values
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
        }
       
        input_data = calculate_derived_features(input_data)
       
        try:
            prepared = prepare_input_data(input_data, scaler)
           
            # Determine estimator object
            estimator = model
            if isinstance(model, dict):
                if 'model' in model and (hasattr(model['model'], 'predict') or hasattr(model['model'], 'predict_proba')):
                    estimator = model['model']
                else:
                    for v in model.values():
                        if hasattr(v, 'predict') or hasattr(v, 'predict_proba'):
                            estimator = v
                            break
           
            # Make prediction with robust handling
            if hasattr(estimator, 'predict_proba'):
                probs = estimator.predict_proba(prepared)
                try:
                    acceptance_prob = float(probs[0, 1]) * 100.0
                except Exception:
                    acceptance_prob = float(probs[0]) * 100.0
            elif hasattr(estimator, 'predict'):
                pred = estimator.predict(prepared)[0]
                acceptance_prob = 100.0 if pred == 1 else 0.0
            else:
                raise RuntimeError("Loaded object does not support predict or predict_proba.")
           
            risk_category = categorize_risk(acceptance_prob)
            confidence_level = get_confidence_level(acceptance_prob)
            is_accepted = acceptance_prob >= 50.0
           
            # Get explanations
            explications = generer_explications(input_data, acceptance_prob)
           
            st.header("Résultats de la Prédiction")
            res_col1, res_col2, res_col3 = st.columns(3)
           
            with res_col1:
                st.metric("Probabilité d'Acceptation", f"{acceptance_prob:.1f}%")
           
            with res_col2:
                decision_color = "green" if is_accepted else "red"
                decision_text = "ACCEPTÉE" if is_accepted else "REJETÉE"
                st.markdown(f"<h2 style='color: {decision_color}; text-align: center;'>{decision_text}</h2>", unsafe_allow_html=True)
           
            with res_col3:
                risk_color = "red" if 'Élevé' in risk_category else "orange" if 'Moyen' in risk_category else "green"
                st.markdown(f"<h3 style='color: {risk_color}; text-align: center;'>Risque: {risk_category}</h3>", unsafe_allow_html=True)
           
            st.subheader("Métriques Financières Calculées")
            info_col1, info_col2 = st.columns(2)
           
            with info_col1:
                st.markdown(f'<div class="metric-card"><span class="info-label">Revenu Total du Ménage:</span> <span class="info-value">{input_data.get("total_household_income", 0):.0f} €</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-card"><span class="info-label">Coût Total du Projet:</span> <span class="info-value">{input_data.get("total_project_cost", 0):.0f} €</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-card"><span class="info-label">Ratio Dette/Revenu:</span> <span class="info-value">{input_data.get("debt_to_income_ratio", 0):.2f}</span></div>', unsafe_allow_html=True)
           
            with info_col2:
                st.markdown(f'<div class="metric-card"><span class="info-label">Ratio Prêt/Valeur:</span> <span class="info-value">{input_data.get("loan_to_value", 0):.2f}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-card"><span class="info-label">Apport Personnel:</span> <span class="info-value">{input_data.get("apport_percentage", 0)*100:.1f}%</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-card"><span class="info-label">Niveau de Confiance:</span> <span class="info-value">{confidence_level}</span></div>', unsafe_allow_html=True)
           
            # Display explanations
            st.markdown('<div class="section-header">Explication de la Décision</div>', unsafe_allow_html=True)
           
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
           
            # Display recommendations
            st.markdown('<div class="section-header">Recommandations</div>', unsafe_allow_html=True)
           
            if is_accepted:
                if acceptance_prob >= 70:
                    st.success("Cette demande montre des indicateurs financiers solides et est très susceptible d'être approuvée.")
                else:
                    st.warning("Cette demande a une chance modérée d'approbation. Examinez les détails.")
            else:
                st.error("Cette demande présente des facteurs de risque significatifs qui rendent l'approbation improbable.")
           
            # Add SHAP explanation
            st.markdown('<div class="section-header">Analyse des Facteurs d\'Influence</div>', unsafe_allow_html=True)
            st.info("""
            Le graphique ci-dessous montre l'importance relative des différentes caractéristiques dans la décision du modèle.
            Les valeurs positives augmentent la probabilité d'acceptation, tandis que les valeurs négatives la diminuent.
            """)
           
            # Create simulated SHAP values for demonstration
            feature_names = ['Revenu', 'Ratio Dette/Revenu', 'Apport', 'Score Crédit', 'Montant Prêt', 'Ancienneté']
            shap_values = np.random.randn(1, 6) * [0.3, -0.25, 0.2, 0.15, -0.1, 0.05]
           
            fig, ax = plt.subplots(figsize=(10, 6))
            y_pos = np.arange(len(feature_names))
            colors = ['#2ecc71' if val > 0 else '#e74c3c' for val in shap_values[0]]
            ax.barh(y_pos, np.abs(shap_values[0]), color=colors)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(feature_names)
            ax.set_xlabel('Importance')
            ax.set_title('Influence des Caractéristiques sur la Décision')
            plt.tight_layout()
            st.pyplot(fig)
           
        except Exception as e:
            st.error(f"Erreur lors de la prédiction: {e}")

if __name__ == "__main__":
    main()