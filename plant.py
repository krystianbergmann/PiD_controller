"""Simple thermal plant model (first order with delay)."""


class ThermalPlant:
    def __init__(
        self,
        gain: float = 0.8,
        time_constant: float = 30.0,
        delay: float = 5.0,
        ambient: float = 20.0,
        dt: float = 0.5,
    ) -> None:
        self.gain = gain
        self.time_constant = time_constant
        self.delay_steps = max(1, int(delay / dt))
        self.ambient = ambient
        self.dt = dt
        self._pv = ambient
        self._delay_buffer: list[float] = [ambient] * self.delay_steps

    @property
    def pv(self) -> float:
        return self._pv

    def reset(self, initial_temp: float | None = None) -> None:
        temp = initial_temp if initial_temp is not None else self.ambient
        self._pv = temp
        self._delay_buffer = [temp] * self.delay_steps

    def step(self, control: float) -> float:
        delayed_u = self._delay_buffer.pop(0)
        self._delay_buffer.append(control)

        target = self.ambient + self.gain * delayed_u
        alpha = self.dt / self.time_constant
        self._pv += alpha * (target - self._pv)
        return self._pv
