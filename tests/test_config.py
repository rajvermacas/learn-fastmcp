"""
Unit tests for the configuration module.

This module tests the MCPConfig class and related configuration functionality,
particularly focusing on transport-specific parameter handling.
"""

import pytest
import os
from unittest.mock import patch

from learn_fastmcp.config import MCPConfig, TransportType, load_config


class TestTransportType:
    """Tests for TransportType enum."""

    def test_stdio_value(self):
        """Test STDIO enum value."""
        assert TransportType.STDIO.value == "stdio"

    def test_streamable_http_value(self):
        """Test STREAMABLE_HTTP enum value."""
        assert TransportType.STREAMABLE_HTTP.value == "streamable-http"


class TestMCPConfigDefaults:
    """Tests for MCPConfig with default values."""

    def test_default_transport(self):
        """Test that default transport is streamable-http."""
        config = MCPConfig()
        assert config.mcp_transport == TransportType.STREAMABLE_HTTP.value

    def test_default_host(self):
        """Test that default host is 0.0.0.0."""
        config = MCPConfig()
        assert config.mcp_host == "0.0.0.0"

    def test_default_port(self):
        """Test that default port is 8000."""
        config = MCPConfig()
        assert config.mcp_port == 8000


class TestMCPConfigValidation:
    """Tests for MCPConfig validation."""

    def test_valid_transport_stdio(self):
        """Test that stdio transport is valid."""
        config = MCPConfig(mcp_transport="stdio")
        assert config.mcp_transport == "stdio"

    def test_valid_transport_streamable_http(self):
        """Test that streamable-http transport is valid."""
        config = MCPConfig(mcp_transport="streamable-http")
        assert config.mcp_transport == "streamable-http"

    def test_transport_case_insensitive(self):
        """Test that transport validation is case-insensitive."""
        config = MCPConfig(mcp_transport="STDIO")
        assert config.mcp_transport == "stdio"

    def test_transport_strips_whitespace(self):
        """Test that transport validation strips whitespace."""
        config = MCPConfig(mcp_transport="  stdio  ")
        assert config.mcp_transport == "stdio"

    def test_invalid_transport(self):
        """Test that invalid transport raises ValueError."""
        with pytest.raises(ValueError):
            MCPConfig(mcp_transport="invalid-transport")

    def test_port_range_minimum(self):
        """Test that port must be >= 1."""
        with pytest.raises(ValueError):
            MCPConfig(mcp_port=0)

    def test_port_range_maximum(self):
        """Test that port must be <= 65535."""
        with pytest.raises(ValueError):
            MCPConfig(mcp_port=65536)

    def test_valid_port_range(self):
        """Test that valid ports work."""
        config1 = MCPConfig(mcp_port=1)
        assert config1.mcp_port == 1

        config2 = MCPConfig(mcp_port=65535)
        assert config2.mcp_port == 65535


class TestToRunConfigStdio:
    """Tests for to_run_config() with STDIO transport."""

    def test_stdio_excludes_host(self):
        """Test that STDIO transport config excludes host."""
        config = MCPConfig(mcp_transport="stdio")
        run_config = config.to_run_config()

        assert "host" not in run_config
        assert run_config["transport"] == "stdio"

    def test_stdio_excludes_port(self):
        """Test that STDIO transport config excludes port."""
        config = MCPConfig(mcp_transport="stdio")
        run_config = config.to_run_config()

        assert "port" not in run_config
        assert run_config["transport"] == "stdio"

    def test_stdio_only_transport_parameter(self):
        """Test that STDIO transport config only contains transport."""
        config = MCPConfig(mcp_transport="stdio")
        run_config = config.to_run_config()

        assert list(run_config.keys()) == ["transport"]
        assert run_config["transport"] == "stdio"


class TestToRunConfigStreamableHttp:
    """Tests for to_run_config() with HTTP transport."""

    def test_streamable_http_includes_host(self):
        """Test that streamable-http transport config includes host."""
        config = MCPConfig(
            mcp_transport="streamable-http",
            mcp_host="127.0.0.1"
        )
        run_config = config.to_run_config()

        assert "host" in run_config
        assert run_config["host"] == "127.0.0.1"

    def test_streamable_http_includes_port(self):
        """Test that streamable-http transport config includes port."""
        config = MCPConfig(
            mcp_transport="streamable-http",
            mcp_port=9000
        )
        run_config = config.to_run_config()

        assert "port" in run_config
        assert run_config["port"] == 9000

    def test_streamable_http_full_config(self):
        """Test that streamable-http includes all required parameters."""
        config = MCPConfig(
            mcp_transport="streamable-http",
            mcp_host="192.168.1.1",
            mcp_port=3000
        )
        run_config = config.to_run_config()

        expected_keys = {"transport", "host", "port"}
        assert set(run_config.keys()) == expected_keys
        assert run_config["transport"] == "streamable-http"
        assert run_config["host"] == "192.168.1.1"
        assert run_config["port"] == 3000

    def test_default_streamable_http_config(self):
        """Test default streamable-http configuration."""
        config = MCPConfig()  # Default is streamable-http
        run_config = config.to_run_config()

        assert run_config["transport"] == "streamable-http"
        assert run_config["host"] == "0.0.0.0"
        assert run_config["port"] == 8000


class TestLoadConfig:
    """Tests for load_config() function."""

    def test_load_config_success(self):
        """Test that load_config() returns MCPConfig instance."""
        config = load_config()
        assert isinstance(config, MCPConfig)

    def test_load_config_with_env_variables(self):
        """Test that load_config() respects environment variables."""
        with patch.dict(os.environ, {
            "MCP_TRANSPORT": "stdio",
            "MCP_HOST": "localhost",
            "MCP_PORT": "5000"
        }):
            config = load_config()
            assert config.mcp_transport == "stdio"
            assert config.mcp_host == "localhost"
            assert config.mcp_port == 5000

    def test_load_config_invalid_transport(self):
        """Test that load_config() raises ValueError for invalid transport."""
        with patch.dict(os.environ, {"MCP_TRANSPORT": "invalid"}):
            with pytest.raises(ValueError):
                load_config()


class TestConfigRepr:
    """Tests for configuration string representation."""

    def test_repr_format(self):
        """Test that __repr__ returns correct format."""
        config = MCPConfig(
            mcp_transport="stdio",
            mcp_host="localhost",
            mcp_port=3000
        )
        repr_str = repr(config)

        assert "MCPConfig" in repr_str
        assert "stdio" in repr_str
        assert "localhost" in repr_str
        assert "3000" in repr_str


class TestConfigLogging:
    """Tests for configuration logging method."""

    def test_log_config_callable(self):
        """Test that log_config() method is callable without error."""
        config = MCPConfig()
        # Should not raise any exception
        config.log_config()

    def test_log_config_with_stdio(self):
        """Test log_config() with STDIO transport."""
        config = MCPConfig(mcp_transport="stdio")
        # Should not raise any exception
        config.log_config()


class TestIntegrationConfigAndRunConfig:
    """Integration tests for config and run_config."""

    def test_run_config_works_with_default_values(self):
        """Test that run_config works with default configuration."""
        config = MCPConfig()
        run_config = config.to_run_config()

        # Default is streamable-http with host/port
        assert isinstance(run_config, dict)
        assert "transport" in run_config
        assert "host" in run_config
        assert "port" in run_config

    def test_transport_change_affects_run_config(self):
        """Test that changing transport affects run_config output."""
        # Test with streamable-http (has host/port)
        config1 = MCPConfig(mcp_transport="streamable-http")
        run_config1 = config1.to_run_config()
        assert len(run_config1) == 3  # transport, host, port

        # Test with stdio (only transport)
        config2 = MCPConfig(mcp_transport="stdio")
        run_config2 = config2.to_run_config()
        assert len(run_config2) == 1  # only transport

    def test_host_port_irrelevant_for_stdio(self):
        """Test that host/port values don't affect STDIO config."""
        config = MCPConfig(
            mcp_transport="stdio",
            mcp_host="ignored-host",
            mcp_port=9999
        )
        run_config = config.to_run_config()

        # Even though host and port are set, STDIO ignores them
        assert run_config == {"transport": "stdio"}
        assert "host" not in run_config
        assert "port" not in run_config
