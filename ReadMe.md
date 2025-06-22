## 🚀 Usage 
├── Run **degiro_IB.py** to retrieve all trading data (stock closing, FX etc)  
├── Run **overview_free.py** to prepare all the banking data and display it

## Structure of the dashboard
The Dashboard has **four sections**:
- A range of **filters** to modify the data being visualised
- Some high level **KPIs**
- A few different **graphs**
- A list of **all transaction** within the filtered range to help deep dive.
![Dashboard overview](assets/dashboard_top.png)

### KPI section
I have chosen to display four KPIs important to me:
![KPI section](assets/KPI_section.png)
- Income saved YTD vs last year (this is purely how much has been put aside and does not consider unrealised gains/lose)
- Restaurant YTD vs last year (As we go often to the restaurant I find it important to monitor it)
- Restaurant current month vs last month
- Dividends YTD and equity YTD

### First graph "Monthly spent (excluding investment)"
 It shows on the left axis how much money has been saved per month, as well as how much is remaining on the bank account (Konto Stand). On the right axis you see two cummulative curves of wealth: 1) Cummulative which reprensent wealth invested (bank account + deposited on trading platform), 2) "incl. 2a" is for swiss usage and to reprensent how much is on top in the pillar 2a retirement fund.

### Second graph Degiro Interactive brokers
Only the third dropdown is a bit more complex (called **Stock details**), it allows you to visualise different aspects of your investments.
The default "High Level". You can see four curves displayed on two y axis On the right axis you can see accumulated dividends overtime. On the left axis you can see the following:
    - How much you invested "invested"
    - A benchark of the s&p 500, I chose VT ETF
    - Actual performance "Degiro IB CHF"

![High Level stock](assets/stock_HighLevel.png)

The "Details Dividends" and "Details Stocks". It shows the cummulated dividends of the stocks (or stock value). To make it visible only dividends which represent 2% of the total would be displayed
<p float="left">
  <img src="assets/dividends_details.png" width="48%" />
  <img src="assets/stock_details.png" width="48%" />
</p>

The "Deep finder YTD" and "Deep finder inception". It shows the growth (YTD or since inception) of your top 20 stocks, which could help identify buy opportunities.
<p float="left">
  <img src="assets/deep_finder_YTD.png" width="48%" />
  <img src="assets/deep_finder_inception.png" width="48%" />
</p>

### Waterfall and tree map graphs
![Tree map wateral](assets/treemap_waterfall.png)
1) Waterfall to see how you spend your money
2) A tree map to visualise the larger categorise and deep dive in the sub categorise

### Last section of the dashboard
Below we see the lsat 3 graphs of the dashboard: 
1) A monthly spent (excluding investment) of the dashboard, stacked values. As well as 3 ,6, 12 months rolling average
2) How is the spend per category is evolving overtime (i.e. holidays 3, 6, 12, 24 months rolling)
3) A list of individual transactions (can be filtered using categorise or date time filters)

![Bottom graphs](assets/bottom_dashboard.png)

## 📌 Motivation Behind the Project

## How to set it up.
The first initial setup is a bit longer as one needs to download the files, potentially apply some initialization or clustering.

1) Download all the files (Bank transacations and Stocks transactions in the corresponding folder)
In my case **neon** is available as yearly csv in the mobile phone. All yearly csv can be dropped in the correspoding folder
**Swisscard** allows from the web to dwonload all transactions as csv. I normally download one year of transaction
**Degiro, interactive brokers**: data can be downloaded as follow:

2) In InputFiles\Initialisation you need to initiate the dashboard with the following information
I have three CSVs "bank_init.csv", "pillar2a.csv", "taxes_init.csv". You can copy the example files for the folder example_data into the folder Initialisation
    
2a) The "bank_init.csv" has the following structure:

        It also contains information to initialize investment (pillar 2a, pillar 3a, interactive brokers) as only transaction are looked at
        I opened a bank account in 2011 and listed the first money transfered from my old bank account to the new as "salary" and initialized the values on the other accounts.
        You should add as "salary" the full amount you owned at the start date, then add the payment you made to investment platforms (pillar 3a, degiro interactive brokers with a negative value as this was leaving the account)
    
    2b) The "pillar2a.csv" has the following structure

        For every salary you receive starting at the date Date you will have a new income going to pillar 2a based on the mentioned value. If you have a salary raise or how much you put in pillar 2a is changing you can add a new row with the start date and associated value.
    
    2c) The "taxes_init.csv" has the following structure

        In the description you can add "tax_add_manual" or "taxes_delete". I created this file if you want to smooth your taxes and remove the full amount paid once a year and add the monthly values

3) In the Exception_csv\categorization_exceptions.csv
    The goal of this file is to identify and modify some transaction for a better categorisation (i.e. if you paid in advance for a holiday house 3 months before but your friends will pay you pack after the holiday you can "move" the initial payment to when you are paid pack to reflect the netto). You can copy the csv "categorization_exceptions.csv" from the example_data into the Exception_csv folder

    The csv has the following structure: description_substring,amount_min,amount_max,year_condition,year_min,year_max,month_condition,month_min,month_max,date_min,date_max,new_description,new_category,new_month,new_year,subject,category, Memo


## Technology


## Structure of the repository
InputFiles/ ├── Degiro/ │ └── Degiro_deposit.csv ├── example_data/ │ └── .gitkeep ├── exception/ │ └── .gitkeep ├── Exception_csv ├── Initialisation ├── neon ├── Postfinance ├── swisscard ├── ZKB