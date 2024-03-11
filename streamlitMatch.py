import pandas as pd
import numpy as np
# import json
# import gspread
# import datetime
import streamlit as st
# from oauth2client.service_account import ServiceAccountCredentials
# from gspread_dataframe import set_with_dataframe
from fuzzywuzzy import fuzz, process
from io import BytesIO
from datetime import datetime

# scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
# creds = ServiceAccountCredentials.from_json_keyfile_name("C:/Users/wyero/Downloads/Tinvio/vertex_ai_key.json", scope)
# client = gspread.authorize(creds)

fuzzy_threshold = 80
current_user = "Wye Rock"

# bank_statement_sheet = client.open("AIReconciliation").worksheet("BankStatements")
# payments_statement_sheet = client.open("AIReconciliation").worksheet("Payments")
# transactions_statement_sheet = client.open("AIReconciliation").worksheet("BusinessTransactions")
# mappings_sheet = client.open("AIReconciliation").worksheet("Mappings")
# user_to_contact_list = client.open("AIReconciliation").worksheet("Contacts")


# bank_statement_sheet = pd.DataFrame(bank_statement_sheet.get_all_records())
# payments_statement_sheet = pd.DataFrame(payments_statement_sheet.get_all_records())
# transactions_statement_sheet = pd.DataFrame(transactions_statement_sheet.get_all_records())

# bank_statement_sheet_test = bank_statement_sheet.replace("", np.nan)
# payments_statement_sheet_test = payments_statement_sheet.replace("", np.nan)
# transactions_statement_sheet_test = transactions_statement_sheet.replace("", np.nan)

# mappings_sheet = pd.DataFrame(mappings_sheet.get_all_records()).replace("", np.nan)

# Drop duplicate cft_names within each group
# mappings_sheet = mappings_sheet.drop_duplicates(subset=['bank_contact_name', 'cft_name'])

# Group by 'bank_contact_name' and aggregate 'cft_name' as a list
# grouped_data = mappings_sheet[mappings_sheet['cft_name'].notnull()].groupby('bank_contact_name')['cft_name'].apply(list).reset_index()

# Convert the grouped data to a dictionary
# result_dict = dict(zip(grouped_data['bank_contact_name'], grouped_data['cft_name']))

# user_to_contact_list_sheet = pd.DataFrame(user_to_contact_list.get_all_records()).replace("", np.nan)
# user_to_contact_list_sheet = user_to_contact_list_sheet.drop_duplicates(subset=['User', 'Contact'])
# grouped_data = user_to_contact_list_sheet[user_to_contact_list_sheet['Contact'].notnull()].groupby('User')['Contact'].apply(list).reset_index()
# user_to_contact_list_sheet_test = dict(zip(grouped_data['User'], grouped_data['Contact']))

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output

def exact_case_check(payer_payee, contact):
    if contact is None:
        return "No Match"
    
    fuzzy_score = fuzz.token_set_ratio(payer_payee, contact)
    if fuzzy_score >= fuzzy_threshold:
        return "Exact Match"
    else: 
        return "No Match"   
    
# def reconcile(bank_statement_df, payments_df, transactions_df_1, mappings_df, contacts_df):
#     bank_df = bank_statement_df.replace("", np.nan)
#     payments_df = payments_df.replace("", np.nan)
#     transactions_df = transactions_df_1.replace("", np.nan)
    


#     user_to_contact_list_sheet = contacts_df.replace("", np.nan)
#     user_to_contact_list_sheet = user_to_contact_list_sheet.drop_duplicates(subset=['User', 'Contact'])
#     grouped_data = user_to_contact_list_sheet[user_to_contact_list_sheet['Contact'].notnull()].groupby('User')['Contact'].apply(list).reset_index()
#     user_to_contact_list_sheet_test = dict(zip(grouped_data['User'], grouped_data['Contact']))
#     user_to_contact_list_sheet = user_to_contact_list_sheet_test

#     mappings_sheet = mappings_df.replace("", np.nan).drop_duplicates(subset=['bank_contact_name', 'cft_name'])
#     grouped_data = mappings_sheet[mappings_sheet['cft_name'].notnull()].groupby('bank_contact_name')['cft_name'].apply(list).reset_index()
#     mapping_dict = dict(zip(grouped_data['bank_contact_name'], grouped_data['cft_name']))


#     # Exercise 1 : Exact Match to Payment
#     exact_matches = []
#     matched_indices = set()
    
#     for index, statement_row in bank_df.iterrows():
#         if index in matched_indices:
#             continue
        
#         if pd.isnull(statement_row["Payer/Payee"]):
#             continue 

#         # Collect exact matches based on date and amount
#         exact_match_ids = []

#         for _, transaction_row in payments_df.iterrows():
#             if statement_row['Date'] == transaction_row['Date'] and statement_row['Amount'] == transaction_row['Amount'] and statement_row['Currency'] == transaction_row['Currency']:
#                 exact_match_ids.append(transaction_row['Transaction ID'])

#         exact_match_ids = [id for id in exact_match_ids if not payments_df.loc[payments_df['Transaction ID'] == id, 'Contact'].empty and pd.notna(payments_df.loc[payments_df['Transaction ID'] == id, 'Contact'].iat[0])]
        
#         remaining_exact_matches = []
        
#         for exact_match_id in exact_match_ids:

#             if statement_row['Payer/Payee'] in mapping_dict:
#                 if payments_df.loc[payments_df['Transaction ID'] == exact_match_id, 'Contact'].iat[0] in mapping_dict[statement_row['Payer/Payee']]:
#                     remaining_exact_matches.append(exact_match_id)
#                     #break Do we stop the exact match? There could be multiple mappings
#                 else: 
#                     if exact_case_check(payments_df.loc[payments_df['Transaction ID'] == exact_match_id, 'Contact'].iat[0], statement_row['Payer/Payee']) == "Exact Match":
#                         remaining_exact_matches.append(exact_match_id)
#             else: 
#                 if exact_case_check(payments_df.loc[payments_df['Transaction ID'] == exact_match_id, 'Contact'].iat[0], statement_row['Payer/Payee']) == "Exact Match":
#                     remaining_exact_matches.append(exact_match_id)

#         if len(remaining_exact_matches) == 1:
#             matched_indices.add(index)
#             exact_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
#                                           'Transaction ID': remaining_exact_matches[0], 'Status': 'Exact Match to Payment. Reconcile'})
        
#         # Exercise 3a : Choose from multiple matches to payments
#         elif len(remaining_exact_matches) > 1: 
#             matched_indices.add(index)
#             exact_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
#                                           'Transaction ID': remaining_exact_matches, 'Status': 'Multiple Matches to Payments. Choose a Payment to Reconcile'})

#         else: 
#             pass

#     # Exercise 2 : Exact Match to Transaction

#     for index, statement_row in bank_df.iterrows():
#         if index in matched_indices:
#             continue
        
#         if pd.isnull(statement_row["Payer/Payee"]):
#             continue 

#         # Collect exact matches based on date and amount
#         exact_match_ids = []

#         for _, transaction_row in transactions_df.iterrows():
#             ####################### Need to include currency here too 
#             if statement_row['Amount'] == transaction_row['Amount'] and statement_row['Currency'] == transaction_row['Currency']:
#                 exact_match_ids.append(transaction_row['Transaction ID'])

#         exact_match_ids = [id for id in exact_match_ids if not transactions_df.loc[transactions_df['Transaction ID'] == id, 'Contact'].empty and pd.notna(transactions_df.loc[transactions_df['Transaction ID'] == id, 'Contact'].iat[0])]
#         remaining_exact_matches = []
        
#         for exact_match_id in exact_match_ids:

#             if statement_row['Payer/Payee'] in mapping_dict:
#                 if transactions_df.loc[transactions_df['Transaction ID'] == exact_match_id, 'Contact'].iat[0] in mapping_dict[statement_row['Payer/Payee']]:
#                     remaining_exact_matches.append(exact_match_id)
#                     #break Do we stop the exact match? There could be multiple mappings
#                 else: 
#                     if exact_case_check(transactions_df.loc[transactions_df['Transaction ID'] == exact_match_id, 'Contact'].iat[0], statement_row['Payer/Payee']) == "Exact Match":
#                         remaining_exact_matches.append(exact_match_id)
#             else: 
#                 if exact_case_check(transactions_df.loc[transactions_df['Transaction ID'] == exact_match_id, 'Contact'].iat[0], statement_row['Payer/Payee']) == "Exact Match":
#                     remaining_exact_matches.append(exact_match_id)

        
#         if len(remaining_exact_matches) == 1:
#             matched_indices.add(index)
#             exact_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
#                                           'Transaction ID': remaining_exact_matches[0], 'Status': 'Exact Match to Transaction. Create Payment and Reconcile'})
        
#         # Exercise 3b : Choose from multiple matches to transactions
#         elif len(remaining_exact_matches) > 1: 
#             matched_indices.add(index)
#             exact_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
#                                           'Transaction ID': remaining_exact_matches, 'Status': 'Multiple Matches to Transactions. Choose a Transaction to Create Payment and Reconcile'})
#         else:
#             pass

#     # Exercise 4 : Recommend "Create Invoice Receipt" or "Create Bill Receipt"
            
#     no_matches = []

#     for index, statement_row in bank_df.iterrows():
#         if index in matched_indices:
#             continue

#         if pd.isnull(statement_row["Payer/Payee"]):
#             matched_indices.add(index)
#             no_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
#                                           'Transaction ID': None, 'Status': "Null Payer/Payee. No match"})
#             continue 


        
#         if current_user in user_to_contact_list_sheet:
#             users_contacts = user_to_contact_list_sheet[current_user]

#             if isinstance(statement_row["Amount"], (float, int)):
#                 # No need to convert if already a numeric type
#                 amount = statement_row["Amount"]
#             else:
#                 # Convert to float
#                 amount = float(statement_row["Amount"])

#             if amount > 0: 
#                 check = [contact for contact in users_contacts if exact_case_check(statement_row['Payer/Payee'], contact) == "Exact Match"]
#                 if len(check) == 1:
#                     matched_indices.add(index)
#                     no_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
#                                             'Transaction ID': None, 'Status': f"Create Invoice Receipt of Amount ${statement_row['Amount']} on {statement_row['Date']} for {check[0]}"})    
#                 else : 
#                     matched_indices.add(index)
#                     no_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
#                                             'Transaction ID': None, 'Status':  f"Create Invoice Receipt of Amount ${statement_row['Amount']} on {statement_row['Date']}"}) 
#             else:
#                 check = [contact for contact in users_contacts if exact_case_check(statement_row['Payer/Payee'], contact) == "Exact Match"]
#                 if len(check) == 1:
#                     matched_indices.add(index)
#                     no_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
#                                             'Transaction ID': None, 'Status':  f"Create Bill Receipt of Amount ${statement_row['Amount']} on {statement_row['Date']} for {check[0]}"})
#                 else:
#                     matched_indices.add(index)
#                     no_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
#                                             'Transaction ID': None, 'Status':  f"Create Bill Receipt of Amount ${statement_row['Amount']} on {statement_row['Date']}"})
#         else :

#             if isinstance(statement_row["Amount"], (float, int)):
#                 # No need to convert if already a numeric type
#                 amount = statement_row["Amount"]
#             else:
#                 # Convert to float
#                 amount = float(statement_row["Amount"])

#             if amount > 0: 
#                 matched_indices.add(index)
#                 no_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
#                                             'Transaction ID': None, 'Status':  f"Create Invoice Receipt of Amount ${statement_row['Amount']} on {statement_row['Date']}"})

#             else :
#                 matched_indices.add(index)
#                 no_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
#                                             'Transaction ID': None, 'Status':  f"Create Bill Receipt of Amount ${statement_row['Amount']} on {statement_row['Date']}"})

            




#     results = exact_matches + no_matches
#     final_df = pd.DataFrame(results)
#     # worksheet=client.open("AIReconciliation").worksheet("Results")
#     # set_with_dataframe(worksheet, final_df)

#     return final_df

def reconcile(processed_dict):

    bank_df = processed_dict['bank_statements']
    payments_df = processed_dict['payments']
    transactions_df = processed_dict['transactions']
    user_to_contact_list_sheet = processed_dict['mappings']
    mapping_dict = processed_dict['contacts']

    # Exercise 1 : Exact Match to Payment
    exact_matches = []
    matched_indices = set()
    
    for index, statement_row in bank_df.iterrows():
        if index in matched_indices:
            continue
        
        if pd.isnull(statement_row["Payer/Payee"]):
            continue 

        # Collect exact matches based on date and amount
        exact_match_ids = []

        for _, transaction_row in payments_df.iterrows():
            if statement_row['Date'] == transaction_row['Date'] and statement_row['Amount'] == transaction_row['Amount'] and statement_row['Currency'] == transaction_row['Currency']:
                exact_match_ids.append(transaction_row['Transaction ID'])

        ## Date buffer for payments
        if len(exact_match_ids) == 0:
            statement_date = pd.to_datetime(statement_row['Date'])
            start_date = statement_date - pd.Timedelta(days=3)
            end_date = statement_date + pd.Timedelta(days=3)
            for _, transaction_row in payments_df.iterrows():
                transaction_date = pd.to_datetime(transaction_row['Date'])
                # Check if the transaction date is within the 3-day buffer of the statement date
                if start_date <= transaction_date <= end_date and statement_row['Amount'] == transaction_row['Amount'] and statement_row['Currency'] == transaction_row['Currency']:
                    exact_match_ids.append(transaction_row['Transaction ID'])

        exact_match_ids = [id for id in exact_match_ids if not payments_df.loc[payments_df['Transaction ID'] == id, 'Contact'].empty and pd.notna(payments_df.loc[payments_df['Transaction ID'] == id, 'Contact'].iat[0])]
        
        remaining_exact_matches = []
        
        for exact_match_id in exact_match_ids:

            if statement_row['Payer/Payee'] in mapping_dict:
                if payments_df.loc[payments_df['Transaction ID'] == exact_match_id, 'Contact'].iat[0] in mapping_dict[statement_row['Payer/Payee']]:
                    remaining_exact_matches.append(exact_match_id)
                    #break Do we stop the exact match? There could be multiple mappings
                else: 
                    if exact_case_check(payments_df.loc[payments_df['Transaction ID'] == exact_match_id, 'Contact'].iat[0], statement_row['Payer/Payee']) == "Exact Match":
                        remaining_exact_matches.append(exact_match_id)
            else: 
                if exact_case_check(payments_df.loc[payments_df['Transaction ID'] == exact_match_id, 'Contact'].iat[0], statement_row['Payer/Payee']) == "Exact Match":
                    remaining_exact_matches.append(exact_match_id)

        if len(remaining_exact_matches) == 1:
            matched_indices.add(index)
            exact_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
                                          'Transaction ID': remaining_exact_matches[0], 'Status': 'Exact Match to Payment. Reconcile'})
        

        ## This part is removed for now
            
        # Exercise 3a : Choose from multiple matches to payments
        # elif len(remaining_exact_matches) > 1: 
        #     matched_indices.add(index)
        #     exact_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
        #                                   'Transaction ID': remaining_exact_matches, 'Status': 'Multiple Matches to Payments. Choose a Payment to Reconcile'})

        else: 
            pass

    # Exercise 2 : Exact Match to Transaction

    for index, statement_row in bank_df.iterrows():
        if index in matched_indices:
            continue
        
        if pd.isnull(statement_row["Payer/Payee"]):
            continue 

        # Collect exact matches based on date and amount
        exact_match_ids = []

        for _, transaction_row in transactions_df.iterrows():

            if statement_row['Amount'] == transaction_row['Amount'] and statement_row['Currency'] == transaction_row['Currency']:
                statement_date = pd.to_datetime(statement_row['Date'])
                start_date = statement_date - pd.Timedelta(days=30)
                end_date = statement_date + pd.Timedelta(days=30)
                transaction_date = pd.to_datetime(transaction_row['Date'])
                if start_date <= transaction_date <= end_date: 
                    exact_match_ids.append(transaction_row['Transaction ID'])


        if len(exact_match_ids) == 0:
            for _, transaction_row in transactions_df.iterrows():

                if statement_row['Amount'] == transaction_row['Amount'] and statement_row['Currency'] == transaction_row['Currency']:
                    statement_date = pd.to_datetime(statement_row['Date'])
                    start_date = statement_date - pd.Timedelta(days=60)
                    end_date = statement_date + pd.Timedelta(days=60)
                    transaction_date = pd.to_datetime(transaction_row['Date'])
                    if start_date <= transaction_date <= end_date: 
                        exact_match_ids.append(transaction_row['Transaction ID'])


        exact_match_ids = [id for id in exact_match_ids if not transactions_df.loc[transactions_df['Transaction ID'] == id, 'Contact'].empty and pd.notna(transactions_df.loc[transactions_df['Transaction ID'] == id, 'Contact'].iat[0])]
        remaining_exact_matches = []
        
        for exact_match_id in exact_match_ids:

            if statement_row['Payer/Payee'] in mapping_dict:
                if transactions_df.loc[transactions_df['Transaction ID'] == exact_match_id, 'Contact'].iat[0] in mapping_dict[statement_row['Payer/Payee']]:
                    remaining_exact_matches.append(exact_match_id)
                    #break Do we stop the exact match? There could be multiple mappings
                else: 
                    if exact_case_check(transactions_df.loc[transactions_df['Transaction ID'] == exact_match_id, 'Contact'].iat[0], statement_row['Payer/Payee']) == "Exact Match":
                        remaining_exact_matches.append(exact_match_id)
            else: 
                if exact_case_check(transactions_df.loc[transactions_df['Transaction ID'] == exact_match_id, 'Contact'].iat[0], statement_row['Payer/Payee']) == "Exact Match":
                    remaining_exact_matches.append(exact_match_id)

        
        if len(remaining_exact_matches) == 1:
            matched_indices.add(index)
            exact_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
                                          'Transaction ID': remaining_exact_matches[0], 'Status': 'Exact Match to Transaction. Create Payment and Reconcile'})
        
        # This part is removed for now
            
        # Exercise 3b : Choose from multiple matches to transactions
        # elif len(remaining_exact_matches) > 1: 
        #     matched_indices.add(index)
        #     exact_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
        #                                   'Transaction ID': remaining_exact_matches, 'Status': 'Multiple Matches to Transactions. Choose a Transaction to Create Payment and Reconcile'})
        else:
            pass


    # This part is removed for now
    # Exercise 4 : Recommend "Create Invoice Receipt" or "Create Bill Receipt"
            
    no_matches = []

    # for index, statement_row in bank_df.iterrows():
    #     if index in matched_indices:
    #         continue

    #     if pd.isnull(statement_row["Payer/Payee"]):
    #         matched_indices.add(index)
    #         no_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
    #                                       'Transaction ID': None, 'Status': "Null Payer/Payee. No match"})
    #         continue 


        
    #     if current_user in user_to_contact_list_sheet:
    #         users_contacts = user_to_contact_list_sheet[current_user]

    #         if isinstance(statement_row["Amount"], (float, int)):
    #             # No need to convert if already a numeric type
    #             amount = statement_row["Amount"]
    #         else:
    #             # Convert to float
    #             amount = float(statement_row["Amount"])

    #         if amount > 0: 
    #             check = [contact for contact in users_contacts if exact_case_check(statement_row['Payer/Payee'], contact) == "Exact Match"]
    #             if len(check) == 1:
    #                 matched_indices.add(index)
    #                 no_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
    #                                         'Transaction ID': None, 'Status': f"Create Invoice Receipt of Amount ${statement_row['Amount']} on {statement_row['Date']} for {check[0]}"})    
    #             else : 
    #                 matched_indices.add(index)
    #                 no_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
    #                                         'Transaction ID': None, 'Status':  f"Create Invoice Receipt of Amount ${statement_row['Amount']} on {statement_row['Date']}"}) 
    #         else:
    #             check = [contact for contact in users_contacts if exact_case_check(statement_row['Payer/Payee'], contact) == "Exact Match"]
    #             if len(check) == 1:
    #                 matched_indices.add(index)
    #                 no_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
    #                                         'Transaction ID': None, 'Status':  f"Create Bill Receipt of Amount ${statement_row['Amount']} on {statement_row['Date']} for {check[0]}"})
    #             else:
    #                 matched_indices.add(index)
    #                 no_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
    #                                         'Transaction ID': None, 'Status':  f"Create Bill Receipt of Amount ${statement_row['Amount']} on {statement_row['Date']}"})
    #     else :

    #         if isinstance(statement_row["Amount"], (float, int)):
    #             # No need to convert if already a numeric type
    #             amount = statement_row["Amount"]
    #         else:
    #             # Convert to float
    #             amount = float(statement_row["Amount"])

    #         if amount > 0: 
    #             matched_indices.add(index)
    #             no_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
    #                                         'Transaction ID': None, 'Status':  f"Create Invoice Receipt of Amount ${statement_row['Amount']} on {statement_row['Date']}"})

    #         else :
    #             matched_indices.add(index)
    #             no_matches.append({'Date': statement_row['Date'], 'Payer/Payee': statement_row['Payer/Payee'], 'Reference': statement_row['Reference'], 'Amount': statement_row['Amount'], 'Currency': statement_row['Currency'],
    #                                         'Transaction ID': None, 'Status':  f"Create Bill Receipt of Amount ${statement_row['Amount']} on {statement_row['Date']}"})

            


    results = exact_matches + no_matches
    final_df = pd.DataFrame(results)


    return final_df


st.set_page_config(layout="wide")
st.title('Data Reconciliation Output')


uploaded_bank_statements = st.file_uploader("Choose a Bank Statements Excel file", type=['xlsx'], key="bank_statements")
uploaded_jaz_transactions = st.file_uploader("Choose a Jaz Transactions Excel file", type=['xlsx'], key="Transactions")
uploaded_historical_mapping = st.file_uploader("Choose a Historical Reconciliations Excel file", type=['xlsx'], key="historical_data")




if uploaded_bank_statements and uploaded_jaz_transactions and uploaded_historical_mapping and st.button('Jaz Magic'):
    bank_statement_df = pd.read_excel(uploaded_bank_statements, sheet_name="BankStatements")
    payments_df = pd.read_excel(uploaded_jaz_transactions, sheet_name='Payments')
    transactions_df = pd.read_excel(uploaded_jaz_transactions, sheet_name='BusinessTransactions')
    mappings_df = pd.read_excel(uploaded_historical_mapping, sheet_name='Mappings')
    contacts_df = pd.read_excel(uploaded_historical_mapping, sheet_name='Contacts')

    bank_statement_df.replace("", np.nan, inplace=True)
    payments_df.replace("", np.nan, inplace=True)
    transactions_df.replace("", np.nan, inplace=True)
    mappings_df.replace("", np.nan, inplace=True)
    contacts_df.replace("", np.nan, inplace=True)

    # Processing 'mappings_sheet'
    mappings_df.drop_duplicates(subset=['bank_contact_name', 'cft_name'], inplace=True)
    grouped_mappings = mappings_df[mappings_df['cft_name'].notnull()].groupby('bank_contact_name')['cft_name'].apply(list).reset_index()
    result_mappings_dict = dict(zip(grouped_mappings['bank_contact_name'], grouped_mappings['cft_name']))

    # Processing 'user_to_contact_list_sheet'
    contacts_df.drop_duplicates(subset=['User', 'Contact'], inplace=True)
    grouped_contacts = contacts_df[contacts_df['Contact'].notnull()].groupby('User')['Contact'].apply(list).reset_index()
    result_contacts_dict = dict(zip(grouped_contacts['User'], grouped_contacts['Contact']))


    # Call the reconcile function with the DataFrames
    df = reconcile({
        'bank_statements': bank_statement_df,
        'payments': payments_df,
        'transactions': transactions_df,
        'mappings': result_mappings_dict,
        'contacts': result_contacts_dict
    })
    df_excel = to_excel(df)
    
    st.download_button(label='📥 Download Excel',
                   data=df_excel,
                   file_name='reconciled_data_excel.xlsx',
                   mime='application/vnd.ms-excel')

    # Display the reconciled DataFrame
    st.write("Reconciled Data:")
    styled_df = df.style.set_table_styles(
        [{
            'selector': 'th',
            'props': [('background-color', 'lightblue'), ('color', 'black')]
        }, {
            'selector': 'td',
            'props': [('text-align', 'center')]
        }]
    ).set_properties(**{'background-color': 'lavender', 'color': 'black'}).format("{:.2f}", subset=['Amount'])

    # Display styled DataFrame as HTML in Streamlit
    st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)
