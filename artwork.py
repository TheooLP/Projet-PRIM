import smartpy as sp

# One contract for each artist, but when an artwork is added, a contract is created

@sp.module
def main():
    class Artwork(sp.Contract):
        def __init__(self, params):
            self.data.id = sp.nat(0)
            self.data.artist = params.artist
            self.data.owner = params.artist
            self.data.sold = False
            self.data.properties = params.properties

        @sp.entry_point
        def modify_artwork(self, properties):
            self.check_sender_is_owner_or_artist()
            self.data.properties = properties

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

    class Artist(sp.Contract):
        def __init__(self, artist_address):
            self.data.artist = artist_address
            self.data.artwork_contracts = sp.set()

        # Params :
        #    - id
        #    - properties
        @sp.entry_point
        def generate_certificate(self, id, properties):
            params = sp.record(
                id = id,
                artist = self.data.artist,
                owner = self.data.artist,
                sold = False,
                properties = properties
            )
            a = sp.create_contract(Artwork, None, sp.mutez(0), params)
            self.data.artwork_contracts.add(a)
            
@sp.add_test(name="Artwork Test")
def test():
    scenario = sp.test_scenario(main)
    scenario.h1("Artwork Test")

    artist_address = sp.address("tz1ArtistAddress1234567890")
    buyer_address = sp.address("tz1BuyerAddress1234567890")
    contract = main.Artist(artist_address)
    scenario += contract

    properties0 = sp.record(
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
    contract.generate_certificate(id=0, properties=properties0).run(sender=artist_address)
    properties1 = sp.record(
        title="La Cene",
        url="https://image.url",
        creation_date=sp.now,
        type="Painting",
        styles=["Art chretien", "Peinture d'histoire"],
        sale_price=300,
        last_purchase_price=0,
        dimensions="460×880 cm",
        description="Refectoire de couvent",
        edition_number=2
    )
    contract.generate_certificate(id=0, properties=properties1).run(sender=artist_address)
