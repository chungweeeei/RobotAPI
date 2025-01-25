from fastapi import (
    APIRouter,
    Request,
    status,
    HTTPException
)

import structlog

from io import BytesIO

from starlette.requests import ClientDisconnect

"""
    If you get data from the Request object directly, it won't be
    validated, converted or documented by FastAPI.
"""

def init_test_router() -> APIRouter:

    test_router = APIRouter(prefix="", tags=["Test"])

    """
        Let's imagine you want to get the client's IP address/host inside of your path operation function.

        - Method:
            The request method is accessed as request.method
        
        - URL:
            The request URL is accessed as request.url.
            The property is a string-like object that exposes all the components that can be parsed out of the URL.

            For example: request.url.path, request.url.port, request.url.scheme.

        - Headers:
            Headers are exposed as an immutable, case-insensitive, multi-dict.

            For example: request.headers['content-type']

        - Query Parameters:
            Query parameters are exposed as an immutable multi-dict.

            For example: request.query_params['search']

        - Path Parameters:
            Router path parameters are exposed as a dictionary interface.

            For example: request.path_params['username']
        
        - Cookies:
            Cookies are exposed as a regular dictionary interface.

            For example: request.cookies.get('mycookie')

        - Body:
            There are a few different interfaces for returning the body of the request:

            The request body as bytes: await request.body()

            The request body, parsed as form data or multipart: async with request.form() as form:

            The request body, parsed as JSON: await request.json()
    """

    @test_router.get("/v1/test/client_info")
    def get_client_info(request: Request):
        client_host = request.client.host
        return {"client_host": client_host}



    @test_router.post("/v1/test/client")
    async def get_client(request: Request):

        structlog.get_logger().info("request headers: {}".format(request.headers))

        test_bytes = BytesIO()

        try:
            async for chunk in request.stream():
                test_bytes.write(chunk)

            structlog.get_logger().info(test_bytes.getbuffer().nbytes)

        except ClientDisconnect:
            structlog.get_logger().error("Client Disconnect")
            structlog.get_logger().info(test_bytes.getbuffer().nbytes)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        except Exception as err:
            structlog.get_logger().error("Failed: {}".format(err))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return status.HTTP_200_OK

    return test_router