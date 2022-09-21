from loader import dp
from .acl import ACLMiddleware
from .throttling import ThrottlingMiddleware


if __name__ == "middlewares":
    dp.middleware.setup(ACLMiddleware())
    dp.middleware.setup(ThrottlingMiddleware())
