from otree.views.export import get_export_response
import vanilla
from .export import export_wide
from otree.models import Session
from django.shortcuts import render


class SpecificSessionDataView(vanilla.TemplateView):
    def get(self, request, *args, **kwargs):
        session_code = kwargs['session_code']
        response, file_extension = get_export_response(
            request, session_code)
        export_wide(response, file_extension, session_code=session_code)
        return response


class AllSessionsList(vanilla.TemplateView):
    template_name = 'otree_export_utils/all_session_list.html'
    url_name = 'individual_sessions_export'
    url_pattern = r'^individual_sessions_export/$'
    display_name = 'Exporting data from individual sessions'

    def get(self, request, *args, **kwargs):
        all_sessions = Session.objects.all()
        return render(request, self.template_name, {'sessions': all_sessions})
