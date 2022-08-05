# Job Scraping Program
## What It Does
The following program is a bulk cover letter writer.
It first scrapes a job board website for listings, as configured in config_dummy.json
Next, it determines most likely web links to explore via company_result.py.
After that, it searches that data for names of likely hiring managers in namefetcher.py.
Based on the names found, namefetcher.py will generate a greeting "Dear First Last";
If none are found, it will provide "To Whom It May Concern"
Then finally, it will write a cover letter based on all the data it has scraped so far, 
using the reportlab module.

## Known Issues
- ~~The namefetcher module will occasionally return false positives for names: e.g. if it sees "Disney" it will try to turn it into "Dis Ney". Existing filters don't appear sufficient.~~ This has been fixed as of August 4, 2022!
- striptags.py may be useless and/or accomplishable through built_in means, not entirely clear how 
- Namefetcher.py might benefit from a refactoring.
- The program only works with BuiltIn listings.
