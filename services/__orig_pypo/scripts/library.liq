# Define a transition that fades out the
# old source, adds a single, and then 
# plays the new source
def to_live(jingle,old,new) = 
  # Fade out old source
  old = fade.final(old)
  # Supperpose the jingle
  s = add([jingle,old])
  # Compose this in sequence with
  # the new source
  
  #new = fade.in(new)
  
  sequence(merge=true,[s,new])
  
  #add(normalize=false,[s,new])
  
end

def to_scheduler(old,new) = 
  # We skip the file
  # currently in new
  # in order to being with
  # a fresh file
  # source.skip(new) 
  sequence([old,new])
end

# A transition when switching back to files:
def to_file(old,new) =
  # We skip the file
  # currently in new
  # in order to being with
  # a fresh file
  # source.skip(new) 
  sequence([old,new])
end


def dp_to_scheduler(old,new) = 
  #old = fade.final(type='lin',duration=5.1,old)
  source.skip(old) 
  sequence([old,new])
end

def scheduler_to_dp(old,new) = 
  source.skip(new) 
  sequence([old,new])
end


#def dp_to_scheduler_trans(old,new) = 
#  old = fade.final(old)
#  sequence([old,new])
#end


def dp_to_scheduler_trans(jingle,old,new) = 
  old = fade.final(type="sin",duration=1.1,old)
  old = add([jingle,old])
  sequence([old,new])
end




def scheduler_to_dp_trans(old,new) = 
  new = fade.in(new)
  sequence([old,new])
end

