# This VCL config file is adapted from template.vcl in http://pypi.python.org/pypi/plone.recipe.varnish
backend default {
    .host = "127.0.0.1";
    .port = "8080";
    .first_byte_timeout = 300s; /* varnish v2.0.3 or later only */
    .probe = {
        .url = "/";
        .timeout = 1s;
        .interval = 5s;
        .window = 1;
        .threshold = 1;
    }
}


sub vcl_recv {
    # unless sessionid/csrftoken is in the request, don't pass ANY cookies (referral_source, utm, etc)
    if (req.request == "GET" && (req.url ~ "^/static" || (req.http.cookie !~ "sessionid" && req.http.cookie !~ "csrftoken"))) {
        remove req.http.Cookie;
    }

    # normalize accept-encoding to account for different browsers
    # see: https://www.varnish-cache.org/trac/wiki/VCLExampleNormalizeAcceptEncoding
    if (req.http.Accept-Encoding) {
        if (req.http.Accept-Encoding ~ "gzip") {
            set req.http.Accept-Encoding = "gzip";
        } elsif (req.http.Accept-Encoding ~ "deflate") {
            set req.http.Accept-Encoding = "deflate";
        } else {
            # unknown algorithm
            remove req.http.Accept-Encoding;
        }
    }
}

sub vcl_fetch {
    # static files always cached
    if (req.url ~ "^/static") {
       unset beresp.http.set-cookie;
       return (deliver);
    }
    set beresp.do_esi = true; /* Do ESI processing               */
    set beresp.ttl = 24 h;

    # pass through for anything with a session/csrftoken set
    if (beresp.http.set-cookie ~ "sessionid" || beresp.http.set-cookie ~ "csrftoken") {
       return (hit_for_pass);
    } else {
       return (deliver);
    }
}