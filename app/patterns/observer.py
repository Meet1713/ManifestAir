from abc import ABC, abstractmethod
from app.db import get_db


class Observer(ABC):

    @abstractmethod
    def update(self, price, provider):
        pass


class NotificationObserver(Observer):

    def update(self, price, provider, user_id, origin, dest):
        """
        Triggered when a flight price goes below the threshold.
        Stores notification in the database
        """

        db = get_db()

        if db != None:
            cursor = db.cursor()

            msg = f"GOOD NEWS! Flight from {origin} to {dest} dropped to ${price} on {provider}!"

            try:
                cursor.execute(
                    "INSERT INTO notifications (user_id, message) VALUES (%s, %s)",
                    (user_id, msg)
                )

                print(f"Notification created for user {user_id}")

            except Exception as e:
                print("Error while inserting notification", e)


class PriceSubject:

    def __init__(self, watch_id, user_id, threshold, origin, dest):
        self.watch_id = watch_id
        self.user_id = user_id
        self.threshold = threshold
        self.origin = origin
        self.dest = dest
        self._observers = []
        self.last_price = None   # unused variable (minor dev artifact)

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def notify(self, current_price, provider):

        # simple logic to check threshold
        if current_price <= self.threshold:

            for obs in self._observers:
                obs.update(
                    current_price,
                    provider,
                    self.user_id,
                    self.origin,
                    self.dest
                )