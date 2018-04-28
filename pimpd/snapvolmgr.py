from volmgr import VolumeManager
import requests
import json


# unfinished attempt at controlling snapcast
# it doesn't provide http interface (https://github.com/badaix/snapcast/issues/109)
# and python implementation (python-snapclient) only supports python 3.0
class SnapcastVolumeManager(VolumeManager):
    def __init__(self, client_id, host, port=1705):
        self._client_id = client_id
        self._host = host
        self._port = port
        self._id = 0

    def _get_id(self):
        id = self._id
        self._id += 1
        return id

    @property
    def volume(self):
        id = self._get_id()
        url = 'http://{}:{}'.format(self._host, self._port)
        headers = {'content-type': 'application/json'}
        payload = {
            'id': id,
            'method': 'Client.GetStatus',
            'jsonrpc': '2.0',
            'params': {
                'id': self._client_id
            }
        }

        try:
            response = requests.post(
                url, timeout=5, data=json.dumps(payload), headers=headers).json()

            print(response)
            return 0
        except requests.exceptions.ReadTimeout as e:
            print(e)
            return 0

