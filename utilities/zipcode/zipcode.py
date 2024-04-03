import posuto


def zipcode_to_address(zipcode):
    tt = posuto.get(str(zipcode))
    return {
        "prefecture": tt.prefecture,
        "city": tt.city,
        "neighborhood": tt.neighborhood,
    }
