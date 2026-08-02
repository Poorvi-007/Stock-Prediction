class Alarm:
    def __init__(self):
        self.threshold = None
        self.last_signal = None

    def set_alarm(self, threshold):
        self.threshold = threshold

    def check_alarm(self, prediction):
        signal = prediction["signal"]
        current_price = prediction["current_price"]

        # Alert if signal changed
        if self.last_signal is not None and self.last_signal != signal:
            print(f"🚨 ALERT: Signal changed to {signal}")

        self.last_signal = signal

        # Alert if target price reached
        if self.threshold is not None:
            if current_price >= self.threshold:
                print(f"🔔 ALERT: Target price ₹{self.threshold} reached!")

        return True