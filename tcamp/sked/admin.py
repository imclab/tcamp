from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from taggit.models import Tag, TaggedItem
from sked.models import Event, Location, Session


class SessionTagsListFilter(admin.SimpleListFilter):
    title = _('tag')

    parameter_name = 'tag'

    def lookups(self, request, model_admin):
        items = TaggedItem.objects.filter(content_type__name='session', content_type__app_label='sked')
        tags = Tag.objects.filter(taggit_taggeditem_items__in=items).distinct().order_by('name')
        return tuple([(t.name, t.name) for t in tags])

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(tags__name__in=[self.value()])


class SessionInline(admin.StackedInline):
    model = Session


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'start_date',
                    'end_date', 'is_public', )
    list_filter = ('is_public', )
    date_hierarchy = 'start_date'
    prepopulated_fields = {'slug': ('name', )}
    search_fields = ('name', )
    inlines = (SessionInline, )


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'is_official', )
    list_editable = ('event', 'is_official', )
    list_filter = ('event', )
    search_fields = ('name', )


class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'speaker_names', 'start_time',
                    'location', 'is_public', 'published_by', )
    list_editable = ('start_time', 'location', )
    readonly_fields = ('is_public', )
    list_filter = (SessionTagsListFilter, 'published_by', )
    prepopulated_fields = {'slug': ('title', )}
    search_fields = ('title', 'description', 'speakers')
    date_hierarchy = 'start_time'
    actions = ['make_public', 'unpublish', ]
    raw_id_fields = ('location', )
    autocomplete_lookup_fields = {
        'fk': ['location', ]
    }

    def make_public(modeladmin, request, queryset):
        for obj in queryset.filter():
            obj.__dict__.update(is_public=True, published_by=request.user)
            obj.save()
    make_public.short_description = 'Make selected sessions public'

    def unpublish(modeladmin, request, queryset):
        for obj in queryset.filter():
            obj.__dict__.update(is_public=False, published_by=request.user)
            obj.save()
    unpublish.short_description = 'Unpublish selected sessions'


admin.site.register(Event, EventAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Session, SessionAdmin)
