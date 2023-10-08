import uvicorn
from sqlalchemy.orm import Session
from pydantic import ValidationError
from fastapi.responses import Response
from fastapi import Depends, FastAPI, HTTPException, UploadFile, status

import crud
import config
import utils
from database import SessionMaker

app = FastAPI()


def get_db():
    db = SessionMaker()
    try:
        yield db
    finally:
        db.close()


@app.post("/load-file")
async def load_file(file: UploadFile, db: Session = Depends(get_db)):
    if file.content_type not in config.ALLOWED_CONTENT_TYPE:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid file format',
        )
    bytes_file = b''
    # async with aiofiles.open(
    #         Path.joinpath(Path(config.PATH_STATIC), file.filename), 'wb',
    # ) as out_file:
    while content := await file.read(config.CHUNK_SIZE):
        bytes_file += content
            # await out_file.write(content)
    try:
        data = utils.parse_csv(bytes_file)
    except (utils.CSVReadFailExceptoin, ValidationError):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Invalid data structure')
    version = crud.create_data(data, db)
    return {"version": version}


@app.get("/file/{version}")
def file(version: int, db: Session = Depends(get_db)):
    try:
        data, years = crud.get_data(version, db)
    except crud.DataIsNotFoundException:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Data is not found')
    csv = utils.create_csv(data, years)
    return Response(
        content=csv,
        media_type='multipart/form-data',
        headers={
            'Content-Disposition': f'attachment; filename="data_{version}.csv"'
        }
    )


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
