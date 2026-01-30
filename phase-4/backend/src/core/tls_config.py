"""
Security configuration for encrypting data in transit (HTTPS/TLS)

This module provides configuration and utilities for securing data transmission
between clients and servers using TLS/SSL encryption.
"""

import ssl
import os
from typing import Optional
from fastapi import FastAPI
from uvicorn import Config, Server


class TLSConfiguration:
    """
    Configuration class for TLS/SSL settings
    """
    
    def __init__(
        self,
        certfile: Optional[str] = None,
        keyfile: Optional[str] = None,
        ssl_version: int = ssl.PROTOCOL_TLS_SERVER,
        ssl_ciphers: str = "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"
    ):
        self.certfile = certfile or os.getenv("SSL_CERT_FILE")
        self.keyfile = keyfile or os.getenv("SSL_KEY_FILE")
        self.ssl_version = ssl_version
        self.ssl_ciphers = ssl_ciphers
    
    def get_ssl_context(self) -> Optional[ssl.SSLContext]:
        """
        Create and return an SSL context with secure settings
        """
        if not self.certfile or not self.keyfile:
            # If no certificate files are provided, return None
            # This allows the server to run without SSL in development
            return None
        
        # Create SSL context with secure settings
        context = ssl.SSLContext(self.ssl_version)
        
        # Load certificate and private key
        context.load_cert_chain(self.certfile, self.keyfile)
        
        # Set secure cipher suites
        context.set_ciphers(self.ssl_ciphers)
        
        # Disable insecure protocols and ciphers
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_TLSv1
        context.options |= ssl.OP_NO_TLSv1_1
        
        # Enable certificate verification
        context.verify_mode = ssl.CERT_REQUIRED
        
        return context
    
    def is_tls_enabled(self) -> bool:
        """
        Check if TLS is properly configured
        """
        return bool(self.certfile and self.keyfile)


def configure_secure_app(app: FastAPI) -> FastAPI:
    """
    Configure the FastAPI app with security headers and settings
    """
    # Add security headers middleware
    from starlette.middleware import Middleware
    from starlette.middleware.trustedhost import TrustedHostMiddleware
    from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
    
    # Add Strict-Transport-Security header to enforce HTTPS
    from starlette.responses import Response
    
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
        
        return response
    
    return app


def create_secure_server_config(
    app: FastAPI,
    host: str = "0.0.0.0",
    port: int = 8443,
    tls_config: Optional[TLSConfiguration] = None
) -> Config:
    """
    Create a Uvicorn server configuration with TLS settings
    """
    if tls_config is None:
        tls_config = TLSConfiguration()
    
    ssl_context = tls_config.get_ssl_context()
    
    # Create the server configuration
    config = Config(
        app=app,
        host=host,
        port=port,
        ssl_keyfile=tls_config.keyfile,
        ssl_certfile=tls_config.certfile,
        ssl_version=tls_config.ssl_version,
        ssl_ciphers=tls_config.ssl_ciphers
    )
    
    return config


# Example usage for development with self-signed certificates
def create_dev_tls_config() -> TLSConfiguration:
    """
    Create a TLS configuration suitable for development
    NOTE: This is for development purposes only.
    In production, use proper certificates from a trusted CA.
    """
    # For development, we'll look for certificates in common locations
    # or create a configuration that can be easily overridden
    cert_path = os.getenv("DEV_SSL_CERT", "./dev-cert.pem")
    key_path = os.getenv("DEV_SSL_KEY", "./dev-key.pem")
    
    return TLSConfiguration(
        certfile=cert_path,
        keyfile=key_path
    )


# Additional utility functions for managing certificates
def validate_certificate_chain(cert_path: str, key_path: str) -> bool:
    """
    Validate that the certificate and key files exist and are valid
    """
    import tempfile
    
    try:
        # Check if files exist
        if not os.path.exists(cert_path):
            raise FileNotFoundError(f"Certificate file not found: {cert_path}")
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"Key file not found: {key_path}")
        
        # Try to load the certificate and key to validate them
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_path, key_path)
        
        return True
    except Exception as e:
        print(f"Certificate validation failed: {str(e)}")
        return False


def generate_self_signed_cert(
    hostname: str = "localhost",
    cert_path: str = "./dev-cert.pem",
    key_path: str = "./dev-key.pem"
) -> None:
    """
    Generate a self-signed certificate for development purposes
    NOTE: This is for development only, not for production use.
    """
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create a self-signed certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Organization"),
            x509.NameAttribute(NameOID.COMMON_NAME, hostname),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            # Our certificate will be valid for 1 year
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).sign(private_key, hashes.SHA256())
        
        # Write the certificate and private key to files
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print(f"Self-signed certificate generated: {cert_path}")
        print(f"Private key generated: {key_path}")
        
    except ImportError:
        print("cryptography library not available. Install it with: pip install cryptography")
    except Exception as e:
        print(f"Failed to generate certificate: {str(e)}")


# Global TLS configuration instance
tls_config = TLSConfiguration()


def get_tls_config() -> TLSConfiguration:
    """
    Get the global TLS configuration instance
    """
    return tls_config