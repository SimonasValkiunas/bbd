from joblib import load
import numpy as np

def load_model():
    return load("C:\\Users\\Simonas\Desktop\\bakis\\back-prod\\trust_evaluation\\trust_eval_prod\\models\\bpnn.pkl")

def load_model_artifacts():
    mean = np.array([862.1823945, 7.39510703, 64.617737, 84.82568807, 61.49266055])
    std_dev = np.array([2894.91982298, 6.61297311, 20.94299947, 20.36659916, 21.09773546])
    return mean, std_dev

def predict_trust(data):
    model = load_model()
    data = np.array(data, dtype=float)
    mean, std_dev = load_model_artifacts()
    standardized_data = (data - mean) / std_dev
    standardized_data = standardized_data.reshape(1, -1)
    predictions = model.predict(standardized_data)
    return predictions

def calculate_metrics(request):
    availability = (request.successful_invocation / (request.successful_invocation + request.failed_invocation)) * 100 if (request.successful_invocation + request.failed_invocation) > 0 else 0
    reliability = (1-(request.error_request / (request.successful_invocation + request.failed_invocation))) * 100 if (request.successful_invocation + request.failed_invocation) > 0 else 0
    successability = (request.successful_request / (request.successful_request + request.error_request)) * 100 if (request.successful_request + request.error_request) > 0 else 0
    throughput = (request.successful_invocation + request.failed_invocation) / request.duration if request.duration > 0 else 0
    response_time = request.duration
    
    data = [round(response_time, 1), round(throughput, 1), round(successability, 1), round(availability, 1), round(reliability, 1)]
    trust = predict_trust(data)
    
    return {"availability": round(availability, 1), "reliability": round(reliability, 1), "successability": round(successability, 1), "throughput": round(throughput, 1), "response_time": round(response_time, 1), "trust": trust }
