"""
🧠 Recommendation Engine — Content-Based Filtering with Activity Boosting

Approach:
1. Content-Based: TF-IDF vectorization + cosine similarity
   - User profile text = skills + preferred roles + location
   - Job text = title + required_skills + description + location
   
2. Activity-Based Boosting:
   - Analyze user's clicked/applied job patterns
   - Boost jobs similar to past activity
   
3. Hybrid Score: final = content_weight * content + activity_weight * activity
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import Counter


class RecommendationEngine:
    """Content-based job recommendation engine using TF-IDF and cosine similarity."""

    def __init__(self, content_weight: float = 0.7, activity_weight: float = 0.3):
        self.content_weight = content_weight
        self.activity_weight = activity_weight
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2),  # Unigrams + bigrams for better matching
        )

    def _build_user_profile_text(self, user: dict) -> str:
        """Combine user attributes into a single searchable text."""
        parts = []
        # Skills are the most important signal
        skills = user.get("skills", [])
        parts.append(" ".join(skills))
        parts.append(" ".join(skills))  # Double weight for skills

        # Preferred roles
        roles = user.get("preferred_roles", [])
        parts.append(" ".join(roles))

        # Location preference
        location = user.get("location", "")
        if location:
            parts.append(location)

        # Experience context
        exp = user.get("experience_years", 0)
        if exp <= 2:
            parts.append("junior entry level fresher")
        elif exp <= 5:
            parts.append("mid level intermediate")
        else:
            parts.append("senior experienced lead")

        return " ".join(parts).lower()

    def _build_job_text(self, job: dict) -> str:
        """Combine job attributes into a single searchable text."""
        parts = []
        parts.append(job.get("title", ""))
        parts.append(" ".join(job.get("required_skills", [])))
        parts.append(" ".join(job.get("required_skills", [])))  # Double weight for skills
        parts.append(job.get("description", ""))
        parts.append(job.get("location", ""))
        parts.append(job.get("experience_level", ""))
        return " ".join(parts).lower()

    def _compute_activity_scores(self, user: dict, jobs: list) -> dict:
        """Compute activity-based scores from user's click/apply history."""
        activity = user.get("activity", [])
        if not activity:
            return {}

        # Count which job IDs were interacted with and how
        interacted_job_ids = set()
        action_weights = {"job_applied": 3.0, "job_clicked": 1.0, "job_searched": 0.5}
        skill_boosts = Counter()

        for act in activity:
            job_id = act.get("job_id")
            if job_id:
                interacted_job_ids.add(job_id)
            act_type = act.get("activity_type", "")
            weight = action_weights.get(act_type, 0.5)
            # Extract search terms if available
            search_q = act.get("search_query", "")
            if search_q:
                for term in search_q.lower().split():
                    skill_boosts[term] += weight

        # Find skills from interacted jobs
        for job in jobs:
            if job.get("id") in interacted_job_ids:
                for skill in job.get("required_skills", []):
                    skill_boosts[skill.lower()] += 2.0

        # Score all jobs based on skill overlap with activity
        scores = {}
        if not skill_boosts:
            return scores

        max_boost = max(skill_boosts.values()) if skill_boosts else 1.0
        for job in jobs:
            job_id = job.get("id")
            if job_id in interacted_job_ids:
                continue  # Don't recommend already-interacted jobs
            score = 0.0
            for skill in job.get("required_skills", []):
                score += skill_boosts.get(skill.lower(), 0)
            scores[job_id] = score / max_boost if max_boost > 0 else 0
        return scores

    def recommend(self, user: dict, jobs: list, top_n: int = 10) -> list:
        """
        Generate top-N job recommendations for a user.
        
        Returns list of dicts: [{"job": {...}, "score": 0.85, "match_reasons": [...]}]
        """
        if not jobs:
            return []

        # Filter out jobs user already applied to
        applied_ids = set()
        for act in user.get("activity", []):
            if act.get("activity_type") == "job_applied" and act.get("job_id"):
                applied_ids.add(act["job_id"])

        available_jobs = [j for j in jobs if j.get("id") not in applied_ids]
        if not available_jobs:
            return []

        # ── Step 1: Content-Based Scores ──
        user_text = self._build_user_profile_text(user)
        job_texts = [self._build_job_text(j) for j in available_jobs]

        # Fit TF-IDF on all documents (user profile + all jobs)
        all_texts = [user_text] + job_texts
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)

        # Cosine similarity: user vector vs all job vectors
        user_vector = tfidf_matrix[0:1]
        job_vectors = tfidf_matrix[1:]
        content_scores = cosine_similarity(user_vector, job_vectors).flatten()

        # ── Step 2: Activity-Based Scores ──
        activity_scores_map = self._compute_activity_scores(user, available_jobs)

        # ── Step 3: Hybrid Scoring ──
        results = []
        for i, job in enumerate(available_jobs):
            content_score = float(content_scores[i])
            activity_score = activity_scores_map.get(job["id"], 0.0)

            # Weighted combination
            if activity_scores_map:
                final_score = (self.content_weight * content_score +
                               self.activity_weight * activity_score)
            else:
                final_score = content_score

            # Generate match reasons
            reasons = self._get_match_reasons(user, job, content_score, activity_score)

            results.append({
                "job": job,
                "score": round(final_score, 4),
                "content_score": round(content_score, 4),
                "activity_score": round(activity_score, 4),
                "match_reasons": reasons,
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_n]

    def find_similar_jobs(self, target_job: dict, all_jobs: list, top_n: int = 5) -> list:
        """Find jobs similar to a given job."""
        job_texts = [self._build_job_text(j) for j in all_jobs]
        target_text = self._build_job_text(target_job)

        all_texts = [target_text] + job_texts
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)

        target_vector = tfidf_matrix[0:1]
        other_vectors = tfidf_matrix[1:]
        similarities = cosine_similarity(target_vector, other_vectors).flatten()

        results = []
        for i, job in enumerate(all_jobs):
            if job.get("id") == target_job.get("id"):
                continue
            results.append({
                "job": job,
                "similarity_score": round(float(similarities[i]), 4),
            })

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_n]

    def _get_match_reasons(self, user: dict, job: dict, content_score: float, activity_score: float) -> list:
        """Generate human-readable match reasons."""
        reasons = []
        user_skills = set(s.lower() for s in user.get("skills", []))
        job_skills = set(s.lower() for s in job.get("required_skills", []))
        matching_skills = user_skills & job_skills

        if matching_skills:
            reasons.append(f"Skills match: {', '.join(sorted(matching_skills))}")

        user_roles = [r.lower() for r in user.get("preferred_roles", [])]
        job_title_lower = job.get("title", "").lower()
        for role in user_roles:
            if role in job_title_lower or any(w in job_title_lower for w in role.split()):
                reasons.append(f"Matches preferred role: {role}")
                break

        user_loc = user.get("location", "").lower()
        job_loc = job.get("location", "").lower()
        if user_loc and (user_loc in job_loc or job_loc == "remote"):
            reasons.append(f"Location match: {job.get('location')}")

        if activity_score > 0.3:
            reasons.append("Similar to your recent activity")

        if content_score > 0.5:
            reasons.append("Strong profile match")
        elif content_score > 0.2:
            reasons.append("Good profile match")

        return reasons if reasons else ["Potential match based on your profile"]


# Global engine instance
engine = RecommendationEngine()
