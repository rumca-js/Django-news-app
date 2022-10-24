from django.shortcuts import render
from django.views import generic
from django.urls import reverse

from django.db.models.query import QuerySet
from django.db.models.query import EmptyQuerySet

from .models import LinkDataModel, LinksData, LinkData
from .forms import NewLinkForm, ImportLinksForm, ChoiceForm
from .basictypes import *
from pathlib import Path


# https://stackoverflow.com/questions/66630043/django-is-loading-template-from-the-wrong-app
app_name = Path("news")


def init_context(context):
    context["page_title"] = "YouTube Index"
    context["django_app"] = str(app_name)
    context["base_generic"] = str(app_name / "base_generic.html")

    c = Configuration.get_object(str(app_name))
    context['app_version'] = c.version

    return context

def get_context(request = None):
    context = {}
    context = init_context(context)
    return context


def index(request):
    # Generate counts of some of the main objects
    num_links = LinkDataModel.objects.all().count()

    context = get_context(request)

    context['num_links'] = num_links

    # Render the HTML template index.html with the data in the context variable
    return render(request, app_name / 'index.html', context=context)


class LinkListView(generic.ListView):
    model = LinkDataModel
    context_object_name = 'link_list'
    paginate_by = 1000

    def get_queryset(self):
        self.filter_form = ChoiceForm(args = self.request.GET)
        return self.filter_form.get_filtered_objects()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LinkListView, self).get_context_data(**kwargs)
        context = init_context(context)
        # Create any data and add it to the context

        self.filter_form.create()
        self.filter_form.method = "GET"
        self.filter_form.action_url = reverse('news:links')

        context['category_form'] = self.filter_form
        context['page_title'] += " - Link list"

        return context


class LinkDetailView(generic.DetailView):
    model = LinkDataModel

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LinkDetailView, self).get_context_data(**kwargs)
        context = init_context(context)

        context['date_created'] = self.object.date_created
        context['page_title'] += " - " + self.object.title
        return context


def add_link(request):
    context = get_context(request)
    context['page_title'] += " - Add link"

    if not request.user.is_authenticated:
        return render(request, app_name / 'missing_rights.html', context)

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        method = "POST"

        # create a form instance and populate it with data from the request:
        form = NewLinkForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            form.save()

            ft = LinkDataModel.objects.filter(url=request.POST.get('url'))
            if ft.exists():
                context['form'] = form
                context['link'] = ft[0]
                return render(request, app_name / 'add_link_exists.html', context)
            else:
                model.save()

                context['form'] = form
                context['link'] = model
                return render(request, app_name / 'add_link_added.html', context)
        #    # process the data in form.cleaned_data as required
        #    # ...
        #    # redirect to a new URL:
        #    #return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NewLinkForm()
        form.method = "POST"
        form.action_url = reverse('news:addlink')
        context['form'] = form

    return render(request, app_name / 'form_basic.html', context)


def import_links(request):
    summary_text = ""
    context = get_context(request)
    context['page_title'] += " - Import links"

    if not request.user.is_authenticated:
        return render(request, app_name / 'missing_rights.html', context)

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        method = "POST"

        # create a form instance and populate it with data from the request:
        form = ImportLinksForm(request.POST)

        if form.is_valid():
            rawlinks = form.cleaned_data['rawlinks']
            links = LinksData(rawlinks)
            for link in links.links:
                if LinkDataModel.objects.filter(url=link.url).exists():
                    summary_text += link.title + " " + link.url + " " + link.artist + " Error: Already present in db\n"
                else:
                    record = LinkDataModel(url=link.url,
                                                artist=link.artist,
                                                album=link.album,
                                                title=link.title,
                                                category=link.category,
                                                subcategory=link.subcategory,
                                             date_created=link.date_created)
                    record.save()
                    summary_text += link.title + " " + link.url + " " + link.artist + " OK\n"

        context["form"] = form
        context['summary_text'] = summary_text
        return render(request, app_name / 'import_links_summary.html', context)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ImportLinksForm()
        form.method = "POST"
        form.action_url = reverse('news:importlinks')

        context["form"] = form
        context['page_title'] += " - Import links"
        return render(request, app_name / 'form_basic.html', context)


def remove_link(request, pk):
    context = get_context(request)
    context['page_title'] += " - Remove link"

    if not request.user.is_authenticated:
        return render(request, app_name / 'missing_rights.html', context)

    ft = LinkDataModel.objects.filter(id=pk)
    if ft.exists():
        ft.delete()
        return render(request, app_name / 'remove_link_ok.html', context)
    else:
        return render(request, app_name / 'remove_link_nok.html', context)


def remove_all_links(request):
    context = get_context(request)
    context['page_title'] += " - Remove all links"

    if not request.user.is_authenticated:
        return render(request, app_name / 'missing_rights.html', context)

    ft = LinkDataModel.objects.all()
    if ft.exists():
        ft.delete()
        return render(request, app_name / 'remove_all_links_ok.html', context)
    else:
        return render(request, app_name / 'remove_all_links_nok.html', context)



def export_data(request):
    context = get_context(request)
    context['page_title'] += " - Export data"
    summary_text = ""

    links = LinkDataModel.objects.all()
    for link in links:
        data = LinkData.to_string(link)
        summary_text += data + "\n"

    context["summary_text"] = summary_text

    return render(request, app_name / 'summary_present.html', context)


from .prjconfig import Configuration

def configuration(request):
    context = get_context(request)
    context['page_title'] += " - Configuration"

    if not request.user.is_authenticated:
        return render(request, app_name / 'missing_rights.html', context)
    
    c = Configuration.get_object(str(app_name))
    context['directory'] = c.directory
    context['version'] = c.version
    context['database_size_bytes'] = get_directory_size_bytes(c.directory)
    context['database_size_kbytes'] = get_directory_size_bytes(c.directory)/1024
    context['database_size_mbytes'] = get_directory_size_bytes(c.directory)/1024/1024

    if c.server_log_file.exists():
        with open(c.server_log_file.resolve(), "r") as fh:
             context['server_log_data'] = fh.read()

    return render(request, app_name / 'configuration.html', context)


def edit_link(request, pk):
    context = get_context(request)
    context['page_title'] += " - Edit link"
    context['pk'] = pk

    if not request.user.is_authenticated:
        return render(request, app_name / 'missing_rights.html', context)

    ft = LinkDataModel.objects.filter(id=pk)
    if not ft.exists():
       return render(request, app_name / 'edit_link_does_not_exist.html', context)

    obj = ft[0]

    if request.method == 'POST':
        form = NewLinkForm(request.POST)
        context['form'] = form

        if form.is_valid():
            model = form.to_model()

            ft = LinkDataModel.objects.filter(url=model.url)
            if ft.exists():
                ft.delete()
                model.save()

                context['link'] = ft[0]
                return render(request, app_name / 'edit_link_ok.html', context)
            else:
                model.save()
                return render(request, app_name / 'edit_link_does_not_exist.html', context)

        context['summary_text'] = "Could not edit link"

        return render(request, app_name / 'summary_present', context)
    else:
        form = NewLinkForm(init_obj=obj)
        form.method = "POST"
        form.action_url = reverse('news:editlink',args=[pk])
        context['form'] = form
        return render(request, app_name / 'basic_form.html', context)
