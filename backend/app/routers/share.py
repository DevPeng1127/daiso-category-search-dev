"""Share router - provides product info for mobile QR sharing"""
from fastapi import APIRouter, HTTPException

from app.models.schemas import ShareResponse, ProductResult, MapInfo, Waypoint
from app.services.product_service import ProductService
from app.data.store_locations import get_location, build_waypoints, get_start_position

router = APIRouter(tags=["share"])
product_service = ProductService()


@router.get("/share/{product_id}", response_model=ShareResponse)
async def get_shared_product(product_id: int) -> ShareResponse:
    """Get product info and map data for mobile sharing"""
    product_dict = product_service.get_product_by_id(product_id)
    if not product_dict:
        raise HTTPException(status_code=404, detail="Product not found")

    category_middle = product_dict.get("category_middle")
    location = get_location(category_middle)

    if location:
        floor = location.floor
        start = get_start_position(floor)
        waypoint_list = build_waypoints(
            location.x, location.y, floor, location.zone_id
        )

        product_result = ProductResult(
            id=product_dict["id"],
            rank=product_dict.get("rank") or 0,
            name=product_dict["name"],
            price=product_dict.get("price") or 0,
            image_url=product_dict.get("image_url", ""),
            category_major=product_dict.get("category_major"),
            category_middle=category_middle,
            counter_number=location.counter_number,
            destination_x=location.x,
            destination_y=location.y,
            location_floor=floor,
            location_description=location.section_description,
            zone_id=location.zone_id,
        )

        map_info = MapInfo(
            floor=floor,
            section=product_dict.get("category_major", ""),
            map_image=f"/maps/map_{floor.lower()}.jpg",
            counter_number=location.counter_number,
            section_description=location.section_description,
            destination=Waypoint(x=location.x, y=location.y),
            start=Waypoint(x=start["x"], y=start["y"]),
            waypoints=[Waypoint(x=w["x"], y=w["y"]) for w in waypoint_list],
        )
    else:
        product_result = ProductResult(
            id=product_dict["id"],
            rank=product_dict.get("rank") or 0,
            name=product_dict["name"],
            price=product_dict.get("price") or 0,
            image_url=product_dict.get("image_url", ""),
            category_major=product_dict.get("category_major"),
            category_middle=category_middle,
        )

        map_info = MapInfo()

    return ShareResponse(product=product_result, map_info=map_info)
