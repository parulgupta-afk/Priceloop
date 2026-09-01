from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_products():
    # TODO: return paginated products for the current user
    return []


@router.post("/")
def create_product():
    # TODO: create product + associated listings, schedule first scrape
    raise NotImplementedError


@router.get("/{product_id}")
def get_product(product_id: str):
    # TODO: return product detail with current price, history, competitors
    raise NotImplementedError
