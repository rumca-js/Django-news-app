from django import forms
from .models import LinkDataModel

# https://docs.djangoproject.com/en/4.1/ref/forms/widgets/

#class NewLinkForm(forms.Form):
#    """
#    New link form
#    """
#    class Meta:
#        model = LinkDataModel
#        fields = ['url', 'category', 'subcategory', 'artist', 'album', 'title', 'date_created']


class NewLinkForm(forms.Form):
    """
    New link form
    """
    url = forms.CharField(label='Url', max_length = 500)
    category = forms.CharField(label='Category', max_length = 100)
    subcategory = forms.CharField(label='Subcategory', max_length = 100)
    artist = forms.CharField(label='Artist', max_length = 100)
    album = forms.CharField(label='Album', max_length = 100)
    title = forms.CharField(label='Title', max_length = 200)
    date_created = forms.DateTimeField(label='Data')

    class Meta:
        model = LinkDataModel
        exclude = ('date_created',)

    def __init__(self, *args, **kwargs):
        init_obj = kwargs.pop('init_obj', ())

        super().__init__(*args, **kwargs)

        if init_obj != ():
            self.fields['url'] = forms.CharField(label='Url', max_length = 500, initial=init_obj.url)
            self.fields['category'] = forms.CharField(label='Category', max_length = 100, initial=init_obj.category)
            self.fields['subcategory'] = forms.CharField(label='Subcategory', max_length = 100, initial=init_obj.subcategory)
            self.fields['artist'] = forms.CharField(label='Artist', max_length = 100, initial=init_obj.artist)
            self.fields['album'] = forms.CharField(label='Album', max_length = 100, initial=init_obj.album)
            self.fields['title'] = forms.CharField(label='Title', max_length = 100, initial=init_obj.title)
            self.fields['date_created'] = forms.DateTimeField(label='Data', initial=init_obj.date_created)
        else:
            from django.utils.timezone import now
            self.fields['date_created'] = forms.DateTimeField(label='Data', initial=now)

    def to_model(self):
        url = self.cleaned_data['url']
        artist = self.cleaned_data['artist']
        album = self.cleaned_data['album']
        category = self.cleaned_data['category']
        subcategory = self.cleaned_data['subcategory']
        title = self.cleaned_data['title']
        date_created = self.cleaned_data['date_created']

        record = LinkDataModel(url=url,
                                    artist=artist,
                                    album=album,
                                    title=title,
                                    category=category,
                                    subcategory=subcategory,
                                    date_created=date_created)

        return record


class ImportLinksForm(forms.Form):
    """
    Import links form
    """
    rawlinks = forms.CharField(widget=forms.Textarea(attrs={'name':'rawlinks', 'rows':30, 'cols':100}))


class ChoiceForm(forms.Form):
    """
    Category choice form
    """

    category = forms.CharField(widget=forms.Select(choices=()))
    subcategory = forms.CharField(widget=forms.Select(choices=()))
    artist = forms.CharField(widget=forms.Select(choices=()))
    album = forms.CharField(widget=forms.Select(choices=()))

    def __init__(self, *args, **kwargs):
        self.args = kwargs.pop('args', ())
        super().__init__(*args, **kwargs)

    def get_filtered_objects(self):
        parameter_map = self.get_filter_args()
        self.filtered_objects = LinkDataModel.objects.filter(**parameter_map)
        return self.filtered_objects

    def create(self):
        # how to unpack dynamic forms
        # https://stackoverflow.com/questions/60393884/how-to-pass-choices-dynamically-into-a-django-form
        categories = self.get_filtered_objects_values('category')
        subcategories = self.get_filtered_objects_values('subcategory')
        artists = self.get_filtered_objects_values('artist')
        albums = self.get_filtered_objects_values('album')

        # custom javascript code
        # https://stackoverflow.com/questions/10099710/how-to-manually-create-a-select-field-from-a-modelform-in-django
        attr = {"onchange" : "this.form.submit()"}

        # default form value
        # https://stackoverflow.com/questions/604266/django-set-default-form-values
        category_init = self.get_init('category')
        subcategory_init = self.get_init('subcategory')
        artist_init = self.get_init('artist')
        album_init = self.get_init('album')

        self.fields['category'] = forms.CharField(widget=forms.Select(choices=categories, attrs=attr), initial=category_init)
        self.fields['subcategory'] = forms.CharField(widget=forms.Select(choices=subcategories, attrs=attr), initial=subcategory_init)
        self.fields['artist'] = forms.CharField(widget=forms.Select(choices=artists, attrs=attr), initial=artist_init)
        self.fields['album'] = forms.CharField(widget=forms.Select(choices=albums, attrs=attr), initial=album_init)

    def get_init(self, column):
        filters = self.get_filter_args()
        if column in filters:
            return filters[column]
        else:
            return "Any"

    def get_filtered_objects_values(self, field):
        values = set()
        values.add("Any")

        for val in self.filtered_objects.values(field):
            if str(val).strip() != "":
                values.add(val[field])

        dict_values = self.to_dict(values)

        return dict_values

    def to_dict(self, alist):
        result = []
        for item in sorted(alist):
            if item.strip() != "":
                result.append((item, item))
        return result

    def get_filter_args(self):
        parameter_map = {}

        category = self.args.get("category")
        if category and category != "Any":
           parameter_map['category'] = category

        subcategory = self.args.get("subcategory")
        if subcategory and subcategory != "Any":
           parameter_map['subcategory'] = subcategory

        artist = self.args.get("artist")
        if artist and artist != "Any":
           parameter_map['artist'] = artist

        album = self.args.get("album")
        if album and album != "Any":
           parameter_map['album'] = album

        return parameter_map

    def get_filter_string(self):
        filters = self.get_filter_args()
        filter_string = ""
        for key in filters:
            filter_string += "&{0}={1}".format(key, filters[key])

        return filter_string
