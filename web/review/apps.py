from django.apps import AppConfig
from better_profanity import profanity


class ReviewConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'review'

    def ready(self):
        profanity.load_censor_words()