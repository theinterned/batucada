from django_nose.runner import NoseTestSuiteRunner

from django.conf import settings


class DrumbeatTestRunner(NoseTestSuiteRunner):

    def run_tests(self, test_labels, extra_tests=None):
        settings.CELERY_ALWAYS_EAGER = True
        return super(DrumbeatTestRunner, self).run_tests(
            test_labels, extra_tests)
