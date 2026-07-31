import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def load_cases() -> list[dict]:
    path = Path(__file__).with_name("cases.json")
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_case(client: TestClient, case: dict) -> dict:
    response = client.post("/api/v1/chat", json={"message": case["input"]})
    body = response.json()
    failures: list[str] = []

    if response.status_code != case["expected_status"]:
        failures.append(f"expected status {case['expected_status']}, got {response.status_code}")

    tools = body.get("tools_used", [])
    actual_tool = tools[0]["name"] if tools else None
    if actual_tool != case["expected_tool"]:
        failures.append(f"expected tool {case['expected_tool']!r}, got {actual_tool!r}")

    searchable = json.dumps(body, ensure_ascii=False)
    if case["required_text"].lower() not in searchable.lower():
        failures.append(f"missing required text {case['required_text']!r}")

    return {
        "id": case["id"],
        "passed": not failures,
        "failures": failures,
    }


def main() -> int:
    with TestClient(app, raise_server_exceptions=False) as client:
        results = [evaluate_case(client, case) for case in load_cases()]

    passed = sum(result["passed"] for result in results)
    total = len(results)
    for result in results:
        symbol = "PASS" if result["passed"] else "FAIL"
        print(f"[{symbol}] {result['id']}")
        for failure in result["failures"]:
            print(f"  - {failure}")
    print(f"\nEvaluation result: {passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
