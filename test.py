import traceback
from env.models import Supplier
try:
    print(Supplier(supplier_id='x', name='x', location='x', capacity_per_day=1, cost_per_unit=1.0, lead_time_days=1, reliability_score=1.0, available_skus=[], lat=1.0, lng=1.0))
except BaseException as e:
    traceback.print_exc()
