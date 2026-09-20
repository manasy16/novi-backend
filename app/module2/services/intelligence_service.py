class IntelligenceService:

    def build_intelligence(
        self,
        profile: dict,
        insights: list[dict],
        career_dna: dict,
        career_matches: list[dict],
        skill_gaps: list[dict],
        readiness: dict,
    ) -> dict:

        top_matches = career_matches[:5]

        return {
            "profile_summary": {
                "total_facts": profile.get(
                    "total_facts",
                    0,
                ),
                "categories_present": profile.get(
                    "categories_present",
                    [],
                ),
            },

            "insights": insights,

            "career_dna": career_dna,

            "career_alignment": {
                "top_careers": [
                    {
                        "career_id": match.get("career_id"),
                        "career_name": match.get("career_name"),
                        "final_score": match.get("final_score"),
                        "skill_score": match.get("skill_score"),
                        "goal_score": match.get("goal_score"),
                    }
                    for match in top_matches
                ]
            },

            "skill_gaps": skill_gaps,

            "readiness": readiness,
        }


intelligence_service = IntelligenceService()