from channels import route_class
from channels.generic.websockets import WebsocketDemultiplexer

from api.bindings import GameBinding


class APIDemultiplexer(WebsocketDemultiplexer):
    http_user = True

    consumers = {
      'games': GameBinding.consumer
    }


channel_routing = [
    route_class(APIDemultiplexer),
]
