Lime is a yet another personal finance/spending tracker.

The main idea is to make entering transactions really, really easy, then show spending data and trends. No future budgeting, no scraping, no fuss.

This started out of a spending-tracking spreadsheet and the basic goal is to do the same things a spreadsheet would except a little easier.

# Current status

- Importing from a CSV into a SQLite database and exporting back to CSV
- Adding new transactions from web page
- Basic stats on transactions (grouped by category, merchant, etc), currently fairly hardcoded
- Basic JSON API for getting transactions and stats, not yet used anywhere
- **Important**: no security whatsoever yet - make sure it's private or behind a server-defined password

# Roadmap

- Proper multi currency support, including automatic conversion
- Reviewing transactions, filtering by date, including grouping into weeks and months; grouping by category, account, merchant, etc
- Second data category for tracking account balances / overall net worth
- Eventually: user-editable database columns for people who have other ways of classifying transactions
