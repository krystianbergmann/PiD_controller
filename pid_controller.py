"""PID controller with output clamping and anti-windup."""


class PIDController:
    def __init__(
        self,
        kp: float,
        ki: float,
        kd: float,
        u_min: float = 0.0,
        u_max: float = 100.0,
    ) -> None:
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.u_min = u_min
        self.u_max = u_max
        self._integral = 0.0
        self._prev_error = 0.0

    def reset(self) -> None:
        self._integral = 0.0
        self._prev_error = 0.0

    def step(self, setpoint: float, pv: float, dt: float) -> float:
        error = setpoint - pv
        self._integral += error * dt
        derivative = (error - self._prev_error) / dt if dt > 0 else 0.0
        self._prev_error = error

        u = self.kp * error + self.ki * self._integral + self.kd * derivative
        u_clamped = max(self.u_min, min(self.u_max, u))

        if u != u_clamped:
            self._integral -= error * dt

        return u_clamped
