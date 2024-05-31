import joblib, os
from fastapi import APIRouter
from schemas.prediction import PredictionRequest, PredictionResponse
from modelling.custom_transformers import EmailToWordCounterTransformer, WordCounterToVectorTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression


router = APIRouter()

with open(os.path.join(os.getcwd(), 'models/preprocess_pipeline.pkl'), 'rb') as pipeline:
    preprocess_pipeline: Pipeline = joblib.load(pipeline)

with open(os.path.join(os.getcwd(), 'models/logistic_classifier.pkl'), 'rb') as logistic:
    logistic_classifier: LogisticRegression = joblib.load(logistic)
    logistic_classifier = logistic_classifier

@router.post('/predict/', response_model=PredictionResponse)
def make_prediction(request: PredictionRequest):
    transformed_request = preprocess_pipeline.transform([request.content])
    classification = logistic_classifier.predict(transformed_request)
    probability = logistic_classifier.predict_proba(transformed_request)[0][1]

    return {'probability':probability, 'classification':classification}
    
