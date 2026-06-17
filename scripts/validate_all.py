from check_category_match import check_category_match
from check_descriptions import check_descriptions
from check_duplicates import check_duplicates
from check_regions import check_regions
from validate import validate
from validate_urls_normalized import validate_urls_normalized


def validate_all():
    validate()
    check_duplicates()
    check_regions()
    check_category_match()
    check_descriptions()
    validate_urls_normalized()


if __name__ == "__main__":
    validate_all()
