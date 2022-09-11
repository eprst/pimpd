import time
import logging
import asyncio

import keyboardmanager
import screenmanager


class Dimmer(object):
    def __init__(self,
                 screen_manager: screenmanager.ScreenManager,
                 keyboard_manager: keyboardmanager.KeyboardManager,
                 dim_after: int,
                 off_after: int,
                 pass_through_buttons: [int]) -> None:
        self._dim_after = dim_after
        self._off_after = off_after
        self._smgr = screen_manager
        self._pass_through_buttons = pass_through_buttons
        self._last_activity = time.time()

        self._dimmed = False
        self._off = False

        keyboard_manager.add_callback(self._on_kbd)
        self._update_task = asyncio.create_task(self._loop())

    async def _loop(self):
        try:
            while True:
                await asyncio.sleep(1)
                sla = time.time() - self._last_activity

                if self._dim_after is not None and sla > self._dim_after and not self._dimmed:
                    logging.info("Dimmer: dimming")
                    self._smgr.dim()
                    self._dimmed = True

                if self._off_after is not None and sla > self._off_after and not self._off:
                    logging.info("Dimmer: screen off")
                    self._smgr.screen_off()
                    self._dimmed = False
                    self._off = True
        except asyncio.CancelledError:
            pass

    async def _on_kbd(self, buttons):
        self._last_activity = time.time()
        processed = False
        logging.info("Dimmer::on_kbd, off:{}, dimmed:{}".format(self._off, self._dimmed))
        if self._off:
            logging.info("Dimmer: screen on")
            self._smgr.screen_on()
            self._off = False
            processed = len(buttons) == 1 and buttons[0] not in self._pass_through_buttons
        if self._dimmed:
            logging.info("Dimmer: un-dimming")
            self._smgr.undim()
            self._dimmed = False
            processed = len(buttons) == 1 and buttons[0] not in self._pass_through_buttons

        return processed
