class ProfileService:

    def build_profile(self, memories: list[dict]) -> dict:

        profile = {
            "education": [],
            "interests": [],
            "skills": [],
            "career_goals": [],
            "learning_preferences": [],
            "strengths": [],
            "weaknesses": [],
            "experience": [],
            "projects": [],
            "achievements": [],
            "extracurricular": [],
            "activities": [],
            "hobbies": [],
            "motivations": [],
            "constraints": [],
            "other_goals": [],
        }

        category_mapping = {
            "education": "education",
            "interest": "interests",
            "skill": "skills",
            "career_goal": "career_goals",

            "learning_preference": "learning_preferences",
            "learning_style": "learning_preferences",
            "preference": "learning_preferences",

            "strength": "strengths",
            "weakness": "weaknesses",
            "experience": "experience",
            "project": "projects",
            "achievement": "achievements",
            "extracurricular": "extracurricular",
            "activity": "activities",
            "hobby": "hobbies",
            "motivation": "motivations",
            "constraint": "constraints",
            "goal": "other_goals",
        }

        seen = set()

        for memory in memories:

            memory_type = memory.get("memory_type")

            if not memory_type:
                continue

            profile_key = category_mapping.get(memory_type)

            if not profile_key:
                continue

            memory_key = memory.get("memory_key")
            value = memory.get("value")
            normalized_value = memory.get("normalized_value")

            dedup_value = normalized_value or value

            dedup_key = (
                memory_type,
                memory_key,
                dedup_value,
            )

            if dedup_key in seen:
                continue

            seen.add(dedup_key)

            profile[profile_key].append({
                "key": memory_key,
                "value": value,
                "normalized_value": normalized_value,
                "confidence": memory.get("confidence"),
                "importance": memory.get("importance"),
            })

        categories_present = [
            category
            for category, values in profile.items()
            if values
        ]

        total_facts = sum(
            len(values)
            for values in profile.values()
        )

        profile["total_facts"] = total_facts
        profile["categories_present"] = categories_present

        return profile


profile_service = ProfileService()