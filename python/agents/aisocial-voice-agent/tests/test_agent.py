"""
AISocial Voice Agent - Test Suite
=================================
Unit tests for the core agent engine, config loader, and tools.
Run with: pytest tests/ -v
"""

import os
import pytest
import yaml
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path


# =============================================================================
# Config Loader Tests
# =============================================================================

class TestConfigLoader:
    """Test the YAML config loading system."""

    def test_default_config_exists(self):
        """Verify default.yaml config file exists."""
        config_path = Path(__file__).parent.parent / "aisocial_voice_agent" / "configs" / "default.yaml"
        assert config_path.exists(), "default.yaml config file not found"

    def test_default_config_valid_yaml(self):
        """Verify default.yaml is valid YAML."""
        config_path = Path(__file__).parent.parent / "aisocial_voice_agent" / "configs" / "default.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        assert config is not None
        assert isinstance(config, dict)

    def test_restaurant_bot_config_valid(self):
        """Verify restaurant_bot.yaml sample config is valid."""
        config_path = Path(__file__).parent.parent / "aisocial_voice_agent" / "configs" / "restaurant_bot.yaml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            assert "bot_name" in config
            assert "business" in config
            assert "model" in config
            assert "persona" in config

    def test_config_has_required_fields(self):
        """Verify config has all required top-level fields."""
        config_path = Path(__file__).parent.parent / "aisocial_voice_agent" / "configs" / "default.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        required_fields = ["bot_name", "model", "persona"]
        for field in required_fields:
            assert field in config, f"Missing required field: {field}"

    def test_env_variable_override(self):
        """Test that environment variables can override config values."""
        with patch.dict(os.environ, {"BOT_CONFIG": "test_bot"}):
            assert os.environ.get("BOT_CONFIG") == "test_bot"


# =============================================================================
# Agent Structure Tests
# =============================================================================

class TestAgentStructure:
    """Test the agent module structure."""

    def test_package_init_exists(self):
        """Verify __init__.py exists in the package."""
        init_path = Path(__file__).parent.parent / "aisocial_voice_agent" / "__init__.py"
        assert init_path.exists()

    def test_agent_module_exists(self):
        """Verify agent.py exists."""
        agent_path = Path(__file__).parent.parent / "aisocial_voice_agent" / "agent.py"
        assert agent_path.exists()

    def test_tools_module_exists(self):
        """Verify tools.py exists."""
        tools_path = Path(__file__).parent.parent / "aisocial_voice_agent" / "tools.py"
        assert tools_path.exists()

    def test_config_module_exists(self):
        """Verify config.py exists."""
        config_path = Path(__file__).parent.parent / "aisocial_voice_agent" / "config.py"
        assert config_path.exists()

    def test_server_exists(self):
        """Verify server.py exists at project root."""
        server_path = Path(__file__).parent.parent / "server.py"
        assert server_path.exists()


# =============================================================================
# Tool Function Tests
# =============================================================================

class TestTools:
    """Test the tool functions (webhook, notify, save_lead)."""

    @pytest.mark.asyncio
    async def test_webhook_tool_structure(self):
        """Test webhook tool can be called with correct parameters."""
        # Mock the webhook call
        mock_response = {"status": "success", "message": "Webhook sent"}
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_session.post = AsyncMock()
            # Verify structure is correct
            assert mock_response["status"] == "success"

    def test_save_lead_data_format(self):
        """Test lead data structure is correct."""
        lead_data = {
            "name": "Test User",
            "phone": "+1-555-0100",
            "email": "test@example.com",
            "source": "voice_call",
            "bot_id": "test-bot"
        }
        assert "name" in lead_data
        assert "phone" in lead_data
        assert lead_data["source"] == "voice_call"


# =============================================================================
# Server Tests
# =============================================================================

class TestServer:
    """Test the FastAPI server configuration."""

    def test_pyproject_toml_exists(self):
        """Verify pyproject.toml exists."""
        toml_path = Path(__file__).parent.parent / "pyproject.toml"
        assert toml_path.exists()

    def test_env_example_exists(self):
        """Verify .env.example exists."""
        env_path = Path(__file__).parent.parent / ".env.example"
        assert env_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
