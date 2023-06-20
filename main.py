from fastapi import FastAPI, Depends, Request
from models import InputUser,CreateUpdateInput, InputUserFive
import os
from sqlalchemy.orm import Session
from mlflow.prophet import load_model
from database import engine, get_db, create_db_and_tables
import pandas as pd
from datetime import datetime, time
from datetime import timedelta
import pytz
from prophet import serialize
import json

# Tell where is the tracking server and artifact server
os.environ['MLFLOW_TRACKING_URI'] = 'http://localhost:5001/'
os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://localhost:9000/'

# Learn, decide and get model from mlflow model registry
model_name = "ElectricConsumptionModeling"
model_version = 1
model = load_model(
    model_uri=f"models:/{model_name}/{model_version}"
)
params={attr: getattr(model, attr) for attr in serialize.SIMPLE_ATTRIBUTES}
print(params)

app = FastAPI()

# Creates all the tables defined in models module
create_db_and_tables()


# Note that model will coming from mlflow
def makePrediction(model, request):
    # parse input from request
    begining_date_str = request["begining_date"]
    time = request["time"]
    finish_date_str = request["finish_date"]
    
    # Convert beginning_date_str, time_str, and finish_date_str to datetime objects
    beginning_date = datetime.strptime(begining_date_str + " " +time, "%Y-%m-%d %H:%M:%S")
    finish_date = datetime.strptime(finish_date_str + " " +time, "%Y-%m-%d %H:%M:%S")
    
    #finish_date = beginning_date + timedelta(days=5)
    
    df = pd.DataFrame({"ds" : pd.date_range(beginning_date,finish_date, freq="H")})
    #df = pd.DataFrame({"ds" : pd.date_range("2023-05-01 10:00","2023-05-03 10:00",freq="H")})
    print(df.head())
    # Make an input vector
    features = df
    #print(model)
    # Predict
    prediction = model.predict(features)
    prediction['date'] = prediction['ds'].dt.date
    prediction['hour'] = prediction['ds'].dt.hour
    daily_average = prediction.groupby(['date'])['yhat'].median()
    print(daily_average)
    print(type(daily_average))
    daily_average = daily_average.reset_index()
    daily_average = daily_average.rename(columns={'yhat': 'y'})
    daily_average = daily_average.rename(columns={'date': 'd'})
    print(daily_average)
    print(type(daily_average))
    daily_average["d"] = daily_average["d"].astype(str)
    daily_average['y'] = daily_average['y'].round(2)
    print(daily_average)
    pred_dict = daily_average[["d","y"]].to_dict(orient="records")
    print(pred_dict)
    return json.dumps(pred_dict)


# Insert Prediction information
def insertRequest(request, prediction, client_ip, db):
    newRequest = CreateUpdateInput(
        begining_date = request["begining_date"],
        finish_date = request["finish_date"],
        time = request["time"],
        prediction=prediction,
        client_ip=client_ip
    )

    with db as session:
        session.add(newRequest)
        session.commit()
        session.refresh(newRequest)

    return newRequest



# Electirical Price Prediction endpoint
@app.post("/electric/prediction/fivedays")
async def predictPrice(request: InputUserFive, fastapi_req: Request,  db: Session = Depends(get_db)):
    prediction = makePrediction(model, request.dict())
    db_insert_record = insertRequest(request=request.dict(), prediction=prediction,
                                          client_ip=fastapi_req.client.host,
                                          db=db)
    return {"prediction": prediction, "db_record": db_insert_record}


# Electirical Price Prediction endpoint
@app.post("/electric/prediction/days")
async def predictPrice(request: InputUser, fastapi_req: Request,  db: Session = Depends(get_db)):
    prediction = makePrediction(model, request.dict())
    db_insert_record = insertRequest(request=request.dict(), prediction=prediction,
                                          client_ip=fastapi_req.client.host,
                                          db=db)
    return {"prediction": prediction, "db_record": db_insert_record}
