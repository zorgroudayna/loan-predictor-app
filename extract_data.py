<<<<<<< HEAD
import json
import re
from bs4 import BeautifulSoup
import html
import os
from datetime import datetime

def clean_html_text(text):
    """Clean HTML entities and unwanted characters"""
    if not text:
        return ""
   
    # Decode HTML entities
    text = html.unescape(text)
   
    # Replace common French encoded characters
    replacements = {
        'Ã©': 'é', 'Ã¨': 'è', 'Ã ': 'à', 'Ã§': 'ç', 'Ã´': 'ô', 'Ã¢': 'â',
        'Ã®': 'î', 'Ã¯': 'ï', 'Ã¹': 'ù', 'Ã»': 'û', 'Ã«': 'ë', 'Ã¼': 'ü',
        'Ã‚': 'Â', 'Ã‡': 'Ç', 'Ã‰': 'É', 'Ã€': 'À', 'RÃ©f.': 'Réf.',
        'prÃ©nom': 'prénom', 'TÃ©l': 'Tél', 'AdressÃ©e': 'Adressée',
        'PrÃ©sentÃ©e': 'Présentée', 'CatÃ©g.': 'Catég.', 'activitÃ©': 'activité',
        'crÃ©dit': 'crédit', 'MÃ©nage': 'Ménage', 'bÃ©nÃ©ficiaire': 'bénéficiaire',
        'DÃ©but': 'Début', 'employÃ©s': 'employés', 'dÃ©jÃ ': 'déjà',
        'rÃ©fÃ©rence': 'référence', 'Ã©nergÃ©tique': 'énergétique',
        'crÃ©Ã©e': 'créée', 'RÃ©fÃ©rences': 'Références', 'Ã©tage': 'étage',
        'RÃ©fÃ¨rences': 'Références', 'rÃ©glementaires': 'réglementaires',
        'Primo-accÃ©dant': 'Primo-accédant', 'AmÃ©nagements': 'Aménagements',
        'DÃ©mÃ©nagement': 'Déménagement', 'CoÃ»t': 'Coût', 'Ã©tablissement': 'établissement',
        'RÃ©capitulatif': 'Récapitulatif', 'DÃ©penses': 'Dépenses',
        'pÃ©nalitÃ©s': 'pénalités', 'MensualitÃ©': 'Mensualité',
        'MensualitÃ©s': 'Mensualités', 'persistante': 'persistante',
        'programmÃ©e': 'programmée', 'versÃ©es': 'versées', 'dÃ©penses': 'dépenses',
        'PrÃªteur': 'Prêteur', 'PrÃªt': 'Prêt', 'rÃ©dacteur': 'rédacteur',
        'CapacitÃ©': 'Capacité', 'aprÃ¨s': 'après', 'opÃ©ration': 'opération',
        'â‚¬': '€', '&nbsp;': ' ', '&#039;': "'", '&amp;': '&'
    }
   
    for old, new in replacements.items():
        text = text.replace(old, new)
   
    # Clean extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
   
    return text

def extract_credits_info(html_content):
    """Extract existing credits information"""
    credits = []
   
    # Find credit table rows
    credit_pattern = r'<tr>.*?<th[^>]*>([^<]*(?:Crédit|Credit)[^<]*)</th>.*?<th[^>]*>([^<]*)</th>.*?<th[^>]*>([^<]*€[^<]*)</th>.*?<th[^>]*>([^<]*€[^<]*)</th>.*?<th[^>]*>([^<]*)</th>.*?<th[^>]*>([^<]*)</th>.*?</tr>'
   
    matches = re.findall(credit_pattern, html_content, re.DOTALL | re.IGNORECASE)
   
    for match in matches:
        credit = {
            "type": clean_html_text(match[0]),
            "lender": clean_html_text(match[1]),
            "remaining_amount": clean_html_text(match[2]),
            "monthly_payment": clean_html_text(match[3]),
            "end_date": clean_html_text(match[4]),
            "status": clean_html_text(match[5])
        }
        if credit["type"] and credit["type"] != "Credit existants":
            credits.append(credit)
   
    return credits

def extract_patrimoine_info(html_content):
    """Extract patrimoine (assets) information"""
    patrimoine = []
   
    # Find patrimoine table rows
    patrimoine_pattern = r'<td[^>]*>([^<]*(?:Residence|propriété)[^<]*)</td>.*?<td[^>]*>([^<]*)</td>.*?<td[^>]*>([^<]*)</td>.*?<td[^>]*>([^<]*)</td>.*?<td[^>]*>([^<]*€[^<]*)</td>.*?<td[^>]*>([^<]*€[^<]*)</td>'
   
    matches = re.findall(patrimoine_pattern, html_content, re.DOTALL | re.IGNORECASE)
   
    for match in matches:
        asset = {
            "type": clean_html_text(match[0]),
            "location": clean_html_text(match[1]),
            "purchase_year": clean_html_text(match[2]),
            "purchase_price": clean_html_text(match[3]),
            "current_value": clean_html_text(match[4]),
            "remaining_debt": clean_html_text(match[5])
        }
        if asset["type"]:
            patrimoine.append(asset)
   
    return patrimoine

def extract_section_data(html_content, pattern, section_name):
    """Generic function to extract section data from HTML"""
    section_data = {}
    match = re.search(pattern, html_content, re.DOTALL)
    if match:
        content = match.group(1)
        soup = BeautifulSoup(content, 'html.parser')
        rows = soup.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                key = clean_html_text(cells[0].get_text())
                value = clean_html_text(cells[1].get_text())
                if key and value:
                    section_data[key] = value
    return section_data

def extract_all_data_from_html(html_content):
    """Extract all data from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
   
    # Extract header information
    header_info = {}
    date_match = re.search(r'Date.*?<strong>([^<]+)', html_content)
    if date_match:
        header_info['date'] = clean_html_text(date_match.group(1))
   
    ref_match = re.search(r'Réf\.affaire.*?<strong>([^<]+)', html_content)
    if ref_match:
        header_info['reference_affaire'] = clean_html_text(ref_match.group(1))
   
    nom_match = re.search(r'Nom affaire.*?<strong>([^<]+)', html_content)
    if nom_match:
        header_info['nom_affaire'] = clean_html_text(nom_match.group(1))
   
    # Extract presenter info (courtier)
    presenter_info = {}
    presenter_pattern = r'Présentée par.*?</th>.*?</tr>(.*?)(?=<th|</table>)'
    presenter_match = re.search(presenter_pattern, html_content, re.DOTALL)
    if presenter_match:
        presenter_content = presenter_match.group(1)
        presenter_soup = BeautifulSoup(presenter_content, 'html.parser')
        rows = presenter_soup.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                key = clean_html_text(cells[0].get_text())
                value = clean_html_text(cells[1].get_text())
                if key and value:
                    presenter_info[key] = value
            elif len(cells) == 1:
                text = clean_html_text(cells[0].get_text())
                if text and not any(x in text.lower() for x in ['présentée', 'conseiller']):
                    if 'company_address' not in presenter_info:
                        presenter_info['company_address'] = []
                    presenter_info['company_address'].append(text)
   
    # Extract addressee info (banque)
    addressee_info = extract_section_data(
        html_content, 
        r'Adressée à.*?</th>.*?</tr>(.*?)(?=<th|</table>)', 
        "addressee"
    )
   
    # Extract borrower information
    borrower_info = extract_section_data(
        html_content,
        r'<th[^>]*><strong>Emprunteur</strong>[^<]*</th>.*?</thead>.*?<tbody>(.*?)</tbody>',
        "borrower"
    )
   
    # Extract co-borrower information
    co_borrower_info = extract_section_data(
        html_content,
        r'<th[^>]*><strong>Co-Emprunteur[^<]*</strong>[^<]*</th>.*?</thead>.*?<tbody>(.*?)</tbody>',
        "co_borrower"
    )
   
    # Extract household info
    household_info = extract_section_data(
        html_content,
        r'<th[^>]*><strong>Ménage[^<]*</strong>[^<]*</th>.*?</thead>.*?<tbody>(.*?)</tbody>',
        "household"
    )
   
    # Extract professional situation
    prof_borrower = extract_section_data(
        html_content,
        r'Situation professionnelle de l\'emprunteur.*?</th>.*?</thead>.*?<tbody>(.*?)(?=</tbody>.*?<table|</div>)',
        "prof_borrower"
    )
    
    prof_co_borrower = extract_section_data(
        html_content,
        r'Situation professionnelle.*?du co-emprunteur.*?</th>.*?</thead>.*?<tbody>(.*?)(?=</tbody>.*?<table|</div>)',
        "prof_co_borrower"
    )
   
    # Extract income information
    income_borrower = extract_section_data(
        html_content,
        r'Revenus mensuels de l\'emprunteur.*?</th>.*?</thead>.*?<tbody>(.*?)</tbody>',
        "income_borrower"
    )
    
    income_co_borrower = extract_section_data(
        html_content,
        r'Revenus mensuels du coemprunteur.*?</th>.*?</thead>.*?<tbody>(.*?)</tbody>',
        "income_co_borrower"
    )
    
    social_income = extract_section_data(
        html_content,
        r'<th[^>]*><strong>Revenus sociaux[^<]*</strong>[^<]*</th>.*?</thead>.*?<tbody>(.*?)</tbody>',
        "social_income"
    )
    
    other_info = extract_section_data(
        html_content,
        r'<th[^>]*><strong>Autres Informations[^<]*</strong>[^<]*</th>.*?</thead>.*?<tbody>(.*?)</tbody>',
        "other_info"
    )
   
    # Extract project characteristics
    project_info = extract_section_data(
        html_content,
        r'Caractéristique du projet à financer.*?</th>.*?</thead>.*?<tbody>(.*?)</tbody>',
        "project"
    )
   
    # Extract project cost
    project_cost = extract_section_data(
        html_content,
        r'Coût du projet.*?</th>.*?</thead>.*?<tbody>(.*?)</tbody>',
        "project_cost"
    )
   
    # Extract financing plan
    financing_plan = {}
    financing_pattern = r'Plan de financement.*?</th>.*?</thead>.*?<tbody>(.*?)</tbody>'
    financing_match = re.search(financing_pattern, html_content, re.DOTALL)
    if financing_match:
        financing_content = financing_match.group(1)
        financing_soup = BeautifulSoup(financing_content, 'html.parser')
        rows = financing_soup.find_all('tr')
        for row in rows:
            cells = row.find_all(['th', 'td'])  # Check both th and td
            if len(cells) >= 2:
                key = clean_html_text(cells[0].get_text())
                value = clean_html_text(cells[1].get_text())
                if key and value:
                    financing_plan[key] = value
   
    # Extract existing credits
    credits = extract_credits_info(html_content)
   
    # Extract patrimoine
    patrimoine = extract_patrimoine_info(html_content)
   
    # Compile all data
    extracted_data = {
        "header_info": header_info,
        "presenter_info": presenter_info,
        "addressee_info": addressee_info,
        "borrower_info": borrower_info,
        "co_borrower_info": co_borrower_info,
        "household_info": household_info,
        "professional_situation": {
            "borrower": prof_borrower,
            "co_borrower": prof_co_borrower
        },
        "income_info": {
            "borrower": income_borrower,
            "co_borrower": income_co_borrower,
            "social_income": social_income,
            "other_info": other_info
        },
        "project_info": project_info,
        "project_cost": project_cost,
        "financing_plan": financing_plan,
        "existing_credits": credits,
        "patrimoine": patrimoine
    }
   
    return extracted_data

def process_ddp_file(input_file='ddp.json', output_file='cleaned_ddp.json'):
    """Process the DDP JSON file and extract clean data from multiple applications"""
    try:
        # Check if input file exists
        if not os.path.exists(input_file):
            print(f"❌ Error: File '{input_file}' not found")
            return None
            
        print(f"📂 Reading file: {input_file}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different data structures
        if isinstance(data, dict):
            # If the JSON contains a single object, convert to list
            data = [data]
        elif not isinstance(data, list):
            print(f"❌ Error: Expected list or dict, got {type(data)}")
            return None
            
        print(f"📊 Found {len(data)} applications to process")
        
        cleaned_data = []
        processed_count = 0
        error_count = 0
        
        for i, item in enumerate(data):
            try:
                print(f"🔄 Processing application {i+1}/{len(data)}...", end='\r')
                
                # Extract metadata with safe get operations
                metadata = {
                    "id": item.get("id"),
                    "name": clean_html_text(str(item.get("name", ""))),
                    "simulation_id": item.get("simulation_id"),
                    "partenaire_bancaire_id": item.get("partenaire_bancaire_id"),
                    "interlocuteurs_id": item.get("interlocuteurs_id"),
                    "banque_id": item.get("banque_id"),
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at"),
                    "commentaire": item.get("commentaire"),
                    "etape": item.get("etape"),
                    "date_envoie": item.get("date_envoie"),
                    "date_decision": item.get("date_decision"),
                    "propositions_id": item.get("propositions_id"),
                    "montant_credit_initio": item.get("montant_credit_initio"),
                    "type": clean_html_text(str(item.get("type", "")))
                }
                
                # Extract data from HTML body
                html_content = item.get("body", "")
                extracted_info = {}
                
                if html_content:
                    extracted_info = extract_all_data_from_html(html_content)
                
                # Combine metadata and extracted info
                cleaned_item = {
                    "metadata": metadata,
                    "extracted_data": extracted_info
                }
                
                cleaned_data.append(cleaned_item)
                processed_count += 1
                
            except Exception as e:
                print(f"\n⚠️  Error processing item {i+1}: {str(e)}")
                error_count += 1
                # Continue processing other items
                continue
        
        print(f"\n✅ Successfully processed {processed_count} applications")
        if error_count > 0:
            print(f"⚠️  {error_count} applications had errors and were skipped")
        
        # Save cleaned data
        print(f"💾 Saving cleaned data to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Cleaned data saved successfully!")
        return cleaned_data
        
    except FileNotFoundError:
        print(f"❌ Error: File '{input_file}' not found")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def analyze_cleaned_data(cleaned_data):
    """Analyze the cleaned data and provide summary statistics"""
    if not cleaned_data:
        return
        
    print("\n" + "="*50)
    print("📊 DATA ANALYSIS SUMMARY")
    print("="*50)
    
    total_applications = len(cleaned_data)
    print(f"📋 Total applications processed: {total_applications}")
    
    # Count applications with different types of data
    apps_with_borrower = sum(1 for app in cleaned_data if app['extracted_data'].get('borrower_info'))
    apps_with_co_borrower = sum(1 for app in cleaned_data if app['extracted_data'].get('co_borrower_info'))
    apps_with_project = sum(1 for app in cleaned_data if app['extracted_data'].get('project_info'))
    apps_with_credits = sum(1 for app in cleaned_data if app['extracted_data'].get('existing_credits'))
    
    print(f"👤 Applications with borrower info: {apps_with_borrower} ({apps_with_borrower/total_applications*100:.1f}%)")
    print(f"👥 Applications with co-borrower info: {apps_with_co_borrower} ({apps_with_co_borrower/total_applications*100:.1f}%)")
    print(f"🏠 Applications with project info: {apps_with_project} ({apps_with_project/total_applications*100:.1f}%)")
    print(f"💳 Applications with existing credits: {apps_with_credits} ({apps_with_credits/total_applications*100:.1f}%)")
    
    # Show sample data structure
    if cleaned_data:
        sample = cleaned_data[0]
        print(f"\n📋 Sample data structure:")
        print(f"🏢 Metadata keys: {list(sample['metadata'].keys())}")
        print(f"📊 Extracted data keys: {list(sample['extracted_data'].keys())}")
        
        # Show some sample values if available
        if sample['extracted_data'].get('borrower_info'):
            print(f"\n👤 Sample borrower info fields:")
            borrower_keys = list(sample['extracted_data']['borrower_info'].keys())[:5]
            for key in borrower_keys:
                value = sample['extracted_data']['borrower_info'][key]
                print(f"  • {key}: {value[:50]}..." if len(str(value)) > 50 else f"  • {key}: {value}")

# Main execution
if __name__ == "__main__":
    print("🚀 Starting DDP JSON Processor")
    print("="*50)
    
    # Process the file
    result = process_ddp_file('ddp.json', 'cleaned_ddp.json')
    
    if result:
        # Analyze the results
        analyze_cleaned_data(result)
        
        print(f"\n🎉 Processing complete!")
        print(f"📁 Original file: ddp.json")
        print(f"📁 Cleaned file: cleaned_ddp.json")
        print(f"📊 Total applications processed: {len(result)}")
    else:
=======
import json
import re
from bs4 import BeautifulSoup
import html
import os
from datetime import datetime

def clean_html_text(text):
    """Clean HTML entities and unwanted characters"""
    if not text:
        return ""
   
    # Decode HTML entities
    text = html.unescape(text)
   
    # Replace common French encoded characters
    replacements = {
        'Ã©': 'é', 'Ã¨': 'è', 'Ã ': 'à', 'Ã§': 'ç', 'Ã´': 'ô', 'Ã¢': 'â',
        'Ã®': 'î', 'Ã¯': 'ï', 'Ã¹': 'ù', 'Ã»': 'û', 'Ã«': 'ë', 'Ã¼': 'ü',
        'Ã‚': 'Â', 'Ã‡': 'Ç', 'Ã‰': 'É', 'Ã€': 'À', 'RÃ©f.': 'Réf.',
        'prÃ©nom': 'prénom', 'TÃ©l': 'Tél', 'AdressÃ©e': 'Adressée',
        'PrÃ©sentÃ©e': 'Présentée', 'CatÃ©g.': 'Catég.', 'activitÃ©': 'activité',
        'crÃ©dit': 'crédit', 'MÃ©nage': 'Ménage', 'bÃ©nÃ©ficiaire': 'bénéficiaire',
        'DÃ©but': 'Début', 'employÃ©s': 'employés', 'dÃ©jÃ ': 'déjà',
        'rÃ©fÃ©rence': 'référence', 'Ã©nergÃ©tique': 'énergétique',
        'crÃ©Ã©e': 'créée', 'RÃ©fÃ©rences': 'Références', 'Ã©tage': 'étage',
        'RÃ©fÃ¨rences': 'Références', 'rÃ©glementaires': 'réglementaires',
        'Primo-accÃ©dant': 'Primo-accédant', 'AmÃ©nagements': 'Aménagements',
        'DÃ©mÃ©nagement': 'Déménagement', 'CoÃ»t': 'Coût', 'Ã©tablissement': 'établissement',
        'RÃ©capitulatif': 'Récapitulatif', 'DÃ©penses': 'Dépenses',
        'pÃ©nalitÃ©s': 'pénalités', 'MensualitÃ©': 'Mensualité',
        'MensualitÃ©s': 'Mensualités', 'persistante': 'persistante',
        'programmÃ©e': 'programmée', 'versÃ©es': 'versées', 'dÃ©penses': 'dépenses',
        'PrÃªteur': 'Prêteur', 'PrÃªt': 'Prêt', 'rÃ©dacteur': 'rédacteur',
        'CapacitÃ©': 'Capacité', 'aprÃ¨s': 'après', 'opÃ©ration': 'opération',
        'â‚¬': '€', '&nbsp;': ' ', '&#039;': "'", '&amp;': '&'
    }
   
    for old, new in replacements.items():
        text = text.replace(old, new)
   
    # Clean extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
   
    return text

def extract_credits_info(html_content):
    """Extract existing credits information"""
    credits = []
   
    # Find credit table rows
    credit_pattern = r'<tr>.*?<th[^>]*>([^<]*(?:Crédit|Credit)[^<]*)</th>.*?<th[^>]*>([^<]*)</th>.*?<th[^>]*>([^<]*€[^<]*)</th>.*?<th[^>]*>([^<]*€[^<]*)</th>.*?<th[^>]*>([^<]*)</th>.*?<th[^>]*>([^<]*)</th>.*?</tr>'
   
    matches = re.findall(credit_pattern, html_content, re.DOTALL | re.IGNORECASE)
   
    for match in matches:
        credit = {
            "type": clean_html_text(match[0]),
            "lender": clean_html_text(match[1]),
            "remaining_amount": clean_html_text(match[2]),
            "monthly_payment": clean_html_text(match[3]),
            "end_date": clean_html_text(match[4]),
            "status": clean_html_text(match[5])
        }
        if credit["type"] and credit["type"] != "Credit existants":
            credits.append(credit)
   
    return credits

def extract_patrimoine_info(html_content):
    """Extract patrimoine (assets) information"""
    patrimoine = []
   
    # Find patrimoine table rows
    patrimoine_pattern = r'<td[^>]*>([^<]*(?:Residence|propriété)[^<]*)</td>.*?<td[^>]*>([^<]*)</td>.*?<td[^>]*>([^<]*)</td>.*?<td[^>]*>([^<]*)</td>.*?<td[^>]*>([^<]*€[^<]*)</td>.*?<td[^>]*>([^<]*€[^<]*)</td>'
   
    matches = re.findall(patrimoine_pattern, html_content, re.DOTALL | re.IGNORECASE)
   
    for match in matches:
        asset = {
            "type": clean_html_text(match[0]),
            "location": clean_html_text(match[1]),
            "purchase_year": clean_html_text(match[2]),
            "purchase_price": clean_html_text(match[3]),
            "current_value": clean_html_text(match[4]),
            "remaining_debt": clean_html_text(match[5])
        }
        if asset["type"]:
            patrimoine.append(asset)
   
    return patrimoine

def extract_section_data(html_content, pattern, section_name):
    """Generic function to extract section data from HTML"""
    section_data = {}
    match = re.search(pattern, html_content, re.DOTALL)
    if match:
        content = match.group(1)
        soup = BeautifulSoup(content, 'html.parser')
        rows = soup.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                key = clean_html_text(cells[0].get_text())
                value = clean_html_text(cells[1].get_text())
                if key and value:
                    section_data[key] = value
    return section_data

def extract_all_data_from_html(html_content):
    """Extract all data from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
   
    # Extract header information
    header_info = {}
    date_match = re.search(r'Date.*?<strong>([^<]+)', html_content)
    if date_match:
        header_info['date'] = clean_html_text(date_match.group(1))
   
    ref_match = re.search(r'Réf\.affaire.*?<strong>([^<]+)', html_content)
    if ref_match:
        header_info['reference_affaire'] = clean_html_text(ref_match.group(1))
   
    nom_match = re.search(r'Nom affaire.*?<strong>([^<]+)', html_content)
    if nom_match:
        header_info['nom_affaire'] = clean_html_text(nom_match.group(1))
   
    # Extract presenter info (courtier)
    presenter_info = {}
    presenter_pattern = r'Présentée par.*?</th>.*?</tr>(.*?)(?=<th|</table>)'
    presenter_match = re.search(presenter_pattern, html_content, re.DOTALL)
    if presenter_match:
        presenter_content = presenter_match.group(1)
        presenter_soup = BeautifulSoup(presenter_content, 'html.parser')
        rows = presenter_soup.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                key = clean_html_text(cells[0].get_text())
                value = clean_html_text(cells[1].get_text())
                if key and value:
                    presenter_info[key] = value
            elif len(cells) == 1:
                text = clean_html_text(cells[0].get_text())
                if text and not any(x in text.lower() for x in ['présentée', 'conseiller']):
                    if 'company_address' not in presenter_info:
                        presenter_info['company_address'] = []
                    presenter_info['company_address'].append(text)
   
    # Extract addressee info (banque)
    addressee_info = extract_section_data(
        html_content, 
        r'Adressée à.*?</th>.*?</tr>(.*?)(?=<th|</table>)', 
        "addressee"
    )
   
    # Extract borrower information
    borrower_info = extract_section_data(
        html_content,
        r'<th[^>]*><strong>Emprunteur</strong>[^<]*</th>.*?</thead>.*?<tbody>(.*?)</tbody>',
        "borrower"
    )
   
    # Extract co-borrower information
    co_borrower_info = extract_section_data(
        html_content,
        r'<th[^>]*><strong>Co-Emprunteur[^<]*</strong>[^<]*</th>.*?</thead>.*?<tbody>(.*?)</tbody>',
        "co_borrower"
    )
   
    # Extract household info
    household_info = extract_section_data(
        html_content,
        r'<th[^>]*><strong>Ménage[^<]*</strong>[^<]*</th>.*?</thead>.*?<tbody>(.*?)</tbody>',
        "household"
    )
   
    # Extract professional situation
    prof_borrower = extract_section_data(
        html_content,
        r'Situation professionnelle de l\'emprunteur.*?</th>.*?</thead>.*?<tbody>(.*?)(?=</tbody>.*?<table|</div>)',
        "prof_borrower"
    )
    
    prof_co_borrower = extract_section_data(
        html_content,
        r'Situation professionnelle.*?du co-emprunteur.*?</th>.*?</thead>.*?<tbody>(.*?)(?=</tbody>.*?<table|</div>)',
        "prof_co_borrower"
    )
   
    # Extract income information
    income_borrower = extract_section_data(
        html_content,
        r'Revenus mensuels de l\'emprunteur.*?</th>.*?</thead>.*?<tbody>(.*?)</tbody>',
        "income_borrower"
    )
    
    income_co_borrower = extract_section_data(
        html_content,
        r'Revenus mensuels du coemprunteur.*?</th>.*?</thead>.*?<tbody>(.*?)</tbody>',
        "income_co_borrower"
    )
    
    social_income = extract_section_data(
        html_content,
        r'<th[^>]*><strong>Revenus sociaux[^<]*</strong>[^<]*</th>.*?</thead>.*?<tbody>(.*?)</tbody>',
        "social_income"
    )
    
    other_info = extract_section_data(
        html_content,
        r'<th[^>]*><strong>Autres Informations[^<]*</strong>[^<]*</th>.*?</thead>.*?<tbody>(.*?)</tbody>',
        "other_info"
    )
   
    # Extract project characteristics
    project_info = extract_section_data(
        html_content,
        r'Caractéristique du projet à financer.*?</th>.*?</thead>.*?<tbody>(.*?)</tbody>',
        "project"
    )
   
    # Extract project cost
    project_cost = extract_section_data(
        html_content,
        r'Coût du projet.*?</th>.*?</thead>.*?<tbody>(.*?)</tbody>',
        "project_cost"
    )
   
    # Extract financing plan
    financing_plan = {}
    financing_pattern = r'Plan de financement.*?</th>.*?</thead>.*?<tbody>(.*?)</tbody>'
    financing_match = re.search(financing_pattern, html_content, re.DOTALL)
    if financing_match:
        financing_content = financing_match.group(1)
        financing_soup = BeautifulSoup(financing_content, 'html.parser')
        rows = financing_soup.find_all('tr')
        for row in rows:
            cells = row.find_all(['th', 'td'])  # Check both th and td
            if len(cells) >= 2:
                key = clean_html_text(cells[0].get_text())
                value = clean_html_text(cells[1].get_text())
                if key and value:
                    financing_plan[key] = value
   
    # Extract existing credits
    credits = extract_credits_info(html_content)
   
    # Extract patrimoine
    patrimoine = extract_patrimoine_info(html_content)
   
    # Compile all data
    extracted_data = {
        "header_info": header_info,
        "presenter_info": presenter_info,
        "addressee_info": addressee_info,
        "borrower_info": borrower_info,
        "co_borrower_info": co_borrower_info,
        "household_info": household_info,
        "professional_situation": {
            "borrower": prof_borrower,
            "co_borrower": prof_co_borrower
        },
        "income_info": {
            "borrower": income_borrower,
            "co_borrower": income_co_borrower,
            "social_income": social_income,
            "other_info": other_info
        },
        "project_info": project_info,
        "project_cost": project_cost,
        "financing_plan": financing_plan,
        "existing_credits": credits,
        "patrimoine": patrimoine
    }
   
    return extracted_data

def process_ddp_file(input_file='ddp.json', output_file='cleaned_ddp.json'):
    """Process the DDP JSON file and extract clean data from multiple applications"""
    try:
        # Check if input file exists
        if not os.path.exists(input_file):
            print(f"❌ Error: File '{input_file}' not found")
            return None
            
        print(f"📂 Reading file: {input_file}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different data structures
        if isinstance(data, dict):
            # If the JSON contains a single object, convert to list
            data = [data]
        elif not isinstance(data, list):
            print(f"❌ Error: Expected list or dict, got {type(data)}")
            return None
            
        print(f"📊 Found {len(data)} applications to process")
        
        cleaned_data = []
        processed_count = 0
        error_count = 0
        
        for i, item in enumerate(data):
            try:
                print(f"🔄 Processing application {i+1}/{len(data)}...", end='\r')
                
                # Extract metadata with safe get operations
                metadata = {
                    "id": item.get("id"),
                    "name": clean_html_text(str(item.get("name", ""))),
                    "simulation_id": item.get("simulation_id"),
                    "partenaire_bancaire_id": item.get("partenaire_bancaire_id"),
                    "interlocuteurs_id": item.get("interlocuteurs_id"),
                    "banque_id": item.get("banque_id"),
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at"),
                    "commentaire": item.get("commentaire"),
                    "etape": item.get("etape"),
                    "date_envoie": item.get("date_envoie"),
                    "date_decision": item.get("date_decision"),
                    "propositions_id": item.get("propositions_id"),
                    "montant_credit_initio": item.get("montant_credit_initio"),
                    "type": clean_html_text(str(item.get("type", "")))
                }
                
                # Extract data from HTML body
                html_content = item.get("body", "")
                extracted_info = {}
                
                if html_content:
                    extracted_info = extract_all_data_from_html(html_content)
                
                # Combine metadata and extracted info
                cleaned_item = {
                    "metadata": metadata,
                    "extracted_data": extracted_info
                }
                
                cleaned_data.append(cleaned_item)
                processed_count += 1
                
            except Exception as e:
                print(f"\n⚠️  Error processing item {i+1}: {str(e)}")
                error_count += 1
                # Continue processing other items
                continue
        
        print(f"\n✅ Successfully processed {processed_count} applications")
        if error_count > 0:
            print(f"⚠️  {error_count} applications had errors and were skipped")
        
        # Save cleaned data
        print(f"💾 Saving cleaned data to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Cleaned data saved successfully!")
        return cleaned_data
        
    except FileNotFoundError:
        print(f"❌ Error: File '{input_file}' not found")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def analyze_cleaned_data(cleaned_data):
    """Analyze the cleaned data and provide summary statistics"""
    if not cleaned_data:
        return
        
    print("\n" + "="*50)
    print("📊 DATA ANALYSIS SUMMARY")
    print("="*50)
    
    total_applications = len(cleaned_data)
    print(f"📋 Total applications processed: {total_applications}")
    
    # Count applications with different types of data
    apps_with_borrower = sum(1 for app in cleaned_data if app['extracted_data'].get('borrower_info'))
    apps_with_co_borrower = sum(1 for app in cleaned_data if app['extracted_data'].get('co_borrower_info'))
    apps_with_project = sum(1 for app in cleaned_data if app['extracted_data'].get('project_info'))
    apps_with_credits = sum(1 for app in cleaned_data if app['extracted_data'].get('existing_credits'))
    
    print(f"👤 Applications with borrower info: {apps_with_borrower} ({apps_with_borrower/total_applications*100:.1f}%)")
    print(f"👥 Applications with co-borrower info: {apps_with_co_borrower} ({apps_with_co_borrower/total_applications*100:.1f}%)")
    print(f"🏠 Applications with project info: {apps_with_project} ({apps_with_project/total_applications*100:.1f}%)")
    print(f"💳 Applications with existing credits: {apps_with_credits} ({apps_with_credits/total_applications*100:.1f}%)")
    
    # Show sample data structure
    if cleaned_data:
        sample = cleaned_data[0]
        print(f"\n📋 Sample data structure:")
        print(f"🏢 Metadata keys: {list(sample['metadata'].keys())}")
        print(f"📊 Extracted data keys: {list(sample['extracted_data'].keys())}")
        
        # Show some sample values if available
        if sample['extracted_data'].get('borrower_info'):
            print(f"\n👤 Sample borrower info fields:")
            borrower_keys = list(sample['extracted_data']['borrower_info'].keys())[:5]
            for key in borrower_keys:
                value = sample['extracted_data']['borrower_info'][key]
                print(f"  • {key}: {value[:50]}..." if len(str(value)) > 50 else f"  • {key}: {value}")

# Main execution
if __name__ == "__main__":
    print("🚀 Starting DDP JSON Processor")
    print("="*50)
    
    # Process the file
    result = process_ddp_file('ddp.json', 'cleaned_ddp.json')
    
    if result:
        # Analyze the results
        analyze_cleaned_data(result)
        
        print(f"\n🎉 Processing complete!")
        print(f"📁 Original file: ddp.json")
        print(f"📁 Cleaned file: cleaned_ddp.json")
        print(f"📊 Total applications processed: {len(result)}")
    else:
>>>>>>> 53c437e1624fe52a63599746e8d3c0dc5be37097
        print("\n❌ Processing failed. Please check your input file.")