######################################
# main liquidsoap development script #
######################################

# author Jonas Ohrstrom <jonas@digris.ch>

########################################
# include configuration                #
########################################

%include "ls_config.liq"
%include "library.liq"

%include "include_dynamic_vars.liq"
%include "include_notify.liq"


silence_threshold = -50.
silence_time = 4.


# log
set("log.file.path",log_file)
set("log.stdout", true)
set("log.level",log_level)

# telnet server
set("server.telnet", true)



######################################
# some functions needed              #
######################################

def fcross(a,b) =
    add(normalize=false,[b,a])
end


######################################
# live recording functions
######################################
def live_start() =
  log("got live source")
  ignore(execute("archives.start"))
end

def live_stop() =
  log("live source has gone")
  ignore(execute("archives.stop"))
end



#######################################################################
# File locations / sources
#######################################################################

#silence = single("/storage/pypo/files/basic/silence.mp3")

# use generated silence, add some noise to not break mp3 encodeing
# silence = amplify(0.00001,noise())
silence = blank()

# transition sound (PCM to test)

jingles_cc = playlist("/storage/pypo/files/jingles/jcc")


fallback_couchcaster = playlist("/storage/pypo/files/fallback_couchcaster")
fallback_couchcaster = audio_to_stereo(fallback_couchcaster)

# default
default = silence

special = request.queue(id="special")



#######################################################################
# Includeing two A/B Queues, daypart & scheduler
# this will give us the sources 'daypart' & 'scheduler' 
#######################################################################

%include "include_daypart.liq"
%include "include_scheduler.liq"

f_scheduler_to_dp_trans = scheduler_to_dp_trans()
f_dp_to_scheduler_trans = dp_to_scheduler_trans()

#source = fallback(track_sensitive=false,transitions=[dp_to_scheduler, scheduler_to_dp],[strip_blank(threshold=silence_threshold,length=silence_time,scheduler),daypart])
source = fallback(track_sensitive=false,transitions=[dp_to_scheduler, f_scheduler_to_dp_trans],[strip_blank(threshold=silence_threshold,length=silence_time,scheduler),daypart])



#####################################
# in-/out-/crossfade
#####################################
# handle the annotate fades
#faded = fade.in(type="log", fade.out(type="log", source))
source = fade.in(fade.out(source))

# add up with a crossfade function (defined above)
source = cross(fcross,source)


#####################################
# Couchcaster & related switches
#####################################
%include "include_live_in.liq"

live = fallback(track_sensitive=false,[strip_blank(threshold=silence_threshold,length=silence_time,live),fallback_couchcaster])
live = switch(track_sensitive=false, [({!live_active},live)])

source = fallback(track_sensitive=false,transitions=[to_live_s, to_scheduler_s],[live, source]) 



#####################################
# Track detection (notifications)
#####################################
source = on_metadata(notify, source)


# special to mix with final source
#source = smooth_add(normal=source,special=special)


#####################################
# Include Monitoring
#####################################
%include "include_monitoring.liq"


#####################################
# Outputs
#####################################

%include "include_alsa.liq"

%include "include_icecast.liq" 
#%include "include_archive.liq" 
    
output.dummy(source)
output.dummy(live_in)
