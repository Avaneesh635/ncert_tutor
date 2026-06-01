import json
from datetime import datetime, timezone

import httpx

from backend.types import ChatResponse
from evals.constants import BASE_URL, PROMPTS_PATH, REPORTS_DIR
from evals.types import EvalCase, EvalResult


def load_cases() -> list[EvalCase]:
    with PROMPTS_PATH.open() as prompt_file:
        payload = json.load(prompt_file)
    return [EvalCase.model_validate(case) for case in payload["cases"]]


def run_case(client: httpx.Client, case: EvalCase) -> EvalResult:
    response = client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": case.prompt}]},
    )
    response.raise_for_status()
    answer = ChatResponse.model_validate(response.json())
    return EvalResult(id=case.id, answer=answer.answer, model=answer.model)


def main() -> None:
    with httpx.Client(base_url=BASE_URL, timeout=60.0) as client:
        client.get("/health").raise_for_status()
        results = [run_case(client, case) for case in load_cases()]

    REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = REPORTS_DIR / f"visible_eval_{timestamp}.json"
    report_path.write_text(json.dumps([result.model_dump() for result in results], indent=2))
    print(f"Wrote {len(results)} eval results to {report_path}")


if __name__ == "__main__":
    main()
