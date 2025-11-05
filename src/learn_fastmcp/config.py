"""
Configuration module for FastMCP server.

This module provides Pydantic-based configuration management with support for:
- Environment variable loading via .env files
- Type validation and coercion
- Custom validation logic
- Default values with clear documentation
"""

import logging
from enum import Enum

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


logger = logging.getLogger(__name__)


class TransportType(str, Enum):
    """
    Supported MCP transport types.

    Attributes:
        STDIO: Standard input/output communication
        STREAMABLE_HTTP: HTTP with chunked/streaming responses (recommended)
    """

    STDIO = "stdio"
    STREAMABLE_HTTP = "streamable-http"


class MCPConfig(BaseSettings):
    """
    FastMCP Server Configuration.

    Configuration is loaded from:
    1. Environment variables (highest priority)
    2. .env file (if present)
    3. Default values (lowest priority)

    Environment Variables:
        MCP_TRANSPORT: Transport type (stdio, streamable-http)
        MCP_HOST: Server host address
        MCP_PORT: Server port number

    Example:
        >>> config = MCPConfig()
        >>> print(config.mcp_port)
        8000
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields in .env
    )

    # Transport configuration
    mcp_transport: TransportType = Field(
        default=TransportType.STREAMABLE_HTTP,
        description="MCP transport type (stdio or streamable-http)",
        validation_alias="MCP_TRANSPORT",
    )

    # Network configuration
    mcp_host: str = Field(
        default="0.0.0.0",
        description="Server host address",
        validation_alias="MCP_HOST",
    )

    mcp_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Server port number (1-65535)",
        validation_alias="MCP_PORT",
    )

    @field_validator("mcp_transport", mode="before")
    @classmethod
    def validate_transport(cls, v: str | TransportType) -> str:
        """
        Validate and normalize transport type.

        Args:
            v: Transport type string or enum

        Returns:
            str: Validated transport type

        Raises:
            ValueError: If transport type is invalid
        """
        if isinstance(v, TransportType):
            logger.debug(f"Transport type is already TransportType enum: {v.value}")
            return v.value

        # Normalize to lowercase
        v = v.lower().strip()
        logger.debug(f"Normalized transport string: {v}")

        # Check if valid
        valid_transports = {t.value for t in TransportType}
        if v not in valid_transports:
            logger.error(
                f"Invalid transport type: '{v}'. Valid options: {valid_transports}"
            )
            raise ValueError(
                f"Invalid transport: '{v}'. Must be one of {valid_transports}"
            )

        logger.debug(f"Transport validation passed: {v}")
        return v

    def to_run_config(self) -> dict[str, str | int]:
        """
        Convert config to dictionary suitable for app.run(**config).

        This method prepares the configuration dictionary for passing to
        the FastMCP app.run() method. Different transport types accept
        different parameters:
        - STDIO: Only accepts 'transport' parameter
        - HTTP/Streamable-HTTP: Accept 'transport', 'host', and 'port' parameters

        Returns:
            dict: Configuration dictionary appropriate for the transport type
                - STDIO: {'transport': 'stdio'}
                - HTTP: {'transport': 'streamable-http', 'host': '0.0.0.0', 'port': 8000}

        Example:
            >>> config = MCPConfig(mcp_transport='stdio')
            >>> run_config = config.to_run_config()
            >>> print(run_config)
            {'transport': 'stdio'}

            >>> config = MCPConfig(mcp_transport='streamable-http')
            >>> run_config = config.to_run_config()
            >>> print(run_config)
            {'transport': 'streamable-http', 'host': '0.0.0.0', 'port': 8000}
        """
        transport_value = (
            self.mcp_transport.value
            if isinstance(self.mcp_transport, TransportType)
            else self.mcp_transport
        )
        logger.debug(f"Converting config to run_config: transport={transport_value}")

        # STDIO transport doesn't accept host/port parameters
        if transport_value == TransportType.STDIO.value:
            logger.debug("STDIO transport: excluding host and port parameters")
            return {
                "transport": transport_value,
            }

        # HTTP/Streamable-HTTP transports require host and port
        logger.debug(
            f"HTTP transport: including host ({self.mcp_host}) "
            f"and port ({self.mcp_port}) parameters"
        )
        return {
            "transport": transport_value,
            "host": self.mcp_host,
            "port": self.mcp_port,
        }

    def log_config(self) -> None:
        """
        Log the current configuration (safe for logging, no secrets).

        This method logs all configuration values for debugging and
        visibility into the server startup configuration.
        """
        logger.info(f"MCP Transport: {self.mcp_transport.value}")
        logger.info(f"MCP Host: {self.mcp_host}")
        logger.info(f"MCP Port: {self.mcp_port}")

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"MCPConfig(transport={self.mcp_transport.value}, "
            f"host={self.mcp_host}, port={self.mcp_port})"
        )


def load_config() -> MCPConfig:
    """
    Load and validate configuration from environment.

    This is the main entry point for loading configuration.
    It handles .env file loading and environment variable parsing.

    Returns:
        MCPConfig: Validated configuration object

    Raises:
        ValueError: If configuration validation fails

    Example:
        >>> config = load_config()
        >>> print(config.mcp_port)
        8000
    """
    try:
        logger.debug("Attempting to load configuration from environment")
        config = MCPConfig()
        logger.debug(f"Configuration loaded successfully: {config}")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}", exc_info=True)
        raise ValueError(f"Configuration error: {e}") from e
