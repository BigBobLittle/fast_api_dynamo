from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends, Header, status
from jose import jwt, jwk, JWTError
from typing import Dict, List, Optional
import requests
import os 
from jose.utils import base64url_decode 
from .utilities.db import DynamoDBManager

dynamodb_manager = DynamoDBManager()
security = HTTPBearer()

JWK = Dict[str, str]
JWKS = Dict[str, List[JWK]]


def get_jwks() -> JWKS:
    """
    Retrieves the JSON Web Key Set (JWKS) from the Cognito Identity Provider (IDP)
    using the specified region and pool ID from the environment variables.

    Returns:
        JWKS: The JSON Web Key Set containing the public keys.

    Raises:
        requests.exceptions.RequestException: If there is an error making the request.
        json.JSONDecodeError: If the response body cannot be parsed as JSON.
    """
    return requests.get(
        f"https://cognito-idp.{os.environ.get('COGNITO_REGION')}.amazonaws.com/"
        f"{os.environ.get('COGNITO_POOL_ID')}/.well-known/jwks.json"
    ).json()


def get_hmac_key(token: str, jwks: JWKS) -> Optional[JWK]:
    """
    Retrieves the HMAC key from the provided JWT token and JWKS.

    Args:
        token (str): The JWT token.
        jwks (JWKS): The JWKS containing the public keys.

    Returns:
        Optional[JWK]: The HMAC key corresponding to the "kid" in the JWT token header,
                       or None if no matching key is found.
    """
    kid = jwt.get_unverified_header(token).get("kid")
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key

def decode_token(token: str) -> Optional[dict]:
    """
    Decodes a JWT token using the provided key and returns the decoded payload as a dictionary.

    Args:
        token (str): The JWT token to decode.

    Returns:
        Optional[dict]: The decoded payload as a dictionary, or None if the token is invalid.

    Raises:
        HTTPException: If the token is invalid.
    """
    try:
        key = get_hmac_key(token, get_jwks())
        
        return jwt.decode(token, key=key, algorithms=["RS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def verify_jwt(token: str, jwks: JWKS) -> bool:
    """
    Verify the JWT token using the provided key and JWKS.

    Args:
        token (str): The JWT token to verify.
        jwks (JWKS): The JWKS containing the public keys.

    Returns:
        bool: True if the token is valid, False otherwise.

    Raises:
        ValueError: If no public key is found.
    """
    hmac_key = get_hmac_key(token, jwks)

    if not hmac_key:
        raise ValueError("No pubic key found!")

    hmac_key = jwk.construct(get_hmac_key(token, jwks))

    message, encoded_signature = token.rsplit(".", 1)
    decoded_signature = base64url_decode(encoded_signature.encode())

    return hmac_key.verify(message.encode(), decoded_signature)




async def authenticate_user(creds: HTTPAuthorizationCredentials = Depends(security)):
    """
    Asynchronously authenticates a user using a Bearer token.

    Args:
        creds (HTTPAuthorizationCredentials, optional): The credentials provided for authentication. Defaults to Depends(security).

    Raises:
        HTTPException: If the authentication scheme is invalid or the token is invalid.

    Returns:
        dict: A dictionary containing the username, sub, and cognito_groups of the authenticated user.

    """
    if creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=403, detail="Invalid authentication scheme")
    token = creds.credentials
    
    jwks = get_jwks()
    webtoken = verify_jwt(token=token, jwks=jwks)
    if not webtoken:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    # # decode token if it is valid 
    decoded_token = decode_token(token=token)
    print('decoded', decoded_token)
    username = decoded_token.get("username")
    sub = decoded_token.get("sub")
    cognito_groups = decoded_token.get("cognito:groups") or []
    
    return {"username": username, "sub": sub, "cognito_groups": cognito_groups}
     