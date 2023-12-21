from zeep import Plugin


class MyLoggingPlugin(Plugin):
    def ingress(self, envelope, http_headers, operation):
        return envelope, http_headers

    def egress(self, envelope, http_headers, operation, binding_options):
        http_headers['Content-Type'] = 'text/xml; charset=utf-8;'
        return envelope, http_headers