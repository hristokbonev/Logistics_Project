from commands.validation_helpers import validate_params_count
from core.application_data import ApplicationData
from models.user import User


class AddUserCommand:
    def __init__(self, params, app_data: ApplicationData):
        validate_params_count(params, 3)
        self._params = params
        self._app_data = app_data

    def execute(self):
        user_id, name, contact_info = self._params
        new_user = User(user_id, name, contact_info)
        self._app_data.users.append(new_user)
        return f'User {user_id} was added successfully!'