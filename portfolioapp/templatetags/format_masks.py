from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.text import Truncator

register = template.Library()


def currency_usd(amount):
    amount = round(float(amount), 2)
    return "$%s%s" % (intcomma(int(amount)), ("%0.2f" % amount)[-3:])


def currency_krw(amount):
    amount = round(float(amount))
    return "￦%s" % (intcomma(int(amount)))


def percentage_rate_format(amount):
    amount = round(float(amount*100), 2)
    result = "%s%s" % (intcomma(int(amount)), ("%0.2f" % amount)[-3:])
    result += '%'
    return result

def asset_name_omit(asset_name):
    return Truncator(asset_name).chars(25)

register.filter('currency_usd', currency_usd)
register.filter('currency_krw', currency_krw)
register.filter('percentage_rate_format', percentage_rate_format)
register.filter('asset_name_omit', asset_name_omit)
register.filter('intcomma', intcomma)