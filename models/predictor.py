import os
import joblib
from sklearn.ensemble import RandomForestClassifier


class StockPredictor:

    def __init__(self):

        self.model_path = "stock_model.pkl"

        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        else:
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=42
            )

    def train(self, data):

        data = data.copy()

        data["target"] = (
            data["close"].shift(-1) > data["close"]
        ).astype(int)

        data = data.dropna()

        features = data[
            [
                "moving_average",
                "volatility",
                "upper_band",
                "lower_band",
                "rsi"
            ]
        ]

        target = data["target"]

        if not os.path.exists(self.model_path):
            self.model.fit(features, target)
            joblib.dump(self.model, self.model_path)

    def predict(self, data):

        latest = data[
            [
                "moving_average",
                "volatility",
                "upper_band",
                "lower_band",
                "rsi"
            ]
        ].tail(1)

        prediction = self.model.predict(latest)[0]

        probability = self.model.predict_proba(latest)[0]

        confidence = round(float(max(probability)) * 100, 2)

        current_price = float(data["close"].iloc[-1])
        moving_average = float(data["moving_average"].iloc[-1])
        rsi = float(data["rsi"].iloc[-1])

        if prediction == 1:
            signal = "BUY"
        else:
            signal = "SELL"

        if confidence < 60:
            signal = "HOLD"

        if signal == "BUY":
            tomorrow_price = round(current_price * 1.015, 2)
        elif signal == "SELL":
            tomorrow_price = round(current_price * 0.985, 2)
        else:
            tomorrow_price = round(current_price, 2)

        estimated_low = round(current_price * 0.97, 2)
        estimated_high = round(current_price * 1.03, 2)

        if confidence >= 80:
            risk = "Low"
        elif confidence >= 60:
            risk = "Medium"
        else:
            risk = "High"

        reason = []

        if rsi < 30:
            reason.append("RSI indicates the stock is oversold.")
        elif rsi > 70:
            reason.append("RSI indicates the stock is overbought.")
        else:
            reason.append("RSI is in the normal range.")

        if current_price > moving_average:
            reason.append("Price is above the moving average.")
        else:
            reason.append("Price is below the moving average.")

        return {
            "signal": signal,
            "confidence": confidence,
            "current_price": round(current_price, 2),
            "tomorrow_price": tomorrow_price,
            "estimated_range": f"{estimated_low} - {estimated_high}",
            "risk": risk,
            "reason": " ".join(reason)
        }