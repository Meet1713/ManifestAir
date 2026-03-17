from abc import ABC, abstractmethod
from app.db import get_db

class Observer(ABC):
    @abstractmethod
    def update(self, price, provider):
        pass

class NotificationObserver(Observer):
    def update(self, price, provider, user_id, origin, dest):
        """
        Triggered when a flight price is BELOW the user's threshold.
        Saves a persistent notification to the MySQL database.
        """
        db = get_db()
        if db:
            cursor = db.cursor()
            message = f"GOOD NEWS! Flight from {origin} to {dest} dropped to ${price} on {provider}!"
            
            try:
                # Insert Notification
                cursor.execute(
                    "INSERT INTO notifications (user_id, message) VALUES (%s, %s)",
                    (user_id, message)
                )
                print(f"🔔 Alert saved for User {user_id}: {message}")
            except Exception as e:
                print(f"❌ Failed to save notification: {e}")

class PriceSubject:
    def __init__(self, watch_id, user_id, threshold, origin, dest):
        self.watch_id = watch_id
        self.user_id = user_id
        self.threshold = threshold
        self.origin = origin
        self.dest = dest
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def notify(self, current_price, provider):
        # SMART LOGIC: Only notify if price is better than threshold
        if current_price <= self.threshold:
            for observer in self._observers:
                observer.update(current_price, provider, self.user_id, self.origin, self.dest)