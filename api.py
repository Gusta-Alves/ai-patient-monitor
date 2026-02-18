from fastapi import FastAPI, HTTPException
import os
import boto3
import hmac
import hashlib
import base64
import requests
from jose import jwt
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn
from orchestrator.cloud_orchestrator import process_patient_video
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AI Patient Monitor API",
    description="API Multimodal para detecção de quedas e emergências em vídeos de pacientes.",
    version="1.0.0"
)


class VideoAnalysisRequest(BaseModel):
    video_key: str
    use_s3: bool = True
    use_localstack: bool = False


class LoginRequest(BaseModel):
    username: str
    password: str


# --- Configuração do Cognito ---
security = HTTPBearer()


def verify_cognito_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Valida o token JWT do Cognito enviado no Header Authorization.
    """
    token = credentials.credentials
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
    client_id = os.getenv("COGNITO_CLIENT_ID")  # Opcional, mas recomendado

    if not user_pool_id:
        # Se não houver configuração, bloqueia por segurança (ou permita bypass em dev se preferir)
        raise HTTPException(
            status_code=500, detail="Configuração de Auth (User Pool ID) ausente.")

    try:
        # 1. Busca as chaves públicas (JWKS) do Cognito
        # DICA: Em produção, implemente cache para não fazer request a cada chamada
        jwks_url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
        jwks = requests.get(jwks_url).json()

        # 2. Encontra a chave correta usada para assinar este token
        header = jwt.get_unverified_header(token)
        rsa_key = next(
            (key for key in jwks["keys"] if key["kid"] == header["kid"]), None)

        if not rsa_key:
            raise HTTPException(
                status_code=401, detail="Chave de assinatura inválida ou expirada.")

        # 3. Decodifica e valida o token
        # Desabilitamos verify_aud automático para suportar tanto ID Token (usa 'aud') 
        # quanto Access Token (usa 'client_id')
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
            issuer=f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}"
        )

        # 4. Validação manual do Client ID (Audience)
        if client_id:
            token_aud = payload.get("aud")
            token_client_id = payload.get("client_id")
            if token_aud != client_id and token_client_id != client_id:
                raise HTTPException(status_code=401, detail="Token não pertence a este App Client.")

        return payload
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Token inválido: {str(e)}")


@app.get("/health", status_code=200)
async def health_check():
    """Endpoint de verificação de saúde para Load Balancers (AWS)."""
    return {"status": "healthy"}


@app.post("/auth/login")
async def login(request: LoginRequest):
    """
    Gera um token JWT (IdToken) usando usuário e senha do Cognito.
    """
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    client_id = os.getenv("COGNITO_CLIENT_ID")
    client_secret = os.getenv("COGNITO_CLIENT_SECRET")

    if not client_secret:
        print("⚠️ AVISO: COGNITO_CLIENT_SECRET não encontrado no ambiente. O cálculo do SECRET_HASH será pulado.")

    if not client_id:
        raise HTTPException(
            status_code=500, detail="COGNITO_CLIENT_ID não configurado.")

    client = boto3.client('cognito-idp', region_name=region)

    auth_params = {
        'USERNAME': request.username,
        'PASSWORD': request.password
    }

    if client_secret:
        message = request.username + client_id
        dig = hmac.new(client_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
        secret_hash = base64.b64encode(dig).decode()
        auth_params['SECRET_HASH'] = secret_hash

    try:
        response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters=auth_params
        )
        # Retorna os tokens (AccessToken, IdToken, RefreshToken)
        return response['AuthenticationResult']
    except client.exceptions.NotAuthorizedException:
        raise HTTPException(
            status_code=401, detail="Usuário ou senha incorretos.")
    except client.exceptions.UserNotConfirmedException:
        raise HTTPException(
            status_code=400, detail="Usuário não confirmado (verifique seu email).")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/analyze-video", status_code=200)
async def analyze_video_endpoint(
    request: VideoAnalysisRequest,
    user_claims: dict = Depends(verify_cognito_token)
):
    """
    Endpoint para processar um vídeo.
    - **video_key**: Nome do arquivo no S3 ou localmente.
    - **use_s3**: Se deve tentar baixar do S3.
    - **use_localstack**: Se deve usar o LocalStack (ambiente dev).
    """
    # Log para confirmar que o Cognito identificou o usuário
    user_id = user_claims.get("sub") or user_claims.get("username", "unknown")
    print(f"🔐 Requisição autenticada. Usuário: {user_id}")

    try:
        # headless=True é mandatório para APIs (não abre janela do OpenCV)
        result = process_patient_video(
            video_key=request.video_key,
            use_s3=request.use_s3,
            use_localstack=request.use_localstack,
            headless=True
        )
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Roda o servidor na porta 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
