from api.models.attraction import Attraction
from api.models.city import City
from api.models.tag_attraction import TagAttraction
from api.models.user_trip_profile import ProfileTag


def agent_mock_call_stub(profile_id, city_id):
    tags_id = [tag.tag_id for tag in ProfileTag.query.filter_by(profile_id=profile_id)]
    attractions = Attraction.query.filter_by(city_id=city_id)
    chosen_attractions = []
    for attraction in attractions:
        try:
            at_tag = TagAttraction.query.filter_by(attraction_id=attraction.id)
        except Exception:
            pass
        else:
            try:
                attraction_tags = [
                    tag.tag_id for tag in at_tag
                ]
                if list(set(tags_id) & set(attraction_tags)):
                    chosen_attractions.append({
                        'id': attraction.id,
                        'name': attraction.name,
                        'rate': attraction.rate,
                        'address': attraction.address,
                        'price': attraction.price,
                        'description': attraction.description,
                        'phone number': attraction.phone_number,
                        'website': attraction.website,
                        'city': City.query.get(attraction.city_id).name
                    })
            except Exception as e:
                print(e)
    return chosen_attractions