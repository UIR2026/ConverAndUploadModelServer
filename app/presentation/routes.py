from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from app.domain.Exception import *
from app.domain.usecase.GetLatestModelUseCase import GetLatestModelUseCase
from app.domain.usecase.UploadModelUseCase import UploadModelUseCase
from app.presentation.dependencies import (
    get_latest_model_use_case,
    get_upload_model_use_case,
    verify_api_key,
)
from app.presentation.response.ModelResponse import ModelResponse

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/models", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
def upload_model(
    file: UploadFile = File(...),
    version: str = Form(...),
    use_case: UploadModelUseCase = Depends(get_upload_model_use_case),
) -> ModelResponse:
    try:
        result = use_case.execute(version=version, upload_file=file)
    except InvalidModelVersionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except InvalidModelFileError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except DuplicateModelVersionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ModelConversionError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    return ModelResponse.from_model(result)


@router.get("/models/latest", response_model=ModelResponse)
def get_latest_model(
    use_case: GetLatestModelUseCase = Depends(get_latest_model_use_case),
) -> ModelResponse:
    try:
        result = use_case.execute()
    except ModelNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ModelResponse.from_model(result)


@router.get("/models/latest/download")
def download_latest_model(
    version: str = Query(...),
    filename: str = Query(...),
    use_case: GetLatestModelUseCase = Depends(get_latest_model_use_case),
) -> FileResponse:
    try:
        result = use_case.execute(version=version, filename=filename)
    except ModelNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ModelFileMissingError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return FileResponse(
        path=result.file_path,
        filename=result.filename,
        media_type="application/octet-stream",
    )
