from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
from djongo import models
from django.forms.models import model_to_dict


class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


UPLOAD_FORM = (
    ('FROM_FILE', 'FROM EXISTING FILE'),
    ('LINK_FROM_YOUTUBE', 'LINK FROM YOUTUBE'),
    ('DOWNLOAD_FROM_YOUTUBE', 'DOWNLOAD FROM YOUTUBE'),
    ('EXTERNAL_REPOSITORY', 'EXTERNAL REPOSITORY'),
)


class Media(models.Model):
    type = models.CharField(max_length=50)
    upload_form = models.CharField(
        choices=UPLOAD_FORM,
        default='',
        max_length=50,
    )
    url = models.CharField(max_length=1000)
    mediaFile = models.FileField()
    text = models.CharField(max_length=3000)

    def __str__(self):
        return self.url + ": " + str(self.mediaFile)

    @staticmethod
    def create(request, number):

        if request.POST['type' + str(number)] == "video":
            if request.POST['upload_form' + str(number)] == "from_existing_file":
                return Media(request.POST['type' + str(number)], Media.buildURL(request, number),
                             request.POST['upload_form' + str(number)], request.FILES['videoFile' + str(number)],
                             request.POST['text' + str(number)])
            else:
                return Media(request.POST['type' + str(number)], Media.buildURL(request, number),
                             request.POST['upload_form' + str(number)], None, request.POST['text' + str(number)])

        if request.POST['type' + str(number)] == "audio":
            return Media(request.POST['type' + str(number)], Media.buildURL(request, number),
                         request.POST['upload_form' + str(number)], request.FILES['videoFile' + str(number)],
                         request.POST['text' + str(number)])

        if request.POST['type' + str(number)] == "text":
            return Media(request.POST['type' + str(number)], None, None, None, request.POST['text' + str(number)])

    def __init__(self, type, url, upload_form, mediaFile, text):
        super(Media, self).__init__()
        self.type = type
        self.url = url
        self.upload_form = upload_form
        self.mediaFile = mediaFile
        self.text = text

    def toDict(self):
        return model_to_dict(self, fields=['type', 'url', 'upload_form', 'text'])

    @staticmethod
    def buildURL(request, number):

        videoURL = ""
        # print(request.POST['type'+str(number)])
        if request.POST['type' + str(number)] == "video":
            videoURL = request.POST['videoURL' + str(number)]
            if request.POST['upload_form' + str(number)] == "link_from_youtube":
                idYoutubeVideo = videoURL.split("v=", 1)[1]
                videoURL = "http://www.youtube.com/embed/" + idYoutubeVideo

            if request.POST['upload_form' + str(number)] == "from_existing_file":
                video_file = request.FILES['videoFile' + str(number)]
                videoURL = video_file.name  # Get the name of the file to access to it when the micro-content is requested from external tool

        if request.POST['type' + str(number)] == "audio":
            video_file = request.FILES['videoFile' + str(number)]
            videoURL = video_file.name  # Get the name of the file to access to it when the micro-content is requested from external tool

        return videoURL


class Choice(models.Model):
    choice_text = models.CharField(max_length=200)

    # votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

    @staticmethod
    def create(request, number, j):
        return Choice(request.POST['choice' + str(number) + "_" + str(j)])

    def __init__(self, choice_text):
        super(Choice, self).__init__()
        self.choice_text = choice_text

    def toDict(self):
        return model_to_dict(self, fields=['choice_text'])


class Question(models.Model):
    question = models.TextField()
    choices = models.ManyToManyField(Choice)
    choices_text = models.TextField()
    answer = models.TextField()
    explanation = models.TextField()

    def __str__(self):
        return self.question

    #    def __init__(self, question, choices_text, answer, explanation):
    #       super(Question, self).__init__()
    #      self.question = question
    #      self.choices_text = choices_text
    #      self.answer = answer
    #     self.explanation = explanation

    @staticmethod
    def create(request, number):
        return Question(request.POST['question' + str(number)], Question.getChoices(request, number),
                        request.POST[request.POST['answer' + str(number)]], request.POST['explanation' + str(number)])

    @staticmethod
    def getChoices(request, number):
        choices = ""
        j = 1
        while True:
            if 'choice' + str(number) + "_" + str(j) in request.POST:
                choices = choices + request.POST['choice' + str(number) + "_" + str(j)] + " "
                j += 1
            else:
                break
        return choices

    def toDict(self):
        return model_to_dict(self, fields=['question', 'choices', 'answer', 'explanation'])


class MetaData(models.Model):
    title = models.CharField()
    author = models.CharField()
    pub_date = models.DateTimeField('date published')
    last_modification = models.DateTimeField('last modification')
    creation_type = models.CharField()

    @staticmethod
    def create(request):
        return MetaData(request.POST['title'], request.POST['author'], timezone.now(), timezone.now(),
                        request.POST['creation_type'])

    def __init__(self, title, author, pub_date, last_modification, creation_type):
        super(MetaData, self).__init__()
        self.title = title
        self.author = author
        self.pub_date = pub_date
        self.last_modification = last_modification
        self.creation_type = creation_type

    def toDict(self):
        return model_to_dict(self, fields=['title', 'author', 'pub_date', 'last_modification', 'creation_type'])

    class Meta:
        abstract = True


class Quest(models.Model):
    question = models.TextField()
    choices = models.ArrayModelField(
        model_container=Choice
    )
    # choices = models.ListField()
    answer = models.TextField()
    explanation = models.TextField()

    def __init__(self, question, choices, answer, explanation):
        super(Quest, self).__init__()
        self.question = question
        self.choices = choices
        self.answer = answer
        self.explanation = explanation

    @staticmethod
    def create(request, number):
        return Quest(request.POST['question' + str(number)], Quest.getChoices(request, number),
                     request.POST[request.POST['answer' + str(number)]], request.POST['explanation' + str(number)])

    @staticmethod
    def getChoices(request, number):
        choices = []
        j = 1
        while True:
            if 'choice' + str(number) + "_" + str(j) in request.POST:
                choice = Choice.create(request, number, j)
                choice.save()
                choices.append(choice)
                j += 1
            else:
                break
        return choices

    def toDict(self):
        # return model_to_dict(self, fields=['question', 'choices', 'answer', 'explanation'])
        dict = model_to_dict(self, fields=['question', 'answer', 'explanation'])
        dict['choices'] = []
        for c in self.choices:
            dict['choices'].append(c.toDict())
        return dict

    class Meta:
        abstract = True


class MicroLearningContent(models.Model):
    #MOD posible problema de tags, duplicado con mc_tags (ver formulario en templates)
    mc_tags = models.ManyToManyField(Tag)
    questions = models.ManyToManyField(Question)
    title = models.CharField(max_length=100)
    #tags = models.CharField(max_length=100)
    text = models.ListField()
    quiz = models.ArrayModelField(
        model_container=Quest
    )
    media = models.ArrayModelField(
        model_container=Media
    )
    meta_data = models.EmbeddedModelField(
        model_container=MetaData
    )
    visible = models.CharField(max_length=4)
    allow_copy = models.CharField(max_length=4)

    #def __init__(self, id, title, tags, text, quiz, media, meta_data, visible, allow_copy):
    def __init__(self, id, title, text, quiz, media, meta_data, visible, allow_copy):
        super(MicroLearningContent, self).__init__()
        self.id = id
        self.title = title
        #self.tags = tags
        self.text = text
        self.quiz = quiz
        self.media = media
        self.meta_data = meta_data
        self.visible = visible
        self.allow_copy = allow_copy

    @staticmethod
    def create(request):
        return MicroLearningContent(None, request.POST['title'], #request.POST['mc_tags'],
                                    MicroLearningContent.getText(request), MicroLearningContent.getQuiz(request),
                                    MicroLearningContent.getMedia(request), MetaData.create(request),
                                    request.POST['visible'], request.POST['allow_copy'])

    @staticmethod
    def getText(request):
        text = []
        i = 1
        while True:
            if 'paragraph' + str(i) in request.POST:
                text.append(request.POST['paragraph' + str(i)])
                i += 1
            else:
                break
        return text

    @staticmethod
    def getMedia(request):
        videos = []
        i = 1
        while True:
            if 'type' + str(i) in request.POST:
                video = Media.create(request, i)
                video.save()
                videos.append(video)
                i += 1
            else:
                break
        return videos

    @staticmethod
    def getQuiz(request):
        quiz = []
        i = 1
        while True:
            if 'question' + str(i) in request.POST:
                quiz.append(Quest.create(request, i))
                i += 1
            else:
                break
        return quiz

    def toDict(self):
        dict = model_to_dict(self, fields=['title', 'text', 'tags'])
        dict['meta_data'] = self.meta_data.toDict()
        dict['media'] = []
        for v in self.media:
            dict['media'].append(v.toDict())
        dict['quiz'] = []
        for q in self.quiz:
            dict['quiz'].append(q.toDict())
        return dict

    def get_mc_tags(self):
        return self.mc_tags


class Unit(models.Model):
    name = models.CharField(max_length=100)
    micro_content = models.ManyToManyField(MicroLearningContent)

    def __init__(self, id, name):
        super(Unit, self).__init__()
        self.id = id
        self.name = name

    @staticmethod
    def create(request):
        return Unit(None, request.POST['unit'].lower())
