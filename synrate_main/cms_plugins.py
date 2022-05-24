from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import FAQ, INTRO, ABOUT, TITLE, CONTACT
from django.utils.translation import gettext_lazy as _


@plugin_pool.register_plugin
class FAQPlugin(CMSPluginBase):
    model = FAQ
    name = _("FAQ блок")
    render_template = "faq_plugin.html"
    cache = False

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        return context


@plugin_pool.register_plugin
class IntroPlugin(CMSPluginBase):
    model = INTRO
    name = _("Титульный плагин")
    render_template = "intro_plugin.html"
    cache = False

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        return context


@plugin_pool.register_plugin
class TitlePlugin(CMSPluginBase):
    model = TITLE
    name = _("Заголовок страницы")
    render_template = "title_plugin.html"
    cache = False

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        return context


@plugin_pool.register_plugin
class AboutPlugin(CMSPluginBase):
    model = ABOUT
    name = _("About Us плагин")
    render_template = "about_plugin.html"
    cache = False

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        return context


@plugin_pool.register_plugin
class ContactPlugin(CMSPluginBase):
    model = CONTACT
    name = _("Контакт")
    render_template = "contact_plugin.html"
    cache = False

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        return context

