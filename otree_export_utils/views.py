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
from django.core.urlresolvers import reverse
import otree_export_utils.forms as forms
# END OF BLOCK

# BLOCK FOR TESTING JSON THINGS

from django.http import JsonResponse
from django.template.loader import render_to_string
from .forms import TestModelForm
from .models import TestModel


# END OF BLOCK

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
        try:
            client = get_mturk_client(use_sandbox=True)
        except NoCredentialsError:
            client = None
        if client is not None:
            try:
                balance = client.get_account_balance()['AvailableBalance']
                hits = client.list_hits()['HITs']
                print(hits[0]['HITId'])
                print(len(hits))
                # response = client.delete_hit(
                #     HITId=hits[0]['HITId']
                # )
                hits = client.list_hits()['HITs']
                print(hits[0]['HITId'])
                print(len(hits))
            except NoCredentialsError:
                print('NO CLIENT')
                balance = 'NO CLIENT'
                hits = None

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

        try:
            client = get_mturk_client(use_sandbox=True)
        except NoCredentialsError:
            client = None
            print('no credentials')
        if client is not None:
            try:
                context['assignments'] = client.list_assignments_for_hit(HITId=current_hit_id)['Assignments']
            except NoCredentialsError:
                context['assignments'] = None
                print('no credentials')
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
        print(form.cleaned_data)
        try:
            client = get_mturk_client(use_sandbox=True)
        except NoCredentialsError:
            client = None
            print('no credentials')
        if client is not None:
            try:
                sending_message = client.notify_workers(
                    Subject=form.cleaned_data['subject'],
                    MessageText=form.cleaned_data['message_text'],
                    WorkerIds=[
                        self.kwargs['worker_id'],
                    ]
                )
                print(sending_message)
            except NoCredentialsError:

                print('something is worng')
        return super().form_valid(form)


class SendBonusView(SendSomethingView):
    template_name = 'otree_export_utils/send_bonus.html'
    form_class = forms.SendBonusForm
    def form_valid(self, form):
        try:
            client = get_mturk_client(use_sandbox=True)
        except NoCredentialsError:
            client = None
            print('no credentials')
        if client is not None:
            try:
                response = client.send_bonus(
                    WorkerId=self.kwargs['worker_id'],
                    BonusAmount=str(form.cleaned_data['bonus_amount']),
                    AssignmentId=self.kwargs['AssignmentID'],
                    Reason=form.cleaned_data['reason'],
                )
                print(response)
            except NoCredentialsError:

                print('something is worng')

        return super().form_valid(form)

def testitem_create(request):
    data = dict()

    if request.method == 'POST':
        form = TestModelForm(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            books = TestModel.objects.all()
            data['html_book_list'] = render_to_string('otree_export_utils/includes/partial_book_list.html', {
                'filka': books
            })
        else:
            data['form_is_valid'] = False
    else:
        form = TestModelForm()

    context = {'form': form}
    data['html_form'] = render_to_string('otree_export_utils/includes/partial_book_create.html',
                                         context,
                                         request=request
                                         )
    return JsonResponse(data)


from django.views.generic.edit import CreateView


class TestItemCreateJson(CreateView):
    model = TestModel
    form_class = TestModelForm

    def get_success_url(self):
        """
        Overridden to ensure that JSON data gets returned, rather
        than HttpResponseRedirect, which is bad.
        """
        return None

    def form_valid(self, form):
        data = dict()
        form.save()
        data['form_is_valid'] = True
        books = TestModel.objects.all()
        data['html_book_list'] = render_to_string('otree_export_utils/includes/partial_book_list.html', {
            'filka': books
        })
        return self.render_to_response(self.get_context_data(success=True))

    def form_invalid(self, form):
        context = self.get_context_data(success=False)
        context['errors'] = form.errors
        return self.render_to_response(context)

    def render_to_response(self, context, **response_kwargs):
        data = dict()

        if self.request.method == 'POST':
            form = TestModelForm(self.request.POST)
            if form.is_valid():
                ...
            else:
                data['form_is_valid'] = False
        else:
            form = TestModelForm()

        context = {'form': form}
        data['html_form'] = render_to_string('otree_export_utils/includes/partial_book_create.html',
                                             context,
                                             request=self.request
                                             )
        return JsonResponse(data)
