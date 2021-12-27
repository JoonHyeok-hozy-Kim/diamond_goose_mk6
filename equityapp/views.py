from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.edit import FormMixin, DeleteView

from assetmasterapp.models import Asset
from equityapp.decorators import equity_ownership_required
from equityapp.forms import EquityCreationForm, EquityTransactionCreationForm
from equityapp.models import Equity, EquityTransaction
from portfolioapp.models import Portfolio

has_equity_ownership = [login_required, equity_ownership_required]


class EquityCreateView(CreateView):
    model = Equity
    form_class = EquityCreationForm
    context_object_name = 'target_equity'
    template_name = 'equityapp/equity_create.html'

    def form_valid(self, form):
        temp_equity = form.save(commit=False)
        temp_equity.owner = self.request.user
        temp_equity.asset = Asset.objects.get(pk=self.request.POST['asset_pk'])
        temp_equity.portfolio = Portfolio.objects.get(owner=self.request.user)
        temp_equity.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('equityapp:equity_detail', kwargs={'pk':self.object.asset.pk})


@method_decorator(has_equity_ownership, 'get')
class EquityDetailView(DetailView, FormMixin):
    model = Equity
    form_class = EquityTransactionCreationForm
    context_object_name = 'target_equity'
    template_name = 'equityapp/equity_detail.html'

    def get_context_data(self, **kwargs):
        # Update Asset's current price
        self.object.asset.update_current_price()
        self.object.asset.refresh_from_db()

        # Update Equity's stats
        self.object.update_equity_data()
        self.object.refresh_from_db()

        context = super(EquityDetailView, self).get_context_data(**kwargs)

        my_portfolio_scalar_query = Portfolio.objects.filter(owner=self.request.user).values()
        if my_portfolio_scalar_query:
            for my_portfolio in my_portfolio_scalar_query:
                my_portfolio_pk = my_portfolio['id']
                target_user_id = my_portfolio['owner_id']
            context.update({'my_portfolio_pk': my_portfolio_pk})
            context.update({'target_user_id': target_user_id})

            my_equity_scalar_query = Equity.objects.filter(asset=self.object.pk,
                                                           portfolio=my_portfolio_pk,
                                                           owner=self.request.user).values()
            if my_equity_scalar_query:
                for my_equity in my_equity_scalar_query:
                    my_equity_pk = my_equity['id']
                context.update({'my_equity_pk': my_equity_pk})

        return context


@method_decorator(has_equity_ownership, 'get')
class EquityListView(ListView):
    model = Equity
    context_object_name = 'target_equity_list'
    template_name = 'equityapp/equity_list.html'


class EquityTransactionCreateView(CreateView):
    model = EquityTransaction
    form_class = EquityTransactionCreationForm
    template_name = 'equityapp/equitytransaction_create.html'

    def form_valid(self, form):
        temp_transaction = form.save(commit=False)
        temp_transaction.equity = Equity.objects.get(pk=self.request.POST['equity_pk'])
        temp_transaction.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('equityapp:equity_detail', kwargs={'pk': self.object.equity.pk})


class EquityTransactionListView(ListView):
    model = EquityTransaction
    context_object_name = 'equity_transaction_list'
    template_name = 'equityapp/equitytransaction_list.html'


class EquityTransactionDeleteView(DeleteView):
    model = EquityTransaction
    context_object_name = 'target_equity_transaction'
    template_name = 'equityapp/equitytransaction_delete.html'

    def get_success_url(self):
        return reverse('equityapp:equity_detail', kwargs={'pk': self.object.equity.pk})


def equitytransaction_export_csv_template(request):
    import csv

    equity_pk = request.POST['equity_pk']

    if request.method == 'POST':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="equitytransaction_csv_template.csv"'
        writer = csv.writer(response)
        # Column Insert
        writer.writerow([
            'transaction_type',
            'quantity',
            'price',
            'transaction_fee',
            'transaction_tax',
            'transaction_date',
            'note',
        ])
        # Sample Line Insert
        writer.writerow([
            'BUY',
            '1',
            '100',
            '1',
            '2',
            '1993-04-27 04:00:00',
            'Sample Format',
        ])

        return response

    return reverse('equityapp:equity_detail', kwargs={'pk': equity_pk})


def equitytransaction_import_csv(request):
    import os
    import datetime
    import pandas as pd

    from django.core.files.storage import FileSystemStorage
    from django.conf import settings
    from django.utils.timezone import make_aware

    equity_pk = request.POST['equity_pk']

    try:
        if request.method == 'POST' and request.FILES['transaction_file']:

            transaction_file = request.FILES['transaction_file']
            save_dir = os.path.join(settings.MEDIA_ROOT, 'equity_transaction_csv')
            fs = FileSystemStorage(location=save_dir)
            file_name = fs.save(transaction_file.name, transaction_file)
            new_dir = 'equity_transaction_csv/' + file_name

            uploaded_file_url = fs.url(new_dir)
            excel_file = uploaded_file_url
            excel_transaction_data = pd.read_csv("."+excel_file, encoding='utf-8')
            db_frame = excel_transaction_data

            for db_frame in db_frame.itertuples():

                # transaction_date input data make_aware
                try:
                    naive_datetime = datetime.datetime.strptime(db_frame.transaction_date, "%Y-%m-%d %H:%M:%S")
                except Exception as datetime_format_exception1:
                    print('datetime_format_exception1 : ', datetime_format_exception1)
                    try:
                        naive_datetime = datetime.datetime.strptime(db_frame.transaction_date, "%Y-%m-%d %H:%M")
                    except Exception as datetime_format_exception2:
                        print('datetime_format_exception2 : ', datetime_format_exception2)
                        exit()

                aware_datetime = make_aware(naive_datetime)

                # import_transaction_data = [
                #     str(db_frame.transaction_type),
                #     str(db_frame.quantity),
                #     str(db_frame.price),
                #     str(db_frame.transaction_fee),
                #     str(db_frame.transaction_tax),
                #     str(aware_datetime),
                #     str(db_frame.note),
                # ]
                # print(','.join(import_transaction_data))

                obj = EquityTransaction.objects.create(
                    equity=Equity.objects.get(pk=equity_pk),
                    transaction_type=db_frame.transaction_type,
                    quantity=db_frame.quantity,
                    price=db_frame.price,
                    transaction_fee=db_frame.transaction_fee,
                    transaction_tax=db_frame.transaction_tax,
                    transaction_date=aware_datetime,
                    note=db_frame.note
                )

                obj.save()

            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(reverse('equityapp:equity_detail', kwargs={'pk':equity_pk}))
    except Exception as identifier:
        print(identifier)

    return reverse('equityapp:equity_detail', kwargs={'pk':equity_pk})