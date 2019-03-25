from django.test import TestCase

# Create your tests here.


try:
    try:
        MicroLearningContent.objects.get(pk=self.request.POST['id'])
    except MicroLearningContent.DoesNotExist:
        raise Http404
    content = MicroLearningContent.create(self.request)
    content.id = self.request.POST['id']
except MultiValueDictKeyError:
    return HttpResponseBadRequest("Error 400. Bad request.")
content.save()

tags = self.request.POST['mc_tags']
tag_args = tags.split()

for tag in tag_args:
    if MicroContentTag.objects.filter(name=tag).count() > 0:
        content.mc_tags.add(MicroContentTag.objects.get(name=tag))
    else:
        content.mc_tags.add(MicroContentTag.objects.create(name=tag))

Tag.objects.update_tags(content, tags)