import discogs_client as discogs
def discogs_image_by_url(url, type='uri'):
    
    image = None
    
    discogs.user_agent = "NRG Processor 0.01 http://anorg.net/"
    
    try:
        id = url.split('/')
        id = id[-1]
        
        print 'DISCOGS ID: %s' % id
        
        release = discogs.Release(int(id))
        
        #i = release.data['images']
        
        print release
        
        imgs = release.data['images']
        
        #images = i
        
        for img in imgs:
            if img['type'] == 'primary':
                print img
                image = img[type]
                #image = img['uri']
        
        
         
        
    except Exception, e:
        print 'discogs_images_by_url error'
        print e
        pass
    
    print image
    
    return image