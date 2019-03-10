from django.utils import timezone
from djongo import models
from django.forms.models import model_to_dict
from tagging.registry import register


UPLOAD_FORM = (
    ('FROM_FILE', 'FROM EXISTING FILE'),
    ('LINK_FROM_YOUTUBE', 'LINK FROM YOUTUBE'),
    ('DOWNLOAD_FROM_YOUTUBE', 'DOWNLOAD FROM YOUTUBE'),
    ('EXTERNAL_REPOSITORY', 'EXTERNAL REPOSITORY'),
)

VIDEO_FORMAT = (
    ('mp4', 'mp4'),
    ('ogg', 'ogg'),
)

class Video(models.Model):
    url = models.URLField()
    video_format = models.CharField(
        choices=VIDEO_FORMAT,
        default='mp4'
        )
    video_upload_form = models.CharField(
        choices=UPLOAD_FORM,
        default='FROM EXISTING FILE'
    )

    @staticmethod
    def create(request):
        return Video(request.POST['videoURL'], request.POST['videoFormat'], request.POST['video_upload_form'])

    def __init__(self, url, video_format, video_upload_form):
        super(Video, self).__init__()
        self.url = url
        self.video_format = video_format
        self.video_upload_form = video_upload_form

    def toDict(self):
        return model_to_dict(self, fields=['url', 'video_format', 'video_upload_form'])

    class Meta:
        abstract = True


class Question(models.Model):
    question = models.TextField()
    choices = models.ListField()
    answer = models.TextField()
    explanation = models.TextField()

    def __init__(self, question, choices, answer, explanation):
        super(Question, self).__init__()
        self.question = question
        self.choices = choices
        self.answer = answer
        self.explanation = explanation

    @staticmethod
    def create(request, number):
        return Question(request.POST['question' + str(number)], Question.getChoices(request, number),
                        request.POST[request.POST['answer' + str(number)]], request.POST['explanation' + str(number)])

    @staticmethod
    def getChoices(request, number):
        choices = []
        j = 1
        while True:
            if 'choice' + str(number) + "_" + str(j) in request.POST:
                choices.append(request.POST['choice' + str(number) + "_" + str(j)])
                j += 1
            else:
                break
        return choices

    def toDict(self):
        return model_to_dict(self, fields=['question', 'choices', 'answer', 'explanation'])

    class Meta:
        abstract = True


class MetaData(models.Model):
    title = models.CharField()
    author = models.CharField()
    pub_date = models.DateTimeField('date published')
    last_modification = models.DateTimeField('last modification')
    creation_type = models.CharField()

    @staticmethod
    def create(request):
        return MetaData(request.POST['title'], request.POST['author'], timezone.now(), timezone.now(), request.POST['creation_type'])

    def __init__(self, title, author, pub_date, last_modification, creation_type):
        super(MetaData, self).__init__()
        self.title = title
        self.author = author
        self.pub_date = pub_date
        self.last_modification = last_modification
        self.creation_type = creation_type

    class Meta:
        abstract = True


class MicroLearningContent(models.Model):
    title = models.CharField(max_length=100)
    text = models.ListField()
    video = models.EmbeddedModelField(
        model_container=Video
    )
    quiz = models.ArrayModelField(
        model_container=Question
    )
    meta_data = models.EmbeddedModelField(
        model_container=MetaData
    )

    def __init__(self, id, title, text, video, quiz, meta_data):
        super(MicroLearningContent, self).__init__()
        self.id = id
        self.title = title
        self.text = text
        self.video = video
        self.quiz = quiz
        self.meta_data = meta_data

    @staticmethod
    def create(request):
        return MicroLearningContent(None, request.POST['title'], MicroLearningContent.getText(request),
                                    Video.create(request), MicroLearningContent.getQuiz(request), MetaData.create(request))

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
    def getQuiz(request):
        quiz = []
        i = 1
        while True:
            if 'question' + str(i) in request.POST:
                quiz.append(Question.create(request, i))
                i += 1
            else:
                break
        return quiz

    def toDict(self):
        dict = model_to_dict(self, fields=['title', 'text'])
        dict['video'] = self.video.toDict()
        dict['quiz'] = []
        for q in self.quiz:
            dict['quiz'].append(q.toDict())
        return dict


register(MicroLearningContent)