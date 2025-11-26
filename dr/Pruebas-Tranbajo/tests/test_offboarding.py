import unittest
from unittest.mock import MagicMock

from services.access_management_service import AccessManagementService


class OffboardingInactiveAccessTest(unittest.TestCase):
    def setUp(self):
        # Crear instancia sin ejecutar __init__
        self.service = AccessManagementService.__new__(AccessManagementService)
        self.service.db_manager = MagicMock()

    def _build_mock_connection(self, rows):
        cursor = MagicMock()
        cursor.description = [
            ('id',),
            ('app_access_name',),
            ('process_access',),
            ('record_date',),
            ('subunit',),
            ('event_description',),
        ]
        cursor.fetchall.return_value = rows

        conn = MagicMock()
        conn.cursor.return_value = cursor
        return conn, cursor

    def test_offboarding_skips_inactive_applications(self):
        scotia_id = "EMP001"
        responsible = "tester"

        self.service.get_employee_by_id = MagicMock(return_value={"scotia_id": scotia_id})

        rows = [
            (1, 'ActiveApp', 'onboarding', '2024-01-01', 'Unidad', 'Desc'),
            (2, 'InactiveApp', 'onboarding', '2024-01-02', 'Unidad', 'Desc'),
        ]
        conn_select, cursor_select = self._build_mock_connection(rows)
        conn_update = MagicMock()
        conn_update.cursor.return_value = MagicMock()

        self.service.get_connection = MagicMock(side_effect=[conn_select, conn_update])

        def fake_app_info(name):
            status = 'Active' if name == 'ActiveApp' else 'Inactive'
            return {'access_status': status}

        self.service._get_application_by_name = MagicMock(side_effect=fake_app_info)
        self.service.create_historical_record = MagicMock(return_value=(True, "ok"))

        success, message, records = self.service.process_employee_offboarding(scotia_id, responsible)

        self.assertTrue(success)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['app_access_name'], 'ActiveApp')
        self.service.create_historical_record.assert_called_once()


if __name__ == "__main__":
    unittest.main()

