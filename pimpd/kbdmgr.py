import RPi.GPIO as GPIO
import threading
import time


class KeyboardManager:
    (UP, DOWN, RIGHT, LEFT, CENTER, A, B) = (1, 2, 3, 4, 5, 6, 7)

    # keyboard poll interval in seconds
    POLL_INTERVAL = 0.03
    # how many poll intervals to wait before registering first keypress
    FIRST_PRESS_CNT = 1
    # how many poll intervals to wait before registering subsequent keypresses
    REPEAT_CNT = 10
    # how often to report key presses after REPEAT_CNT is reached
    REPEAT_EVERY = 3

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

        self._states = {
            self.UP: self.ButtonState('up'),
            self.DOWN: self.ButtonState('down'),
            self.RIGHT: self.ButtonState('right'),
            self.LEFT: self.ButtonState('left'),
            self.CENTER: self.ButtonState('center'),
            self.A: self.ButtonState('a'),
            self.B: self.ButtonState('b')
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

        self._callbacks = []

        self._stop = False
        self._stopmon = threading.Condition()

        self._thread = threading.Thread(target=self._poll)
        self._thread.setDaemon(True)
        self._thread.start()

    def add_callback(self, callback):
        self._callbacks.append(callback)

    def remove_callback(self, callback):
        self._callbacks.remove(callback)

    def stop(self):
        self._stopmon.acquire()
        self._stop = True
        self._stopmon.wait()
        self._stopmon.release()

    def _update(self, state, is_pressed):
        # type: (KeyboardManager, self.ButtonState, bool) -> bool
        if is_pressed:
            state.pressed()
            return state.pressed_for == self.FIRST_PRESS_CNT or (
                        state.pressed_for > self.REPEAT_CNT and
                        state.pressed_for % self.REPEAT_EVERY == 0
                    )
        else:
            state.released()
            return False

    def _poll(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._B_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._L_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._R_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._U_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._D_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._C_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        prev_buttons_pressed = []

        while not self._stop and GPIO is not None:
            buttons_pressed = []

            for pin, button in self._pins_to_buttons.items():
                state = self._states[button]
                if self._update(state, not GPIO.input(pin)):
                    buttons_pressed.append(button)

            if 0 < len(buttons_pressed) < len(prev_buttons_pressed):
                # force release all buttons
                buttons_pressed = []
                for state in self._states.values():
                    state.released()

            if len(buttons_pressed) > 0:
                for callback in self._callbacks:
                    if callback(buttons_pressed):
                        break

            prev_buttons_pressed = buttons_pressed

            time.sleep(self.POLL_INTERVAL)

        if GPIO is not None:
            GPIO.cleanup()
        self._stopmon.acquire()
        self._stopmon.notifyAll()
        self._stopmon.release()

    class ButtonState:
        def __init__(self, name):
            self._name = name
            self.is_pressed = False
            self.pressed_for = 0

        def pressed(self):
            if not self.is_pressed:
                self.is_pressed = True
            else:
                self.pressed_for += 1
            #print(self._name, ': ', self.is_pressed, ': ', self.pressed_for)

        def released(self):
            self.is_pressed = False
            self.pressed_for = 0
            #if self._name == 'up':
            #    print(self._name, ': released..')
