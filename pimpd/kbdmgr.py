import RPi.GPIO as GPIO
import threading
import time


class KeyboardManager:
    (UP, DOWN, RIGHT, LEFT, CENTER, A, B) = (1, 2, 3, 4, 5, 6, 7)

    def __init__(self, rotated):
        if rotated:
            self._L_pin = 23
            self._R_pin = 27
            self._U_pin = 22
            self._D_pin = 17
        else:
            self._L_pin = 27
            self._R_pin = 23
            self._U_pin = 17
            self._D_pin = 22
        self._C_pin = 4
        self._A_pin = 5
        self._B_pin = 6

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._B_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._L_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._R_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._U_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._D_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._C_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self._states = {
            self.UP: self.ButtonState,
            self.DOWN: self.ButtonState,
            self.RIGHT: self.ButtonState,
            self.LEFT: self.ButtonState,
            self.CENTER: self.ButtonState,
            self.A: self.ButtonState,
            self.B: self.ButtonState
        }

        self._pins_to_buttons = {
            self._U_pin: self.UP,
            self._D_pin: self.DOWN,
            self._R_pin: self.RIGHT,
            self._L_pin: self.LEFT,
            self._C_pin: self.CENTER,
            self._A_pin: self.A,
            self._B_pin: self.B
        }

        self._thread = threading.Thread(target=self._poll)
        self._thread.setDaemon(True)

    def _update(self, state, is_pressed):
        # type: (KeyboardManager, self.ButtonState, bool) -> bool
        if is_pressed:
            state.pressed()
            return state.pressed_for == 1 or state.pressed_for > 10
        else:
            state.released()
            return False

    def _poll(self):
        while True:
            buttons_pressed = []

            for pin, button in self._pins_to_buttons:
                state = self._states[button]
                if self._update(state, not GPIO.input(pin)):
                    buttons_pressed.append(button)

            if len(buttons_pressed) > 0:
                print("buttons pressed: %s", ', '.join(map(str, buttons_pressed)))

            # todo: report

            time.sleep(0.01)

    class ButtonState:
        def __init__(self, button):
            self.button = button
            self.is_pressed = False
            self.pressed_for = 0

        def pressed(self):
            if not self.is_pressed:
                self.is_pressed = True
            else:
                self.pressed_for += 1

        def released(self):
            self.is_pressed = False
            self.pressed_for = 0
