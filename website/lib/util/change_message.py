from django.utils.text import capfirst, get_text_list
from django.utils.encoding import force_unicode

def construct(request, form, formsets):
    """
    Construct a change message from a changed object.
    """
    change_message = []
    if form.changed_data:
        
        try:
            form.changed_data.remove('d_tags')
        except:
            pass
            
        if len(form.changed_data) > 0:
            change_message.append(_('Changed %s. \n') % get_text_list(form.changed_data, _('and')))

    if formsets:
        for formset in formsets:
            for added_object in formset.new_objects:
                change_message.append(_('Added %(name)s "%(object)s". \n')
                                      % {'name': force_unicode(added_object._meta.verbose_name),
                                         'object': force_unicode(added_object)})
            for changed_object, changed_fields in formset.changed_objects:              
                change_message.append(_('Changed %(list)s for %(name)s "%(object)s". \n')
                                      % {'list': get_text_list(changed_fields, _('and')),
                                         'name': force_unicode(changed_object._meta.verbose_name),
                                         'object': force_unicode(changed_object)})
                
            for deleted_object in formset.deleted_objects:
                change_message.append(_('Deleted %(name)s "%(object)s". \n')
                                      % {'name': force_unicode(deleted_object._meta.verbose_name),
                                         'object': force_unicode(deleted_object)})
    change_message = ' '.join(change_message)
    return change_message or _('Nothing changed.')