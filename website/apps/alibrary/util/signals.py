# library post save

from filer.models.foldermodels import Folder

def library_post_save(sender, **kwargs):

    obj = kwargs['instance']
    
    print 'library_post_save signal:'
    print 'label:',
    print obj._meta.app_label
    print obj._meta.object_name.lower()
    
    if not obj.folder:
        print 'no folder, try to create'
        app_folder, created = Folder.objects.get_or_create(name=obj._meta.app_label)
        print 'app_folder creates'
        model_folder, created = Folder.objects.get_or_create(name=obj._meta.object_name.lower(), parent=app_folder)
        print 'model_folder creates'
        obj.folder, created = Folder.objects.get_or_create(name=obj.uuid, parent=model_folder)
        print 'folder assigned'
        obj.save()
        print 'obj saved'
        
    else:
        print 'have folder'