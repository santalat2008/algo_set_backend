import httpx


CODEFORCES_API_URL = "https://codeforces.com/api/user.info"


class CodeforcesAPIError(Exception):
    pass


def fetch_user_info(handle: str) -> dict:
    try:
        response = httpx.get(
            CODEFORCES_API_URL,
            params={"handles": handle},
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise CodeforcesAPIError(
            "Codeforces API bilan bog'lanib bo'lmadi."
        ) from exc

    if data.get("status") != "OK":
        raise CodeforcesAPIError(
            data.get("comment", "Codeforces foydalanuvchisi topilmadi.")
        )

    result = data.get("result", [])
    if not result:
        raise CodeforcesAPIError("Foydalanuvchi topilmadi.")

    return result[0]



PROBLEMSET_API_URL = "https://codeforces.com/api/problemset.problems"


def fetch_problems() -> list[dict]:
    try:
        response = httpx.get(PROBLEMSET_API_URL, timeout=60.0)
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise CodeforcesAPIError(
            "Codeforces masalalarini yuklab bo'lmadi."
        ) from exc

    if data.get("status") != "OK":
        raise CodeforcesAPIError(
            data.get("comment", "Codeforces API xatosi.")
        )

    result = data.get("result", {})
    problems = result.get("problems", [])

    if not isinstance(problems, list):
        raise CodeforcesAPIError("API javobidagi masalalar formati noto'g'ri.")

    return problems



USER_STATUS_API_URL = "https://codeforces.com/api/user.status"


def fetch_user_submissions(handle: str, from_id: int = 1) -> list[dict]:
    try:
        response = httpx.get(
            USER_STATUS_API_URL,
            params={"handle": handle, "from": from_id},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise CodeforcesAPIError(
            "Codeforces submissionlarini yuklab bo'lmadi."
        ) from exc

    if data.get("status") != "OK":
        raise CodeforcesAPIError(
            data.get("comment", "Codeforces API xatosi.")
        )

    result = data.get("result", [])
    if not isinstance(result, list):
        raise CodeforcesAPIError(
            "Submissionlar formati noto'g'ri."
        )

    return result
