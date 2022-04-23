import unittest


from bitfield import BitFieldMeta


class TestBitfield(unittest.TestCase):

    def test_define_bitfield(self):

        class DateBitField(metaclass=BitFieldMeta):
            day: 5

    def test_instantiate_default_bitfield(self):

        class DateBitField(metaclass=BitFieldMeta):
            day: 5

        _ = DateBitField()

    def test_instantiate_bitfield_with_named_argument(self):

        class DateBitField(metaclass=BitFieldMeta):
            day: 5

        _ = DateBitField(day=23)

    def test_bitfield_without_fields_raises_type_error(self):

        with self.assertRaises(TypeError):

            class EmptyBitField(metaclass=BitFieldMeta):
                pass

    def test_mismatched_constructor_argument_names_raises_type_error(self):

        class DateBitField(metaclass=BitFieldMeta):
            day: 5
            month: 4
            year: 14

        with self.assertRaises(TypeError) as exc_info:
            _ = DateBitField(day=13, m=5, yr=1999)

        self.assertEqual(
            str(exc_info.exception),
            "DateBitField.__init__() got unexpected keyword arguments: 'm', 'yr'"
        )

    def test_non_integer_annotation_value_raises_type_error(self):

        with self.assertRaises(TypeError) as exc_info:

            class DateBitField(metaclass=BitFieldMeta):
                day: "Wednesday"

        self.assertEqual(
            str(exc_info.exception),
            "DateBitField field 'day' has annotation 'Wednesday' "
            "that is not an integer"
        )

    def test_zero_field_width_raises_type_error(self):

        with self.assertRaises(TypeError) as exc_info:

            class DateBitField(metaclass=BitFieldMeta):
                day: 0

        self.assertEqual(
            str(exc_info.exception),
            "DateBitField field 'day' has non-positive field width 0"
        )

    def test_negative_field_width_raises_type_error(self):

        with self.assertRaises(TypeError) as exc_info:

            class DateBitField(metaclass=BitFieldMeta):
                day: -1

        self.assertEqual(
            str(exc_info.exception),
            "DateBitField field 'day' has non-positive field width -1"
        )

    def test_field_name_with_leading_underscore_raises_type_error(self):

        with self.assertRaises(TypeError) as exc_info:

            class DateBitField(metaclass=BitFieldMeta):
                _day: 5

        self.assertEqual(
            str(exc_info.exception),
            "DateBitField field '_day' begins with an underscore"
        )

    def test_initialization_out_of_lower_field_range_raises_value_error(self):

        class DateBitField(metaclass=BitFieldMeta):
            day: 5

        with self.assertRaises(ValueError) as exc_info:
            _ = DateBitField(day=-1)

        self.assertEqual(
            str(exc_info.exception),
            "DateBitField field 'day' got value -1 "
            "which is out of range 0-31 for a 5-bit field"
        )


    def test_initialization_out_of_upper_field_range_raises_value_error(self):

        class DateBitField(metaclass=BitFieldMeta):
            day: 5

        with self.assertRaises(ValueError) as exc_info:
            _ = DateBitField(day=32)

        self.assertEqual(
            str(exc_info.exception),
            "DateBitField field 'day' got value 32 "
            "which is out of range 0-31 for a 5-bit field"
        )


    def test_fields_are_default_initialized_to_zero(self):

        class DateBitField(metaclass=BitFieldMeta):
            day: 5

        d = DateBitField()

        self.assertEqual(d.day, 0)


    def test_initialized_field_values_can_be_retrieved(self):

        class DateBitField(metaclass=BitFieldMeta):
            day: 5

        d = DateBitField(day=17)

        self.assertEqual(d.day, 17)


    def test_conversion_to_integer(self):

        class DateBitField(metaclass=BitFieldMeta):
            day: 5
            month: 4
            year: 14

        d = DateBitField(day=25, month=3, year=2010)
        i = int(d)
        self.assertEqual(
            i,
            0b00011111011010_0011_11001
            # <--------2010> <-3> <-25>
        )

    def test_conversion_to_bytes(self):

        class DateBitField(metaclass=BitFieldMeta):
            day: 5
            month: 4
            year: 14

        d = DateBitField(day=25, month=3, year=2010)
        b = d.to_bytes()
        self.assertEqual(
            b,
            (0b00011111011010_0011_11001).to_bytes(3, "little", signed=False)
            #  <--------2010> <-3> <-25>
        )

    def test_assigning_to_field_sets_value(self):

        class DateBitField(metaclass=BitFieldMeta):
            day: 5

        d = DateBitField()
        d.day = 26
        self.assertEqual(d.day, 26)


    def test_assigning_out_of_lower_range_value_to_field_raises_value_error(self):

        class DateBitField(metaclass=BitFieldMeta):
            day: 5

        d = DateBitField()
        with self.assertRaises(ValueError) as exc_info:
            d.day = -1

        self.assertEqual(
            str(exc_info.exception),
            "DateBitField field 'day' got value -1 "
            "which is out of range 0-31 for a 5-bit field"
        )


    def test_assigning_out_of_upper_range_value_to_field_raises_value_error(self):

        class DateBitField(metaclass=BitFieldMeta):
            day: 5

        d = DateBitField()
        with self.assertRaises(ValueError) as exc_info:
            d.day = 32

        self.assertEqual(
            str(exc_info.exception),
            "DateBitField field 'day' got value 32 "
            "which is out of range 0-31 for a 5-bit field"
        )

if __name__ == '__main__':
    unittest.main()
