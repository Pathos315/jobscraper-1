from time import perf_counter

from src.configs import CONFIG
from src.coverletterwriter import CoverLetterContents, CoverLetterPrinter
from src.jobspicker import find_jobs
from src.log import logger
from tqdm import tqdm


def main() -> None:
    """jobscraper takes the provided querystring, searches for job results,
    and for each of those job results generates a cover letter.
    """
    start = perf_counter()

    logger.info("Initializing Jobscraper Program...")
    search_term = input(
        "Enter desired search term, e.g. Python, Graphic Designer, Engineer..."
    )
    all_jobs = find_jobs(search_term)
    for job in tqdm(all_jobs):
        letter_contents: CoverLetterContents = CoverLetterContents(job, CONFIG)
        letter_printer: CoverLetterPrinter = CoverLetterPrinter(CONFIG, letter_contents)
        letter_printer()

    elapsed = perf_counter() - start
    logger.info("Job search finished in %.3f seconds.", elapsed)


if __name__ == "__main__":
    main()
