from django.db import models
from django.urls import reverse


class LinkDataModel(models.Model):

    url = models.TextField(max_length=2000, help_text='url')
    artist = models.TextField(max_length=1000, help_text='artist')
    album = models.TextField(max_length=1000, help_text='album')
    title = models.TextField(max_length=1000, help_text='title')
    category = models.TextField(max_length=1000, help_text='category')
    subcategory = models.TextField(max_length=1000, help_text='subcategory')
    tag = models.TextField(max_length=1000, help_text='tag')
    date_saved = models.DateTimeField(auto_now = True)
    date_created = models.DateTimeField(auto_now = False, auto_now_add = False)

    class Meta:
        ordering = ['date_created', 'artist', 'album', 'title']

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse('news:link-detail', args=[str(self.id)])


class LinkData(object):
    def __init__(self, row_data):
         delimiter = ";"
         link_info = row_data.split(delimiter)

         self.url = link_info[0]
         self.title = link_info[1]
         self.artist = link_info[2]
         self.album = link_info[3]
         self.category = link_info[4]
         self.subcategory = link_info[5]
         self.tag = link_info[6]
         self.date_created = link_info[7]
         self.date_saved = link_info[8]

    def to_string(link):
        return "{0};{1};{2};{3};{4};{5};{6};{7};{8}".format(link.url, link.title, link.artist, link.album, link.category, link.subcategory, link.tag, link.date_created, link.date_saved)


class LinksData(object):
    def __init__(self, data):
        delimiter = "\n"
        links = data.split(delimiter)
        self.links = []

        for link_row in links:
             link_row = link_row.replace("\r", "")
             link = LinkData(link_row)
             self.links.append(link)
