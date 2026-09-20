class SkillGapService:

    def analyze_gaps(
        self,
        profile: dict,
        career_matches: list[dict],
    ) -> list[dict]:

        student_skills = {
            (
                item.get("normalized_value")
                or item.get("value")
            ).lower()
            for item in profile.get("skills", [])
            if (
                item.get("normalized_value")
                or item.get("value")
            )
        }

        all_gaps = []

        for match in career_matches:

            career_id = match["career_id"]

            required_skill_details = match.get(
                "required_skill_details",
                [],
            )

            if required_skill_details:
                required_skills = required_skill_details
            else:
                required_skills = [
                    {
                        "skill_name": skill,
                        "required_level": None,
                        "importance": 3,
                        "is_core": False,
                    }
                    for skill in match.get("required_skills", [])
                ]

            matched_skills = {
                skill.lower()
                for skill in match.get(
                    "matched_skills",
                    [],
                )
            }

            for required_skill in required_skills:

                skill_name = required_skill["skill_name"]

                normalized_required = (
                    skill_name.lower()
                )

                if normalized_required in matched_skills:
                    continue

                importance = required_skill["importance"]
                is_core = required_skill["is_core"]
                severity = importance / 5

                if is_core:
                    severity += 0.2

                severity = min(severity, 1.0)

                gap = {
                    "career_id": career_id,
                    "skill_name": skill_name,
                    "student_skill_level": None,
                    "required_level": required_skill["required_level"],
                    "importance": importance,
                    "is_core": is_core,
                    "gap_severity": severity,
                    "is_critical": is_core and importance >= 4,
                }

                all_gaps.append(gap)

        return all_gaps


skill_gap_service = SkillGapService()