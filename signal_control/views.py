import json

from django.shortcuts import render

from accounts.decorators import admin_required
from .forms import IntersectionInputForm
from .models import SignalLog
from .services import compute_cycle, decide_signal_states


@admin_required
def signal_simulator(request):
    """Admin-only page to run the intersection decision logic -- placeholder
    for what the vehicle-counting detection model will eventually feed in
    automatically (Week 5 of the roadmap)."""
    result = None
    cycle = []
    if request.method == 'POST':
        form = IntersectionInputForm(request.POST)
        if form.is_valid():
            lane_counts = form.get_lane_counts()
            ambulance_lane = form.cleaned_data['ambulance_lane'] or None
            result = decide_signal_states(
                intersection_id=form.cleaned_data['intersection_id'],
                lane_counts=lane_counts,
                ambulance_lane=ambulance_lane,
            )
            cycle = compute_cycle(lane_counts, ambulance_lane)
    else:
        form = IntersectionInputForm()

    recent_logs = SignalLog.objects.order_by('-timestamp')[:20]
    return render(request, 'signal_control/simulator.html', {
        'form': form, 'result': result, 'recent_logs': recent_logs,
        'cycle_json': json.dumps(cycle),
    })