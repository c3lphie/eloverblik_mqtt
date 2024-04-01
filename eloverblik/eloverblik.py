from requests import Session
from tarif import Tarif
from subscription import Subscription


class ElOverblik:
    def __init__(self, url="https://api.eloverblik.dk/customerapi/", token=""):
        if token:
            self.refresh_token = token
            self.session = Session()
            self.session.headers = {"Authorization": f"Bearer {token}"}
        else:
            raise Exception("Token not given")

        self.url = url

        self.get_data_token()

    def get_data_token(self) -> None:
        self.session.headers = {"Authorization": f"Bearer {self.refresh_token}"}
        res = self._get("api/token").json()["result"]
        self.session.headers = {"Authorization": f"Bearer {res}"}

    def _get(self, endpoint, *args, **kwargs):
        return self.session.get(self.url + endpoint, *args, **kwargs)

    def _post(self, endpoint, *args, **kwargs):
        return self.session.post(self.url + endpoint, *args, **kwargs)

    def get_meteringpointids(self) -> list[str]:
        res = self._get("api/meteringpoints/meteringpoints")
        if not res.ok:
            print(res)

        res = res.json()["result"]
        self.metering_id_list = [x["meteringPointId"] for x in res]
        return self.metering_id_list

    def get_chargedata(self):
        meterpoints = {
            "meteringPoints": {"meteringPoint": self.metering_id_list}
        }
        res = self._post(
            "api/meteringpoints/meteringpoint/getcharges", json=meterpoints
        ).json()["result"]

        return [
            {
                "tariffs": [Tarif(**y) for y in x["result"]["tariffs"]],
                "subscription": [Subscription(**y) for y in x["result"]["subscriptions"]]
            }
            for x in res
        ]
        
