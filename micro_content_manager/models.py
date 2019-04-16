from django.utils import timezone
from djongo import models
from django.forms.models import model_to_dict
from tagging.registry import register

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
    def create(request, number):
        return Video(Video.buildURL(request, number), request.POST['videoFormat'+str(number)], request.POST['video_upload_form'+str(number)])


    def __init__(self, url, video_format, video_upload_form):
        super(Video, self).__init__()
        self.url = url
        self.video_format = video_format
        self.video_upload_form = video_upload_form

    def toDict(self):
        return model_to_dict(self, fields=['url', 'video_format', 'video_upload_form'])

    @staticmethod
    def buildURL(request, number):
        videoURL = request.POST['videoURL'+str(number)]
        if request.POST['video_upload_form'+str(number)] == "link_from_youtube":
            idYoutubeVideo = videoURL.split("v=", 1)[1]
            videoURL = "http://www.youtube.com/embed/"+idYoutubeVideo


        return videoURL

    class Meta:
        abstract = True


class Choice(models.Model):
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


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
    mc_tags = models.ManyToManyField(Tag)
    questions = models.ManyToManyField(Question)
    title = models.CharField(max_length=100)
    text = models.ListField()
   # video = models.EmbeddedModelField(
   #     model_container=Video
   # )
    videos = models.ArrayModelField(
        model_container=Video
    )

    meta_data = models.EmbeddedModelField(
        model_container=MetaData
    )

    def __init__(self, id, title, text, videos, meta_data):
        super(MicroLearningContent, self).__init__()
        self.id = id
        self.title = title
        self.text = text
        self.videos = videos
        self.meta_data = meta_data

    @staticmethod
    def create(request):
        return MicroLearningContent(None, request.POST['title'], MicroLearningContent.getText(request),
                                    MicroLearningContent.getVideos(request), MetaData.create(request))

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
    def getVideos(request):
        videos = []
        i = 1
        while True:
            if 'videoURL' + str(i) in request.POST:
                videos.append(Video.create(request, i))
                i += 1
            else:
                break
        return videos

    def toDict(self):
        dict = model_to_dict(self, fields=['title', 'text'])
        dict['video'] = self.videos.toDict()
        return dict

    def get_mc_tags(self):
        return self.mc_tags


register(MicroLearningContent)