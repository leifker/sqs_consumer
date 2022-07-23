from project.database_models import UserLogins
from datetime import datetime


class TestModels:

    def test_mask(self):
        test = UserLogins(
                user_id="abc",
                device_type="mobile",
                masked_ip="127.0.0.1",
                masked_device_id="89ABCDEF-01234567-89ABCDEF",
                locale="us",
                app_version=1,
                create_date=datetime.utcnow()
            )

        assert test.masked_ip == "12ca17b49af2289436f303e0166030a21e525d266e209267433801a8fd4071a0"
        assert test.masked_device_id == "e5e25c45362fb8d4ca13845b5d4c043e77b03616ac6b75748386a03c4d490bf2"
