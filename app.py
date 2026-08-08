from flask import Flask, request, jsonify, render_template
import plotly.graph_objects as go
import json

from data.loader import load_historical_data
from features.feature_engineering import calculate_features
from models.predictor import StockPredictor
from alerts.alarm import Alarm


app = Flask(__name__)

predictor = StockPredictor()
alarm = Alarm()


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- PREDICTION ----------------
@app.route("/predict", methods=["POST"])
def predict():

    symbol = request.json.get("symbol", "").upper()

    if not symbol:
        return jsonify({"error": "Please enter a stock symbol"}), 400

    try:
        # Load stock data
        data = load_historical_data(symbol)

        # Calculate indicators/features
        data = calculate_features(data)

        # Train model
        predictor.train(data)

        # Make prediction
        result = predictor.predict(data)

        # Check alarm
        alarm.check_alarm(result)

        # Add chart data
        result["chart"] = {
            "dates": [str(d.date()) for d in data.index],
            "open": [float(x) for x in data["open"].tolist()],
            "high": [float(x) for x in data["high"].tolist()],
            "low": [float(x) for x in data["low"].tolist()],
            "close": [float(x) for x in data["close"].tolist()],
            "volume": [float(x) for x in data["volume"].tolist()]
        }

        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 400


# ---------------- CANDLESTICK CHART ----------------
@app.route("/candlestick", methods=["POST"])
def candlestick():

    symbol = request.json.get("symbol", "").upper()

    if not symbol:
        return jsonify({
            "error": "Please enter a stock symbol"
        }), 400

    try:
        # Load historical data
        data = load_historical_data(symbol)

        dates = [str(d.date()) for d in data.index]

        # Create figure
        fig = go.Figure()

        # ---------------- CANDLESTICKS ----------------
        fig.add_trace(
            go.Candlestick(
                x=dates,
                open=data["open"].astype(float).tolist(),
                high=data["high"].astype(float).tolist(),
                low=data["low"].astype(float).tolist(),
                close=data["close"].astype(float).tolist(),
                name=symbol
            )
        )

        # ---------------- VOLUME ----------------
        fig.add_trace(
            go.Bar(
                x=dates,
                y=data["volume"].astype(float).tolist(),
                name="Volume",
                yaxis="y2",
                opacity=0.4
            )
        )

        # ---------------- LAYOUT ----------------
        fig.update_layout(

            title=f"{symbol} Candlestick Chart",

            xaxis=dict(
                title="Date",

                rangeselector=dict(
                    buttons=[
                        dict(
                            count=1,
                            label="1M",
                            step="month",
                            stepmode="backward"
                        ),
                        dict(
                            count=3,
                            label="3M",
                            step="month",
                            stepmode="backward"
                        ),
                        dict(
                            count=6,
                            label="6M",
                            step="month",
                            stepmode="backward"
                        ),
                        dict(
                            count=1,
                            label="1Y",
                            step="year",
                            stepmode="backward"
                        ),
                        dict(
                            step="all",
                            label="All"
                        )
                    ]
                ),

                type="date"
            ),

            yaxis=dict(
                title="Price ($)",
                autorange=True
            ),

            yaxis2=dict(
                title="Volume",
                overlaying="y",
                side="right",
                showgrid=False
            ),

            height=650,

            hovermode="x unified",

            margin=dict(
                l=60,
                r=60,
                t=80,
                b=60
            )
        )

        # Remove Plotly range slider because we already
        # have 1M / 3M / 6M / 1Y / All buttons
        fig.update_layout(
            xaxis_rangeslider_visible=False
        )

        # Convert Plotly figure to JSON
        chart_json = json.loads(fig.to_json())

        return jsonify(chart_json)

    except Exception as e:
        import traceback
        traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 400


# ---------------- SET ALARM ----------------
@app.route("/set_alarm", methods=["POST"])
def set_alarm():

    threshold = request.json.get("threshold")

    if threshold is None:
        return jsonify({
            "error": "Threshold is required"
        }), 400

    try:
        threshold = float(threshold)

        alarm.set_alarm(threshold)

        return jsonify({
            "message": "Alarm set successfully!",
            "threshold": threshold
        })

    except ValueError:
        return jsonify({
            "error": "Threshold must be a number"
        }), 400


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)