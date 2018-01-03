from otree.views.export import get_export_response
import vanilla
from .export import export_wide
from otree.models import Session
from django.shortcuts import render

# BLOCK FOR MTURK HITS
from django.conf import settings
from otree.views.mturk import get_mturk_client
from botocore.exceptions import NoCredentialsError
import json
from django.core.urlresolvers import reverse, reverse_lazy
import otree_export_utils.forms as forms
from django.http import JsonResponse, HttpResponseRedirect
# END OF BLOCK

# BLOCK FOR TESTING JSON THINGS

from django.http import JsonResponse
from django.template.loader import render_to_string
from .forms import (UpdateExpirationForm)

# END OF BLOCK

from contextlib import contextmanager


@contextmanager
def mturkclient(use_sandbox=True):
    try:
        yield get_mturk_client(use_sandbox=use_sandbox)
    except NoCredentialsError:

        return


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
        from .models import TestModel
        newtest = TestModel()
        newtest.title = 'asdf'
        newtest.myf = 'kuku'
        newtest.save()
        all_sessions = Session.objects.all()
        return render(request, self.template_name, {'sessions': all_sessions})


class HitsList(vanilla.TemplateView):
    template_name = 'otree_export_utils/hits_list.html'
    url_name = 'hits_list'
    url_pattern = r'^hits_list/$'
    display_name = 'mTurk HITs'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        with mturkclient() as client:
            if client is not None:
                balance = client.get_account_balance()['AvailableBalance']
                hits = client.list_hits()['HITs']
                context['balance'] = balance
                context['hits'] = hits
        return context


class AssignmentListView(vanilla.TemplateView):
    template_name = 'otree_export_utils/assignments_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_hit_id = self.kwargs['HITId']
        print(current_hit_id)
        context['current_hit_id'] = current_hit_id
        with mturkclient() as client:
            if client is not None:
                context['assignments'] = client.list_assignments_for_hit(HITId=current_hit_id)['Assignments']
        return context


class SendSomethingView(vanilla.FormView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['worker_id'] = self.kwargs['worker_id']
        context['current_hit_id'] = self.kwargs['HITId']
        return context

    def get_success_url(self):
        return reverse('assignments_list', kwargs={'HITId': self.kwargs['HITId']})


class SendMessageView(SendSomethingView):
    form_class = forms.SendMessageForm
    template_name = 'otree_export_utils/send_message.html'

    def form_valid(self, form):
        with mturkclient() as client:
            if client is not None:
                sending_message = client.notify_workers(
                    Subject=form.cleaned_data['subject'],
                    MessageText=form.cleaned_data['message_text'],
                    WorkerIds=[
                        self.kwargs['worker_id'],
                    ]
                )
        return super().form_valid(form)


class SendBonusView(SendSomethingView):
    template_name = 'otree_export_utils/send_bonus.html'
    form_class = forms.SendBonusForm

    def form_valid(self, form):
        with mturkclient() as client:
            if client is not None:
                response = client.send_bonus(
                    WorkerId=self.kwargs['worker_id'],
                    BonusAmount=str(form.cleaned_data['bonus_amount']),
                    AssignmentId=self.kwargs['AssignmentID'],
                    Reason=form.cleaned_data['reason'],
                )
                print(response)
        return super().form_valid(form)


class DeleteHitView(vanilla.TemplateView):
    def get(self, request, *args, **kwargs):
        response = JsonResponse({'foo': 'bar'})
        return response

    def render_to_response(self, context, **response_kwargs):
        data = super().render_to_response(context, **response_kwargs)
        print(data)
        return JsonResponse(data)


class UpdateExpirationView(vanilla.FormView):
    form_class = UpdateExpirationForm
    template_name = 'otree_export_utils/update_expiration.html'
    success_url = reverse_lazy('hits_list')

    # def get_success_url(self):
    #     return

    def form_valid(self, form):
        print('AAAA', form.cleaned_data['expire_time'])
        with mturkclient() as client:
            if client is not None:
                response = client.update_expiration_for_hit(
                    HITId=self.kwargs['HITId'],
                    ExpireAt=form.cleaned_data['expire_time']
                )
                print(response)
        return super().form_valid(form)


from datetime import datetime, timedelta


class ExpireHitView(vanilla.View):
    def get(self, request, *args, **kwargs):
        d = datetime.today() - timedelta(days=1)
        with mturkclient() as client:
            if client is not None:
                response = client.update_expiration_for_hit(
                    HITId=self.kwargs['HITId'],
                    ExpireAt=d
                )
                print(response)
        return HttpResponseRedirect(reverse('hits_list'))


class AjaxUpdateExpirationView(vanilla.FormView):
    form_class = UpdateExpirationForm

    def get_success_url(self):
        return None

    def get(self, request, *args, **kwargs):
        response = JsonResponse({'foo': 'bar'})
        return response

    def render_to_response(self, context, **response_kwargs):
        data = super().render_to_response()
        return JsonResponse(data)


class ApproveAssignmentView(vanilla.FormView):
    form_class = forms.ApproveAssignmentForm
    template_name = 'otree_export_utils/approve_assignment.html'
    success_url = reverse_lazy('hits_list')

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        with mturkclient() as client:
            if client is not None:
                response = client.approve_assignment(
                    AssignmentId=self.kwargs['AssignmentID'],
                    RequesterFeedback=form.cleaned_data['message_text'],
                    OverrideRejection=True,
                )
                print(response)
        return super().form_valid(form)


class RejectAssignmentView(vanilla.FormView):
    form_class = forms.RejectAssignmentForm
    template_name = 'otree_export_utils/reject_assignment.html'
    success_url = reverse_lazy('hits_list')

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)
