from bson import json_util
import json
from bson.json_util import loads, dumps, CANONICAL_JSON_OPTIONS
from typing import List
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from pymongo import MongoClient
from rest_framework.response import Response
from rest_framework.views import APIView
#from tagging.models import Tag

from micro_content_manager.forms import MicroContentEditForm
from micro_content_manager.models import MicroLearningContent, Question, Choice, Media, Unit
from micro_content_manager.models import Tag as MicroContentTag
from django.http import Http404, JsonResponse, HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.utils.datastructures import MultiValueDictKeyError
import operator

NUMBER_PARAGRAPHS = 1
NUMBER_QUESTIONS = 3
NUMBER_CHOICES = 3
NUMBER_VIDEOS = 1

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = 'authoring_tool'
COLLECTION_NAME = 'micro_content_manager_microlearningcontent'

# API imports
from rest_framework import viewsets
from micro_content_manager.serializers import UnitSerializer, MicroContentSerializer
from rest_framework.decorators import api_view
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from micro_content_manager.models import Unit


# API classes
class UnitViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


class UnitList(APIView):
    def get(self, request, format=None):
        units = Unit.objects.all()
        serializer = UnitSerializer(units, many=True)
        return Response(serializer.data)


class UnitDetail(APIView):
    def get_object(self, unit):
        try:
            return Unit.objects.get(name=unit)
        except Unit.DoesNotExist:
            raise Http404

    def get(self, request, unit, format=None):
        unit_selected = self.get_object(unit)
        micro_content = unit_selected.micro_content
        serializer = MicroContentSerializer(micro_content, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def unit_list(request, format=None):  # Format to choose the json format or any other
    if request.method == 'GET':
        units = Unit.objects.all()
        serializer = UnitSerializer(units, many=True)
        return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def unit_detail(request, unit, format=None):
    try:
        unit = Unit.objects.get(name=unit)
    except Unit.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = UnitSerializer(unit)
        return JsonResponse(serializer.data)
#  end API classes


class CreateSelectionView(generic.TemplateView):
    template_name = 'micro_content_manager/create_selection.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'micro_content_manager/create_selection.html')


class MicroContentCreationView(generic.CreateView):
    success_url = reverse_lazy('auth_tool:index')
    template_name = 'micro_content_manager/create.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'micro_content_manager/create.html', {'paragraphs': ' ' * NUMBER_PARAGRAPHS,
                                                                     'medias': ' ' * kwargs['m'],
                                                                     'questions': ' ' * kwargs['q'],
                                                                     'nQuestions': kwargs['q'],
                                                                     'choices': ' ' * NUMBER_CHOICES})


class DoTheMicroContentView(generic.DetailView):
    template_name = 'micro_content_manager/do_the_micro_content.html'

    def get(self, request, *args, **kwargs):
        connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
        collection = connection[DB_NAME][COLLECTION_NAME]

        micro_content = collection.find_one({"id": kwargs['id']})

        return render(request, 'micro_content_manager/do_the_micro_content.html', {"micro_content": micro_content})


def microcontent(request):
    try:
        connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
        collection = connection[DB_NAME][COLLECTION_NAME]
        micro_content = collection.find_one({"id": request.GET['id']})

        return JsonResponse(MicroLearningContent.objects.get(pk=request.GET['id']).toDict())



    except (MicroLearningContent.DoesNotExist, MultiValueDictKeyError):
        raise Http404()


def vote(request):
    # micro_content = get_object_or_404(MicroLearningContent, pk=int(request.POST['mc_id']))
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DB_NAME][COLLECTION_NAME]

    micro_content = collection.find_one({"id": int(request.POST['mc_id'])})
    correct_answers = 0
    i = 0
    sol_messages = {}
    selections = {}

    for question in micro_content['quiz']:
        i += 1
        # Computing the votes. IMPLEMENT AGAIN IN A FUTURE DEVELOPMENT (4/dic/19)
        # 'selection1', 'selection2'... have as a value the index of the selected choice in the question 1, question 2 respectively...
        # selected_choice = question.choices.get(pk=int(request.POST['selection' + str(i)]))
        selected_choice_index = int(request.POST['selection' + str(i)]) - 1
        # selected_choice.votes += 1
        # selected_choice.save()
        selections[i] = question['choices'][selected_choice_index]['choice_text']
        if question['answer'] == question['choices'][selected_choice_index]['choice_text']:
            correct_answers += 1
            sol_messages[i] = "CORRECT!"
        else:
            sol_messages[i] = "WRONG. The correct answer is '" + question['answer'] + "'."

    return render(request, 'micro_content_manager/do_the_micro_content.html',
                  {"micro_content": micro_content, "correct_answers": correct_answers,
                   "sol_messages": sol_messages, "selections": selections,
                   "quiz_size": len(micro_content["quiz"])})


class MicroContentInfoView(generic.DetailView):
    template_name = 'micro_content_manager/micro_content_info.html'

    def get(self, request, *args, **kwargs):
        connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
        collection = connection[DB_NAME][COLLECTION_NAME]

        micro_content = collection.find_one({"id": kwargs['id']})
        mc_text = micro_content["tags"]
        # micro_content = MicroLearningContent.objects.get(pk=kwargs['id'])

        # mc_t = Tag.objects.get_for_object(micro_content).values_list('name', flat=True)
        # mc_tags: List[str] = []
        # for tag in mc_t:
        #     mc_tags.append(str(tag))
        # mc_text = micro_content.getText(self.request)

        return render(request, 'micro_content_manager/micro_content_info.html', {'micro_content': micro_content,
                                                                                 'quiz': micro_content['quiz'],
                                                                                 'mc_text': mc_text,
                                                                                 })


class MicroContentSearchView(generic.DetailView):
    template_name = 'micro_content_manager/mc_search.html'

    def get(self, request, *args, **kwargs):

        connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
        collection = connection[DB_NAME][COLLECTION_NAME]
        # list = MicroLearningContent.objects.all()
        list_result = {}

        for mc in collection.find():
            list_result.update({mc["id"]: [mc["title"], mc["meta_data"]["author"], mc["allow_copy"], mc["visible"]]})
        return render(request, 'micro_content_manager/mc_search.html',
                      {"list_result": list_result, "tab": kwargs['tab']})

    def post(self, request, tab):
        micro_contents_search = self.request.POST['search']
        searchIn = self.kwargs['tab']
        micro_contents_search = micro_contents_search.split()
        list = MicroLearningContent.objects.all()
        list_result = {}

        for mc in list:
            mc_tags: List[str] = []
            mc_queryset = mc.mc_tags.all()
            for tag in mc_queryset:
                mc_tags.append(str(tag))
                if bool(set(micro_contents_search) & set(mc_tags)):
                    list_result.update({mc.id: [mc.title, mc.meta_data.author, mc.allow_copy]})

        list = MicroLearningContent.objects.all()
        for mc2 in list:
            if self.request.POST['search'] == mc2.title:
                list_result.update({mc2.id: [mc2.title, mc2.meta_data.author, mc2.allow_copy]})

        return render(self.request, 'micro_content_manager/mc_search.html',
                      {"list_result": list_result, "tab": searchIn, "search": micro_contents_search})


class MicroContentEditView(generic.FormView):
    template_name = 'micro_content_manager/edit.html'
    form = MicroContentEditForm

    def get(self, request, *args, **kwargs):
        connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
        collection = connection[DB_NAME][COLLECTION_NAME]
        micro_content = collection.find_one({"id": kwargs['pk']})
        mc_text = micro_content["tags"]

        # try:
        #     content = MicroLearningContent.objects.get(pk=kwargs['pk'])
        # except (MicroLearningContent.DoesNotExist, MultiValueDictKeyError):
        #     raise Http404()
        # mc_t = Tag.objects.get_for_object(MicroLearningContent.objects.get(pk=kwargs['pk'])).values_list('name',
        #                                                                                                  flat=True)
        # mc_tags = ""
        # for tag in mc_t:
        #     mc_tags = mc_tags + " " + str(tag)

        return render(request, 'micro_content_manager/edit.html', {"content": micro_content,
                                                                   "number_questions": len(micro_content["quiz"]),
                                                                   "quiz": micro_content["quiz"],
                                                                   "id": kwargs['pk'],
                                                                   "mc_tags": mc_text})

    # def form_valid(self, form):
    #     form = MicroContentEditForm(self.request.POST)
    #     try:
    #         MicroLearningContent.objects.get(pk=self.request.POST['id'])
    #     except MicroLearningContent.DoesNotExist:
    #         raise Http404
    #     content = MicroLearningContent.objects.get(pk=self.request.POST['id'])
    #
    #     tags = self.request.POST['mc_tags']
    #     tag_args = tags.split()
    #     content.mc_tags.clear()
    #     for tag in tag_args:
    #         if MicroContentTag.objects.filter(name=tag).count() > 0:
    #             content.mc_tags.add(MicroContentTag.objects.get(name=tag))
    #         else:
    #             content.mc_tags.add(MicroContentTag.objects.create(name=tag))
    #
    #     MicroLearningContent.objects.filter(id=self.request.POST['id']).update(title=self.request.POST['title'])
    #     Tag.objects.update_tags(content, None)
    #     Tag.objects.update_tags(content, tags)

    # return render(self.request, 'micro_content_manager/update.html', {"id": self.request.POST['id']})


class MicroContentCopyView(generic.TemplateView):
    template_name = 'micro_content_manager/copy.html'

    def get(self, request, *args, **kwargs):
        micro_content = MicroLearningContent.objects.get(pk=kwargs['id'])
        micro_content.id = None
        micro_content.meta_data.author = request.user
        micro_content.meta_data.creation_type = "copy"
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
    def get(self, request, *args, **kwargs):
        return render(request, 'micro_content_manager/rtc.html')


class StoreView(generic.TemplateView):
    template_name = 'micro_content_manager/store.html'

    def post(self, request, *args, **kwargs):

        content = MicroLearningContent.create(request)

        content.save()
        tags = request.POST['mc_tags']
        tag_args = tags.split()
        for tag in tag_args:  # If the tags does not exist, it is added to the set of Tags in mongodb
            if MicroContentTag.objects.filter(name=tag).count() > 0:
                content.mc_tags.add(MicroContentTag.objects.get(name=tag))
            else:
                content.mc_tags.add(MicroContentTag.objects.create(name=tag))

        list = {}
        q = 0
        for order in ' ' * int(request.POST['idQuestions']):
            try:
                q += 1
                qs = str(q)
                list.update({"question" + qs: str(request.POST['order' + qs])})
            except MultiValueDictKeyError:
                pass

        sorted_list = sorted(list.items(), key=operator.itemgetter(1))

        for qu in sorted_list:
            try:
                index = int(qu[0][8])
                question = request.POST[qu[0]]
                choices_text = Question.getChoices(request, index)
                answer = request.POST[request.POST['answer' + str(index)]]
                explanation = request.POST['explanation' + str(index)]
                question = Question.objects.create(question=question, choices_text=choices_text, answer=answer,
                                                   explanation=explanation)
                question.save()
                for c in [1, 2, 3]:
                    question.choices.add(
                        Choice.objects.create(choice_text=request.POST['choice' + str(index) + '_' + str(c)]))
                content.questions.add(question)
            except MultiValueDictKeyError:
                pass

        Tag.objects.update_tags(content, tags)

        unit_selected = request.POST['unit'].lower()
        print(unit_selected)

        if Unit.objects.filter(name=unit_selected).count() > 0:
            unit = Unit.objects.get(name=unit_selected)
        elif Unit.objects.filter(name=unit_selected).count() == 0:
            unit = Unit.create(request)
            unit.save()

        unit.micro_content.add(content)  # Adding the Micro content to its Unit.

        return render(request, 'micro_content_manager/store.html')


def update(request, **kwargs):
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DB_NAME][COLLECTION_NAME]

    # micro_content = collection.find_one({"id": request.POST['id']})

    # IMPLEMENT TAG SYSTEM AFTER SOLVING ALL THE MONGODB ACCESS DATA ERRORS (03/12/19)

    # content = MicroLearningContent.objects.get(pk=request.POST['id'])
    # tags = request.POST['mc_tags']
    # tag_args = tags.split()
    # content.mc_tags.clear()
    # for tag in tag_args:
    #     if MicroContentTag.objects.filter(name=tag).count() > 0:
    #         content.mc_tags.add(MicroContentTag.objects.get(name=tag))
    #     else:
    #         content.mc_tags.add(MicroContentTag.objects.create(name=tag))
    # Tag.objects.update_tags(content, None)
    # Tag.objects.update_tags(content, tags)

    id = int(request.POST['id'])  # id of the micro content to edit

    print(request.POST['title'])
    collection.update_one({"id": id}, {"$set": {"title": request.POST['title']}})

    collection.update_one({"id": id}, {"$set": {"title": request.POST['title'],
                                                                "tags": request.POST['mc_tags'],
                                                                "text": MicroLearningContent.getText(request),
                                                                "visible": request.POST['visible'],
                                                                "allow_copy": request.POST['allow_copy'],
                                                                "meta_data.title": request.POST['title'],
                                                                "meta_data.last_modification": timezone.now()
                                                                }})
    if 'type' + str(2) in request.POST:  # If two media have been entered, they are both updated.

        collection.update_one({"id": id}, {"$set": {
            "media.0.type": request.POST['type1'],
            "media.0.upload_form": request.POST['upload_form1'],
            "media.0.url": request.POST['videoURL1'],
            "media.0.text" : request.POST['text1'],

            "media.1.type": request.POST['type2'],
            "media.1.upload_form": request.POST['upload_form2'],
            "media.1.url": request.POST['videoURL2'],
            "media.1.text" : request.POST['text2'],
        }
        })
        # if request.POST['type1'] == 'video':
        #     collection.update_one({"id": id}, {"$set": {
        #         "media.0.mediaFile": request.FILES['videoFile1'],
        #     }})
        # elif request.POST['type1'] == 'audio':
        #     collection.update_one({"id": id}, {"$set": {
        #         "media.0.mediaFile": request.FILES['audioFile1'],
        #     }})

        if request.POST['type2'] == 'video':
            collection.update_one({"id": id}, {"$set": {
                "media.0.mediaFile": request.FILES.get('videoFile2'),
            }})
        elif request.POST['type2'] == 'audio':
            collection.update_one({"id": id}, {"$set": {
                "media.0.mediaFile": request.FILES.get('audioFile2'),
            }})


    else:  # Just one media updated
        collection.update_one({"id": id}, {"$set": {
            "media.0.type": request.POST['type1'],
            "media.0.upload_form": request.POST['upload_form1'],
            "media.0.url": request.POST['videoURL1'],
            "media.0.text" : request.POST['text1'],
        }})

        # if request.POST['type1'] == 'video':
        #     collection.update_one({"id": id}, {"$set": {
        #         "media.0.mediaFile": request.FILES['videoFile1'],
        #     }})
        # elif request.POST['type1'] == 'audio':
        #     collection.update_one({"id": id}, {"$set": {
        #         "media.0.mediaFile": request.FILES['audioFile1'],
        #     }})

    if request.POST['type1'] == 'video':
        collection.update_one({"id": id}, {"$set": {
            "media.0.mediaFile": request.FILES.get('videoFile1')
        }})
    elif request.POST['type1'] == 'audio':
        collection.update_one({"id": id}, {"$set": {
            "media.0.mediaFile": request.FILES.get('audioFile1')
        }})
    # content.questions.all().delete()

    list = {}
    q = 0
    for order in ' ' * int(request.POST['idQuestions']):
        try:
            q += 1
            qs = str(q)
            list.update({"question" + qs: str(request.POST['order' + qs])})
        except MultiValueDictKeyError:
            pass

    sorted_list = sorted(list.items(), key=operator.itemgetter(
        1))  # We sort the questions with the new order specified by the instructor

    question_index = 0
    for qu in sorted_list:
        try:
            index = int(qu[0][8])  # Get the index of each question to access to its fields
            question = request.POST[qu[0]]  # qu[0] will be 'question1', 'question2, etc in each iteration of the for
            # choices_text = Question.getChoices(request, index)  # CHANGE TO GET EACH CHOICE SEPARATELY TO KEEP THE
            # STRUCTURE OF THE JSON
            answer = request.POST[request.POST['answer' + str(index)]]
            explanation = request.POST['explanation' + str(index)]

            collection.update_one({"id": id}, {"$set": {
                "quiz." + str(question_index) + ".question": question,
                "quiz." + str(question_index) + ".answer": answer,
                "quiz." + str(question_index) + ".explanation": explanation,
            }})

            # Editing choices
            choice_index = 0
            while choice_index < 3:
                choice_value = request.POST[
                    'choice' + str(question_index + 1) + '_' + str(choice_index + 1)]  # Adding 1
                # to get the value of the input field whose numeration starts in 1, not in 0
                collection.update_one({"id": id},
                                      {"$set": {"quiz." + str(question_index) + ".choices." + str(
                                          choice_index) + ".choice_text": choice_value, }})
                choice_index += 1

            question_index += 1

            # question = Question.objects.create(question=question, choices_text=choices_text, answer=answer,
            #                                    explanation=explanation)
            # question.save()
            # for c in [1, 2, 3]:
            #     question.choices.add(
            #         Choice.objects.create(choice_text=request.POST['choice' + str(index) + '_' + str(c)], votes=0))
            # content.questions.add(question)


        except MultiValueDictKeyError:
            pass

    return render(request, 'micro_content_manager/update.html',
                  {"id": request.POST['id'], "title": request.POST['title']})


class TestView(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'micro_content_manager/test.html', {"videoFile": "videos/chest.webm"})

    def post(self, ab):
        video = Video.create(self.request, 1)
        video.save()

        return render(self.request, 'micro_content_manager/test.html', {"url": self.request.POST['url1']})
