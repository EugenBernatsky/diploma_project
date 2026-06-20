import html

import httpx
from fastapi import HTTPException

from app.core.config import settings


BREVO_SEND_EMAIL_URL = "https://api.brevo.com/v3/smtp/email"


async def send_email_verification_code(
    to_email: str,
    username: str,
    code: str,
) -> None:
    if not settings.BREVO_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Brevo API key is not configured",
        )

    if not settings.BREVO_SENDER_EMAIL:
        raise HTTPException(
            status_code=500,
            detail="Brevo sender email is not configured",
        )

    safe_username = html.escape(username)
    safe_code = html.escape(code)

    subject = "MediaCompass email verification"

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.5;">
        <h2>Email verification</h2>
        <p>Hi, <strong>{safe_username}</strong>!</p>
        <p>Your verification code:</p>
        <p style="font-size: 24px; font-weight: bold; letter-spacing: 4px;">
          {safe_code}
        </p>
        <p>The code is valid for {settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES} minutes.</p>
        <p>If you did not create a MediaCompass account, you can ignore this email.</p>
      </body>
    </html>
    """

    text_content = (
        f"Hi, {username}!\n\n"
        f"Your MediaCompass email verification code: {code}\n\n"
        f"The code is valid for "
        f"{settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES} minutes.\n\n"
        "If you did not create a MediaCompass account, you can ignore this email."
    )

    payload = {
        "sender": {
            "name": settings.BREVO_SENDER_NAME,
            "email": settings.BREVO_SENDER_EMAIL,
        },
        "to": [
            {
                "email": to_email,
                "name": username,
            }
        ],
        "subject": subject,
        "htmlContent": html_content,
        "textContent": text_content,
    }

    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                BREVO_SEND_EMAIL_URL,
                headers=headers,
                json=payload,
            )

        if response.status_code >= 400:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to send verification email via Brevo: {response.text}",
            )

    except httpx.RequestError as error:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to connect to Brevo: {str(error)}",
        ) from error
