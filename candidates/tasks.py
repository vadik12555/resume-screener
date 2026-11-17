import logging

from celery import shared_task

from .models import Candidate
from .services.llm import LLMError, evaluate_resume
from .services.parsing import ParsingError, extract_text

logger = logging.getLogger(__name__)


@shared_task
def process_candidate(candidate_id: int) -> None:
    """Background job: read the file, ask the LLM, store the evaluation."""
    candidate = Candidate.objects.select_related("vacancy").get(pk=candidate_id)
    candidate.processing = Candidate.Processing.PROCESSING
    candidate.error = ""
    candidate.save(update_fields=["processing", "error"])

    try:
        if not candidate.resume_text:
            with candidate.file.open("rb") as fh:
                candidate.resume_text = extract_text(candidate.original_filename, fh.read())
        evaluation = evaluate_resume(candidate.vacancy, candidate.resume_text)
    except (ParsingError, LLMError) as exc:
        _fail(candidate, str(exc))
        return
    except Exception:  # never leave a candidate stuck in "processing"
        logger.exception("Unexpected error while processing candidate %s", candidate_id)
        _fail(candidate, "Непредвиденная ошибка при обработке. Попробуйте повторить анализ.")
        return

    candidate.name = evaluation.name
    candidate.age = evaluation.age
    candidate.position = evaluation.position
    candidate.city = evaluation.city
    candidate.experience_years = evaluation.experience_years
    candidate.skills = evaluation.skills
    candidate.score = evaluation.score
    candidate.summary = evaluation.summary
    candidate.strengths = evaluation.strengths
    candidate.gaps = evaluation.gaps
    candidate.questions = evaluation.questions
    candidate.processing = Candidate.Processing.DONE
    candidate.save()


def _fail(candidate: Candidate, message: str) -> None:
    candidate.processing = Candidate.Processing.ERROR
    candidate.error = message
    candidate.save()
