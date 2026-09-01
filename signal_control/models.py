from django.db import models


class SignalLog(models.Model):
    """Snapshot of one lane's signal state at a point in time -- written by
    the signal_control app's detection loop (Week 5 of the roadmap)."""

    intersection_id = models.CharField(max_length=50)
    lane = models.CharField(max_length=20)
    vehicle_count = models.PositiveIntegerField(default=0)
    ambulance_detected = models.BooleanField(default=False)
    signal_state = models.CharField(
        max_length=10,
        choices=[('green', 'Green'), ('red', 'Red'), ('off', 'Off/Skipped')],
        default='red',
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.intersection_id}/{self.lane} -> {self.signal_state} @ {self.timestamp:%H:%M:%S}'
