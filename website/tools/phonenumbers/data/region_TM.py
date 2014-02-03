"""Auto-generated file, do not edit by hand. TM metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_TM = PhoneMetadata(id='TM', country_code=993, international_prefix='810',
    general_desc=PhoneNumberDesc(national_number_pattern='[1-6]\\d{7}', possible_number_pattern='\\d{8}'),
    fixed_line=PhoneNumberDesc(national_number_pattern='(?:1(?:2\\d|3[1-9])|2(?:22|4[0-35-8])|3(?:22|4[03-9])|4(?:22|3[128]|4\\d|6[15])|5(?:22|5[7-9]|6[014-689]))\\d{5}', possible_number_pattern='\\d{8}', example_number='12345678'),
    mobile=PhoneNumberDesc(national_number_pattern='6[3-8]\\d{6}', possible_number_pattern='\\d{8}', example_number='66123456'),
    toll_free=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    premium_rate=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    shared_cost=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    personal_number=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    voip=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    pager=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    uan=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    emergency=PhoneNumberDesc(national_number_pattern='0[1-3]', possible_number_pattern='\\d{2}', example_number='03'),
    voicemail=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    no_international_dialling=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    preferred_international_prefix='8~10',
    national_prefix='8',
    national_prefix_for_parsing='8',
    number_format=[NumberFormat(pattern='(\\d{2})(\\d{2})(\\d{2})(\\d{2})', format=u'\\1 \\2-\\3-\\4', leading_digits_pattern=['12'], national_prefix_formatting_rule=u'(8 \\1)'),
        NumberFormat(pattern='(\\d{2})(\\d{6})', format=u'\\1 \\2', leading_digits_pattern=['6'], national_prefix_formatting_rule=u'8 \\1'),
        NumberFormat(pattern='(\\d{3})(\\d)(\\d{2})(\\d{2})', format=u'\\1 \\2-\\3-\\4', leading_digits_pattern=['13|[2-5]'], national_prefix_formatting_rule=u'(8 \\1)')])
