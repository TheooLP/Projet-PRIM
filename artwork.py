import smartpy as sp

# One contract for each artist, but when an artwork is added, a contract is created

@sp.module
def main():
    class Artist(sp.Contract):
        def __init__(self, artist_address):
            self.data.artist = artist_address
            self.data.artwork_contracts = sp.set()

        @sp.entry_point
        def generate_certificate(self, properties):
            

    
    class Artwork(sp.Contract):
        def __init__(self, properties):
            self.id = sp.self_address
            self.data.artist = sp.sender
            self.data.owner = sp.sender
            self.data.sold = False
            self.data.properties = properties

        @sp.entry_point
        def modify_artwork(self, properties):
            self.check_sender_is_owner_or_artist(artwork)
            artwork.properties = properties

        @sp.entry_point
        def transfer_artwork(self, params):
            self.check_sender_is_owner()
            self.check_positive_price(params.purchase_price)
            self.data.owner = params.new_owner
            self.data.properties.last_purchase_price = params.purchase_price

        @sp.entry_point
        def update_sale_price(self, params):
            self.check_sender_is_owner()
            self.check_positive_price(params.sale_price)
            self.data.properties.sale_price = params.sale_price
        
        @sp.private(with_storage="read-only")
        def check_sender_is_artist(self):
            assert sp.sender == self.data.artist, "Sender is not the artist"

        @sp.private(with_storage="read-only")
        def check_sender_is_owner(self):
            assert sp.sender == self.data.owner, "Not authorized"

        @sp.private(with_storage="read-only")
        def check_sender_is_owner_or_artist(self):
            assert sp.sender == self.data.owner or sp.sender == self.data.artist, "Not authorized"

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
