
# ~~Deactivation of automatic savings/distribution~~  - DONE

# Export of Savings History as CSV / Excel


# ~~App localisation (currency/labels etc.) -> i18n-Plugins?~~ - DONE


# Auth / Login / PIN
- Accounts secured by PIN / Login
  
# Multi-User-Login


# Multi-Calls / synced pages


# Banking API Connection
- https://tink.com/de/blog/open-banking/einmaleins-des-api-banking/
- PSD2 - Auth
- --> "Auto Detection of Savings"- in der App bestimmten VERWENDUNGSZWECK speichert, der auf dem physik. Konto alle Eingänge beobachtet und Einzahlung mit dem festgelegenen Verwendungszweck automatisch als "Sparzyklus" betrachtet, statt in der App fest monatlich automatisch zu sparen (und davon auszugehen, dass die Summer tatsächlich auf dem physik. Konto gelandet ist.)


# Different Currencies

# Endpoint for error logs

# Bug Report Endpoint / UI Mockup needed?

# Use oauth2 as login?
--> auth0? clerk?
--> or implement own system? (e.g. google login, github, twitch, apple,...)

# Revert prioritized distributed saving
--> e.g. 800€ was distributed but 600 € should be, sub difference of 200 € from last moneyboxes
--> can be done by collecting informations from transactionlogs from moneyboxes to detect all releated moneyboxes while this specific diestribution