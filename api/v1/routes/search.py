from http import HTTPStatus

from sanic import Request, json

from ...caching import cache_response
from ...utils import log_exception
from ..extractors import search as search_extractor


@cache_response(300)
async def handler(request: Request):
    "Procura pelo filme desejado no site"
    query = request.args.get('q')
    if not query:
        return json(
            body={'error': 'query not specified'},
            status=HTTPStatus.BAD_REQUEST
        )
    page = int(request.args.get("page", "1"))
    try:
        results, err_info = await search_extractor.search(query, page)
    except Exception as err:
        log_exception(err)
        return json(
            body={'error': f'failed to search: {str(err)}'},
            status=HTTPStatus.INTERNAL_SERVER_ERROR
        )
    if err_info is not None:
        return json({'error': err_info}, HTTPStatus.BAD_REQUEST)
    return json(
        body={
            'page': {'number': page, 'has_next': results[1]},
            'results': list(map(lambda r: r.dict(), results[0]))
        },
        status=HTTPStatus.OK
    )
