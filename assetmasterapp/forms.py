from django.forms import ModelForm

from assetmasterapp.models import Asset


class AssetCreationForm(ModelForm):
    class Meta:
        model = Asset
        fields = ['asset_type','market', 'ticker', 'name', 'currency', 'image']
