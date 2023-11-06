import smartpy as sp

@sp.module
def main():
    class MyContract(sp.Contract):
        def __init__(self, artist_address):
            self.data.artist = artist_address
            self.data.artworks = sp.big_map()
        
        @sp.entry_point
        def generate_certificate(self, params):
            self.check_artwork_does_not_exist(params.id)
            self.check_sender_is_artist()
            self.data.artworks[params.id] = sp.record(
                owner=self.data.artist,
                sold=False,
                properties=params.properties
            )

        @sp.entry_point
        def modify_artwork(self, params):
            artwork = self.get_artwork(params.id)
            self.check_sender_is_owner_or_artist(artwork)
            artwork.properties = params.properties

        @sp.entry_point
        def transfer_artwork(self, params):
            artwork = self.get_artwork(params.id)
            self.check_sender_is_owner(artwork)
            self.check_positive_price(params.purchase_price)
            artwork.owner = params.new_owner
            artwork.properties.last_purchase_price = params.purchase_price
            self.data.artworks[params.id] = artwork

        @sp.entry_point
        def update_sale_price(self, params):
            artwork = self.get_artwork(params.id)
            self.check_sender_is_owner(artwork)
            self.check_positive_price(params.sale_price)
            artwork.properties.sale_price = params.sale_price
            self.data.artworks[params.id] = artwork
        
        @sp.private(with_storage="read-only")
        def check_artwork_does_not_exist(self, id):
            assert not self.data.artworks.contains(id), "Artwork ID already exists"

        @sp.private(with_storage="read-only")
        def get_artwork(self, id):
            assert self.data.artworks.contains(id), "Artwork does not exist"
            return self.data.artworks[id]
        
        @sp.private(with_storage="read-only")
        def check_sender_is_artist(self):
            assert sp.sender == self.data.artist, "Sender is not the artist"

        @sp.private
        def check_sender_is_owner(self, artwork):
            assert sp.sender == artwork.owner, "Not authorized"

        @sp.private(with_storage="read-only")
        def check_sender_is_owner_or_artist(self, artwork):
            assert sp.sender == artwork.owner or sp.sender == self.data.artist, "Not authorized"

        @sp.private
        def check_positive_price(self, price):
            assert price > 0, "Price must be positive"
            
@sp.add_test(name="Artwork Test")
def test():
    scenario = sp.test_scenario(main)
    scenario.h1("Artwork Test")

    artist_address = sp.address("tz1ArtistAddress1234567890")
    buyer_address = sp.address("tz1BuyerAddress1234567890")
    contract = main.MyContract(artist_address)
    scenario += contract

    properties = sp.record(
        title="Mona Lisa",
        url="https://image.url",
        creation_date=sp.now,
        type="Painting",
        styles=["Renaissance", "Portrait"],
        sale_price=1000,
        last_purchase_price=0,
        dimensions="70x53 cm",
        description="A masterpiece",
        edition_number=1
    )
    contract.generate_certificate(id=1, properties=properties).run(sender=artist_address)
    contract.transfer_artwork(id=1, new_owner=buyer_address, purchase_price=1100).run(sender=artist_address)
    contract.update_sale_price(id=1, sale_price=2000).run(sender=artist_address, valid=False)
    contract.update_sale_price(id=1, sale_price=1400).run(sender=buyer_address)
