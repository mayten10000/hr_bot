# позжe AI

def parse_requirements(requirements_str):
    return [s.strip() for s in requirements_str.split(',') if s.strip()]

def calculate_match_score(user_skills: dict[str, int]) -> int:
    return sum(user_skills.values())  # '+' → 1, '-' → 0
