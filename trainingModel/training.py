from prophet import Prophet
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from urllib.parse import urlparse
from mlflow.tracking import MlflowClient
import mlflow.sklearn
from mlflow.store.artifact.runs_artifact_repo import RunsArtifactRepository

os.environ['MLFLOW_TRACKING_URI'] = 'http://localhost:5001/'
os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://localhost:9000/'

def edit_and_get_data():
    data=pd.read_csv("GercekZamanliTuketim-01012021-17062023.csv",encoding='ISO-8859-1')
    data['Tarih'] = pd.to_datetime(data['Tarih'], format='%d.%m.%Y', errors='coerce')

    data['Saat'] = pd.to_datetime(data['Saat'], format='%H:%M').dt.time
    data['ds'] = data['Tarih'].astype(str) + ' ' + data['Saat'].astype(str)

    data=data.iloc[:,2:]

    data=data.rename(columns={"Tüketim Miktarý (MWh)":"y"})
    data['y'] = data['y'].str.replace('.', '')
    data['y'] = data['y'].str.replace(',', '.')
    data['y'] = data['y'].astype(float)

    return data

def prophet_train(train,test):

    model = Prophet(seasonality_mode='multiplicative',seasonality_prior_scale=0.1)

    model.add_seasonality(name='hourly', period=24, fourier_order=5)

    model.fit(train)

    y_test=test["y"]

    forecast = model.predict(test.iloc[:,1:])

    error=(abs((list(y_test) - forecast["yhat"])/list(y_test))*100).mean()
    
    experiment_name = "Electric Consumption Training Model"
    mlflow.set_experiment(experiment_name)

    registered_model_name="ElectricConsumptionModeling"
    
    with mlflow.start_run(run_name="with-reg-rf-sklearn") as run:

        print("  Error: %s" % error)
        print(model.seasonality_prior_scale)
        print(model.seasonality_mode)
        mlflow.log_param("seasonality_prior_scale", model.seasonality_prior_scale)
        mlflow.log_param("seasonality_mode", model.seasonality_mode)
        mlflow.log_metric("error", error)
        
        tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme
    
        # Model registry does not work with file store
        if tracking_url_type_store != "file":
        
            # Register the model
            mlflow.prophet.log_model(model, "model", registered_model_name=registered_model_name)
        else:
            mlflow.prophet.log_model(model, "model")

    return forecast[["ds","yhat"]],error

if __name__ == "__main__":
    data=edit_and_get_data()

    test=data[data.ds>="2023-06-01"]
    train=data[data.ds<"2023-06-01"]

    result_data,error=prophet_train(train,test)

    print("Error : ",error)
    print(result_data)