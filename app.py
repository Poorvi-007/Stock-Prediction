from flask import Flask, request, jsonify, render_template
import plotly.graph_objects as go

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

        result["chart"] = {
            "dates": [str(d.date()) for d in data.index],
            "prices": [float(x) for x in data["close"].tolist()]
        }

        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400


@app.route("/candlestick", methods=["POST"])
def candlestick():

    symbol = request.json.get("symbol", "").upper()

    try:
        data = load_historical_data(symbol)

        fig = go.Figure()

        fig.add_trace(
        go.Candlestick(
        x=[str(d.date()) for d in data.index],
        open=data["open"].tolist(),
        high=data["high"].tolist(),
        low=data["low"].tolist(),
        close=data["close"].tolist(),
        name=symbol
    )
)

        fig.add_trace(
        go.Bar(
        x=[str(d.date()) for d in data.index],
        y=data["volume"].tolist(),
        name="Volume",
        yaxis="y2"
    )
)
        xaxis=dict(
        rangeselector=dict(
        buttons=[
            dict(count=1, label="1M", step="month", stepmode="backward"),
            dict(count=3, label="3M", step="month", stepmode="backward"),
            dict(count=6, label="6M", step="month", stepmode="backward"),
            dict(count=1, label="1Y", step="year", stepmode="backward"),
            dict(step="all", label="All")
        ]
    ),
    type="date"
    ),

        return jsonify(fig.to_plotly_json())

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
    