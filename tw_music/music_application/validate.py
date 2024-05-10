import re    
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _  
from difflib import SequenceMatcher

class MinimumLengthValidator:
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("Your password must contain at least 8 characters."),
                
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least %(self.min_length)d characters."
            % {'min_length': self.min_length}
        )


class NumericPasswordValidator:
    """
    Validate whether the password is alphanumeric.
    """
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                _("Your password can't be entirely numeric."),
                code='password_entirely_numeric',
            )

    def get_help_text(self):
        return _("Your password can't be entirely numeric.")


class UserAttributeSimilarityValidator:
    """
    Validate whether the password is sufficiently different from the user's
    attributes.

    If no specific attributes are provided, look at a sensible list of
    defaults. Attributes that don't exist are ignored. Comparison is made to
    not only the full attribute value, but also its components, so that, for
    example, a password is validated against either part of an email address,
    as well as the full address.
    """
    DEFAULT_USER_ATTRIBUTES = ('username', 'email')

    def __init__(self, user_attributes=DEFAULT_USER_ATTRIBUTES, max_similarity=0.7):
        self.user_attributes = user_attributes
        self.max_similarity = max_similarity

    def validate(self, password, user_attributes_array, user=None, ):
        
        for attribute_name in user_attributes_array:
            value = attribute_name
            if not value or not isinstance(value, str):
                continue
            value_parts = re.split(r'\W+', value) + [value]
            for value_part in value_parts:

                if SequenceMatcher(a=password.lower(), b=value_part.lower()).quick_ratio() >= self.max_similarity:

                    # try:
                    #     verbose_name = str(user._meta.get_field(attribute_name).verbose_name)
                    # except FieldDoesNotExist:
                    verbose_name = attribute_name
                    raise ValidationError(
                        _("Your password can't be too similar to your other personal information.")
                    )

    def get_help_text(self):
        return _("Your password can't be too similar to your other personal information.")