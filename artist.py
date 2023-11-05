import smartpy as sp

### Artwork data structure (sp.map)
'''
"artwork_name" = {
    "artwork_type"  : type,
    "artist_name"   : artist_name,
    "creation_date" : date,
    "current_owner" : owner,
    "property1"     : ...,
    "property2"     : ...
}
'''

@sp.module
def main():
    
    class Artist(sp.Contract):
        def __init__(self, artist_name, artist_address):
            self.data.artist_name = artist_name
            self.data.admin = artist_address
            self.data.artworks = {}

        @sp.private()
        def art_types(self):
            return sp.set("Drawing", "Painting", "Photography", "Sculpture")

        @sp.entrypoint
        def add_artwork(self, artwork_name, artwork_type, date):
            # First need to verify that the owner of the SC is calling the entrypoint
            assert sp.sender == self.data.admin
            # Check artwork type is known
            assert self.art_types().contains(artwork_type)
            # Verify that the artwork name is unique
            for name in self.data.artworks.keys():
                assert artwork_name != name
                
            sp.cast(artwork_name, sp.string)
            self.data.artworks[artwork_name] = {
                "artwork_type"  : artwork_type,
                "artist_name"   : self.data.artist_name,
                "creation_date" : date,                     # Type sp.timestamp creates an error, don't know how to cast to sp.string
                "current_owner" : self.data.artist_name
            }

        @sp.entrypoint
        def add_property(self, artwork_name, property_name, value):
            assert sp.sender == self.data.admin
            sp.cast(property_name, sp.string)
            sp.cast(value, sp.string)
            self.data.artworks[artwork_name][property_name] = value


@sp.add_test(name="Artist")
def test():
    artist_address = sp.test_account("Picasso").address
    bob_address = sp.test_account("Bob").address
    
    s = sp.test_scenario(main)
    s.h1("Artist")
    c1 = main.Artist("Picasso", artist_address)
    s += c1

    c1.add_artwork(artwork_name = "Guernica", artwork_type = "Painting", date = "01-06-1937").run(sender = artist_address)
    c1.add_property(artwork_name = "Guernica", property_name = "dimensions", value = "h:349 - w:777 (cm)").run(sender = artist_address)

    ### Errors
    # Adding artwork with same name
    c1.add_artwork(artwork_name = "Guernica", artwork_type = "Drawing", date = "01-01-1950").run(sender = artist_address, valid = False)
    # Adding artwork with invalid artwork type
    c1.add_artwork(artwork_name = "Avatar", artwork_type = "Movie", date = "01-01-1950").run(sender = artist_address, valid = False)
    # Trying to add property to none-existing artwork
    c1.add_property(artwork_name = "Guernico", property_name = "dimensions", value = "h: 349cm - w: 777cm").run(sender = artist_address, valid = False)
    # Adding artwork if not admin
    c1.add_artwork(artwork_name = "Blabla", artwork_type = "Photography", date = "01-01-1950").run(sender = bob_address, valid = False)
    # Adding property if not admin
    c1.add_property(artwork_name = "Guernica", property_name = "weight", value = "5 kg").run(sender = bob_address, valid = False)

