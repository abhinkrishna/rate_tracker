class RateValidator:
    @staticmethod
    def is_valid(data: dict) -> bool:
        """
        Checks if the provided data dictionary is suitable for the Rate model.
        Fields: provider, currency, rate_type, rate_value, effective_date, ingestion_ts, raw_response_id
        """
        if not isinstance(data, dict):
            return False

        required_fields = [
            "provider",
            "currency",
            "rate_type",
            "rate_value",
            "effective_date",
            "ingestion_ts",
        ]

        # 1. Existence Check
        for field in required_fields:
            if field not in data or data[field] is None:
                return False

        # 2. Type & Compatibility Checks
        try:
            # Check if rate_value is numeric
            float(data["rate_value"])

            # Basic check: non-empty strings or date/datetime objects
            if not str(data["effective_date"]):
                return False
            if not str(data["ingestion_ts"]):
                return False

        except (ValueError, TypeError, KeyError):
            return False

        return True
