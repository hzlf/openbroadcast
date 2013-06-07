#####################################
# Monitoring Outputs
#####################################

# finally the output | mp3
#clock(id="clock_monitoring_scheduler",
#  output.icecast(%mp3(bitrate=64),
#    host = icecast_host, port = icecast_port,
#    password = icecast_pass, mount = mount_scheduler,
#    fallible = true,
#    restart = true,
#    restart_delay = 5,
#    buffer(source)))
    
#clock(id="clock_monitoring_daypart",
#  output.icecast(%mp3(bitrate=64),
#    host = icecast_host, port = icecast_port,
#    password = icecast_pass, mount = mount_daypart,
#    fallible = true,
#    restart = true,
#    restart_delay = 5,
#    buffer(source)))
    
#clock(id="clock_monitoring_live_in",
#  output.icecast(%mp3(bitrate=64),
#    host = icecast_host, port = icecast_port,
#    password = icecast_pass, mount = mount_live_in,
#    fallible = true,
#    restart = true,
#    restart_delay = 5,
#    buffer(source)))
    
clock(id="clock_monitoring_final",
  output.icecast(%mp3(bitrate=64),
    host = icecast_host, port = icecast_port,
    password = icecast_pass, mount = mount_final,
    fallible = true,
    restart = true,
    restart_delay = 5,
    buffer(source)))
    