from django import forms

from .services import LANE_ORDER

AMBULANCE_CHOICES = [('', 'No ambulance detected')] + [(lane, lane.title()) for lane in LANE_ORDER]


class IntersectionInputForm(forms.Form):
    """Standing in for the vehicle-counting model's output."""

    intersection_id = forms.CharField(initial='Main Square', max_length=50)
    north_count = forms.IntegerField(min_value=0, initial=0, label='North lane - vehicle count')
    south_count = forms.IntegerField(min_value=0, initial=0, label='South lane - vehicle count')
    east_count = forms.IntegerField(min_value=0, initial=0, label='East lane - vehicle count')
    west_count = forms.IntegerField(min_value=0, initial=0, label='West lane - vehicle count')
    ambulance_lane = forms.ChoiceField(choices=AMBULANCE_CHOICES, required=False)

    def get_lane_counts(self):
        return {
            'north': self.cleaned_data['north_count'],
            'south': self.cleaned_data['south_count'],
            'east': self.cleaned_data['east_count'],
            'west': self.cleaned_data['west_count'],
        }