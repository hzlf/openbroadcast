import discogs_client as discogs

import logging
import time

log = logging.getLogger(__name__)

def discogs_image_by_url(url, type='uri'):
    
    log = logging.getLogger('importer.base.discogs_image_by_url')
    
    image = None
    
    discogs.user_agent = "NRG Processor 0.01 http://anorg.net/"
    
    try:
        id = url.split('/')
        id = id[-1]

        log.debug('Lookup image for discog id: %s' % (id))
        
        if '/master/' in url:
            log.debug('Type is "master-release"')
            item = discogs.MasterRelease(int(id))
        
        if '/release/' in url:
            log.debug('Type is "release"')
            item = discogs.Release(int(id))
        
        if '/artist/' in url:
            log.debug('Type is "artist"')
            item = discogs.Artist(id)
            

            
        time.sleep(1.1)

        
        imgs = item.data['images']
        have_img = False
        
        for img in imgs:
            if img['type'] == 'primary':
                print img
                image = img[type]
                have_img = True
     
        if not have_img:
            for img in imgs:
                if img['type'] == 'secondary':
                    print img
                    image = img[type]


    except Exception, e:
        log.info('Unable to get image: %s', e)


    log.debug('Got image at: %s' % (image))

    return image

def discogs_id_by_url(url, type='uri'):
    
    log = logging.getLogger('importer.base.discogs_artist_id_by_url')
    
    discogs_id = None
    
    discogs.user_agent = "NRG Processor 0.01 http://anorg.net/"
    
    try:
        id = url.split('/')
        id = id[-1]
        
        if '/master/' in url:
            log.debug('Type is "master-release"')
            item = discogs.MasterRelease(int(id))
        
        if '/release/' in url:
            log.debug('Type is "release"')
            item = discogs.Release(int(id))
        
        if '/artist/' in url:
            log.debug('Type is "artist"')
            item = discogs.Artist(id)
                        
        time.sleep(1.1)

        
        discogs_id = item.data['id']



    except Exception, e:
        log.info('Unable to get id: %s', e)


    log.debug('Got id: %s' % (discogs_id))

    return discogs_id