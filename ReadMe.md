'''🚀 **Usage**
├── Run **degiro_IB.py** to retrieve all trading data (stock closing, FX etc)
├── Run **overview_free.py** to prepare all the banking data and display it'''

The Dashboard has four sections:
- A range of filters to modify the data being visualised
- Some high level KPIs
- A few different graphs
- A list of all transactiosn within the filtered range to help deep dive.
![Dashboard overview](assets/dashboard_top.png)
Only the third dropdown is a bit more complex (called **Stock details**), it allows you to visualise different aspects of your investments.
- The default "High Level". You can see four curves displayed on two y axis On the right axis you can see accumulated dividends overtime. On the left axis you can see the following:
    - How much you invested "invested"
    - A benchark of the s&p 500, I chose VT ETF
    - Actual performance "Degiro IB CHF"
![DeepFinder YTD](assets/stock_HighLevel.png)
- The "Details Dividends". It shows the cummulated dividends of the stocks. To make it visible only dividends which represent 2% of the total would be displayed
![Stock Details](assets/stock_details.png)
- The "Details Stocks". It shows the cummulated stocks breakdown. To make it visible only stocks which represent 2% of the total would be displayed
![Stock Details](assets/stock_details.png)
- The "Deep finder YTD". It shows the growth (YTD) of your top 20 stocks, which could help identify buy opportunities.
![DeepFinder YTD](assets/deep_finder_ytd.png)
- The "Deep finder inception". It shows the growth (since you first bought a stock) of your top 20 stocks, which could help identify buy opportunities, and benchmark them.
![DeepFinder Inception](assets/deep_finder_inception.png)

'''**KPI section**, I have chosen to display four KPIs important to me:
- Income saved YTD vs last year (this is purely how much has been put aside and does not consider unrealised gains/lose)
- Restaurant YTD vs last year (As we go often to the restaurant I find it important to monitor it)
- Restaurant current month vs last month
- Dividends YTD vs last year
'''

<pre lang="markdown"> ``` InputFiles/ ├── Degiro/ │ └── Degiro_deposit.csv ├── example_data/ │ └── .gitkeep ├── exception/ │ └── .gitkeep ├── Exception_csv ├── Initialisation ├── neon ├── Postfinance ├── swisscard ├── ZKB ``` </pre>

1) Download all the files (Bank transacations and Stocks transactions in the corresponding folder)
2) In InputFiles\Initialisation you need to initiate the dashboard with the following infomration
2a) Column Description: Start Date Dashboard (put the date from which you started to use this account)
2b) Below add your total wealth value with the category "salary" and day one day before point 2a
2c) You can add with a negative value, how much left your account for investment (initiating them as well), category investment
2d) In Switzerland we get a second pillar, thus I initiate how much I have at the date from 2a, category is also investment
3a) In file pillar 2a, for each for put the date until which you received a given value of pillar 2a, category pillar 2a
4a) In file taxes you can smooth your taxes, in column description you can put "taxes_delete", or "tax_add_manual" to add or remove transaction so they are spread monthly
