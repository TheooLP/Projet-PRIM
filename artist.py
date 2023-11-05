import smartpy as sp

### Artwork data structure (sp.map)
'''
"artwork_name" = {
    "artwork_type"  : type,
    "artist_name"   : artist_name,
    "creation_date" : date,
    "current_owner" : owner,
    "properties"    : {            # Depends on the artwork type (sp.map)
        ...
    }
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
        def art_types():
            return sp.set("Drawing", "Painting", "Photography", "Sculpture")

        @sp.entrypoint
        def add_artwork(self, artwork_name, artwork_type):
            # First need to verify that the owner of the SC is calling the entrypoint
            assert sp.sender == self.data.admin
            # Check artwork type is known
            assert art_types().contains(artwork_type)
            # Verify that the artwork name is unique
            assert artwork_name not in self.data.artworks.keys()
            self.data.artworks[artwork_name] = {
                "artwork_type"  : artwork_type,
                "artist_name"   : self.data.artist_name,
                "creation_date" : sp.now,
                "current_owner" : self.data.admin,
                "properties"    : {}
            }

        @sp.entrypoint
        def add_property(self, artwork_name, property_name, value):
            assert artwork_name in self.data.artworks.keys()
            assert property_name not in self.data.artworks[artwork_name]["properties"].keys()
            self.data.artworks[artwork_name]["properties"][property_name] = value


@sp.add_test(name="Artist")
def test():
    artist_address = sp.test_account("Picasso").address
    bob_address = sp.test_account("Bob").address
    
    s = sp.test_scenario(main)
    s.h1("Artist")
    c1 = main.Artist("Picasso", artist_address)
    s += c1
    
