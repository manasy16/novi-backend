class CareerMatchingService:

    def match_careers(
        self,
        profile: dict,
        career_dna: dict,
        careers: list,
    ) -> list[dict]:

        student_skills = {
            item.get("normalized_value")
            or item.get("value")
            for item in profile.get("skills", [])
        }

        student_goals = {
            (
                item.get("normalized_value")
                or item.get("value")
            ).lower()
            for item in profile.get("career_goals", [])
            if (
                item.get("normalized_value")
                or item.get("value")
            )
        }

        matches = []

        for career_data in careers:

            career = career_data["career"]
            required_skills = career_data["skills"]
            tags = career_data["tags"]

            required_skill_details = [
                {
                    "skill_name": skill.name,
                    "required_level": career_skill.required_level,
                    "importance": career_skill.importance,
                    "is_core": career_skill.is_core,
                }
                for career_skill, skill in required_skills
            ]

            # -----------------------------------------
            # Skill alignment
            # -----------------------------------------

            required_skill_names = {
    (
        skill.name
        or ""
    ).lower()
    for career_skill, skill in required_skills
}

            student_skill_names = {
                skill.lower()
                for skill in student_skills
                if skill
            }

            matched_skills = (
                required_skill_names
                & student_skill_names
            )

            if required_skill_names:
                skill_score = (
                    len(matched_skills)
                    / len(required_skill_names)
                )
            else:
                skill_score = 0.0

            # -----------------------------------------
            # Career goal alignment
            # -----------------------------------------

            career_name = (
                career.name or ""
            ).lower()

            goal_match = any(
                goal in career_name
                or career_name in goal
                for goal in student_goals
            )

            goal_score = 1.0 if goal_match else 0.0

            # -----------------------------------------
            # Combined score
            # -----------------------------------------

            final_score = (
                0.7 * skill_score
                + 0.3 * goal_score
            )

            matches.append({
                "career_id": career.id,
                "career_name": career.name,
                "skill_score": round(
                    skill_score,
                    4,
                ),
                "goal_score": goal_score,
                "final_score": round(
                    final_score,
                    4,
                ),
                "matched_skills": list(
                    matched_skills
                ),
                "required_skills": list(
                    required_skill_names
                ),
                "required_skill_details": required_skill_details,
                "tags": tags,
            })

        matches.sort(
            key=lambda item: item["final_score"],
            reverse=True,
        )

        return matches


career_matching_service = CareerMatchingService()