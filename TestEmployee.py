import unittest
from employee import Employee
from unittest.mock import patch


class TestEmployee(unittest.TestCase):

    def setUp(self):
        self.emp_1 = Employee('Umesh', 'Gawde', 5000)
        self.emp_2 = Employee('Pratiksha', 'Gawde', 5000)

    def tearDown(self):
        pass

    def test_email(self):

        self.assertEqual(self.emp_1.email, 'Umesh.Gawde@email.com')
        self.assertEqual(self.emp_2.email, 'Pratiksha.Gawde@email.com')

    def test_full_name(self):

        self.assertEqual(self.emp_1.full_name, 'Umesh Gawde')
        self.assertEqual(self.emp_2.full_name, 'Pratiksha Gawde')

    def test_apply_raise(self):

        self.emp_1.apply_raise()
        self.emp_2.apply_raise()

        self.assertEqual(self.emp_1.pay, 7500)
        self.assertEqual(self.emp_2.pay, 7500)

    def test_monthly_schedule(self):
        with patch('employee.request.get') as mocked_get:
            mocked_get.return_value.ok = True
            mocked_get.return_value.text = 'Success'

            schedule = self.emp_1.monthly_schedule('May')
            mocked_get.assert_called_with('http://company.com/Gawde/May')
            self.assertEqual(schedule, 'Success')

if __name__ == '__main__':
    unittest.main()
