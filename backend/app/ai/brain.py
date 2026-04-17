import json
import logging
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIBrain:
    def __init__(self):
        self.client = None
        self._initialized = False

    def _ensure_client(self):
        if not self._initialized:
            if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-your-openai-api-key-here":
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self._initialized = True

    def _is_available(self):
        self._ensure_client()
        return self.client is not None

    async def analyze_candidate(self, cv_text: str, job_role: str) -> dict:
        """Score candidate CV and decide next action using GPT-4"""
        if not self._is_available():
            return self._fallback_analysis(cv_text, job_role)

        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert HR recruiter AI. Analyze candidates and respond ONLY with valid JSON, no markdown."
                    },
                    {
                        "role": "user",
                        "content": f"""
Job Role: {job_role}

Candidate CV:
{cv_text}

Analyze this candidate and respond ONLY with JSON:
{{
    "score": 85,
    "reasoning": "5 years experience, matches tech stack",
    "decision": "proceed",
    "missing_skills": ["Docker", "AWS"],
    "next_action": "request_documents",
    "email_subject": "Next Steps - Your Application",
    "email_body": "Hi! Great profile. Please send your documents."
}}

Scoring: 90-100 Excellent, 70-89 Good, 50-69 Average, Below 50 Reject.
Decision: "proceed" or "reject"
"""
                    }
                ],
                max_tokens=1000,
                temperature=0.3,
            )

            response_text = response.choices[0].message.content
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)

        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            return self._fallback_analysis(cv_text, job_role)

    async def generate_email(self, context: dict, email_type: str) -> str:
        """Generate personalized email using GPT-4"""
        if not self._is_available():
            return self._fallback_email(context, email_type)

        prompts = {
            "welcome": f"Write a friendly, professional welcome email to {context.get('name', 'candidate')} who applied for {context.get('job_role')}. Ask for: CV, CNIC, Educational Certificates, 2 Professional References. Max 150 words.",
            "reminder": f"Write a polite reminder email to {context.get('name')} about missing documents: {', '.join(context.get('missing_docs', []))}. Reminder #{context.get('reminder_count', 1)}. Max 100 words.",
            "interview": f"Write an interview scheduling email to {context.get('name')} with 3 time slots: 1) {context.get('slot1')} 2) {context.get('slot2')} 3) {context.get('slot3')}. Ask them to reply with slot number.",
            "offer": f"Write a job offer email for {context.get('name')}, Role: {context.get('role')}, Salary: PKR {context.get('salary')}, Start Date: {context.get('start_date')}. Professional, exciting tone.",
            "rejection": f"Write a polite, empathetic rejection email to {context.get('name')} for the {context.get('job_role')} position. Thank them and encourage future applications. Max 100 words.",
            "onboarding": f"Write an onboarding welcome email to {context.get('name')} who is joining as {context.get('role')} on {context.get('start_date')}. Include first-day instructions. Max 200 words.",
        }

        prompt = prompts.get(email_type, f"Write a professional HR email about: {email_type}")

        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an HR email writer. Write professional, warm emails. No markdown formatting - plain text only."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7,
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI email generation failed: {e}")
            return self._fallback_email(context, email_type)

    async def suggest_interview_questions(self, job_role: str, cv_summary: str = "") -> list:
        """Generate interview questions based on role"""
        if not self._is_available():
            return [
                f"Tell me about your experience relevant to {job_role}.",
                "What are your greatest strengths?",
                "Where do you see yourself in 5 years?",
                "Why are you interested in this role?",
                "Describe a challenging project you worked on.",
            ]

        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Generate interview questions. Respond with a JSON array of strings only."
                    },
                    {
                        "role": "user",
                        "content": f"Generate 8 interview questions for a {job_role} position. CV summary: {cv_summary}. Mix technical and behavioral. Return JSON array."
                    }
                ],
                max_tokens=800,
                temperature=0.5,
            )
            text = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            return [f"Tell me about your experience for {job_role}."]

    async def analyze_sentiment(self, email_text: str) -> dict:
        """Analyze candidate email sentiment"""
        if not self._is_available():
            return {"sentiment": "neutral", "confidence": 0.5, "summary": "AI unavailable"}

        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze email sentiment. Return JSON: {\"sentiment\": \"positive/neutral/negative\", \"confidence\": 0.0-1.0, \"summary\": \"brief\"}"
                    },
                    {"role": "user", "content": f"Analyze sentiment:\n{email_text}"}
                ],
                max_tokens=200,
                temperature=0.2,
            )
            text = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"sentiment": "neutral", "confidence": 0.5, "summary": str(e)}

    async def score_resume(self, resume_text: str, job_requirements: str) -> dict:
        """Deep resume scoring against specific requirements"""
        if not self._is_available():
            return {"overall_score": 50, "skills_match": 50, "experience_match": 50, "education_match": 50, "recommendation": "Review manually - AI unavailable"}

        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an ATS resume scorer. Return JSON only."
                    },
                    {
                        "role": "user",
                        "content": f"""Score this resume against requirements.

Requirements: {job_requirements}

Resume: {resume_text}

Return JSON:
{{
    "overall_score": 85,
    "skills_match": 90,
    "experience_match": 80,
    "education_match": 85,
    "key_strengths": ["strength1", "strength2"],
    "gaps": ["gap1", "gap2"],
    "recommendation": "Proceed to interview"
}}"""
                    }
                ],
                max_tokens=600,
                temperature=0.2,
            )
            text = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            logger.error(f"Resume scoring failed: {e}")
            return {"overall_score": 50, "recommendation": "Manual review needed"}

    def _fallback_analysis(self, cv_text: str, job_role: str) -> dict:
        """Fallback when AI is unavailable"""
        return {
            "score": 50,
            "reasoning": "AI analysis unavailable - manual review required",
            "decision": "proceed",
            "missing_skills": [],
            "next_action": "request_documents",
            "email_subject": f"Application Received - {job_role}",
            "email_body": f"Thank you for applying to the {job_role} position. We will review your application and get back to you shortly."
        }

    def _fallback_email(self, context: dict, email_type: str) -> str:
        """Fallback email templates when AI is unavailable"""
        name = context.get("name", "Candidate")
        job_role = context.get("job_role", "the position")

        templates = {
            "welcome": f"Dear {name},\n\nThank you for applying to the {job_role} position. We have received your application and will review it shortly.\n\nPlease submit the following documents:\n- Updated CV\n- CNIC copy\n- Educational Certificates\n- 2 Professional References\n\nBest regards,\nHR Team",
            "reminder": f"Dear {name},\n\nThis is a friendly reminder to submit your pending documents. Please send them at your earliest convenience.\n\nBest regards,\nHR Team",
            "interview": f"Dear {name},\n\nWe would like to schedule an interview with you. Please let us know your availability.\n\nBest regards,\nHR Team",
            "offer": f"Dear {name},\n\nWe are pleased to offer you the {context.get('role', 'position')}. Please review the attached offer letter.\n\nBest regards,\nHR Team",
            "rejection": f"Dear {name},\n\nThank you for your interest in the {job_role} position. After careful review, we've decided to move forward with other candidates. We encourage you to apply for future openings.\n\nBest regards,\nHR Team",
            "onboarding": f"Dear {name},\n\nWelcome to the team! We're excited to have you join us. Your first day details will follow shortly.\n\nBest regards,\nHR Team",
        }
        return templates.get(email_type, f"Dear {name},\n\nThank you for your correspondence.\n\nBest regards,\nHR Team")


ai_brain = AIBrain()
