from django.conf import urls
from otree_export_utils.views import SpecificSessionDataView
from otree_export_utils.views import TestItemCreateJson, AssignmentListView, SendBonusView, SendMessageView

urlpatterns = [
    urls.url(r'^session_data/(?P<session_code>.*)/(?P<filetype>.*)/$', SpecificSessionDataView.as_view(),
             name='session_data'),
    urls.url(r'^HIT/(?P<HITId>.*)/assignments/$', AssignmentListView.as_view(), name='assignments_list'),
    urls.url(r'^HIT/(?P<HITId>.*)/assignment/(?P<AssignmentID>.*)/worker/(?P<worker_id>.*)/send_bonus/$', SendBonusView.as_view(), name='send_bonus'),
    urls.url(r'^HIT/(?P<HITId>.*)/assignment/(?P<AssignmentID>.*)/worker/(?P<worker_id>.*)/send_message/$', SendMessageView.as_view(), name='send_message'),
    urls.url(r'^test_items/create/$', TestItemCreateJson.as_view(), name='testitem_create'),
]
print(urlpatterns)
