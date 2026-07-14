from check_category_match import check_category_match
from check_descriptions import check_descriptions
from check_duplicates import check_duplicates
from check_locations import check_locations
from check_stale import check_stale
from check_types import check_types
from validate import validate
from validate_urls_normalized import validate_urls_normalized


def validate_all():
    validate()
    check_duplicates()
    check_locations()
    check_types()
    check_category_match()
    check_descriptions()
    validate_urls_normalized()
    check_stale()


if __name__ == "__main__":
    validate_all()
