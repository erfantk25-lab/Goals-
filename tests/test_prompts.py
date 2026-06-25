import pytest
from prompts.prompt_manager import PromptManager

def test_prompt_loading():
    pm = PromptManager()
    prompt_text = pm.load_prompt("v1")
    assert "12-STEP RULE" in prompt_text
    assert "{goal}" in prompt_text

def test_prompt_generation():
    pm = PromptManager()
    messages = pm.generate_messages(
        goal="Launch a Startup",
        category="Business",
        difficulty="Hard",
        estimated_success=42.5
    )
    
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    
    user_content = messages[1]["content"]
    assert "Launch a Startup" in user_content
    assert "Business" in user_content
    assert "Hard" in user_content
    assert "42.5%" in user_content

def test_invalid_prompt_version():
    pm = PromptManager()
    with pytest.raises(FileNotFoundError):
        pm.load_prompt("v999_nonexistent")
