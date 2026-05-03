"""
API Gateway — reverse proxy logic using httpx.
"""
import httpx
from fastapi import Request, Response, HTTPException


async def proxy_request(request: Request, target_url: str) -> Response:
    """Forward a request to a downstream microservice."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Build the proxied request
            url = target_url
            
            # Forward query params
            if request.query_params:
                url += "?" + str(request.query_params)

            # Get request body
            body = await request.body()

            # Forward the request
            response = await client.request(
                method=request.method,
                url=url,
                content=body if body else None,
                headers={
                    "content-type": request.headers.get("content-type", "application/json"),
                    "accept": "application/json",
                },
            )

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers={"content-type": response.headers.get("content-type", "application/json")},
            )
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Service unavailable")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Service timeout")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gateway error: {str(e)}")
