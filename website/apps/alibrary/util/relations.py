def get_service_by_url(url, service):

    if url.find('facebook.com') != -1:
        service = 'facebook'

    if url.find('youtube.com') != -1:
        service = 'youtube'

    if url.find('discogs.com') != -1:
        if url.find('/master/') != -1:
            service = 'discogs_master'
        else:
            service = 'discogs'

    if url.find('wikipedia.org') != -1:
        service = 'wikipedia'

    if url.find('last.fm') != -1 or url.find('lastfm') != -1:
        service = 'lastfm'

    if url.find('musicbrainz.org') != -1:
        service = 'musicbrainz'

    if url.find('soundcloud.com') != -1:
        service = 'soundcloud'

    if url.find('bandcamp.com') != -1:
        service = 'bandcamp'

    if url.find('itunes.apple.com') != -1:
        service = 'itunes'

    if url.find('linkedin.com') != -1:
        service = 'linkedin'

    if url.find('twitter.com') != -1:
        service = 'twitter'


    if not service:
        service = 'generic'

    return service