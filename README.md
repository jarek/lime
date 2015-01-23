Lime is a yet another personal finance/spending tracker.

The main idea is to make entering transactions really, really easy, then show spending data and trends. No future budgeting, no scraping, no fuss.

This started out of a spending-tracking spreadsheet and the basic goal is to do the same things a spreadsheet would except a little easier.

# Current status

- Importing from a CSV into a SQL database (tested with SQLite and PostgreSQL) and exporting back to CSV
- Adding new transactions from web page
- Basic stats on transactions (grouped by category, merchant, etc), currently fairly hardcoded
- Currency of a transaction can be specified and stats will break down by currency
- Basic JSON API for getting transactions and stats, not yet used anywhere
- Single-user authentication through HTTP auth, password must match env variable LIME_WEB_PASSWORD
- Heroku set-up with Procfile; environment variables DATABASE_URL, FLASK_CONFIG, LIME_WEB_PASSWORD must be set

# Running

Locally:
- Defaults to dev settings; change with FLASK_CONFIG environment variable
- Specify database URL in DATABASE_URL env var; config.py has examples for PostgreSQL and SQLite
- Set LIME_WEB_PASSWORD or check the default in config.py (hardcoded default is only available on dev settings)
- Set up environment with `pip install -r requirements.txt`
- Run with `./manage.py runserver`
- When prompted for password, username doesn't matter, only password is checked

On heroku:
- Procfile and requirements.txt are provided in the repo
- Environment variables DATABASE_URL, FLASK_CONFIG, LIME_WEB_PASSWORD must be set; LIME_SECRET_KEY is optional but recommended
- FLASK_CONFIG should be "production"
- Proceed as standard: `git add origin heroku ...; git push heroku`

# Roadmap

- Proper multi currency support, including automatic conversion
- Reviewing transactions, filtering by date, including grouping into weeks and months; grouping by category, account, merchant, etc
- Second data category for tracking account balances / overall net worth
- Eventually: user-editable database columns for people who have other ways of classifying transactions
