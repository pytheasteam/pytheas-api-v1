import os

SERVER_SECRET_KEY = os.environ.get('SERVER_SECRET_KEY')
PROFILE_REMOVE_SP = 'pytheas.delete_profile'
PROFILE_RATE_SET_SP = 'pytheas.set_profile_attraction_rate'
TRIP_UPDATE_RSRV_SP = 'pytheas.update_profile_trip_rsrv'
UPSERT_TRIP_FLIGHT_SP = 'pytheas.upsert_trip_flight'

DEFAULT_STARS = "Not Specified"