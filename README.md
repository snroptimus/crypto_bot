#ReadME

This is the Arbitrage bot built with Django/Python.

How to Install and Run.

1. clone the repository
git clone https://bitbucket.org/asafnir/cryptocurrency_arbitrage.git
2. Install Python 2.7 and Django 1.9.2
3. Run the project.
1) Run only the bot
python Arbitrage.py
2) Run the site with UI/UX
python manage.py runserver
go to http://localhost:8080

You can see the bot status in "orderlist.json" file.
Currently You can change the parameters in Arbitrage.py file.

diffpercent(%) represents the difference of the price between two sites that will be used for opportunity detection.
amount(BTC) represents the amount to be orderded.

