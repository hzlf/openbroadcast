########################################
# call pypo api gateway
########################################

def notify(m)

  if m['export_source'] == 'daypart' then

    # daypart can only be playlist
    print('playlist')
    command = "./notify.sh --playing --playlist-type=#{!daypart_playlist_type} --media-id=#{m['media_id']} --export-source=#{m['export_source']} --playlist-id=#{m['playlist_id']}"
    print(command)
    system(command)
    
  else
  
    print('playlist from scheduler')

    # call the notify script
    if !scheduler_playlist_type=='5' then 
      print('livesession')
      command = "./notify.sh --playing --playlist-type=#{!scheduler_playlist_type} --transmission-id=#{!scheduler_transmission_id} --export-source=scheduler --playlist-id=#{!scheduler_playlist_id} --user-id=#{!scheduler_user_id}"
      print(command)
      system(command)
    end
    if !scheduler_playlist_type=='6' then
      print('couchcaster')
      command = "./notify.sh --playing --playlist-type=#{!scheduler_playlist_type} --transmission-id=#{!scheduler_transmission_id} --export-source=scheduler --playlist-id=#{!scheduler_playlist_id} --user-id=#{!scheduler_user_id}"
      print(command)
      system(command)
    end 
    if !scheduler_playlist_type=='7' then
      print('couchcaster')
      command = "./notify.sh --playing --playlist-type=#{!scheduler_playlist_type} --transmission-id=#{!scheduler_transmission_id} --export-source=scheduler --playlist-id=#{!scheduler_playlist_id} --user-id=#{!scheduler_user_id}"
      print(command)
      system(command)
    end 
    if !scheduler_playlist_type=='0' or !scheduler_playlist_type=='1' or !scheduler_playlist_type=='2' or !scheduler_playlist_type=='3' or !scheduler_playlist_type=='4' then
      print('playlist')
      command = "./notify.sh --playing --playlist-type=#{!scheduler_playlist_type} --media-id=#{m['media_id']} --export-source=#{m['export_source']} --playlist-id=#{m['playlist_id']}"
      print(command)
      system(command)
    end

  end

end
