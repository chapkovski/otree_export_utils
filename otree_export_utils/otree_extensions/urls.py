from django.conf.urls import url
from otree_export_utils.views import SpecificSessionDataView
from otree_export_utils.views import ( AssignmentListView, SendBonusView, SendMessageView,
                                      UpdateExpirationView, DeleteHitView,ExpireHitView,
                                       ApproveAssignmentView,RejectAssignmentView )

urlpatterns = [
    url(r'^session_data/(?P<session_code>.*)/(?P<filetype>.*)/$', SpecificSessionDataView.as_view(),
             name='session_data'),
    url(r'^HIT/(?P<HITId>.*)/assignments/$', AssignmentListView.as_view(), name='assignments_list'),
    url(r'^HIT/(?P<HITId>.*)/delete/$', DeleteHitView.as_view(), name='delete_hit'),
    url(r'^HIT/(?P<HITId>.*)/change_expiration/$', UpdateExpirationView.as_view(), name='change_expiration'),
    url(r'^HIT/(?P<HITId>.*)/expire/$', ExpireHitView.as_view(), name='expire_hit'),
    url(r'^HIT/(?P<HITId>.*)/assignment/(?P<AssignmentID>.*)/worker/(?P<worker_id>.*)/send_bonus/$',
        SendBonusView.as_view(), name='send_bonus'),
    url(r'^HIT/(?P<HITId>.*)/assignment/(?P<AssignmentID>.*)/worker/(?P<worker_id>.*)/send_message/$',
        SendMessageView.as_view(), name='send_message'),
    url(r'^assignment/(?P<AssignmentID>.*)/approve/$',
        ApproveAssignmentView.as_view(), name='approve_assignment'),
    url(r'^assignment/(?P<AssignmentID>.*)/reject/$',
        RejectAssignmentView.as_view(), name='reject_assignment'),

]
print(urlpatterns)

