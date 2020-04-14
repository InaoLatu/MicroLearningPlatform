import random
import string

from django.test import TestCase

from micro_content_manager.models import Unit


class MicroContentManagerTests(TestCase):

    def test_create_units(self):

        for i in range(5):
            Unit.objects.create(id=random.randrange(10000), name=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits)))



