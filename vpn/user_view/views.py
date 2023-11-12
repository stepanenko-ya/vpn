from django import forms
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView, ListView
from .models import User, Site, UserStatistics
from urllib.parse import urlparse
from .forms import UserRegisterForm, UserLoginForm, SiteForm
import requests
from django.db.models import F
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"


class RegisterUser(CreateView):
    form_class = UserRegisterForm
    template_name = 'authorization/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registration'
        return context


class LoginUser(LoginView):
    form_class = UserLoginForm
    template_name = 'authorization/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login'
        return context

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(604800)  # remember me works 7days
        return super().form_valid(form)


@login_required
def logout_user(request):
    logout(request)
    return redirect('login')


class UserProfile(LoginRequiredMixin, UpdateView):
    template_name = 'core/profile.html'
    model = User
    success_url = reverse_lazy('home')

    fields = [
        'first_name', 'last_name', 'email', 'phone', 'username'
    ]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in self.fields:
            form.fields[field].widget = forms.TextInput(
                attrs={'class': 'input'})
        return form

    def get_object(self, queryset=None):
        return self.request.user


class StatisticsView(LoginRequiredMixin, ListView):
    template_name = 'core/statistics.html'
    context_object_name = 'table_data'
    model = UserStatistics

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Statistics page'
        context['table_column_names'] = [
            'Site name', 'URL', 'Page transitions', 'Data sent',
            'Data received'
        ]
        return context

    def get_queryset(self):
        user = self.request.user
        queryset = self.model.objects.select_related('user', 'website').filter(
            user=user)
        if queryset:
            result = [
                {
                    'site_name': data.website.name,
                    'url': data.website.url,
                    'page_transitions': data.page_transitions,
                    'data_sent': data.data_sent,
                    'data_received': data.data_received

                } for data in queryset]
            return result


class SitesList(LoginRequiredMixin, ListView):
    context_object_name = 'table_data'
    template_name = 'core/sites_list.html'
    model = Site

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'List of sites'
        context['table_column_names'] = ['Site name', 'URL', 'Actions']
        return context

    def get_queryset(self):
        result = []
        user = self.request.user
        queryset = self.model.objects.select_related('user').filter(user=user)

        if queryset:
            for data in queryset:
                url = data.url
                parsed_url = urlparse(url)
                site_name = data.name.replace(' ', '_')
                new_url = f'/{site_name}/{parsed_url.netloc}{parsed_url.path}'

                result.append({
                    'name': data.name,
                    'url': url,
                    'new_url': new_url
                })
        return result


class AddSite(LoginRequiredMixin, CreateView):
    template_name = 'core/site_creation.html'
    model = Site
    form_class = SiteForm
    success_url = reverse_lazy('sites_list')

    def form_valid(self, form):
        scheme = urlparse(form.cleaned_data['url']).scheme
        site = form.save(commit=False)
        site.name = form.cleaned_data['name'].replace(' ', '_')
        site.user_id = self.request.user.id
        site.protocol_security = scheme == 'https'
        site.save()
        return super().form_valid(form)


class HomePage(LoginRequiredMixin, TemplateView):
    template_name = 'core/home.html'


def get_html(url):
    statistics_dict = {
        'sent_bytes': 0,
        'received_bytes': 0,
        'page_transitions': 0
    }
    try:
        req = requests.get(url, headers={"user-agent": USER_AGENT}, timeout=10)
        req.raise_for_status()
        content = req.text
        statistics_dict['sent_bytes'] = len(
            req.request.body) if req.request.body else 0
        statistics_dict['received_bytes'] = len(
            req.content) if req.content else 0
        statistics_dict['page_transitions'] = 1 if req.content else 0

    except requests.exceptions.RequestException as ex:
        content = f"An error occurred while requesting the server.\nError {ex}"

    return [content, statistics_dict]


def parser_content(content, origin_domain, site_obj, protocol_security):
    soup = BeautifulSoup(content, features='lxml')
    finders_element = soup.find_all(name="a", href=True)
    for el in finders_element:
        if (origin_domain in el['href'] and protocol_security in el['href']
                or not protocol_security in el['href']):
            if protocol_security in el['href']:
                el['href'] = el['href'].replace(
                    protocol_security, '').replace(origin_domain, '')

            el['href'] = \
                f"/{site_obj.name}/{origin_domain}/{el['href'].strip('/')}"
    return soup


def replace_content(content, protocol_security, origin_domain):
    base_url = f'{protocol_security}{origin_domain}'
    content = content.replace('src="/media/', f'src="{base_url}/media/')
    content = content.replace('href="/media/', f'href="{base_url}/media/')
    content = content.replace('src="/static/', f'src="{base_url}/static/')
    content = content.replace('href="/static/', f'src="{base_url}/static/')
    return content


def update_statistics(bytes_count, site_obj):
    statistics_obj, created = UserStatistics.objects.get_or_create(
        user_id=site_obj.user.id,
        website_id=site_obj.id,
    )
    statistics_obj.data_sent = F('data_sent') + bytes_count['sent_bytes']
    statistics_obj.data_received = F('data_received') + bytes_count[
        'received_bytes']
    statistics_obj.page_transitions = F('page_transitions') + bytes_count[
        'page_transitions']
    statistics_obj.save()


@login_required
def test(request, url_path, site_name):
    origin_domain = url_path.split('/')[0]
    content = ''
    site_obj = Site.objects.select_related('user').filter(
        url__icontains=origin_domain).first()
    if site_obj:
        protocol_security = \
            'https://' if site_obj.protocol_security else 'http://'
        content, bytes_count = get_html(f'{protocol_security}{url_path}')
        update_statistics(bytes_count, site_obj)
        content = replace_content(content, protocol_security, origin_domain)
        content = parser_content(
            content, origin_domain, site_obj, protocol_security
        )

    return HttpResponse(content)
