# Job Scraping Program
## What It Does
The following program is a bulk cover letter writer, it does the following:
1. It first scrapes a job board website for listings, via the `jobspy` module.
2. It runs a google search for the relevant company recruiter, using a formatted string as configured in `config.json`, and fetches the first results.
3. It will then generate a cover letter, addressed to that recruiter, using the `reportlab` module.

## Known Issues as of 18 February 2024
- Matches may not be entirely correct. No checks are performed to verify identity of recruiters.
- There are insufficient pytests in place.
- Logging tends to duplicate.