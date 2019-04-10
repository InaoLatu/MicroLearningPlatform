from typing import List

import null as null
import request as request
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import generic
from pymongo import MongoClient
from tagging.models import Tag, TaggedItem
from tagging.utils import LOGARITHMIC, LINEAR
from tagging.utils import calculate_cloud
from tagging.models import TagManager


from micro_content_manager.forms import MicroContentEditForm
from micro_content_manager.models import MicroLearningContent, Question, Choice
from micro_content_manager.models import Tag as MicroContentTag
from django.http import Http404, JsonResponse, HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.utils.datastructures import MultiValueDictKeyError
import pymongo

NUMBER_PARAGRAPHS = 1
NUMBER_QUESTIONS = 3
NUMBER_CHOICES = 3
NUMBER_VIDEOS = 1

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = 'tfg'
COLLECTION_NAME = 'micro_content_manager_microlearningcontent'


class CreateSelectionView(generic.TemplateView):
    template_name = 'micro_content_manager/create_selection.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'micro_content_manager/create_selection.html')


class MicroContentCreationView(generic.CreateView):
    success_url = reverse_lazy('auth_tool:index')
    template_name = 'micro_content_manager/create.html'

    def get(self, request, *args, **kwargs):
        NUMBER_QUESTIONS = kwargs['q']
        return render(request, 'micro_content_manager/create.html', {'paragraphs': ' ' * NUMBER_PARAGRAPHS,
                                                                     'videos': ' ' * kwargs['v'],
                                                                     'questions': ' ' * kwargs['q'],
                                                                     'nQuestions': kwargs['q'],
                                                                     'choices': ' ' * NUMBER_CHOICES})

class DoTheMicroContentView(generic.DetailView):
    template_name = 'micro_content_manager/do_the_micro_content.html'

    def get(self, request, *args, **kwargs):
        micro_content = MicroLearningContent.objects.get(pk=kwargs['id'])

        return render(request, 'micro_content_manager/do_the_micro_content.html', {"micro_content": micro_content})


class MicroContentInfoView(generic.DetailView):
    template_name = 'micro_content_manager/micro_content_info.html'

    def get(self, request, *args, **kwargs):
        micro_content = MicroLearningContent.objects.get(pk=kwargs['id'])
        mc_t = Tag.objects.get_for_object(micro_content).values_list('name', flat=True)
        mc_tags: List[str] = []
        for tag in mc_t:
            mc_tags.append(str(tag))
        mc_text = micro_content.getText(self.request)
        connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
        collection = connection[DB_NAME][COLLECTION_NAME]

        return render(request, 'micro_content_manager/micro_content_info.html', {'micro_content': micro_content,
                                                                                 'mc_tags': mc_tags,
                                                                                 'number_tags': len(mc_tags),
                                                                                 'mc_text': mc_text,
                                                                                 })

class MicroContentSearchView(generic.DetailView):
    template_name = 'micro_content_manager/mc_search.html'

    def get(self, request, *args, **kwargs):
        list = MicroLearningContent.objects.all()
        list_result = {}
        for mc in list:
            list_result.update({mc.id: [mc.title, mc.meta_data.author]})

        return render(request, 'micro_content_manager/mc_search.html', {"list_result": list_result})

    def post(self, request):
        micro_contents_search = self.request.POST['search']
        searchIn = self.request.POST['searchIn']
        micro_contents_search = micro_contents_search.split()
        list = MicroLearningContent.objects.all()
        list_result = {}


        for mc in list:
            mc_tags: List[str] = []
            mc_queryset = mc.mc_tags.all()
            for tag in mc_queryset:
                mc_tags.append(str(tag))
            if bool(set(micro_contents_search) & set(mc_tags)):
                if searchIn == "all":
                    list_result.update({mc.id: [mc.title, mc.meta_data.author]})
                else:
                    if request.user == mc.meta_data.author:
                        list_result.update({mc.id: {mc.title, mc.meta_data.author}})

        return render(self.request, 'micro_content_manager/mc_search.html', {"list_result": list_result})


def index(request):
    contents = [(e.id, e.title) for e in MicroLearningContent.objects.all()]
    return render(request, 'micro_content_manager/index.html', {'contents': contents})


def json(request):
    try:
        content = MicroLearningContent.objects.get(pk=request.GET['content'])
        return JsonResponse(content.toDict())
    except (MicroLearningContent.DoesNotExist, MultiValueDictKeyError):
        raise Http404()


class MicroContentEditView(generic.FormView):
    template_name = 'micro_content_manager/edit.html'
    form = MicroContentEditForm

    def get(self, request, *args, **kwargs):
        try:
            content = MicroLearningContent.objects.get(pk=kwargs['pk'])
        except (MicroLearningContent.DoesNotExist, MultiValueDictKeyError):
            raise Http404()
        mc_t = Tag.objects.get_for_object(MicroLearningContent.objects.get(pk=kwargs['pk'])).values_list('name', flat=True)
        mc_tags = ""
        for tag in mc_t:
            mc_tags = mc_tags + " " + str(tag)
        return render(request, 'micro_content_manager/edit.html', {"content": content,
                                                                   "id": kwargs['pk'],
                                                                   "mc_tags": mc_tags})

    def form_valid(self, form):
        form = MicroContentEditForm(self.request.POST)
        try:
            MicroLearningContent.objects.get(pk=self.request.POST['id'])
        except MicroLearningContent.DoesNotExist:
            raise Http404
        content = MicroLearningContent.objects.get(pk=self.request.POST['id'])

        tags = self.request.POST['mc_tags']
        tag_args = tags.split()
        content.mc_tags.clear()
        for tag in tag_args:
            if MicroContentTag.objects.filter(name=tag).count() > 0:
                content.mc_tags.add(MicroContentTag.objects.get(name=tag))
            else:
                content.mc_tags.add(MicroContentTag.objects.create(name=tag))

        MicroLearningContent.objects.filter(id=self.request.POST['id']).update(title=self.request.POST['title'])
        Tag.objects.update_tags(content, None)
        Tag.objects.update_tags(content, tags)

        return render(self.request, 'micro_content_manager/update.html', {"id": self.request.POST['id'],
                                                                            "video_format": self.request.POST['videoFormat']})



class MicroContentCopyView(generic.TemplateView):
    template_name = 'micro_content_manager/copy.html'

    def get(self, request, *args, **kwargs):

        micro_content = MicroLearningContent.objects.get(pk=kwargs['id'])
        micro_content.id = None
        micro_content.meta_data.author = request.user
        micro_content.save()
        return render(request, 'micro_content_manager/copy.html', {"micro_content": micro_content})



class MicroContentDeleteView(generic.TemplateView):
    template_name = 'micro_content_manager/delete.html'

    def get(self, request, *args, **kwargs):

        micro_content = MicroLearningContent.objects.get(pk=kwargs['id'])
        connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
        collection = connection[DB_NAME][COLLECTION_NAME]
        collection.delete_one({'id': kwargs['id']})
        return render(request, 'micro_content_manager/delete.html', {"micro_content": micro_content})


class RecordVideoView(generic.TemplateView):
    template_name = 'micro_content_manager/webcam_record.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'micro_content_manager/webcam_record.html')


class StoreView(generic.TemplateView):
    template_name = 'micro_content_manager/store.html'

    def post(self, request, *args, **kwargs):
        try:
            content = MicroLearningContent.create(request)
        except MultiValueDictKeyError:
            return HttpResponseBadRequest("Error 400. Bad request.")

        content.save()
        tags = request.POST['mc_tags']
        tag_args = tags.split()
        for tag in tag_args:
            if MicroContentTag.objects.filter(name=tag).count() > 0:
                content.mc_tags.add(MicroContentTag.objects.get(name=tag))
            else:
                content.mc_tags.add(MicroContentTag.objects.create(name=tag))

        i = 0
        for n in ' ' * int(request.POST['idQuestions']):
                try:
                    i += 1
                    question = request.POST['question' + str(i)]
                    choices_text = Question.getChoices(request, i)
                    answer = request.POST[request.POST['answer' + str(i)]]
                    explanation = request.POST['explanation' + str(i)]
                    question = Question.objects.create(question=question, choices_text=choices_text, answer=answer, explanation=explanation)
                    question.save()
                    for c in [1, 2, 3]:
                        question.choices.add(Choice.objects.create(choice_text=request.POST['choice'+str(i)+'_'+str(c)], votes=0))
                    content.questions.add(question)
                except MultiValueDictKeyError:
                    pass

        Tag.objects.update_tags(content, tags)

        url = 'http://' + request.META['SERVER_NAME'] + '/micro_content_manager/json?content=' + str(content.id)
        return render(request, 'micro_content_manager/store.html', {'id': content.id, 'url': url})


def update(request, **kwargs):
        try:
            MicroLearningContent.objects.get(pk=request.POST['id'])
        except MicroLearningContent.DoesNotExist:
            raise Http404
        content = MicroLearningContent.objects.get(pk=request.POST['id'])
        tags = request.POST['mc_tags']
        tag_args = tags.split()
        content.mc_tags.clear()
        for tag in tag_args:
            if MicroContentTag.objects.filter(name=tag).count() > 0:
                content.mc_tags.add(MicroContentTag.objects.get(name=tag))
            else:
                content.mc_tags.add(MicroContentTag.objects.create(name=tag))
        Tag.objects.update_tags(content, None)
        Tag.objects.update_tags(content, tags)
        id = int(request.POST['id'])
        connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
        collection = connection[DB_NAME][COLLECTION_NAME]
        collection.update_one({"id": id}, {"$set": {"title": request.POST['title'],
                                                    "text":  MicroLearningContent.getText(request),
                                                    "meta_data.title": request.POST['title'],
                                                    "meta_data.last_modification": timezone.now()
                                                    }})
        if 'videoURL' + str(2) in request.POST:

            collection.update_one({"id": id}, {"$set": {
                "videos.0.url": request.POST['videoURL1'],
                "videos.0.video_format": request.POST['videoFormat1'],
                "videos.0.video_upload_form": request.POST['video_upload_form1'],

                "videos.1.url": request.POST['videoURL2'],
                "videos.1.video_format": request.POST['videoFormat2'],
                "videos.1.video_upload_form": request.POST['video_upload_form2']
                }
            })
        else:
            collection.update_one({"id": id}, {"$set": {
                "videos.0.url": request.POST['videoURL1'],
                "videos.0.video_format": request.POST['videoFormat1'],
                "videos.0.video_upload_form": request.POST['video_upload_form1']
            }})

        q = 0
        for question in content.questions.all():
            q += 1
            question.question = request.POST['question' + str(q)]
            question.choices_text = Question.getChoices(request, q)
            question.answer = request.POST[request.POST['answer' + str(q)]]
            question.explanation = request.POST['explanation' + str(q)]
            c = 0
            for choice in question.choices.all():
                c += 1
                choice.choice_text = request.POST['choice'+str(q)+'_'+str(c)]
                choice.save()
            question.save()


        return render(request, 'micro_content_manager/update.html', {"id": request.POST['id']})


def download(request):
    try:
        content = 'http://' + request.META['SERVER_NAME'] + '/micro_content_manager/json?content=' + request.GET['content']
        script = 'http://' + request.META['SERVER_NAME'] + '/static/micro_content_manager/micro-learning.js'
        image = 'http://' + request.META['SERVER_NAME'] + '/static/micro_content_manager/elemend-logo.png'
        response = render(request, 'micro_content_manager/download.html',
                          {'content': content, 'script': script, 'image': image})
    except MultiValueDictKeyError:
        raise Http404()
    response['Content-Disposition'] = 'attachment; filename=%s' % 'micro-learning.html'
    return response


def vote(request):
    micro_content = get_object_or_404(MicroLearningContent, pk=int(request.POST['mc_id']))
    correct_answers = 0
    i = 0
    for question in micro_content.questions.all():
        i += 1
        pk = request.POST['choice1']
        selected_choice = question.choices.get(pk=int(request.POST['choice'+str(i)]))
        selected_choice.votes += 1
        selected_choice.save()
        if question.answer.strip() == selected_choice.choice_text.strip():
                correct_answers += 1
    return render(request, 'micro_content_manager/results.html', {"micro_content": micro_content, "correct_answers": correct_answers})


def test(request):

    return render(request, 'micro_content_manager/test.html')



