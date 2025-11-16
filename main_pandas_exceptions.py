import csv
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from datetime import datetime
import numpy as np
import os
from rapidfuzz import process, fuzz
import re
import unicodedata

cwd = os.getcwd()

def normalize(s: str) -> str:
    if not isinstance(s, str):
        return ""
    # lower, strip accents, collapse spaces
    s = s.lower().strip()
    s = ''.join(
        c for c in unicodedata.normalize('NFKD', s)
        if not unicodedata.combining(c)
    )
    s = re.sub(r'\s+', ' ', s)
    return s

def initialisation_manual(df_all):
    file_path = f'{os.getcwd()}\\InputFiles\\Initialisation\\bank_init.csv'

    if os.path.exists(file_path):
        df_init = pd.read_csv(f'{file_path}')
        df_init['Date'] = pd.to_datetime(df_init['Date'], format='%d/%m/%Y')

        df_init['Date'] = df_init['Date'].dt.strftime('%Y-%m-%d')
        description_search_init = "Start Date Dashboard"
        start_transactions = df_init[df_init["Description"] == description_search_init]["Date"].iloc[0]
        df_init = df_init[df_init["Description"] != description_search_init].copy()

        df_all = df_all[df_all["Date"] >= start_transactions].copy()

        df_all = pd.concat([df_all, df_init]).reset_index(drop=True)
    else:
        print(f"No files to initialise banking")

    return df_all

def initialisation_taxes(df_all):
    file_path = f'{os.getcwd()}\\InputFiles\\Initialisation\\taxes_init.csv'

    if os.path.exists(file_path):
        df_init = pd.read_csv(f'{file_path}')
        df_init['Date'] = pd.to_datetime(df_init['Date'], format='%d/%m/%Y')
        df_init['Date'] = df_init['Date'].dt.strftime('%Y-%m-%d')
        description_search_init = "taxes_delete"
        tax_amount = df_init[df_init["Description"] == description_search_init]["Amount"].tolist()
        df_init = df_init[~(df_init["Description"] == description_search_init)].copy()
        df_init["Description"] = "taxes"
        df_all = df_all[~((df_all['Amount'].isin(tax_amount)))].copy()
        df_all = pd.concat([df_all, df_init]).reset_index(drop=True)
        df_all["Date"] = pd.to_datetime(df_all['Date'], format='%Y-%m-%d')
        
        df_all["month"] = df_all["Date"].dt.month
        df_all["year"] = df_all["Date"].dt.year 
        df_all["category"] = np.nan
        df_all["sub-category"] = np.nan
    else:
        print(f'No files to initialise taxes')
    return df_all

def pillar2a(df_all):
    file_path = f'{os.getcwd()}\\InputFiles\\Initialisation\\pillar2a.csv'

    if os.path.exists(file_path):
        df_2a = pd.read_csv(f'{file_path}')
        df_2a['Date'] = pd.to_datetime(df_2a['Date'], format='%d/%m/%Y')
        df_2a = df_2a.sort_values(by='Date')

        result = []

        for idx, row_salary in df_all[df_all["category"] == "salary"].iterrows():
            date_salary = pd.to_datetime(row_salary['Date'])
            
            previous_date = pd.to_datetime('2000-01-01')  # Initialize previous_date
            
            for index_pke, row_pke in df_2a.iterrows():
                current_date = row_pke['Date']  # Current date of row in df_2a

                if (date_salary < current_date) and (date_salary >= previous_date):
                    previous_date = current_date  # Update the previous_date

                    modified_row = row_pke.copy()
                    modified_row["Date"] = date_salary

                    result.append(modified_row)
                    break
        
        if result:
            df_all = pd.concat([df_all, pd.DataFrame(result)], ignore_index=True)
            df_all["Date"] = pd.to_datetime(df_all['Date'], format='%Y-%m-%d') 
            df_all["month"] = df_all["Date"].dt.month
            df_all["year"] = df_all["Date"].dt.year 
            df_all["day"] = df_all["Date"].dt.day 

    else:
        print("No files to initialise pillar 2a")

    return df_all

def read_flags(cwd):
    flag_dir  = fr"{cwd}\InputFiles\Flags"
    if not os.path.exists(flag_dir):
        print(f"⚠️ Folder {flag_dir} not found — no flags loaded.")

    # Loop through all CSVs and create variables dynamically
    for filename in os.listdir(flag_dir):
        if filename.endswith(".csv"):
            varname = os.path.splitext(filename)[0]  # e.g., e.csv → e
            path = os.path.join(flag_dir, filename)
            flags = (
                pd.read_csv(path, header=None)[0]  # first column
                .dropna()
                .map(str.strip)
                .tolist()
            )
            globals()[varname] = flags   # creates variable like e, flag_utilities
            print(f"Loaded {varname} with {len(flags)} items.")
    


def apply_exceptions(cwd, df_all):
    exceptions_path = f"{cwd}\\InputFiles\\Exception_csv\\categorization_exceptions.csv"
    
    if os.path.exists(exceptions_path):
        exceptions_df = pd.read_csv(exceptions_path, dtype=str)
        print("Exceptions applied.")
    
        # Ensure correct types in df_all
        df_all["Amount"] = pd.to_numeric(df_all["Amount"], errors="coerce")
        df_all["month"] = pd.to_numeric(df_all["month"], errors="coerce")
        df_all["year"] = pd.to_numeric(df_all["year"], errors="coerce")
        if "Date" in df_all.columns:
            df_all["Date"] = pd.to_datetime(df_all["Date"], errors="coerce")

        print_rule = False
        for index, row in df_all.iterrows():

            for _, rule in exceptions_df.iterrows():
                # --- Match subject and category with AND condition if both are specified ---
                subject_specified = pd.notna(rule.get("subject")) and rule["subject"].strip() != ""
                category_specified = pd.notna(rule.get("category")) and rule["category"].strip() != ""

                if subject_specified and category_specified:
                    rule_subject = rule["subject"].strip().lower()
                    row_subject = str(row.get("Subject", "")).strip().lower()
                    rule_category = rule["category"].strip().lower()
                    row_category = str(row.get("category", "")).strip().lower()

                    if rule_subject not in row_subject or rule_category != row_category:
                        continue

                elif subject_specified:
                    rule_subject = rule["subject"].strip().lower()
                    row_subject = str(row.get("Subject", "")).strip().lower()
                    if rule_subject not in row_subject:
                        continue

                elif category_specified:
                    rule_category = rule["category"].strip().lower()
                    row_category = str(row.get("category", "")).strip().lower()
                    if rule_category != row_category:
                        continue

                # --- Description substring match ---
                if pd.notna(rule["description_substring"]) and rule["description_substring"].lower() not in str(row["Description"]).lower():
                    continue

                # --- Amount range ---
                if pd.notna(rule["amount_min"]) and row["Amount"] < float(rule["amount_min"]):
                    continue
                if pd.notna(rule["amount_max"]) and row["Amount"] > float(rule["amount_max"]):
                    continue

                # --- Year logic ---
                year_cond = str(rule.get("year_condition", "")).strip()
                y_min = str(rule.get("year_min", "")).strip()
                y_max = str(rule.get("year_max", "")).strip()

                if year_cond in {"&", "|"} and y_min.isdigit() and y_max.isdigit():
                    y_min, y_max = int(y_min), int(y_max)
                    if year_cond == "&":
                        if not (y_min <= row["year"] <= y_max):
                            continue
                    elif year_cond == "|":
                        if not (row["year"] <= y_min or row["year"] >= y_max):
                            continue
                else:
                    if y_min.isdigit() and row["year"] < int(y_min):
                        continue
                    if y_max.isdigit() and row["year"] > int(y_max):
                        continue

                # --- Month logic ---
                month_cond = str(rule.get("month_condition", "")).strip()
                m_min = str(rule.get("month_min", "")).strip()
                m_max = str(rule.get("month_max", "")).strip()

                if month_cond in {"&", "|"} and m_min.isdigit() and m_max.isdigit():
                    m_min, m_max = int(m_min), int(m_max)
                    if m_min == m_max:
                        if row["month"] != m_min:
                            continue
                    elif month_cond == "&":
                        if not (m_min <= row["month"] <= m_max):
                            continue
                    elif month_cond == "|":
                        if not (row["month"] >= m_min or row["month"] <= m_max):
                            continue
                elif m_min.isdigit() and row["month"] != int(m_min):
                    continue

                # --- Date range ---
                if pd.notna(rule["date_min"]) or pd.notna(rule["date_max"]):
                    if "Date" not in df_all.columns:
                        continue
                    row_date = row["Date"]
                    if pd.notna(rule["date_min"]) and row_date < pd.to_datetime(rule["date_min"], dayfirst=True, errors="coerce"):
                        continue
                    if pd.notna(rule["date_max"]) and row_date > pd.to_datetime(rule["date_max"], dayfirst=True, errors="coerce"):
                        continue

                # --- Apply changes ---
                if pd.notna(rule["new_description"]):
                    df_all.at[index, "Description"] = rule["new_description"]
                if pd.notna(rule["new_category"]):
                    df_all.at[index, "category"] = rule["new_category"]
                if pd.notna(rule["new_month"]):
                    df_all.at[index, "month"] = int(rule["new_month"])
                if pd.notna(rule["new_year"]):
                    df_all.at[index, "year"] = int(rule["new_year"])

                break  # Stop at first matching rule

            print_rule = False
    else:
        print("No exceptions file found. Skipping exceptions.")
    return df_all


def clean_postfinance(df_all, format):

    if format == 'csv':
        extracted = df_all['Description'].str.extract(r'CARTE N° XXXX\d{4} (.*?) ID PAIEMENT')[0]
        df_all["Description"] = extracted.fillna(df_all['Description'])
        extracted = df_all['Description'].str.extract(r'CARTE NO XXXX\d{4} (.*?)')[0]
        df_all["Description"] = extracted.fillna(df_all['Description'])

        extracted = df_all['Description'].str.extract(r'CRÉDIT CH\d{19} (.*?) REFERENCE DE L')[0]
        df_all["Description"] = extracted.fillna(df_all['Description'])

        extracted = df_all['Description'].str.extract(r'DÉBIT CH\d{19} (.*?) REFERENCE DE L')[0]
        df_all["Description"] = extracted.fillna(df_all['Description'])

        extracted = df_all['Description'].str.extract(r'DÉBIT CH\d{19} (.*?)')[0]
        df_all["Description"] = extracted.fillna(df_all['Description'])

        extracted = df_all['Description'].str.extract(r'CRÉDIT CH\d{19} (.*?)')[0]
        df_all["Description"] = extracted.fillna(df_all['Description'])

        extracted = df_all['Description'].str.extract(r'^(?:.*DESTINATAIRE PAIEMENT:.*)?DESTINATAIRE PAIEMENT:\s*(.*?)\s*ID DE TRANSACTION:')[0]
        df_all["Description"] = extracted.fillna(df_all['Description'])

        extracted = df_all['Description'].str.extract(r'DESTINATAIRE PAIEMENT:\s*(.*?)\s*ID DE TRANSACTION:')[0]
        df_all["Description"] = extracted.fillna(df_all['Description'])

        for index, row in df_all.iterrows():
            if "RÉCEPTION D'ARGENT TWINT" in row["Description"]:
                df_all.loc[index, "Description"] = "Twint" + row["Description"].split("41763588431")[1]
            elif "41763588431 POUR NUMERO MOBILE" in row["Description"]:
                df_all.loc[index, "Description"] = "Twint" + row["Description"].split("41763588431 POUR NUMERO MOBILE")[1]
            elif "ACHAT/PRESTATION TWINT" in row["Description"]:
                df_all.loc[index, "Description"] = "Achat" + row["Description"].split("41763588431")[1]
    original_descriptions = df_all['Description'].copy()

    original_descriptions = df_all['Description'].copy()

    # Apply case-insensitive replacement
    pattern = r'achat/prestation twint du\d{2}\.\d{2}\.\d{4} depuis le n° de téléphone \+\d+'
    df_all['Description'] = df_all['Description'].str.replace(pattern, '', regex=True, flags=re.IGNORECASE).str.strip()

    changed_rows = df_all[original_descriptions != df_all['Description']]
    #print(changed_rows)
    pattern = r'charge\s+cpte\s+carte\s+de\s+credit\s+[a-z]*\s*\d+\s+du\s+\d{2}\.\d{2}\.\d{4}'
    df_all['Description'] = (
        df_all['Description']
        .str.replace(pattern, 'charge carte de credit', regex=True, flags=re.IGNORECASE)
        .str.strip()
    )

    pattern = r"envoi d'argent twint du \d{2}\.\d{2}\.\d{4} pour numero mobile\. \+\d+\s*"
    df_all['Description'] = (
        df_all['Description']
        .str.replace(pattern, '', regex=True, flags=re.IGNORECASE)
        .str.strip()
    )

    df_all.loc[df_all['Description'].str.contains(r"retrait d'espèces", case=False, na=False), 'Description'] = "retrait d'espèces"


    pattern = r"envoi d'argent twint du\d{2}\.\d{2}\.\d{4} depuis le n° de téléphone \+\d+ pour numero mobile\. \+\d+\s*"
    df_all['Description'] = (
        df_all['Description']
        .str.replace(pattern, '', regex=True, flags=re.IGNORECASE)
        .str.strip()
    )

    delete_lst = [
        "CRÉDIT DONNEUR D'ORDRE:",
    ]
    for word in delete_lst:
        df_all["Description"] = df_all["Description"].str.replace(word, "", regex=False)
    return df_all


def read_postfinance_xml(cwd, df_prev):
    all_data = []
    file_inputs = fr'{cwd}\InputFiles\Postfinance'
    file_names = [i for i in os.listdir(file_inputs) if i[-4:] == ".xml"]

    if file_names:
        for filename in file_names:
            filepath = os.path.join(file_inputs, filename)
            print(f"Processing {filename}...")
            all_data.extend(parse_xml_file(filepath))
        
        df_all = pd.DataFrame(all_data)
        df_all["category"] = "others"
        df_all.rename(columns={"ValueDate":"Date"}, inplace=True)
        df_all["Amount"] = df_all["Amount"].astype(float)
        df_all["Amount"] = df_all.apply(
            lambda row: -float(row["Amount"]) if row["CreditDebit"] == "DBIT" else float(row["Amount"]),
            axis=1
        )
        df_all.replace('', 0, inplace=True)  # Replace empty strings
        df_all.fillna(0, inplace=True)        # Replace NaN values
        df_all["Date"] = pd.to_datetime(df_all['Date'], format='%Y-%m-%d')
        df_all['Date'] = df_all['Date'].dt.strftime('%Y-%m-%d')
        df_all = df_all[["Date","category","Description","Amount"]].copy()
        df_all = clean_postfinance(df_all,'xml')
        if df_prev is not None:
            df_all = pd.concat([df_prev, df_all])
    else:
        print("No files from post finance found")        
        if df_prev is not None:
            return df_prev
        else:
            return None
    return df_all


def read_postfinance_csv(cwd, df_prev):
    file_inputs = fr'{cwd}\InputFiles\Postfinance'
    file_names = [i for i in os.listdir(file_inputs) if i[-4:] == ".csv"]
    df_all = []
    if file_names:
        for file_name in file_names:
            df_valid, df_postprocess = process_data(f'{file_inputs}\\{file_name}')
            df_valid, new_header = process_valid(df_valid)
            df_postprocess = process_postprocess(df_postprocess, new_header)

            df = pd.concat([df_postprocess, df_valid]).reset_index(drop=True)
            df_all.append(df)
        df_all = pd.concat(df_all)

        df_all = df_all.rename(columns={"Texte de notification":"Description"})
        df_all.replace('', 0, inplace=True)  # Replace empty strings
        df_all.fillna(0, inplace=True)        # Replace NaN values
        df_all["Débit en CHF"] = df_all["Débit en CHF"].astype(float)
        df_all["Crédit en CHF"] = df_all["Crédit en CHF"].astype(float)
        df_all["Amount"] = df_all["Débit en CHF"] + df_all["Crédit en CHF"] 
        df_all = df_all.drop(columns = ["Débit en CHF", "Crédit en CHF"])
        df_all["Date"] = pd.to_datetime(df_all['Date'], format='%d.%m.%Y')
        df_all['Date'] = df_all['Date'].dt.strftime('%Y-%m-%d')

        df_all["category"] = "others"
        df_all["sub-category"] = np.nan
        df_all = df_all[["Date","category","Description","Amount"]].copy()
        
        df_all = clean_postfinance(df_all,'csv')

        if df_prev is not None:
            df_all = pd.concat([df_prev, df_all])
    else:
        print("No files from post finance found")        
        if df_prev is not None:
            return df_prev
        else:
            return None

    return df_all


def categorise(cwd, df_all):
    read_flags(cwd)
    df_all['category'] = df_all['category'].astype('object')
    df_all.loc[(df_all["Original currency"].notna()) & (df_all["category"].isna()) & (df_all["Original currency"] != "CHF"), 'category'] = "holidays"
    df_all.loc[df_all["category"].isna(), 'category'] = "others"
    df_all.loc[(df_all["month"] == 10) & (df_all["year"] == 2021) & (df_all["Amount"] >= 16000), 'category'] = "salary" #Money from Credit Suisse
    
    for index, row in df_all.iterrows():
        #Salary
        skip = False
        for flag in flag_salary:
            if (flag.lower() in row["Description"].lower()) & (skip == False):
                df_all.loc[index, "category"] = "salary"
                skip = True
                if flag.lower() != "salary": #Note de frais et voyage rembourse
                    df_all.loc[index, "Description"] = "salary"
                    df_all.loc[index, "category"] = "salary"
        #Investments
        for flag in flag_investments:
            if (flag.lower() in row["Description"].lower()) & (skip == False):
                df_all.loc[index, "category"] = "investment"
                skip = True
                if "WIR Bank" in df_all.loc[index, "Description"]: 
                    df_all.loc[index, "Description"] = "Viac 3a"
        
        for flag in flag_pillar2a:
            if (flag.lower() in row["Description"].lower()) & (skip == False):
                df_all.loc[index, "category"] = "pillar2a"
                skip = True
        
        #Housing
        for flag in flag_house:
            if (flag.lower() in row["Description"].lower()) & (skip == False):
                df_all.loc[index, "category"] = "housing"
                skip = True
        #Taxes
        for flag in flag_taxes:
            if (flag.lower() in row["Description"].lower()) & (skip == False):
                df_all.loc[index, "category"] = "taxes"
                skip = True

        #Transportation
        for flag in flag_transportation:
            if (flag.lower() in row["Description"].lower()) & (skip == False):
                df_all.loc[index, "category"] = "transportation"
                skip = True
        #Insurance
        for flag in flag_insurance:
            if (flag.lower() in row["Description"].lower()) & (skip == False):
                df_all.loc[index, "category"] = "insurance"
                skip = True
        #Food
        for flag in flag_food:
            if (flag.lower() in row["Description"].lower()) & (skip == False):
                df_all.loc[index, "category"] = "food"
                skip = True
        #Clothes
        for flag in flag_clothes:
            if (flag.lower() in row["Description"].lower()) & (skip == False):
                df_all.loc[index, "category"] = "clothes"
                skip = True
        #Other
        for flag in flag_other:
            if (flag.lower() in row["Description"].lower()) & (skip == False):
                df_all.loc[index, "category"] = "others"
                skip = True
        #Sport
        for flag in flag_sport:
            if (flag.lower() in row["Description"].lower()) & (skip == False):
                df_all.loc[index, "category"] = "sport"
                skip = True

        #Health
        for flag in flag_health:
            if (flag.lower() in row["Description"].lower()) & (skip == False):
                df_all.loc[index, "category"] = "health"
                skip = True
        
        #Restaurant
        for flag in flag_restaurant:
            if (flag.lower() in row["Description"].lower()) & (skip == False):
                df_all.loc[index, "category"] = "restaurant"
                
                for flag_res in flag_holidays: #IF I wrote before doing the neon transfer the subject
                    if (flag_res in str(df_all.loc[index, "Subject"])):
                        df_all.loc[index, "Description"] = "Twint"
                        df_all.loc[index, "category"] = "holidays"
                
                for flag_other_lvl2 in flag_other: #IF I wrote before doing the neon transfer the subject
                    if (flag_other_lvl2 in str(df_all.loc[index, "Subject"])):
                        df_all.loc[index, "Description"] = "Twint_present"
                        df_all.loc[index, "category"] = "others"
                
                for flag_other_lvl2 in flag_sport: #IF I wrote before doing the neon transfer the subject
                    if (flag_other_lvl2 in str(df_all.loc[index, "Subject"])):
                        df_all.loc[index, "Description"] = "Twint_sport"
                        df_all.loc[index, "category"] = "sport"
                        
                for flag_t in flag_twint:
                    if (flag_t.lower() in df_all.loc[index, "Description"].lower()) & (abs(df_all.loc[index, "Amount"]) <= 110)&(skip==False):  #Twint must be below 200 chf otherwise holidays
                        df_all.loc[index, "Description"] = "Twint"
                        
                    elif (flag_t.lower() in df_all.loc[index, "Description"].lower()) & (abs(df_all.loc[index, "Amount"]) >= 110)&(skip==False):
                        df_all.loc[index, "category"] = "holidays"    
                        df_all.loc[index, "Description"] = "Twint"
    
                if "Uber" in df_all.loc[index, "Description"]:
                    df_all.loc[index, "Description"] = "Uber eat"
                skip = True
        
        #Holidays
        for flag in flag_holidays:
                if (flag.lower() in row["Description"].lower()) & (skip ==False):
                    skip = True
                    df_all.loc[index, "category"] = "holidays"

        #Entertainment
        for flag in flag_entertainment:
            if (flag in row["Description"].lower()) & (skip == False):
                df_all.loc[index, "category"] = "entertainment"
                skip = True
        #Drop rows (swiss card for double counting etc)
        for flag in flag_drop_row:
            if (flag.lower() in row["Description"].lower()) & (row["Date"] >= datetime(2022,7,11)) & (skip == False): #No historiy of swisscard before
                df_all = df_all.drop(labels=index, axis=0)
                skip = True

        for flag in flag_pirates:
            if (flag.lower() in row["Description"].lower()) & (skip == False):
                df_all.loc[index, "category"] = "website"
    
                skip = True

    df_all["Date"] = pd.to_datetime(dict(year=df_all.year, month=df_all.month, day=df_all.Date.dt.day))
    df_all = apply_exceptions(cwd, df_all)
    df_all["Date"] = pd.to_datetime(dict(year=df_all.year, month=df_all.month, day=df_all.Date.dt.day))
    #print(df_all[df_all["Description"].str.lower().str.contains("ilham")])

    return df_all

def swisscard(cwd, df_prev):
    cwd = fr'{cwd}\InputFiles\swisscard'
    file_names = [i for i in os.listdir(f'{cwd}') if i[-4:] == ".csv"]

    if file_names:
        df_all = []
        for file_name in file_names:
            df = pd.read_csv(f'{cwd}\\{file_name}', on_bad_lines='skip', sep=',')
            df_all.append(df)

        df_all = pd.concat(df_all)
        df_all = df_all.reset_index(drop=True)
        df_all = df_all.rename(columns={"Transaction date" : "Date","Currency":"Original currency"})
        df_all['Date'] = pd.to_datetime(df_all['Date'],dayfirst = True)

        df_all.loc[:,"category"] = np.nan
        df_all.loc[:,"sub-category"] = np.nan
        df_all.loc[:,"Subject"] = np.nan
        df_all["Amount"] = df_all["Amount"] * -1
        #df_swisscard_all = categorise(df_all)
        df_all = df_all[['Date', 'Amount', 'Original currency', 'Description', 'Subject']]
        df_all['Date'] = df_all['Date'].dt.strftime('%Y-%m-%d')

        if df_prev is not None:
            df_all = pd.concat([df_prev, df_all])
    else:
        print("No files from swisscard found")
        if df_prev is not None:
            return df_prev
        else:
            return None
    return df_all

def read_neon(cwd):
    cwd = fr'{cwd}\InputFiles\neon'

    file_names = [i for i in os.listdir(f'{cwd}') if i[-4:] == ".csv"]
    if file_names:
        df_all = []
        for file_name in file_names:
            file_name = f'{cwd}\\{file_name}'
            df = pd.read_csv(file_name, on_bad_lines='skip', sep=';')
            df_all.append(df)

        df_all = pd.concat(df_all)
        df_all = df_all.reset_index(drop=True)
        df_all["Date"] = pd.to_datetime(df_all['Date'], format='%Y-%m-%d')
        df_all['Date'] = df_all['Date'].dt.strftime('%Y-%m-%d')
        df_all = df_all[['Date', 'Amount', 'Original currency', 'Description', 'Subject', 'Category']]
    else:
        print("No files from neon found")
        return None
    return df_all

def sbb_half_tax(df_all):
    modified_rows = []
    for index, row in df_all[(df_all["category"]=="transportation")&(df_all["Amount"]<=-1600)].iterrows():
        Sbb_amount = row["Amount"] / 10 # make it monthly
        df_all = df_all.drop(labels=index, axis=0)
        row["Date"] = row["Date"] + relativedelta(months=-1)
        for month in range(1,13):
            new_row = row.copy()
            new_row["Date"] = row["Date"] + relativedelta(months=month)
            new_row["Amount"] = Sbb_amount
            new_row["year"] = new_row["Date"].year
            new_row["month"] = new_row["Date"].month
            if new_row["Date"] <= datetime.now(): # do not add if in the future
                modified_rows.append(new_row)
    df_all = pd.concat([df_all, pd.DataFrame(modified_rows)], axis=0, ignore_index=True)
    df_all["Date"] = pd.to_datetime(dict(year=df_all.year, month=df_all.month, day=df_all.Date.dt.day))
    df_all["month"] = df_all["Date"].dt.month
    df_all["year"] = df_all["Date"].dt.year 
    df_all["day"] = df_all["Date"].dt.day
        
    #Add fix and variable categories
    fix_list = ["housing", "transportation", "insurance", "taxes"]
    df_all.loc[df_all["category"].isin(fix_list),"fix_variable"] = "fix"
    df_all.loc[~df_all["category"].isin(fix_list),"fix_variable"] = "variable"
    return df_all

def find_header(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')  # Use semicolon as delimiter
        header_row_index = None
        for index, row in enumerate(reader):
            if row and row[0].strip().lower() == 'date':  # Adjust based on your actual header
                header_row_index = index
                break
    
    return header_row_index

def process_data(file_path, col_valid="Unnamed: 1"):
    header_row_index = find_header(file_path)
    df = pd.read_csv(file_path, delimiter=',', skiprows=header_row_index)

    df_valid = df[df[col_valid].isna()]
    df_postprocess = df[~(df[col_valid].isna())]

    df_valid = df_valid.drop(columns=[col_valid])
    df_valid.dropna(inplace=True)
    return df_valid, df_postprocess

def process_valid(df_valid):
    data = []
    
    # Iterate over each row in df_valid
    for index, row in df_valid.iterrows():
        # If the row has only one column
        if len(row) == 1:
            # Get the content of the first (and only) column
            cell_value = row.iloc[0].strip()  # Strip leading/trailing whitespace
            
            # Check if there is a semicolon in the cell value
            if ';' not in cell_value:
                continue  # Skip this row if no semicolon
            
            # Split the single string into columns using semicolon
            row = cell_value.split(';')
        
        # Truncate or pad the row to ensure it has exactly 5 elements
        row = row[:5]  # Keep first 5 columns
        while len(row) < 5:  # Pad with None if fewer than 5 columns
            row.append(None)
        
        data.append(row)
    
    # Rebuild the DataFrame using the processed data, keeping the original header
    new_header = df_valid.columns[:5] # Keep first 5 column names from the original
    new_header = new_header[0].split(';')
    df_processed = pd.DataFrame(data, columns=new_header)
    
    return df_processed, new_header

def process_postprocess(df_postprocess, new_header):
    if df_postprocess.shape[1] >= 2:
        df_postprocess['merged'] = df_postprocess.iloc[:, 0].astype(str) + ' ' + df_postprocess.iloc[:, 1].astype(str)        
        df_postprocess = df_postprocess.drop(columns=[df_postprocess.columns[0], df_postprocess.columns[1]])  # Drop first two columns

    data = []
    for index, row in df_postprocess.iterrows():
        new_row = ""
        row_count = 0
        
        for line in row:
            line = line.replace('"', '')
            new_row = new_row + line
            continue
        new_row = new_row.split(';') 

        if len(new_row) < 5:
            print(f"{len(row)} Skipping malformed row: {row}")
            continue  # Skip malformed rows
        
        new_row = new_row[:5] 
        while len(new_row) < 5:
            new_row.append(None)

        data.append(new_row)

    df_processed = pd.DataFrame(data, columns = new_header)
    return df_processed

def read_postfiannce(cwd, df_prev):
    file_inputs = fr'{cwd}\InputFiles\Postfinance'
    file_names = [i for i in os.listdir(file_inputs) if i[-4:] == ".csv"]
    df_all = []
    if file_names:
        for file_name in file_names:
            df_valid, df_postprocess = process_data(f'{file_inputs}\\{file_name}')
            df_valid, new_header = process_valid(df_valid)
            df_postprocess = process_postprocess(df_postprocess, new_header)

            df = pd.concat([df_postprocess, df_valid]).reset_index(drop=True)
            df_all.append(df)
        df_all = pd.concat(df_all)

        df_all = df_all.rename(columns={"Texte de notification":"Description"})
        df_all.replace('', 0, inplace=True)  # Replace empty strings
        df_all.fillna(0, inplace=True)        # Replace NaN values
        df_all["Débit en CHF"] = df_all["Débit en CHF"].astype(float)
        df_all["Crédit en CHF"] = df_all["Crédit en CHF"].astype(float)
        df_all["Amount"] = df_all["Débit en CHF"] + df_all["Crédit en CHF"] 
        df_all = df_all.drop(columns = ["Débit en CHF", "Crédit en CHF"])
        df_all["Date"] = pd.to_datetime(df_all['Date'], format='%d.%m.%Y')
        df_all['Date'] = df_all['Date'].dt.strftime('%Y-%m-%d')

        df_all["category"] = "others"
        df_all["sub-category"] = np.nan
        df_all = df_all[["Date","category","Description","Amount"]].copy()
        extracted = df_all['Description'].str.extract(r'CARTE N° XXXX\d{4} (.*?) ID PAIEMENT')[0]
        df_all["Description"] = extracted.fillna(df_all['Description'])
        extracted = df_all['Description'].str.extract(r'CARTE NO XXXX\d{4} (.*?)')[0]
        df_all["Description"] = extracted.fillna(df_all['Description'])

        extracted = df_all['Description'].str.extract(r'CRÉDIT CH\d{19} (.*?) REFERENCE DE L')[0]
        df_all["Description"] = extracted.fillna(df_all['Description'])

        extracted = df_all['Description'].str.extract(r'DÉBIT CH\d{19} (.*?) REFERENCE DE L')[0]
        df_all["Description"] = extracted.fillna(df_all['Description'])

        extracted = df_all['Description'].str.extract(r'DÉBIT CH\d{19} (.*?)')[0]
        df_all["Description"] = extracted.fillna(df_all['Description'])

        extracted = df_all['Description'].str.extract(r'CRÉDIT CH\d{19} (.*?)')[0]
        df_all["Description"] = extracted.fillna(df_all['Description'])

        extracted = df_all['Description'].str.extract(r'^(?:.*DESTINATAIRE PAIEMENT:.*)?DESTINATAIRE PAIEMENT:\s*(.*?)\s*ID DE TRANSACTION:')[0]
        df_all["Description"] = extracted.fillna(df_all['Description'])

        extracted = df_all['Description'].str.extract(r'DESTINATAIRE PAIEMENT:\s*(.*?)\s*ID DE TRANSACTION:')[0]
        df_all["Description"] = extracted.fillna(df_all['Description'])

        for index, row in df_all.iterrows():
            if "RÉCEPTION D'ARGENT TWINT" in row["Description"]:
                df_all.loc[index, "Description"] = "Twint" + row["Description"].split("41763588431")[1]
            elif "41763588431 POUR NUMERO MOBILE" in row["Description"]:
                df_all.loc[index, "Description"] = "Twint" + row["Description"].split("41763588431 POUR NUMERO MOBILE")[1]
            elif "ACHAT/PRESTATION TWINT" in row["Description"]:
                df_all.loc[index, "Description"] = "Achat" + row["Description"].split("41763588431")[1]


        if df_prev is not None:
            df_all = pd.concat([df_prev, df_all])
    else:
        print("No files from post finance found")        
        if df_prev is not None:
            return df_prev
        else:
            return None

    return df_all

def read_zkb(cwd, df_prev):
    cwd = fr'{cwd}\InputFiles\ZKB'

    file_names = [i for i in os.listdir(f'{cwd}') if i[-4:] == ".csv"]
    if file_names:
        df_all = []
        for file_name in file_names:
            file_name = f'{cwd}\\{file_name}'
            df = pd.read_csv(file_name, on_bad_lines='skip', sep=';')
            df_all.append(df)

        df_all = pd.concat(df_all)
        df_all = df_all.reset_index(drop=True)
        df_all["Date"] = pd.to_datetime(df_all['Date'], format='%d.%m.%Y')
        df_all.rename(columns = {"Booking text":"Description", "Curr": "Original currency"}, inplace=True)
        df_all["Amount"] = df_all["Credit CHF"].astype(float).fillna(0) - df_all["Debit CHF"].astype(float).fillna(0)
        df_all.drop(columns=["Credit CHF", "Debit CHF","ZKB reference", "Payment purpose", "Details", "Reference number", "Balance CHF","Amount details"], inplace =True)
        df_all["Description"] = df_all["Description"].astype(str)
        df_all['Description'] = df_all['Description'].str.replace(r'Purchase ZKB Visa Debit card no. xxxx \d{4},', '', regex=True).str.strip()
        df_all['Description'] = df_all['Description'].str.replace(r'Debit Standing order:', '', regex=True).str.strip()
        df_all['Description'] = df_all['Description'].str.replace(r'Debit eBill:', '', regex=True).str.strip()
        df_all['Date'] = df_all['Date'].dt.strftime('%Y-%m-%d')

        if df_prev is not None:
            df_all = pd.concat([df_prev, df_all])
    else:
        print("No files from ZKB found")
        if df_prev is not None:
            return df_prev
        else:
            return None
    return df_all

def map_similar_descriptions(df, threshold=80):
    description_to_group = {}
    used = set()
    df['Description'] = df['Description'].str.replace(r'zürich', '', regex=True).str.strip()
    df['Description'] = df['Description'].str.replace(r'gmbh', '', regex=True).str.strip()
    df['Description'] = df['Description'].str.replace(r'restaurant', '', regex=True).str.strip()
    
    for desc in df['Description']:
        if desc not in used:
            # Find matches above the threshold and unpack only match and score
            matches = [(match[0], match[1]) for match in process.extract(
                desc, df['Description'].tolist(), scorer=fuzz.ratio, limit=None
            )]
            
            # Filter matches based on the threshold
            similar_descriptions = [match for match, score in matches if score >= threshold]
            
            representative = desc
            for similar_desc in similar_descriptions:
                description_to_group[similar_desc] = representative
            used.update(similar_descriptions)
    
    df['Description'] = df['Description'].map(description_to_group)
    return df

def main(cwd):
    df_all = read_neon(cwd)
    df_all = read_zkb(cwd, df_all)
    df_all = swisscard(cwd, df_all)
    df_all = read_postfinance_csv(cwd, df_all)
    df_all = read_postfinance_xml(cwd, df_all)
    df_all = initialisation_manual(df_all)
    df_all = initialisation_taxes(df_all)
    df_all["Description"] = df_all["Description"].astype(str)
    df_all = categorise(cwd, df_all)
    df_all = pillar2a(df_all)
    df_all = sbb_half_tax(df_all)

    df_all_save = df_all[["year", "month","day", "category","fix_variable","Description","Amount"]].copy()

    #%% Prepare and save
    df_group = df_all.groupby(["year", "month", "category","fix_variable"], as_index=False)[["Amount"]].sum()  # ,'category_name'
    
    df_all_save['Description_original'] =df_all_save['Description']
    df_all_save['Description'] = df_all_save['Description'].str.lower()

    df_all_save = map_similar_descriptions(df_all_save, threshold=80)
    #print(df_all_save[df_all_save["Description"].str.contains("five", na=False)])

    df_all_save.to_csv(r"{cwd}\datasets\spent_all.csv".format(cwd=cwd),index=False)
    df_group.to_csv(r"{cwd}\datasets\spent_category.csv".format(cwd=cwd),index=False)
    pd.DataFrame(df_group["category"].unique(),columns=["category"]).to_csv(r"{cwd}\datasets\category.csv".format(cwd=cwd),index=False)

if __name__ == "__main__":
    main(cwd)