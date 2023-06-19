from fastapi import FastAPI, Depends, Request
from models import InputUser,CreateUpdateInput
import os
from sqlalchemy.orm import Session
from mlflow.sklearn import load_model
from database import engine, get_db, create_db_and_tables
import pandas as pd
from datetime import datetime

# Tell where is the tracking server and artifact server
os.environ['MLFLOW_TRACKING_URI'] = 'http://localhost:5001/'
os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://localhost:9000/'

# Learn, decide and get model from mlflow model registry
model_name = "ElectricConsumptionModeling"
model_version = 1
model = load_model(
    model_uri=f"models:/{model_name}/{model_version}"
)

app = FastAPI()

# Creates all the tables defined in models module
create_db_and_tables()


# Note that model will coming from mlflow
def makePrediction(model, request):
    # parse input from request
    begining_date = request["begining_date"]
    time = request["time"]
    finish_date = request["finish_date"]
    
    begining_date = datetime.combine(begining_date,time)
    
    finish_date = datetime.combine(finish_date,time)
    
    df = pd.DataFrame({"ds" : pd.date_range(begining_date,finish_date)})

    # Make an input vector
    features = df

    # Predict
    prediction = model.predict(features)

    return prediction[0]



# Insert Prediction information
def insertRequest(request, prediction, client_ip, db):
    newRequest = CreateUpdateInput(
        Age = request["begining_date"],
        CreditScore = request["finish_date"],
        prediction=prediction,
        client_ip=client_ip
    )

    with db as session:
        session.add(newRequest)
        session.commit()
        session.refresh(newRequest)

    return newRequest



# Electirical Price Prediction endpoint
@app.post("/electric/prediction")
async def predictPrice(request: InputUser, fastapi_req: Request,  db: Session = Depends(get_db)):
    prediction = makePrediction(model, request.dict())
    db_insert_record = insertRequest(request=request.dict(), prediction=prediction,
                                          client_ip=fastapi_req.client.host,
                                          db=db)
    return {"prediction": prediction, "db_record": db_insert_record}
