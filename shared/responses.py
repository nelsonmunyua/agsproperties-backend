class ApiResponse:

    @staticmethod
    def success(data=None, message="Success", status_code=200):
        payload = {
            "success": True,
            "message": message,
        }

        if data is not None:
            payload["data"] = data

        return payload, status_code

    @staticmethod
    def created(data=None, message="Created successfully."):
        return ApiResponse.success(
            data=data,
            message=message,
            status_code=201,
        )