from django.forms import widgets, ModelForm, ModelChoiceField, RadioSelect
from pensionapp.models import Pension, PensionTransaction, PENSION_TRANSACTION_TYPES, PensionAsset


class PensionCreationForm(ModelForm):
    class Meta:
        model = Pension
        fields = ['pension_type', 'risk_ratio_force_flag']


class PensionTransactionCreationForm(ModelForm):
    class Meta:
        model = PensionTransaction
        fields = ['transaction_type', 'amount', 'transaction_date']
        widgets = {
            'transaction_date': widgets.DateTimeInput(attrs={'type':'date'}),
        }


class PensionAssetCreationForm(ModelForm):
    class Meta:
        model = PensionAsset
        fields = []
        # fields = ['pension']
        #
        # radio_select_instance = widgets.RadioSelect()
        # pension_queryset = Pension.objects.all()
        # PENSION_CHOICE = []
        # for pension in pension_queryset:
        #     radio_select_instance.id_for_label(pension.pension_type, pension.pk)
        # widgets = {
        #     'pension': radio_select_instance
        # }