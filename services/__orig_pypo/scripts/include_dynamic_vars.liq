#######################################################################
# Dynamic variables
#######################################################################

playlist_id = ref '0'
user_id = ref '0'
transmission_id = ref '0'
playlist_type = ref '0'

# global object id's
def set_user_id(s)
  user_id := s
end

def set_playlist_id(s)
  playlist_id := s
end

def set_transmission_id(s)
  transmission_id := s
end

def set_playlist_type(s)
  playlist_type := s
end


server.register(namespace="vars", "user_id", fun (s) ->  begin set_user_id(s) "Done!" end)
server.register(namespace="vars", "playlist_id", fun (s) ->  begin set_playlist_id(s) "Done!" end)
server.register(namespace="vars", "transmission_id", fun (s) ->  begin set_transmission_id(s) "Done!" end)
server.register(namespace="vars", "playlist_type", fun (s) ->  begin set_playlist_type(s) "Done!" end)


# separated by instance

daypart_playlist_id = ref '0'
daypart_user_id = ref '0'
daypart_transmission_id = ref '0'
daypart_playlist_type = ref '0'

# global object id's
def set_daypart_user_id(s)
  daypart_user_id := s
end

def set_daypart_playlist_id(s)
  daypart_playlist_id := s
end

def set_daypart_transmission_id(s)
  daypart_transmission_id := s
end

def set_daypart_playlist_type(s)
  daypart_playlist_type := s
end


server.register(namespace="vars_daypart", "user_id", fun (s) ->  begin set_daypart_user_id(s) "Done!" end)
server.register(namespace="vars_daypart", "playlist_id", fun (s) ->  begin set_daypart_playlist_id(s) "Done!" end)
server.register(namespace="vars_daypart", "transmission_id", fun (s) ->  begin set_daypart_transmission_id(s) "Done!" end)
server.register(namespace="vars_daypart", "playlist_type", fun (s) ->  begin set_daypart_playlist_type(s) "Done!" end)



scheduler_playlist_id = ref '0'
scheduler_user_id = ref '0'
scheduler_transmission_id = ref '0'
scheduler_playlist_type = ref '0'

# global object id's
def set_scheduler_user_id(s)
  scheduler_user_id := s
end

def set_scheduler_playlist_id(s)
  scheduler_playlist_id := s
end

def set_scheduler_transmission_id(s)
  scheduler_transmission_id := s
end

def set_scheduler_playlist_type(s)
  scheduler_playlist_type := s
end


server.register(namespace="vars_scheduler", "user_id", fun (s) ->  begin set_scheduler_user_id(s) "Done!" end)
server.register(namespace="vars_scheduler", "playlist_id", fun (s) ->  begin set_scheduler_playlist_id(s) "Done!" end)
server.register(namespace="vars_scheduler", "transmission_id", fun (s) ->  begin set_scheduler_transmission_id(s) "Done!" end)
server.register(namespace="vars_scheduler", "playlist_type", fun (s) ->  begin set_scheduler_playlist_type(s) "Done!" end)





# couchcaster related id's

cc_playlist_id = ref '0'
cc_user_id = ref '0'
cc_transmission_id = ref '0'

# global object id's
def set_cc_user_id(s)
  cc_user_id := s
end

def set_cc_playlist_id(s)
  cc_playlist_id := s
end

def set_cc_transmission_id(s)
  cc_transmission_id := s
end



server.register(namespace="vars_cc", "user_id", fun (s) ->  begin set_cc_user_id(s) "Done!" end)
server.register(namespace="vars_cc", "playlist_id", fun (s) ->  begin set_cc_playlist_id(s) "Done!" end)
server.register(namespace="vars_cc", "transmission_id", fun (s) ->  begin set_cc_transmission_id(s) "Done!" end)

