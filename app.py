from flask import Flask, request, jsonify, render_template
from data.loader import load_historical_data
from features.feature_engineering import calculate_features
from models.predictor import StockPredictor
from alerts.alarm import Alarm

app = Flask(__name__)

predictor = StockPredictor()
alarm = Alarm()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():

    symbol = request.json.get("symbol", "").upper()

    try:
        data = load_historical_data(symbol)
        data = calculate_features(data)

        predictor.train(data)

        result = predictor.predict(data)

        alarm.check_alarm(result)

        # Add historical data for the chart
        result["chart"] = {
            "dates": [str(d.date()) for d in data.index],
            "prices": [float(x) for x in data["close"].tolist()]
        }

        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400


@app.route("/set_alarm", methods=["POST"])
def set_alarm():

    threshold = request.json.get("threshold")

    alarm.set_alarm(threshold)

    return jsonify({
        "message": "Alarm set successfully!",
        "threshold": threshold
    })


if __name__ == "__main__":
    app.run(debug=True)