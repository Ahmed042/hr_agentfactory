"""Tests for AI brain fallback functionality"""
import pytest
from app.ai.brain import AIBrain


@pytest.fixture
def ai():
    """AI brain instance with no API key (fallback mode)"""
    return AIBrain()


@pytest.mark.asyncio
async def test_fallback_analysis(ai):
    result = await ai.analyze_candidate("5 years Python experience", "Software Engineer")
    assert "score" in result
    assert "reasoning" in result
    assert "decision" in result
    assert result["score"] == 50  # fallback score


@pytest.mark.asyncio
async def test_fallback_email_welcome(ai):
    result = await ai.generate_email(
        context={"name": "John", "job_role": "Developer"},
        email_type="welcome"
    )
    assert "John" in result
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_fallback_email_rejection(ai):
    result = await ai.generate_email(
        context={"name": "Jane", "job_role": "Designer"},
        email_type="rejection"
    )
    assert "Jane" in result
    assert "Designer" in result


@pytest.mark.asyncio
async def test_fallback_interview_questions(ai):
    result = await ai.suggest_interview_questions("Data Analyst")
    assert isinstance(result, list)
    assert len(result) >= 1


@pytest.mark.asyncio
async def test_fallback_sentiment(ai):
    result = await ai.analyze_sentiment("Thank you for the opportunity!")
    assert result["sentiment"] == "neutral"
    assert result["confidence"] == 0.5


@pytest.mark.asyncio
async def test_fallback_resume_scoring(ai):
    result = await ai.score_resume("Python, SQL, 3 years", "Data Engineer")
    assert "overall_score" in result
    assert result["overall_score"] == 50


@pytest.mark.asyncio
async def test_fallback_email_unknown_type(ai):
    result = await ai.generate_email(
        context={"name": "Test"},
        email_type="unknown_type"
    )
    assert "Test" in result
    assert isinstance(result, str)
