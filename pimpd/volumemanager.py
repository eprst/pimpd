class VolumeManager(object):
    @property
    async def volume(self) -> int:
        return 0

    async def set_volume(self, volume: int) -> None:
        pass
