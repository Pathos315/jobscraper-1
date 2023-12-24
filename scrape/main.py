from time import perf_counter

from src.configs import CONFIG, PERSONA
from src.coverletterwriter import CoverLetterContents, CoverLetterPrinter
from src.jobspicker import pick_jobs
from src.log import logger
from tqdm import tqdm


def main() -> None:
    """jobscraper takes the provided querystring, searches for job results,
    and for each of those job results generates a cover letter.
    """
    start = perf_counter()

    logger.info("Initializing Jobscraper Program...")
    all_jobs = pick_jobs()
    for job in tqdm(all_jobs):
        letter_contents = CoverLetterContents(job, PERSONA, CONFIG)
        letter_printer = CoverLetterPrinter(CONFIG, PERSONA, letter_contents)
        letter_printer.write_cover_letter()

    elapsed = perf_counter() - start
    logger.info("Job search finished in %s seconds.", elapsed)  # type: ignore


if __name__ == "__main__":
    main()