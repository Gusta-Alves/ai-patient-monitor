from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from cloud_orchestrator import process_patient_video

app = FastAPI(
    title="AI Patient Monitor API",
    description="API Multimodal para detecção de quedas e emergências em vídeos de pacientes.",
    version="1.0.0"
)


class VideoAnalysisRequest(BaseModel):
    video_key: str
    use_s3: bool = True
    use_localstack: bool = False


@app.post("/analyze-video", status_code=200)
async def analyze_video_endpoint(request: VideoAnalysisRequest):
    """
    Endpoint para processar um vídeo.
    - **video_key**: Nome do arquivo no S3 ou localmente.
    - **use_s3**: Se deve tentar baixar do S3.
    - **use_localstack**: Se deve usar o LocalStack (ambiente dev).
    """
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
