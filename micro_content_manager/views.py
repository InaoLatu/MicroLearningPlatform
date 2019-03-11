from _ctypes import sizeof
from typing import List

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from tagging.models import Tag

from micro_content_manager.models import MicroLearningContent
from django.http import Http404, JsonResponse, HttpResponseBadRequest, HttpResponse
from django.utils.datastructures import MultiValueDictKeyError

NUMBER_PARAGRAPHS = 1
NUMBER_QUESTIONS = 2
NUMBER_CHOICES = 3


class MicroContentCreationView(generic.CreateView):
    success_url = reverse_lazy('auth_tool:index')
    template_name = 'micro_content_manager/create.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'micro_content_manager/create.html', {'paragraphs': ' ' * NUMBER_PARAGRAPHS,
                                                                     'questions': ' ' * NUMBER_QUESTIONS,
                                                                     'choices': ' ' * NUMBER_CHOICES})

class MicroContentInfoView(generic.DetailView):
    template_name = 'micro_content_manager/micro_content_info.html'

    def get(self, request, *args, **kwargs):
        micro_content = MicroLearningContent.objects.get(pk=kwargs['id'])
        mc_t = Tag.objects.get_for_object(micro_content).values_list('name', flat=True)
        mc_tags: List[str] = []
        for tag in mc_t:
            mc_tags.append(str(tag))
        mc_text = micro_content.getText(self.request)
        questions = micro_content.getQuiz(request)

        return render(request, 'micro_content_manager/micro_content_info.html', {'micro_content': micro_content,
                                                                                 'mc_tags': mc_tags,
                                                                                 'number_tags': len(mc_tags),
                                                                                 'mc_text': mc_text,
                                                                                 'questions': questions
                                                                                 })


def index(request):
    contents = [(e.id, e.title) for e in MicroLearningContent.objects.all()]
    return render(request, 'micro_content_manager/index.html', {'contents': contents})


def json(request):
    try:
        content = MicroLearningContent.objects.get(pk=request.GET['content'])
        return JsonResponse(content.toDict())
    except (MicroLearningContent.DoesNotExist, MultiValueDictKeyError):
        raise Http404()


def create(request):
    return render(request, 'micro_content_manager/create.html', {'paragraphs': ' ' * NUMBER_PARAGRAPHS,
                                                         'questions': ' ' * NUMBER_QUESTIONS,
                                                         'choices': ' ' * NUMBER_CHOICES})


def edit(request):
    try:
        content = MicroLearningContent.objects.get(pk=request.GET['content']).toDict()
    except (MicroLearningContent.DoesNotExist, MultiValueDictKeyError):
        raise Http404()
    content['id'] = request.GET['content']
    return render(request, 'micro_content_manager/edit.html', content)


def store(request):
    try:
        content = MicroLearningContent.create(request)
    except MultiValueDictKeyError:
        return HttpResponseBadRequest("Error 400. Bad request.")
    content.save()
    tags = request.POST['mc_tags']
    Tag.objects.update_tags(content, tags)
    url = 'http://' + request.META['SERVER_NAME'] + '/micro_content_manager/json?content=' + str(content.id)
    return render(request, 'micro_content_manager/store.html', {'id': content.id, 'url': url})


def update(request):
    try:
        try:
            MicroLearningContent.objects.get(pk=request.POST['id'])
        except MicroLearningContent.DoesNotExist:
            raise Http404
        content = MicroLearningContent.create(request)
        content.id = request.POST['id']
    except MultiValueDictKeyError:
        return HttpResponseBadRequest("Error 400. Bad request.")
    content.save()
    url = 'https://' + request.META['SERVER_NAME'] + '/micro_content_manager/json?content=' + str(content.id)
    return render(request, 'micro_content_manager/update.html', {'id': content.id, 'url': url})


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

