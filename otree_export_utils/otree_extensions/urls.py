from django.conf import urls
from otree_export_utils.views import SpecificSessionDataView

urlpatterns = [
    urls.url(r'^session_data/(?P<session_code>.*)/(?P<filetype>.*)/$', SpecificSessionDataView.as_view(), name='session_data')
]
print(urlpatterns)