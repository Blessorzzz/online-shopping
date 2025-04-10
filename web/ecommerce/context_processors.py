from django.conf import settings

def currency_context(request):
    lang = request.LANGUAGE_CODE
    config = settings.LANGUAGE_CURRENCY_MAP.get(lang, {'symbol': '¥', 'rate': 1})
    return {
        'currency_symbol': config['symbol'],
        'currency_rate': config['rate'],
    }
