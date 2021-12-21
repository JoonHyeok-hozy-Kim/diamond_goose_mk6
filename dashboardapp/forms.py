from django.forms import ModelForm

from dashboardapp.models import Dashboard


class DashboardCreationForm(ModelForm):
    class Meta:
        model = Dashboard
        fields = []