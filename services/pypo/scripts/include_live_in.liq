#######################################################################
# Live input - From external icecast server
#######################################################################


live_in = input.http(id="live_in",poll_delay=2.,autostart=false,buffer=2., max=10.,couchcaster_list)
live_in = buffer(id="buffer_live_in",buffer=.1,fallible=true,live_in)
live_in = mksafe(live_in)


########################################
# record live streams                  #
########################################


title = 'couchcaster_recorded'
output.file(%mp3(bitrate=320), id="archive",start=false,fallible=true,reopen_on_metadata=false,archive_dir ^ "couchcaster_recorded.mp3",live_in)


live_active = ref false
def live_switch(i)
  print(i)
  if i=='1' then
    live_active:=true 
    ignore(server.execute("archive.start"))
  else 
    live_active:=false
    ignore(server.execute("archive.stop"))
    # call archiver & upload script
    if !cc_transmission_id != '0' and !scheduler_playlist_type == '6' then
      system("./archive.sh --move --user-id=#{!cc_user_id} --playlist-id=#{!cc_playlist_id} --transmission-id=#{!cc_transmission_id}")
    end
    
    # reset id's
    cc_playlist_id := '0'
    cc_user_id := '0'
    cc_transmission_id := '0'  
  
  end
  print(live_active)
  "Done"
end
server.register(namespace="live","active", live_switch)

#live_in = limit(live_in)

live = switch(track_sensitive=false, [({!live_active},live_in)])

to_live_s = to_live(jingles_cc)
to_scheduler_s = to_scheduler()
